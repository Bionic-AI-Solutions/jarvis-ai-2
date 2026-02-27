"""SAA — Step-Action Adapter (Agent 5).

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 5
Role: Choose execution method per plan step (PowerShell, keyboard, filesystem, etc.)
Model: qwen2.5:3b
Responsibilities:
  1. Map each annotated step → primary execution method
  2. Add recovery/fallback methods per step
  3. Estimate resource needs
  4. Wire API call details, hotkeys, CLI commands
Output is the final execution-ready plan sent to the Execution Agent.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Method priorities for action types (Architecture V3 Table)
METHOD_MAP: Dict[str, Dict[str, Any]] = {
    "open_application": {
        "primary": "powershell",
        "command_template": "Start-Process '{target}'",
        "fallback": "keyboard_shortcut",
        "fallback_detail": "Win+R → type app name → Enter",
        "resource": "low",
    },
    "close_application": {
        "primary": "powershell",
        "command_template": "Stop-Process -Name '{target}' -Force",
        "fallback": "keyboard_shortcut",
        "fallback_detail": "Alt+F4",
        "resource": "low",
    },
    "click": {
        "primary": "desktop_automation",
        "command_template": "mouse_click({x}, {y})",
        "fallback": "accessibility_api",
        "fallback_detail": "UI Automation click by name/id",
        "resource": "medium",
    },
    "type_text": {
        "primary": "keyboard",
        "command_template": "type_text('{text}')",
        "fallback": "clipboard",
        "fallback_detail": "Set-Clipboard + Ctrl+V",
        "resource": "low",
    },
    "key_press": {
        "primary": "keyboard",
        "command_template": "key_combination('{keys}')",
        "fallback": None,
        "resource": "low",
    },
    "screenshot": {
        "primary": "powershell",
        "command_template": "screenshot capture",
        "fallback": "keyboard_shortcut",
        "fallback_detail": "PrtScn key",
        "resource": "medium",
    },
    "navigate": {
        "primary": "powershell",
        "command_template": "Start-Process '{url}'",
        "fallback": "keyboard",
        "fallback_detail": "Ctrl+L → type URL → Enter",
        "resource": "low",
    },
    "file_create": {
        "primary": "filesystem",
        "command_template": "New-Item -Path '{path}' -ItemType File",
        "fallback": "powershell",
        "resource": "low",
    },
    "file_delete": {
        "primary": "filesystem",
        "command_template": "Remove-Item -Path '{path}' -Force",
        "fallback": "powershell",
        "resource": "low",
    },
    "file_copy": {
        "primary": "filesystem",
        "command_template": "Copy-Item -Path '{source}' -Destination '{dest}'",
        "fallback": "powershell",
        "resource": "low",
    },
    "file_move": {
        "primary": "filesystem",
        "command_template": "Move-Item -Path '{source}' -Destination '{dest}'",
        "fallback": "powershell",
        "resource": "low",
    },
    "web_request": {
        "primary": "rest_api",
        "command_template": "Invoke-RestMethod -Uri '{url}'",
        "fallback": "powershell",
        "resource": "medium",
    },
    "wait": {
        "primary": "sleep",
        "command_template": "Start-Sleep -Milliseconds {duration}",
        "fallback": None,
        "resource": "low",
    },
}


class SAAAgent(BaseAgent):
    """Step-Action Adapter — selects execution method for each plan step.

    Architecture V3, Agent 5:
    Input:  {annotated_plan: [{action, target, parameters, preconditions, ...}]}
    Output: {execution_plan: [{primary_method, command, recovery_methods,
             tools_required, resource_estimate}], next_agent: "execution_agent"}
    """

    def __init__(self, ollama_service=None):
        super().__init__(
            agent_name="saa_agent",
            agent_type="planning",
            description="Step-Action Adapter — maps annotated steps to execution methods",
        )
        self.ollama_service = ollama_service

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: produce execution-ready plan.

        Args:
            input_data: {
                "annotated_plan": [...annotated steps from SPA...],
                "system_state": dict,  # optional OS/app context
                "context": dict,
            }
        """
        start = time.perf_counter()
        annotated_plan = input_data.get("annotated_plan") or input_data.get("plan", [])

        if not annotated_plan:
            return {
                "status": "failure",
                "error": "No annotated plan provided",
                "next_agent": None,
            }

        if isinstance(annotated_plan, dict) and "steps" in annotated_plan:
            annotated_plan = annotated_plan["steps"]
        elif not isinstance(annotated_plan, list):
            annotated_plan = [annotated_plan]

        execution_steps: List[Dict[str, Any]] = []
        for step in annotated_plan:
            exec_step = await self._adapt_step(step)
            execution_steps.append(exec_step)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            "status": "success",
            "execution_plan": execution_steps,
            "step_count": len(execution_steps),
            "next_agent": "execution_agent",
            "duration_ms": duration_ms,
        }

    async def _adapt_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Map a single annotated step to an execution specification."""
        action = step.get("action", "unknown").lower()
        target = step.get("target", "")
        parameters = step.get("parameters", {})

        # Look up method mapping
        method_info = METHOD_MAP.get(action, None)

        if method_info:
            result = self._rule_based_adapt(action, target, parameters, method_info, step)
        else:
            # Unknown action — try LLM, fall back to generic
            result = await self._llm_adapt(step)
            if not result:
                result = self._generic_adapt(action, target, parameters, step)

        return result

    def _rule_based_adapt(
        self,
        action: str,
        target: str,
        parameters: Dict,
        method_info: Dict,
        original_step: Dict,
    ) -> Dict[str, Any]:
        """Generate execution spec from rule-based method mapping."""
        # Fill command template
        command = method_info["command_template"]
        command = command.replace("{target}", target or "")
        for k, v in parameters.items():
            command = command.replace(f"{{{k}}}", str(v))

        # Build recovery methods
        recovery_methods: List[Dict[str, str]] = []
        if method_info.get("fallback"):
            recovery_methods.append({
                "method": method_info["fallback"],
                "detail": method_info.get("fallback_detail", ""),
            })

        return {
            # Preserve original step data
            **original_step,
            # Execution specification
            "primary_method": method_info["primary"],
            "command": command,
            "recovery_methods": recovery_methods,
            "tools_required": [method_info["primary"]],
            "resource_estimate": method_info.get("resource", "low"),
        }

    async def _llm_adapt(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to determine execution method for unknown actions."""
        if not self.ollama_service:
            return None

        try:
            system_prompt = (
                "You are a system-action adapter. Given a plan step, determine:\n"
                "1. primary_method: powershell|keyboard|filesystem|rest_api|"
                "desktop_automation|clipboard|sleep\n"
                "2. command: the actual command/instruction to execute\n"
                "3. recovery_methods: list of fallback approaches\n"
                "Return ONLY valid JSON."
            )
            prompt = f"Adapt this step for execution: {json.dumps(step)}"

            response = await self.ollama_service.generate(
                prompt=prompt,
                system=system_prompt,
                temperature=0.3,
                max_tokens=512,
            )

            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    **step,
                    "primary_method": data.get("primary_method", "powershell"),
                    "command": data.get("command", ""),
                    "recovery_methods": data.get("recovery_methods", []),
                    "tools_required": [data.get("primary_method", "powershell")],
                    "resource_estimate": "medium",
                }
        except Exception as e:
            logger.debug(f"SAA LLM adaptation failed: {e}")

        return None

    def _generic_adapt(
        self,
        action: str,
        target: str,
        parameters: Dict,
        original_step: Dict,
    ) -> Dict[str, Any]:
        """Fallback: wrap unknown action in PowerShell."""
        param_str = " ".join(f"-{k} '{v}'" for k, v in parameters.items())
        command = f"# Unknown action: {action} {target} {param_str}".strip()

        return {
            **original_step,
            "primary_method": "powershell",
            "command": command,
            "recovery_methods": [],
            "tools_required": ["powershell"],
            "resource_estimate": "low",
        }
