"""Workflow orchestrator — executes workflows step-by-step via agents.

Story 2.3: Basic Orchestration
Story 2.4: Recovery Levels L1-L2
Stories 3.1-3.6: Full 6-Level Recovery Engine integration

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

import httpx

from app.agents.protocol import (
    AgentExecutePayload,
    AgentMessage,
    AgentMessageType,
    AgentResultPayload,
)
from app.agents.registry import AgentRegistry, AgentStatus, agent_registry
from app.config import get_settings
from app.core.errors import ErrorCode
from app.core.exceptions import AgentError, WorkflowError
from app.core.logging_config import get_logger
from app.routes.ws import manager as ws_manager
from app.services.recovery_engine import (
    RecoveryContext,
    RecoveryEngine,
    RecoveryLevel as RecoveryLevelEnum,
    recovery_engine,
)

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
        self._user_confirm_futures: Dict[str, asyncio.Future] = {}

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

            # Notify: step_complete
            await ws_manager.broadcast_to_execution(execution_id, {
                "type": "step_complete",
                "execution_id": execution_id,
                "step_index": idx,
                "status": step_status,
                "duration_ms": result.get("duration_ms", 0),
            })

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
        logger.info("workflow_cancel_requested", execution_id=execution_id)

    async def resolve_user_confirmation(
        self, execution_id: str, step_index: int, choice: str,
    ) -> None:
        """Called when user responds to L5 confirmation dialog."""
        key = f"{execution_id}:{step_index}"
        fut = self._user_confirm_futures.pop(key, None)
        if fut and not fut.done():
            fut.set_result({"action": choice})

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
        """Send an execute command to an agent and parse the response."""
        agent = self.registry.get(agent_name)
        if agent is None:
            return {"success": False, "error": f"Agent '{agent_name}' not found in registry", "duration_ms": 0}

        if agent.status == AgentStatus.UNHEALTHY:
            return {"success": False, "error": f"Agent '{agent_name}' is unhealthy", "duration_ms": 0}

        settings = get_settings()
        payload = AgentExecutePayload(
            action=action,
            parameters=parameters,
            timeout_seconds=settings.agent_timeout_seconds,
        )
        message = AgentMessage(
            type=AgentMessageType.EXECUTE,
            agent_name=agent_name,
            payload=payload.model_dump(),
        )

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=settings.agent_timeout_seconds) as client:
                resp = await client.post(
                    agent.execute_url,
                    json=message.model_dump(),
                )
            elapsed = round((time.perf_counter() - start) * 1000, 2)

            if resp.status_code == 200:
                result = AgentResultPayload.model_validate(resp.json())
                return {
                    "success": result.success,
                    "data": result.data,
                    "duration_ms": result.duration_ms or elapsed,
                    "screenshot_path": result.screenshot_path,
                    "error": result.error_message,
                }
            else:
                return {
                    "success": False,
                    "error": f"Agent returned HTTP {resp.status_code}",
                    "duration_ms": elapsed,
                }

        except httpx.TimeoutException:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            return {
                "success": False,
                "error": f"Agent '{agent_name}' timed out after {settings.agent_timeout_seconds}s",
                "duration_ms": elapsed,
            }
        except Exception as exc:
            elapsed = round((time.perf_counter() - start) * 1000, 2)
            return {
                "success": False,
                "error": str(exc),
                "duration_ms": elapsed,
            }
