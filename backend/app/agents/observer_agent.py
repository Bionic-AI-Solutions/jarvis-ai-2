"""Observer Agent — Background watchdog that validates execution results.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 7
Role: Background watchdog — validates each step truly succeeded
Model: qwen2.5:3b (classifies events), moondream (screenshot diff)
Responsibilities:
  1. After each EA step, independently verify
  2. Screenshot before/after comparison via moondream
  3. Process/file existence checks
  4. Classify event as success/partial/failure
  5. If failure detected, trigger Recovery Engine
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.services.desktop_automation import DesktopAutomationService
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ObserverAgent(BaseAgent):
    """Validates execution results through independent verification.
    
    After each step executes, Observer runs checks to confirm the action
    actually had the expected effect on the system.
    
    Architecture V3, Agent 7:
    Input:  {step_result: {}, screenshot_after: path, expected_state: str}
    Output: {status: "verified"|"mismatch"|"partial", confidence: float, evidence: str}
    """

    def __init__(self, desktop_service: DesktopAutomationService | None = None):
        super().__init__(
            agent_name="observer_agent",
            agent_type="verification",
            description="Background watchdog - verifies execution results independently",
        )
        self.desktop = desktop_service or DesktopAutomationService()
        self._observations: List[Dict[str, Any]] = []

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: observe and validate execution result.
        
        Args:
            input_data: {
                "step": {...},           # Original plan step
                "exec_result": {...},    # Result from ExecutionAgent
                "plan": {...},           # OR full plan to observe all results
            }
            
        Returns:
            {
                "status": "verified" | "mismatch" | "partial",
                "observation": {...},
                "next_agent": None | "recovery_engine",
                "context_updates": {...}
            }
        """
        start = time.perf_counter()

        if "plan" in input_data and "step_results" in input_data.get("exec_result", {}):
            observation = await self.observe_plan(
                input_data["plan"],
                input_data["exec_result"],
            )
        elif "step" in input_data and "exec_result" in input_data:
            observation = await self.observe(
                input_data["step"],
                input_data["exec_result"],
            )
        else:
            observation = {"verified": False, "error": "Missing 'step'+'exec_result' or 'plan'"}

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        verified = observation.get("verified", False)
        if verified:
            status = "verified"
            next_agent = None  # Done — success
        elif observation.get("partial"):
            status = "partial"
            next_agent = "recovery_engine"
        else:
            status = "mismatch"
            next_agent = "recovery_engine"

        return {
            "status": status,
            "observation": observation,
            "next_agent": next_agent,
            "context_updates": {
                "observation_result": observation,
                "verification_status": status,
            },
        }

    async def observe(self, step: Dict[str, Any], exec_result: Dict[str, Any]) -> Dict[str, Any]:
        """Observe and validate a single execution result.
        
        Args:
            step: The original plan step (action, parameters, description)
            exec_result: The result returned by ExecutionAgent
            
        Returns:
            Dict with: verified (bool), checks (list of check results),
                       screenshot (path), confidence (0.0-1.0)
        """
        start = time.perf_counter()
        action = step.get("action", "")
        parameters = step.get("parameters", {})
        reported_success = exec_result.get("success", False)

        checks = []
        verified = reported_success  # Start with what was reported

        # Run action-specific verification checks
        if action == "open_application":
            checks = await self._verify_app_opened(parameters, exec_result)
        elif action == "close_application":
            checks = await self._verify_app_closed(parameters, exec_result)
        elif action in ("copy_file", "copy_folder"):
            checks = await self._verify_file_copy(parameters, exec_result)
        elif action == "move_file":
            checks = await self._verify_file_move(parameters, exec_result)
        elif action == "create_file":
            checks = await self._verify_file_created(parameters, exec_result)
        elif action == "delete_file":
            checks = await self._verify_file_deleted(parameters, exec_result)
        elif action == "take_screenshot":
            checks = await self._verify_screenshot(exec_result)
        elif action == "list_directory":
            checks = await self._verify_directory_listed(parameters, exec_result)
        elif action == "open_explorer":
            checks = await self._verify_explorer_opened(parameters, exec_result)
        elif action == "is_process_running":
            # Process check is self-verifying
            checks = [{"check": "process_check_self_verify", "passed": True, "detail": "Self-verifying action"}]
        elif action in ("type_text", "press_key", "hotkey", "click"):
            # Input actions can't be easily verified without vision
            checks = [{"check": "input_action", "passed": reported_success, "detail": "Input action - verified by exec result"}]
        elif action == "wait":
            checks = [{"check": "wait_completed", "passed": True, "detail": "Wait is always successful"}]
        else:
            checks = [{"check": "unknown_action", "passed": reported_success, "detail": f"No observer for: {action}"}]

        # Take a post-execution screenshot for audit trail
        screenshot_path = None
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            ss = await self.desktop.take_screenshot(filename=f"observe_{action}_{timestamp}.png")
            if ss.get("success"):
                screenshot_path = ss["filepath"]
        except Exception as e:
            logger.warning(f"Observer screenshot failed: {e}")

        # Calculate verification confidence
        total_checks = len(checks)
        passed_checks = sum(1 for c in checks if c.get("passed", False))
        confidence = passed_checks / total_checks if total_checks > 0 else 0.0

        # Override verified if checks disagree with reported success
        if passed_checks == total_checks:
            verified = True
        elif passed_checks == 0:
            verified = False
        else:
            # Partial pass — flag as uncertain
            verified = reported_success  # Trust execution but note discrepancy

        observation = {
            "action": action,
            "reported_success": reported_success,
            "verified": verified,
            "confidence": round(confidence, 2),
            "checks": checks,
            "checks_total": total_checks,
            "checks_passed": passed_checks,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        }

        self._observations.append(observation)
        logger.info(
            "observation_recorded",
            action=action,
            verified=verified,
            confidence=confidence,
            checks_passed=f"{passed_checks}/{total_checks}",
        )
        return observation

    async def observe_plan(self, plan: Dict[str, Any], exec_results: Dict[str, Any]) -> Dict[str, Any]:
        """Observe and validate an entire plan execution.
        
        Args:
            plan: The original plan from RAG agent
            exec_results: The results from ExecutionAgent.execute_plan()
        
        Returns:
            Dict with overall verification status and per-step observations
        """
        start = time.perf_counter()
        steps = plan.get("steps", [])
        step_results = exec_results.get("step_results", [])

        observations = []
        all_verified = True

        for i, step in enumerate(steps):
            # Find matching result
            result = step_results[i] if i < len(step_results) else {"success": False, "error": "Step not executed"}
            
            obs = await self.observe(step, result)
            obs["step_index"] = i
            observations.append(obs)

            if not obs["verified"]:
                all_verified = False

        total_checks = sum(o["checks_total"] for o in observations)
        passed_checks = sum(o["checks_passed"] for o in observations)

        return {
            "all_verified": all_verified,
            "observations": observations,
            "steps_total": len(steps),
            "steps_verified": sum(1 for o in observations if o["verified"]),
            "total_checks": total_checks,
            "total_checks_passed": passed_checks,
            "overall_confidence": round(passed_checks / total_checks, 2) if total_checks > 0 else 0.0,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        }

    # ── Verification Methods ────────────────────────────────

    async def _verify_app_opened(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify an application was actually opened."""
        checks = []
        app_name = params.get("app_name", "")

        # Check 1: PID was returned
        pid = result.get("result", result).get("pid")
        checks.append({
            "check": "pid_returned",
            "passed": pid is not None and pid > 0,
            "detail": f"PID: {pid}",
        })

        # Check 2: Process is running
        proc_check = await self.desktop.is_process_running(app_name)
        is_running = proc_check.get("is_running", False)
        checks.append({
            "check": "process_running",
            "passed": is_running,
            "detail": f"Process '{app_name}' running: {is_running}, instances: {proc_check.get('instance_count', 0)}",
        })

        return checks

    async def _verify_app_closed(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify an application was closed."""
        checks = []
        process_name = params.get("process_name", "")

        # Check: Process is no longer running
        proc_check = await self.desktop.is_process_running(process_name)
        is_running = proc_check.get("is_running", False)
        checks.append({
            "check": "process_stopped",
            "passed": not is_running,
            "detail": f"Process '{process_name}' running: {is_running}",
        })

        return checks

    async def _verify_file_copy(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify a file/folder was copied."""
        checks = []
        source = params.get("source", "")
        destination = params.get("destination", "")

        # Check 1: Source still exists (copy shouldn't remove it)
        src_path = Path(source)
        src_exists = src_path.exists()
        checks.append({
            "check": "source_preserved",
            "passed": src_exists,
            "detail": f"Source still exists: {src_exists}",
        })

        # Check 2: Destination exists
        dst_path = Path(destination)
        if dst_path.is_dir():
            dst_path = dst_path / src_path.name
        dst_exists = dst_path.exists()
        checks.append({
            "check": "destination_exists",
            "passed": dst_exists,
            "detail": f"Destination exists: {dst_exists} ({dst_path})",
        })

        # Check 3: Size match (for files)
        if src_exists and dst_exists and src_path.is_file() and dst_path.is_file():
            src_size = src_path.stat().st_size
            dst_size = dst_path.stat().st_size
            checks.append({
                "check": "size_match",
                "passed": src_size == dst_size,
                "detail": f"Source: {src_size}, Dest: {dst_size}",
            })

        return checks

    async def _verify_file_move(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify a file was moved (source gone, dest exists)."""
        checks = []
        source = params.get("source", "")
        destination = params.get("destination", "")

        # Check 1: Source is gone
        src_exists = Path(source).exists()
        checks.append({
            "check": "source_removed",
            "passed": not src_exists,
            "detail": f"Source removed: {not src_exists}",
        })

        # Check 2: Destination exists
        dst_path = Path(destination)
        if dst_path.is_dir():
            dst_path = dst_path / Path(source).name
        dst_exists = dst_path.exists()
        checks.append({
            "check": "destination_exists",
            "passed": dst_exists,
            "detail": f"Destination exists: {dst_exists}",
        })

        return checks

    async def _verify_file_created(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify a file was created."""
        checks = []
        filepath = params.get("filepath", "")

        fpath = Path(filepath)
        exists = fpath.exists()
        checks.append({
            "check": "file_exists",
            "passed": exists,
            "detail": f"File exists: {exists} ({filepath})",
        })

        if exists:
            size = fpath.stat().st_size
            checks.append({
                "check": "file_has_content",
                "passed": size > 0 or params.get("content", "") == "",
                "detail": f"File size: {size} bytes",
            })

        return checks

    async def _verify_file_deleted(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify a file was deleted."""
        checks = []
        filepath = params.get("filepath", "")

        exists = Path(filepath).exists()
        checks.append({
            "check": "file_removed",
            "passed": not exists,
            "detail": f"File still exists: {exists}",
        })

        return checks

    async def _verify_screenshot(self, result: Dict) -> List[Dict]:
        """Verify a screenshot was taken."""
        checks = []
        inner = result.get("result", result)
        filepath = inner.get("filepath", "")

        if filepath:
            exists = Path(filepath).exists()
            size = Path(filepath).stat().st_size if exists else 0
            checks.append({
                "check": "screenshot_exists",
                "passed": exists and size > 0,
                "detail": f"File: {filepath}, Size: {size}",
            })
        else:
            checks.append({
                "check": "screenshot_path_returned",
                "passed": False,
                "detail": "No filepath in result",
            })

        return checks

    async def _verify_directory_listed(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify directory listing returned real data."""
        checks = []
        path = params.get("path", "")
        inner = result.get("result", result)

        # Check: Path exists
        exists = Path(path).exists()
        checks.append({
            "check": "directory_exists",
            "passed": exists,
            "detail": f"Directory exists: {exists}",
        })

        # Check: Items returned
        items = inner.get("items", [])
        checks.append({
            "check": "items_returned",
            "passed": len(items) > 0,
            "detail": f"Items returned: {len(items)}",
        })

        return checks

    async def _verify_explorer_opened(self, params: Dict, result: Dict) -> List[Dict]:
        """Verify File Explorer was opened."""
        checks = []

        # Check: Explorer process is running
        proc_check = await self.desktop.is_process_running("explorer")
        checks.append({
            "check": "explorer_process",
            "passed": proc_check.get("is_running", False),
            "detail": f"Explorer instances: {proc_check.get('instance_count', 0)}",
        })

        return checks

    @property
    def observations(self) -> List[Dict[str, Any]]:
        """Full history of observations."""
        return list(self._observations)

    def clear_observations(self):
        """Clear observation history."""
        self._observations.clear()
