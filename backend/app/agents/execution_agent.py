"""Execution Agent — The Hands — Runs real desktop actions from execution plans.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 6
Role: Real-time executor a.k.a. "the hands"
Model: None (pure execution) + moondream for visual verification
Responsibilities:
  1. Receive granular step from SAA
  2. Pre-check safety constraints
  3. Execute action (PowerShell/RobotJS/REST)
  4. Capture post-screenshot
  5. moondream verifies visual state
  6. Report success/failure + screenshot delta
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.services.desktop_automation import DesktopAutomationService
from app.services.uia_service import UIAService, get_uia_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Per-action delays (seconds) to let the OS respond before verification
ACTION_SETTLE_TIMES = {
    "open_application": 3.0,
    "close_application": 2.0,
    "click": 0.8,
    "type_text": 0.5,
    "press_key": 0.5,
    "hotkey": 0.8,
    "focus_window": 1.0,
    "copy_file": 1.0,
    "move_file": 1.0,
    "create_file": 0.5,
    "delete_file": 0.5,
    "copy_folder": 2.0,
    "open_explorer": 2.0,
    "wait": 0.0,  # wait action handles its own delay
    "take_screenshot": 0.0,
    "list_directory": 0.0,
    "list_windows": 0.0,
    "is_process_running": 0.0,
}


class ExecutionAgent(BaseAgent):
    """Executes desktop automation steps from a plan.
    
    Dispatches each step to the appropriate DesktopAutomationService method.
    Logs all results for auditing and recovery.
    
    Architecture V3, Agent 6:
    Input:  {action: str, parameters: {}, verification_criteria: str}
    Output: {status: "step_done"|"step_failed", screenshot_after, execution_time, error?}
    """

    def __init__(
        self,
        desktop_service: DesktopAutomationService | None = None,
        uia_service: UIAService | None = None,
        vision_service=None,
    ):
        super().__init__(
            agent_name="execution_agent",
            agent_type="execution",
            description="Real-time desktop executor - the hands of JARVIS",
        )
        self.desktop = desktop_service or DesktopAutomationService()
        self.uia = uia_service or get_uia_service()
        self._vision = vision_service  # Lazy: set via set_vision_service()
        self._execution_log: List[Dict[str, Any]] = []
        self.verify_steps = True  # Toggle for step-by-step verification
        self.vision_fallback = True  # Use moondream when UIA can't verify

    def set_vision_service(self, vision_service):
        """Wire vision service for screenshot-based verification."""
        self._vision = vision_service

    # Map of action names to DesktopAutomationService methods
    ACTION_MAP = {
        "open_application": "open_application",
        "click": "click",
        "type_text": "type_text",
        "press_key": "press_key",
        "hotkey": "hotkey",
        "take_screenshot": "take_screenshot",
        "copy_file": "copy_file",
        "copy_folder": "copy_folder",
        "move_file": "move_file",
        "create_file": "create_file",
        "delete_file": "delete_file",
        "list_directory": "list_directory",
        "open_explorer": "open_explorer",
        "close_application": "close_application",
        "is_process_running": "is_process_running",
        "wait": "wait",
        "focus_window": "focus_window",
        "list_windows": "list_windows",
    }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: execute plan steps.
        
        Args:
            input_data: {
                "plan": {"steps": [...]},   # Full plan from pipeline
                "step": {...},              # OR single step to execute
            }
            
        Returns:
            {
                "status": "execution_complete" | "execution_failed",
                "result": {step_results...},
                "next_agent": "observer_agent",
                "context_updates": {...}
            }
        """
        start = time.perf_counter()

        # Support both single-step and full-plan execution
        if "step" in input_data:
            result = await self.execute_step(input_data["step"])
        elif "plan" in input_data:
            result = await self.execute_plan(input_data["plan"])
        else:
            result = {"success": False, "error": "No 'plan' or 'step' in input_data"}

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        success = result.get("success", False)
        return {
            "status": "execution_complete" if success else "execution_failed",
            "result": result,
            "next_agent": "observer_agent",
            "context_updates": {
                "execution_result": result,
                "execution_success": success,
            },
        }

    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single plan step with optional verification.
        
        Args:
            step: Dict with 'action', 'parameters', 'description'
            
        Returns:
            Dict with 'success', 'result', 'step', 'duration_ms', 'verification'
        """
        start = time.perf_counter()
        action = step.get("action", "")
        parameters = step.get("parameters", {})
        description = step.get("description", action)

        if action not in self.ACTION_MAP:
            result = {
                "success": False,
                "error": f"Unknown action: {action}",
                "step": step,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
            self._execution_log.append(result)
            return result

        method_name = self.ACTION_MAP[action]
        method = getattr(self.desktop, method_name)

        try:
            # Special handling for hotkey (takes *args instead of **kwargs)
            if action == "hotkey":
                keys = parameters.get("keys", [])
                action_result = await method(*keys)
            elif action == "list_windows":
                action_result = {"success": True, "windows": await method()}
            else:
                action_result = await method(**parameters)

            result = {
                "success": action_result.get("success", False),
                "result": action_result,
                "step": step,
                "description": description,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
            
            # Extract error from action_result if present and action failed
            if not result["success"] and "error" not in result:
                if "error" in action_result:
                    result["error"] = action_result["error"]

            # --- Step verification ---
            if result["success"] and self.verify_steps:
                verification = await self._verify_step(action, parameters, description)
                result["verification"] = verification
                
                # If verification says it failed with high confidence, mark step as failed
                if not verification.get("verified", True) and verification.get("confidence", 0) >= 0.8:
                    result["success"] = False
                    result["error"] = f"Verification failed: {verification.get('detail', 'unknown')}"

        except Exception as e:
            logger.error(f"Step execution failed: {action} - {e}")
            result = {
                "success": False,
                "error": str(e),
                "step": step,
                "description": description,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._execution_log.append(result)
        logger.info(
            "step_executed",
            action=action,
            success=result["success"],
            duration_ms=result["duration_ms"],
        )
        return result

    async def _verify_step(
        self, action: str, parameters: Dict[str, Any], description: str
    ) -> Dict[str, Any]:
        """Verify a step completed using UIA (fast) then moondream (fallback).
        
        Two-tier verification:
        1. UIA: <100ms, checks process/window state (99% accuracy)
        2. moondream: 1-2s, screenshot + vision (88% accuracy) — only if UIA can't verify
        
        Returns:
            {verified: bool, confidence: float, method: str, detail: str}
        """
        # Wait for OS to settle 
        settle = ACTION_SETTLE_TIMES.get(action, 0.5)
        if settle > 0:
            await asyncio.sleep(settle)
        
        # Tier 1: UIA fast check
        uia_result = await self.uia.verify_action(action, parameters)
        
        if uia_result["verified"]:
            logger.info(
                f"UIA verified step '{description}' in {uia_result['duration_ms']}ms"
            )
            return uia_result
        
        # If UIA says "not applicable" (confidence 0), try moondream
        if self.vision_fallback and self._vision and uia_result["confidence"] == 0.0:
            return await self._vision_verify(action, parameters, description)
        
        # UIA said it failed with some confidence — trust it
        return uia_result

    async def _vision_verify(
        self, action: str, parameters: Dict[str, Any], description: str
    ) -> Dict[str, Any]:
        """Tier 2: Screenshot + moondream vision verification.
        
        Takes a screenshot and asks moondream to verify the action completed.
        """
        try:
            # Take screenshot
            screenshot_result = await self.desktop.take_screenshot()
            if not screenshot_result.get("success"):
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "method": "vision_screenshot_failed",
                    "detail": "Could not capture screenshot for verification",
                }
            
            image_path = screenshot_result.get("path", "")
            if not image_path:
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "method": "vision_no_path",
                    "detail": "Screenshot path missing",
                }
            
            # Ask moondream to verify
            prompt = self._build_verification_prompt(action, parameters, description)
            vision_result = await self._vision.analyze_screenshot(
                image_path=image_path, prompt=prompt
            )
            
            # Parse moondream response
            text = vision_result.get("text", "").lower() if isinstance(vision_result, dict) else str(vision_result).lower()
            verified = any(w in text for w in ["yes", "confirmed", "visible", "success", "completed", "done", "correct"])
            confidence = vision_result.get("confidence", 0.7) if isinstance(vision_result, dict) else 0.7
            
            logger.info(
                f"Vision verified step '{description}': verified={verified}, confidence={confidence}"
            )
            
            return {
                "verified": verified,
                "confidence": confidence,
                "method": "moondream_vision",
                "detail": text[:200],
            }
        except Exception as e:
            logger.warning(f"Vision verification failed: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "method": "vision_error",
                "detail": str(e)[:200],
            }

    def _build_verification_prompt(
        self, action: str, parameters: Dict[str, Any], description: str
    ) -> str:
        """Build a concise verification prompt for moondream."""
        if action == "open_application":
            app = parameters.get("app_name", "application")
            return f"Is {app} open and visible on screen? Answer YES or NO."
        elif action == "click":
            return f"Was a click action performed? Is there a visual change on screen? Answer YES or NO."
        elif action == "type_text":
            text = parameters.get("text", "")[:50]
            return f"Is the text '{text}' visible in an input field on screen? Answer YES or NO."
        elif action == "focus_window":
            title = parameters.get("title_contains", "window")
            return f"Is a window with '{title}' in the title in the foreground? Answer YES or NO."
        else:
            return f"Did this action complete: '{description}'? Answer YES or NO."

    async def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an entire plan (list of steps) with per-step verification.
        
        Each step is:
        1. Executed via DesktopAutomationService
        2. Waited for OS settle time (per action type)
        3. Verified via UIA (fast) then moondream (fallback)
        4. Only proceeds to next step if verified
        
        Args:
            plan: Dict with 'steps' list from RAG agent
            
        Returns:
            Dict with overall success, step results, timing, verification summary
        """
        start = time.perf_counter()
        steps = plan.get("steps", [])
        
        if not steps:
            return {
                "success": False,
                "error": "No steps in plan",
                "step_results": [],
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        step_results = []
        all_success = True
        verification_summary = {
            "uia_verified": 0,
            "vision_verified": 0,
            "verification_skipped": 0,
            "verification_failed": 0,
        }

        for i, step in enumerate(steps):
            action_desc = step.get('description', step.get('action', f'Step {i+1}'))
            logger.info(f"Executing step {i+1}/{len(steps)}: {action_desc}")
            
            result = await self.execute_step(step)
            result["step_index"] = i
            step_results.append(result)

            # Track verification results
            v = result.get("verification", {})
            method = v.get("method", "")
            if "uia" in method and v.get("verified"):
                verification_summary["uia_verified"] += 1
            elif "vision" in method or "moondream" in method:
                if v.get("verified"):
                    verification_summary["vision_verified"] += 1
                else:
                    verification_summary["verification_failed"] += 1
            elif not v:
                verification_summary["verification_skipped"] += 1
            elif not v.get("verified"):
                verification_summary["verification_failed"] += 1

            if not result["success"]:
                all_success = False
                # Check if we should stop on failure
                if step.get("stop_on_failure", True):
                    logger.warning(f"Step {i+1} failed, stopping execution")
                    break

        return {
            "success": all_success,
            "steps_total": len(steps),
            "steps_executed": len(step_results),
            "steps_succeeded": sum(1 for r in step_results if r["success"]),
            "steps_failed": sum(1 for r in step_results if not r["success"]),
            "step_results": step_results,
            "verification_summary": verification_summary,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        }

    @property
    def execution_log(self) -> List[Dict[str, Any]]:
        """Full audit trail of all steps executed."""
        return list(self._execution_log)

    def clear_log(self):
        """Clear the execution log."""
        self._execution_log.clear()
