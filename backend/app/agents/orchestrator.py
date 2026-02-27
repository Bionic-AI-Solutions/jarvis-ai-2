"""Workflow orchestrator — executes workflows step-by-step via local agents.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 11
Role: Central coordinator with 6-level backtracking
Dispatch: In-process — calls agent.process() directly via AgentRegistry

Recovery Levels:
  L1: Timeout retry with exponential backoff (3x, 1.5x multiplier)
  L2: Alternative method (npm↔yarn, PowerShell↔CMD, etc.)
  L3: Re-verification with screenshot + analysis
  L4: Replan with SAA (LLM-based replanning)
  L5: User confirmation dialog (retry/skip/cancel)
  L6: Mark impossible
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Optional

from app.agents.registry import AgentRegistry, AgentStatus, agent_registry
from app.config import get_settings
from app.core.errors import ErrorCode
from app.core.exceptions import AgentError, WorkflowError
from app.core.logging_config import get_logger
from app.routes.ws import manager as ws_manager
from app.services.desktop_automation import DesktopAutomationService
from app.services.recovery_engine import (
    RecoveryContext,
    RecoveryEngine,
    RecoveryLevel as RecoveryLevelEnum,
    recovery_engine,
)
from app.services.vision_service import VisionService

logger = get_logger(__name__)


class RecoveryLevel:
    """Constants for recovery levels (kept for backward compat)."""

    L1_RETRY = 1
    L2_SKIP = 2
    L3_ROLLBACK = 3
    L4_ABORT = 4


class WorkflowOrchestrator:
    """Executes workflows by dispatching steps to agents.

    Manages execution lifecycle, step-by-step progress,
    WebSocket notifications, and recovery on failure.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        max_retries: int = 3,
        base_backoff_seconds: float = 1.0,
        recovery: RecoveryEngine | None = None,
    ) -> None:
        self.registry = registry or agent_registry
        self.max_retries = max_retries
        self.base_backoff = base_backoff_seconds
        self.recovery = recovery or recovery_engine
        self._running_executions: Dict[str, bool] = {}
        self._paused_executions: Dict[str, asyncio.Event] = {}
        self._user_confirm_futures: Dict[str, asyncio.Future] = {}

        # Services for screenshot/vision-based verification & recovery
        self._desktop = DesktopAutomationService()
        self._vision = VisionService()

        # Lazy-loaded observer — resolved from registry on first use
        self._observer: Any | None = None

    async def execute_workflow(
        self,
        execution_id: str,
        steps: list[Dict[str, Any]],
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        """Run a full workflow execution.

        Args:
            execution_id: Unique execution ID (from DB).
            steps: List of step dicts with agent, action, parameters, etc.
            session_id: Optional chat session for context.

        Returns:
            Summary dict with status, completed_steps, total_steps.
        """
        self._running_executions[execution_id] = True
        total = len(steps)
        completed = 0
        failed_steps: list[Dict[str, Any]] = []

        # Notify: plan_ready
        await ws_manager.broadcast_to_execution(execution_id, {
            "type": "plan_ready",
            "execution_id": execution_id,
            "total_steps": total,
            "steps": [{"index": i, "agent": s.get("agent", "unknown"), "action": s.get("action", "")} for i, s in enumerate(steps)],
        })

        for idx, step in enumerate(steps):
            # Check if cancelled
            if not self._running_executions.get(execution_id, False):
                logger.info("workflow_cancelled_mid_execution", execution_id=execution_id, step=idx)
                return {
                    "status": "cancelled",
                    "completed_steps": completed,
                    "total_steps": total,
                    "failed_steps": failed_steps,
                }

            # Check if paused — wait until resumed or auto-resume after 30 min
            pause_event = self._paused_executions.get(execution_id)
            if pause_event is not None and not pause_event.is_set():
                await ws_manager.broadcast_to_execution(execution_id, {
                    "type": "execution_paused",
                    "execution_id": execution_id,
                    "step_index": idx,
                    "completed_steps": completed,
                })
                try:
                    await asyncio.wait_for(pause_event.wait(), timeout=1800)  # 30 min auto-resume
                except asyncio.TimeoutError:
                    logger.warning("pause_auto_resumed", execution_id=execution_id, timeout_seconds=1800)
                await ws_manager.broadcast_to_execution(execution_id, {
                    "type": "execution_resumed",
                    "execution_id": execution_id,
                    "step_index": idx,
                })

            # Re-check cancellation after resume
            if not self._running_executions.get(execution_id, False):
                return {
                    "status": "cancelled",
                    "completed_steps": completed,
                    "total_steps": total,
                    "failed_steps": failed_steps,
                }

            agent_name = step.get("agent", "unknown")
            action = step.get("action", "")
            params = step.get("parameters", {})
            skippable = step.get("skippable", False)

            # Notify: step_started
            await ws_manager.broadcast_to_execution(execution_id, {
                "type": "step_started",
                "execution_id": execution_id,
                "step_index": idx,
                "agent": agent_name,
                "action": action,
            })

            result = await self._execute_step_with_recovery(
                execution_id=execution_id,
                step_index=idx,
                agent_name=agent_name,
                action=action,
                parameters=params,
                skippable=skippable,
            )

            step_status = "success" if result.get("success") else "failed"

            # Notify: step_complete (includes observation data when available)
            step_complete_msg: Dict[str, Any] = {
                "type": "step_complete",
                "execution_id": execution_id,
                "step_index": idx,
                "status": step_status,
                "duration_ms": result.get("duration_ms", 0),
            }
            if result.get("observation"):
                step_complete_msg["observation"] = {
                    "verified": result["observation"].get("verified", False),
                    "confidence": result["observation"].get("confidence", 0),
                }
            if result.get("recovery_level"):
                step_complete_msg["recovery_level"] = result["recovery_level"]
            await ws_manager.broadcast_to_execution(execution_id, step_complete_msg)

            if result.get("success"):
                completed += 1
            elif result.get("skipped"):
                completed += 1  # count skipped as completed
            else:
                failed_steps.append({"index": idx, "agent": agent_name, "error": result.get("error")})
                # L4 abort: stop execution on non-skippable failure
                await ws_manager.broadcast_to_execution(execution_id, {
                    "type": "error",
                    "execution_id": execution_id,
                    "step_index": idx,
                    "error_code": "WF_003",
                    "message": f"Step {idx} failed: {result.get('error', 'unknown')}",
                })
                break

        # Determine final status
        final_status = "completed" if completed == total else "failed"
        self._running_executions.pop(execution_id, None)
        self._paused_executions.pop(execution_id, None)

        # Notify: workflow_complete
        await ws_manager.broadcast_to_execution(execution_id, {
            "type": "workflow_complete",
            "execution_id": execution_id,
            "status": final_status,
            "completed_steps": completed,
            "total_steps": total,
        })

        return {
            "status": final_status,
            "completed_steps": completed,
            "total_steps": total,
            "failed_steps": failed_steps,
        }

    async def cancel(self, execution_id: str) -> None:
        """Signal a running execution to stop."""
        self._running_executions[execution_id] = False
        # If paused, wake it so it can see the cancel flag
        pause_event = self._paused_executions.pop(execution_id, None)
        if pause_event is not None:
            pause_event.set()
        logger.info("workflow_cancel_requested", execution_id=execution_id)

    async def pause(self, execution_id: str) -> None:
        """Pause execution at the next step boundary."""
        if execution_id not in self._running_executions:
            raise WorkflowError(ErrorCode.WORKFLOW_NOT_FOUND, detail="Execution not running")
        if execution_id in self._paused_executions and not self._paused_executions[execution_id].is_set():
            raise WorkflowError(ErrorCode.WORKFLOW_PAUSED, detail="Already paused")
        evt = asyncio.Event()
        self._paused_executions[execution_id] = evt
        logger.info("workflow_pause_requested", execution_id=execution_id)

    async def resume(self, execution_id: str) -> None:
        """Resume a paused execution."""
        evt = self._paused_executions.pop(execution_id, None)
        if evt is None:
            raise WorkflowError(ErrorCode.WORKFLOW_NOT_FOUND, detail="Execution not paused")
        evt.set()
        logger.info("workflow_resumed", execution_id=execution_id)

    def is_paused(self, execution_id: str) -> bool:
        """Check if an execution is currently paused."""
        evt = self._paused_executions.get(execution_id)
        return evt is not None and not evt.is_set()

    async def resolve_user_confirmation(
        self, execution_id: str, step_index: int, choice: str,
    ) -> None:
        """Called when user responds to L5 confirmation dialog."""
        key = f"{execution_id}:{step_index}"
        fut = self._user_confirm_futures.pop(key, None)
        if fut and not fut.done():
            fut.set_result({"action": choice})

    # ── Observer Integration (Fix #2) ───────────────────────

    def _get_observer(self):
        """Lazy-load observer agent from registry."""
        if self._observer is None:
            self._observer = self.registry.get_instance("observer_agent")
            if self._observer is None:
                # Fallback: instantiate directly (imported at module level)
                from app.agents.observer_agent import ObserverAgent
                self._observer = ObserverAgent(desktop_service=self._desktop)
                logger.info("observer_agent instantiated directly (not in registry)")
        return self._observer

    async def _observe_step(
        self,
        execution_id: str,
        step_index: int,
        step: Dict[str, Any],
        exec_result: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """Run observer validation on a single executed step.

        Returns observation dict or None if observer unavailable.
        """
        observer = self._get_observer()
        if observer is None:
            return None

        try:
            obs_result = await observer.process({
                "step": step,
                "exec_result": exec_result,
            })
            return obs_result.get("observation", {})
        except Exception as e:
            logger.warning("observer_step_failed", step=step_index, error=str(e))
            return None

    async def _execute_step_with_recovery(
        self,
        execution_id: str,
        step_index: int,
        agent_name: str,
        action: str,
        parameters: Dict[str, Any],
        skippable: bool = False,
    ) -> Dict[str, Any]:
        """Execute a single step with full 6-level recovery chain.

        Returns:
            Dict with success, duration_ms, data, error, skipped, recovery_level.
        """
        # First attempt (no recovery)
        result = await self._dispatch_to_agent(agent_name, action, parameters)

        # ── Observer validation (Fix #2) ────────────────────
        # If the agent reports success, run independent verification
        if result.get("success"):
            observation = await self._observe_step(
                execution_id=execution_id,
                step_index=step_index,
                step={"action": action, "parameters": parameters},
                exec_result=result.get("data", result),
            )
            if observation and not observation.get("verified", True):
                # Observer disagrees with the agent — treat as failure
                logger.warning(
                    "observer_mismatch",
                    execution_id=execution_id,
                    step=step_index,
                    action=action,
                    confidence=observation.get("confidence", 0),
                )
                result = {
                    "success": False,
                    "error": f"Observer verification failed (confidence {observation.get('confidence', 0):.0%})",
                    "data": result.get("data"),
                    "duration_ms": result.get("duration_ms", 0),
                    "observation": observation,
                }

        if result.get("success"):
            return result

        # Build recovery context
        async def _exec(a_name: str, a_action: str, a_params: dict) -> Any:
            r = await self._dispatch_to_agent(a_name, a_action, a_params)
            if not r.get("success"):
                raise RuntimeError(r.get("error", "dispatch failed"))
            return r.get("data")

        async def _notify(msg: dict) -> None:
            await ws_manager.broadcast_to_execution(execution_id, msg)

        async def _user_confirm(exec_id: str, s_index: int, error: str) -> dict:
            loop = asyncio.get_running_loop()
            key = f"{exec_id}:{s_index}"
            fut: asyncio.Future = loop.create_future()
            self._user_confirm_futures[key] = fut
            try:
                return await asyncio.wait_for(fut, timeout=300)  # 5 min timeout
            except asyncio.TimeoutError:
                self._user_confirm_futures.pop(key, None)
                return {"action": "cancel"}

        # ── Recovery callback: screenshot capture ─────────────
        async def _screenshot(exec_id: str, s_index: int) -> dict:
            """Capture a screenshot for recovery L3 re-verification."""
            ss = await self._desktop.take_screenshot(
                filename=f"recovery_{exec_id}_step{s_index}.png"
            )
            return ss  # {success, filepath, ...}

        # ── Recovery callback: analyze screenshot ─────────────
        async def _analyze_screenshot(screenshot_result: dict, action_desc: str) -> dict:
            """Analyze a screenshot via moondream for recovery L3."""
            filepath = screenshot_result.get("filepath")
            if not filepath:
                return {"confidence": 0.0, "error": "No screenshot filepath"}
            vision_result = await self._vision.analyze_screenshot(
                screenshot_path=filepath,
                query=f"Did the following action succeed? Action: {action_desc}. "
                      "Describe what you see and whether the expected result is visible.",
            )
            return {
                "confidence": vision_result.confidence,
                "text": vision_result.text,
                "verified": vision_result.verified,
                "ui_changes": vision_result.ui_changes,
            }

        # ── Recovery callback: replan via SAA ─────────────────
        async def _replan(a_name: str, a_action: str, a_params: dict, error_msg: str) -> dict:
            """Ask SAA agent to generate an alternative plan for a failed step."""
            saa = self.registry.get_instance("saa_agent")
            if not saa:
                return {"steps": []}
            try:
                replan_result = await saa.process({
                    "action": "replan",
                    "original_agent": a_name,
                    "original_action": a_action,
                    "parameters": a_params,
                    "error": error_msg,
                })
                return replan_result.get("plan", {"steps": []})
            except Exception as e:
                logger.error("replan_failed", error=str(e))
                return {"steps": []}

        ctx = RecoveryContext(
            execution_id=execution_id,
            step_index=step_index,
            agent_name=agent_name,
            action=action,
            parameters=parameters,
            error=result.get("error", "Unknown error"),
            max_retries=self.max_retries,
            base_timeout=float(get_settings().agent_timeout_seconds),
            backoff_multiplier=1.5,
            skippable=skippable,
            execute_fn=_exec,
            screenshot_fn=_screenshot,
            analyze_screenshot_fn=_analyze_screenshot,
            replan_fn=_replan,
            notify_fn=_notify,
            user_confirm_fn=_user_confirm,
        )

        recovery_result = await self.recovery.recover(ctx)

        if recovery_result.success:
            action_taken = recovery_result.action_taken or "recovered"
            return {
                "success": action_taken != "skip",
                "skipped": action_taken == "skip",
                "data": recovery_result.output,
                "duration_ms": recovery_result.total_duration_ms,
                "recovery_level": recovery_result.final_level.value,
                "error": None,
            }

        # All recovery exhausted
        return {
            "success": False,
            "skipped": False,
            "error": result.get("error", "Unknown error"),
            "duration_ms": recovery_result.total_duration_ms,
            "recovery_level": recovery_result.final_level.value,
        }

    async def _dispatch_to_agent(
        self,
        agent_name: str,
        action: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Dispatch to a local BaseAgent instance via the registry.
        
        Calls agent.process() directly — no HTTP needed.
        """
        agent_instance = self.registry.get_instance(agent_name)
        if agent_instance is None:
            # Fallback: check by AgentInfo
            agent_info = self.registry.get(agent_name)
            if agent_info is None:
                return {"success": False, "error": f"Agent '{agent_name}' not found in registry", "duration_ms": 0}
            if agent_info.status == AgentStatus.UNHEALTHY:
                return {"success": False, "error": f"Agent '{agent_name}' is unhealthy", "duration_ms": 0}
            return {"success": False, "error": f"Agent '{agent_name}' registered but has no local instance", "duration_ms": 0}

        start = time.perf_counter()
        try:
            result = await agent_instance.process({
                "action": action,
                "parameters": parameters,
                "step": {"action": action, "parameters": parameters},
            })
            elapsed = round((time.perf_counter() - start) * 1000, 2)

            # Normalize result to orchestrator format
            success = result.get("status", "") not in ("failure", "blocked", "execution_failed", "mismatch")
            return {
                "success": success,
                "data": result,
                "duration_ms": elapsed,
                "error": result.get("error") if not success else None,
            }

        except asyncio.TimeoutError:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            settings = get_settings()
            return {
                "success": False,
                "error": f"Agent '{agent_name}' timed out after {settings.agent_timeout_seconds}s",
                "duration_ms": elapsed,
            }
        except Exception as exc:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            logger.error("agent_dispatch_error", agent=agent_name, error=str(exc))
            return {
                "success": False,
                "error": str(exc),
                "duration_ms": elapsed,
            }
