"""Safety Agent — Pre-execution security gate that blocks dangerous commands.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 8
Role: Safety enforcement — hard rules + LLM classification
Model: qwen2.5:3b (risk classification, borderline cases)
Responsibilities:
  1. Pre-execution gate: every step must pass Safety before EA runs it
  2. Hard rules: protected paths, processes, dangerous shell commands
  3. LLM classification for ambiguous/borderline cases
  4. Returns ALLOW, BLOCK, or WARN
  5. Maintains audit log and blocked operations list
"""

from __future__ import annotations

import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# Paths that should NEVER be modified
PROTECTED_PATHS = [
    r"C:\Windows",
    r"C:\Windows\System32",
    r"C:\Windows\SysWOW64",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\ProgramData",
    r"C:\Users\Default",
    r"C:\Recovery",
    r"C:\$Recycle.Bin",
    r"C:\Boot",
    r"C:\bootmgr",
    r"C:\pagefile.sys",
    r"C:\hiberfil.sys",
    r"C:\swapfile.sys",
]

# Process names that should NEVER be killed
PROTECTED_PROCESSES = [
    "csrss",
    "wininit",
    "winlogon",
    "lsass",
    "services",
    "svchost",
    "smss",
    "dwm",
    "conhost",
    "system",
    "registry",
    "explorer",  # Could be killed but causes desktop issues
    "taskmgr",
    "ctfmon",
    "sihost",
]

# Dangerous shell commands that should be blocked
DANGEROUS_COMMANDS = [
    r"format\s+[a-zA-Z]:",
    r"del\s+/[sS]",
    r"rmdir\s+/[sS]",
    r"rd\s+/[sS]",
    r"reg\s+delete",
    r"reg\s+add",
    r"bcdedit",
    r"diskpart",
    r"cipher\s+/w",
    r"net\s+user\s+.+\s+/delete",
    r"net\s+stop",
    r"sc\s+delete",
    r"powershell.*-encodedcommand",
    r"powershell.*iex\(",
    r"powershell.*invoke-expression",
    r"shutdown\s+/[srt]",
    r"taskkill\s+/f\s+/im\s+(csrss|lsass|services|svchost|smss|system)",
]


class SafetyAgent(BaseAgent):
    """Pre-execution safety gate that blocks dangerous operations.
    
    Every plan step must pass through SafetyAgent before the ExecutionAgent
    runs it. Returns ALLOW, BLOCK, or WARN.
    
    Architecture V3, Agent 8:
    Input:  {plan_step: {action, parameters}, context: {user_role, recent_failures}}
    Output: {verdict: "allow"|"block"|"warn", reason: str, risk_score: float}
    """

    def __init__(self, strict_mode: bool = True):
        super().__init__(
            agent_name="safety_agent",
            agent_type="safety",
            description="Pre-execution safety gate - blocks dangerous operations",
        )
        self.strict_mode = strict_mode
        self._audit_log: List[Dict[str, Any]] = []
        self._blocked_count = 0
        self._allowed_count = 0
        self._warned_count = 0

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: evaluate plan/steps for safety.
        
        Args:
            input_data: {
                "plan": {"steps": [...]},  # Full plan to evaluate
                "step": {...},             # OR single step to evaluate
            }
            
        Returns:
            {
                "status": "approved" | "blocked" | "warning",
                "evaluation": {...},
                "next_agent": "execution_agent" | None,
                "context_updates": {...}
            }
        """
        start = time.perf_counter()

        if "plan" in input_data:
            evaluation = self.evaluate_plan(input_data["plan"])
        elif "step" in input_data:
            evaluation = self.evaluate(input_data["step"])
        else:
            evaluation = {"verdict": "block", "reason": "No 'plan' or 'step' in input"}

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        verdict = evaluation.get("decision", evaluation.get("verdict", "BLOCK")).lower()
        if verdict == "allow":
            status = "approved"
            next_agent = "execution_agent"
        elif verdict == "warn":
            status = "warning"
            next_agent = "execution_agent" if not self.strict_mode else None
        else:
            status = "blocked"
            next_agent = None

        return {
            "status": status,
            "evaluation": evaluation,
            "next_agent": next_agent,
            "context_updates": {
                "safety_verdict": verdict,
                "safety_evaluation": evaluation,
            },
        }

    def evaluate(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single step for safety.
        
        Args:
            step: Plan step with 'action', 'parameters', 'description'
            
        Returns:
            Dict with:
                decision: "ALLOW" | "BLOCK" | "WARN"
                reason: explanation
                risk_level: "none" | "low" | "medium" | "high" | "critical"
                checks: list of individual check results
        """
        start = time.perf_counter()
        action = step.get("action", "")
        parameters = step.get("parameters", {})
        checks = []

        # Run all safety checks for this action
        if action == "delete_file":
            checks = self._check_delete(parameters)
        elif action in ("copy_file", "copy_folder", "move_file"):
            checks = self._check_file_operation(action, parameters)
        elif action == "close_application":
            checks = self._check_close_app(parameters)
        elif action == "open_application":
            checks = self._check_open_app(parameters)
        elif action == "type_text":
            checks = self._check_type_text(parameters)
        elif action in ("hotkey", "press_key"):
            checks = self._check_keyboard(action, parameters)
        elif action == "create_file":
            checks = self._check_create_file(parameters)
        else:
            # Default: allow actions like screenshot, list_directory, wait, etc.
            checks = [{"check": "default_safe", "result": "ALLOW", "detail": f"Action '{action}' is inherently safe"}]

        # Aggregate: worst check wins
        decisions = [c.get("result", "ALLOW") for c in checks]
        
        if "BLOCK" in decisions:
            decision = "BLOCK"
            risk_level = "critical"
            self._blocked_count += 1
        elif "WARN" in decisions:
            decision = "BLOCK" if self.strict_mode else "WARN"
            risk_level = "high"
            self._warned_count += 1
        else:
            decision = "ALLOW"
            risk_level = "none"
            self._allowed_count += 1

        # Find reason from the most severe check
        reason = "Safe operation"
        for c in checks:
            if c.get("result") == decision or (decision == "BLOCK" and c.get("result") == "WARN"):
                reason = c.get("detail", "No detail")
                break

        result = {
            "decision": decision,
            "reason": reason,
            "risk_level": risk_level,
            "action": action,
            "parameters": parameters,
            "checks": checks,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            "timestamp": datetime.now().isoformat(),
        }

        self._audit_log.append(result)
        
        if decision != "ALLOW":
            logger.warning(
                "safety_gate",
                decision=decision,
                action=action,
                reason=reason,
                risk_level=risk_level,
            )

        return result

    def evaluate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an entire plan for safety.
        
        Args:
            plan: Plan from RAG agent with 'steps' list
            
        Returns:
            Dict with overall decision and per-step evaluations
        """
        steps = plan.get("steps", [])
        evaluations = []
        blocked_steps = []
        warned_steps = []

        for i, step in enumerate(steps):
            eval_result = self.evaluate(step)
            eval_result["step_index"] = i
            evaluations.append(eval_result)

            if eval_result["decision"] == "BLOCK":
                blocked_steps.append(i)
            elif eval_result["decision"] == "WARN":
                warned_steps.append(i)

        # Overall: block entire plan if any step is blocked
        if blocked_steps:
            overall = "BLOCK"
        elif warned_steps:
            overall = "WARN"
        else:
            overall = "ALLOW"

        return {
            "decision": overall,
            "steps_total": len(steps),
            "steps_allowed": len(steps) - len(blocked_steps) - len(warned_steps),
            "steps_blocked": blocked_steps,
            "steps_warned": warned_steps,
            "evaluations": evaluations,
        }

    # ── Individual Check Methods ────────────────────────────

    def _check_delete(self, params: Dict) -> List[Dict]:
        """Check if a delete operation is safe."""
        checks = []
        filepath = params.get("filepath", "")

        # Check 1: Protected paths
        if self._is_protected_path(filepath):
            checks.append({
                "check": "protected_path",
                "result": "BLOCK",
                "detail": f"BLOCKED: Cannot delete protected path: {filepath}",
            })
        else:
            checks.append({
                "check": "protected_path",
                "result": "ALLOW",
                "detail": f"Path is not protected: {filepath}",
            })

        # Check 2: Drive root deletion
        if re.match(r"^[a-zA-Z]:\\?$", filepath.strip()):
            checks.append({
                "check": "drive_root",
                "result": "BLOCK",
                "detail": f"BLOCKED: Cannot delete drive root: {filepath}",
            })

        # Check 3: Wildcard deletion
        if "*" in filepath or "?" in filepath:
            checks.append({
                "check": "wildcard_delete",
                "result": "BLOCK",
                "detail": f"BLOCKED: Wildcard deletion not allowed: {filepath}",
            })

        # Check 4: System file extensions
        dangerous_extensions = [".sys", ".dll", ".exe", ".drv", ".inf", ".bat", ".cmd", ".reg"]
        ext = Path(filepath).suffix.lower()
        if ext in dangerous_extensions and self._is_system_area(filepath):
            checks.append({
                "check": "system_file_type",
                "result": "BLOCK",
                "detail": f"BLOCKED: System file type in system area: {filepath}",
            })

        if not checks:
            checks.append({"check": "delete_safe", "result": "ALLOW", "detail": "Delete target appears safe"})

        return checks

    def _check_file_operation(self, action: str, params: Dict) -> List[Dict]:
        """Check copy/move operations."""
        checks = []
        source = params.get("source", "")
        destination = params.get("destination", "")

        # Check: destination is not a protected system directory
        if self._is_protected_path(destination):
            checks.append({
                "check": "protected_destination",
                "result": "WARN",
                "detail": f"WARNING: Writing to protected area: {destination}",
            })

        # Check: not overwriting system files
        if action == "move_file" and self._is_protected_path(source):
            checks.append({
                "check": "moving_protected_file",
                "result": "BLOCK",
                "detail": f"BLOCKED: Cannot move from protected path: {source}",
            })

        if not checks:
            checks.append({"check": "file_op_safe", "result": "ALLOW", "detail": "File operation is safe"})

        return checks

    def _check_close_app(self, params: Dict) -> List[Dict]:
        """Check if closing an application is safe."""
        checks = []
        process_name = params.get("process_name", "").lower()

        for protected in PROTECTED_PROCESSES:
            if protected in process_name:
                checks.append({
                    "check": "protected_process",
                    "result": "BLOCK",
                    "detail": f"BLOCKED: Cannot kill protected process: {process_name} (matches: {protected})",
                })
                break

        if not checks:
            checks.append({"check": "close_app_safe", "result": "ALLOW", "detail": f"Safe to close: {process_name}"})

        return checks

    def _check_open_app(self, params: Dict) -> List[Dict]:
        """Check if opening an application is safe."""
        checks = []
        app_name = params.get("app_name", "")
        args = params.get("args", [])

        # Check for dangerous command-line arguments
        args_str = " ".join(str(a) for a in args) if args else ""
        combined = f"{app_name} {args_str}"

        for pattern in DANGEROUS_COMMANDS:
            if re.search(pattern, combined, re.IGNORECASE):
                checks.append({
                    "check": "dangerous_command",
                    "result": "BLOCK",
                    "detail": f"BLOCKED: Dangerous command detected: {combined[:100]}",
                })
                break

        if not checks:
            checks.append({"check": "open_app_safe", "result": "ALLOW", "detail": f"Safe to open: {app_name}"})

        return checks

    def _check_type_text(self, params: Dict) -> List[Dict]:
        """Check if typed text contains dangerous commands."""
        checks = []
        text = params.get("text", "")

        for pattern in DANGEROUS_COMMANDS:
            if re.search(pattern, text, re.IGNORECASE):
                checks.append({
                    "check": "dangerous_text",
                    "result": "WARN",
                    "detail": f"WARNING: Text may contain dangerous command: {text[:100]}",
                })
                break

        if not checks:
            checks.append({"check": "text_safe", "result": "ALLOW", "detail": "Text appears safe"})

        return checks

    def _check_keyboard(self, action: str, params: Dict) -> List[Dict]:
        """Check keyboard shortcuts for dangerous combinations."""
        checks = []

        if action == "hotkey":
            keys = [k.lower() for k in params.get("keys", [])]
            # Block: Alt+F4 on system processes (could close critical apps)
            # Allow it generally but warn
            if "alt" in keys and "f4" in keys:
                checks.append({
                    "check": "alt_f4",
                    "result": "WARN",
                    "detail": "WARNING: Alt+F4 may close the active application unexpectedly",
                })

        if not checks:
            checks.append({"check": "keyboard_safe", "result": "ALLOW", "detail": "Keyboard action is safe"})

        return checks

    def _check_create_file(self, params: Dict) -> List[Dict]:
        """Check if file creation location is safe."""
        checks = []
        filepath = params.get("filepath", "")

        if self._is_protected_path(filepath):
            checks.append({
                "check": "protected_create_path",
                "result": "BLOCK",
                "detail": f"BLOCKED: Cannot create files in protected area: {filepath}",
            })
        else:
            checks.append({"check": "create_file_safe", "result": "ALLOW", "detail": f"Safe to create: {filepath}"})

        return checks

    # ── Helper Methods ──────────────────────────────────────

    def _is_protected_path(self, filepath: str) -> bool:
        """Check if a path is in a protected system directory."""
        if not filepath:
            return False
        
        normalized = os.path.normpath(filepath).lower()
        for protected in PROTECTED_PATHS:
            protected_norm = os.path.normpath(protected).lower()
            if normalized.startswith(protected_norm):
                return True
        return False

    def _is_system_area(self, filepath: str) -> bool:
        """Check if path is in Windows system areas."""
        normalized = os.path.normpath(filepath).lower()
        system_areas = [
            os.path.normpath(r"C:\Windows").lower(),
            os.path.normpath(r"C:\Program Files").lower(),
            os.path.normpath(r"C:\Program Files (x86)").lower(),
        ]
        return any(normalized.startswith(area) for area in system_areas)

    @property
    def audit_log(self) -> List[Dict[str, Any]]:
        """Full audit trail of safety evaluations."""
        return list(self._audit_log)

    @property
    def stats(self) -> Dict[str, int]:
        """Safety gate statistics."""
        return {
            "total_evaluated": len(self._audit_log),
            "allowed": self._allowed_count,
            "blocked": self._blocked_count,
            "warned": self._warned_count,
        }

    def clear_log(self):
        """Clear audit log and reset counters."""
        self._audit_log.clear()
        self._blocked_count = 0
        self._allowed_count = 0
        self._warned_count = 0
