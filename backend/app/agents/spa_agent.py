"""SPA — Semantic Plan Annotator (Agent 4).

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 4
Role: Annotate raw plan steps with preconditions, timeouts, rollback hints,
      expected UI changes, and verification queries.
Model: qwen2.5:3b
Performance: 2-5s per plan annotation
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Default timeouts by action category (milliseconds)
DEFAULT_TIMEOUTS: Dict[str, int] = {
    "open_application": 10000,
    "close_application": 5000,
    "click": 3000,
    "type_text": 2000,
    "key_press": 1000,
    "screenshot": 3000,
    "file_operation": 5000,
    "navigate": 8000,
    "wait": 15000,
    "default": 5000,
}


class SPAAgent(BaseAgent):
    """Semantic Plan Annotator — enriches raw plans with execution metadata.

    Architecture V3, Agent 4:
    Input:  {raw_plan: [{action, target, parameters}...]}
    Output: {annotated_plan: [{...step, preconditions, timeout_ms, rollback,
             expected_ui_change, verification_query}], next_agent: "saa"}
    """

    def __init__(self, ollama_service=None):
        super().__init__(
            agent_name="spa_agent",
            agent_type="planning",
            description="Semantic Plan Annotator — enriches plans with preconditions, "
                        "timeouts, rollback hints, and verification queries",
        )
        self.ollama_service = ollama_service

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: annotate every step in the raw plan.

        Args:
            input_data: {
                "raw_plan": [
                    {"action": str, "target": str, "parameters": {}, "step_number": int},
                    ...
                ],
                "user_intent": str,   # original request text
                "context": dict,
            }
        """
        start = time.perf_counter()
        raw_plan = input_data.get("raw_plan") or input_data.get("plan", [])
        user_intent = input_data.get("user_intent", "")

        if not raw_plan:
            return {
                "status": "failure",
                "error": "No plan steps to annotate",
                "next_agent": None,
            }

        # Normalize to list of dicts
        if isinstance(raw_plan, dict) and "steps" in raw_plan:
            raw_plan = raw_plan["steps"]
        elif not isinstance(raw_plan, list):
            raw_plan = [raw_plan]

        annotated_steps: List[Dict[str, Any]] = []
        for i, step in enumerate(raw_plan):
            annotated = await self._annotate_step(step, i, raw_plan, user_intent)
            annotated_steps.append(annotated)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            "status": "success",
            "annotated_plan": annotated_steps,
            "step_count": len(annotated_steps),
            "next_agent": "saa_agent",
            "duration_ms": duration_ms,
        }

    async def _annotate_step(
        self,
        step: Dict[str, Any],
        index: int,
        full_plan: List[Dict],
        user_intent: str,
    ) -> Dict[str, Any]:
        """Annotate a single step with metadata."""
        action = step.get("action", "unknown")
        target = step.get("target", "")

        # Try LLM annotation first
        llm_annotation = await self._llm_annotate(step, index, full_plan, user_intent)
        
        # Merge LLM annotation with rule-based defaults
        rule_annotation = self._rule_based_annotate(action, target, index, full_plan)
        
        # LLM takes precedence where it provided values, rule-based fills gaps
        merged = {**rule_annotation, **{k: v for k, v in llm_annotation.items() if v}}

        return {
            **step,
            "step_number": index + 1,
            "preconditions": merged.get("preconditions", []),
            "timeout_ms": merged.get("timeout_ms", DEFAULT_TIMEOUTS["default"]),
            "rollback_hint": merged.get("rollback_hint", ""),
            "expected_ui_change": merged.get("expected_ui_change", ""),
            "verification_query": merged.get("verification_query", ""),
            "retry_count": merged.get("retry_count", 1),
            "critical": merged.get("critical", False),
        }

    async def _llm_annotate(
        self,
        step: Dict[str, Any],
        index: int,
        full_plan: List[Dict],
        user_intent: str,
    ) -> Dict[str, Any]:
        """Use LLM to generate rich annotations."""
        if not self.ollama_service:
            return {}

        try:
            system_prompt = (
                "You are a plan annotation system. For each execution step, provide:\n"
                "1. preconditions: list of conditions that must be true\n"
                "2. timeout_ms: max time in milliseconds\n"
                "3. rollback_hint: how to undo this step\n"
                "4. expected_ui_change: what should visually change\n"
                "5. verification_query: how to verify success\n"
                "Return ONLY valid JSON with these keys."
            )
            prompt = (
                f"User intent: \"{user_intent}\"\n"
                f"Step {index + 1} of {len(full_plan)}: {json.dumps(step)}\n"
                "Annotate this step with preconditions, timeout_ms, rollback_hint, "
                "expected_ui_change, verification_query:"
            )

            response = await self.ollama_service.generate(
                prompt=prompt,
                system=system_prompt,
                temperature=0.3,
                max_tokens=512,
            )

            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "preconditions": data.get("preconditions", []),
                    "timeout_ms": data.get("timeout_ms"),
                    "rollback_hint": data.get("rollback_hint", ""),
                    "expected_ui_change": data.get("expected_ui_change", ""),
                    "verification_query": data.get("verification_query", ""),
                }
        except Exception as e:
            logger.debug(f"SPA LLM annotation skipped: {e}")

        return {}

    def _rule_based_annotate(
        self,
        action: str,
        target: str,
        index: int,
        full_plan: List[Dict],
    ) -> Dict[str, Any]:
        """Generate annotations using rules (no LLM)."""
        action_lower = action.lower()
        target_lower = target.lower() if target else ""

        # --- Preconditions ---
        preconditions: List[str] = []
        if index > 0:
            prev_action = full_plan[index - 1].get("action", "")
            preconditions.append(f"Step {index} ({prev_action}) completed successfully")

        if "open" in action_lower:
            preconditions.append(f"Application '{target}' is installed")
        elif "click" in action_lower:
            preconditions.append(f"UI element '{target}' is visible and clickable")
        elif "type" in action_lower:
            preconditions.append("Input field is focused")
        elif "close" in action_lower:
            preconditions.append(f"Application '{target}' is running")

        # --- Timeout ---
        timeout_ms = DEFAULT_TIMEOUTS.get(action_lower, DEFAULT_TIMEOUTS["default"])
        if any(kw in target_lower for kw in ["browser", "chrome", "firefox", "edge"]):
            timeout_ms = max(timeout_ms, 15000)

        # --- Rollback hint ---
        rollback_hint = ""
        if "open" in action_lower:
            rollback_hint = f"Close {target}"
        elif "close" in action_lower:
            rollback_hint = f"Re-open {target}"
        elif "type" in action_lower:
            rollback_hint = "Select all and delete typed text (Ctrl+A, Delete)"
        elif "click" in action_lower:
            rollback_hint = "Press Escape or Ctrl+Z to undo click action"
        elif "delete" in action_lower:
            rollback_hint = "Restore from Recycle Bin or backup"
        elif "move" in action_lower or "rename" in action_lower:
            rollback_hint = "Move/rename back to original path"

        # --- Expected UI change ---
        expected_ui_change = ""
        if "open" in action_lower:
            expected_ui_change = f"{target} window appears on screen"
        elif "close" in action_lower:
            expected_ui_change = f"{target} window disappears"
        elif "click" in action_lower:
            expected_ui_change = f"Response after clicking {target}"
        elif "type" in action_lower:
            expected_ui_change = "Text appears in active input field"
        elif "screenshot" in action_lower:
            expected_ui_change = "Screenshot file created"

        # --- Verification query ---
        verification = ""
        if "open" in action_lower:
            verification = f"Is {target} window visible in taskbar/screen?"
        elif "close" in action_lower:
            verification = f"Is {target} no longer in running processes?"
        elif "type" in action_lower:
            verification = "Does the input field contain the typed text?"
        elif "screenshot" in action_lower:
            verification = "Does the screenshot file exist and have non-zero size?"

        # --- Critical flag ---
        critical = "delete" in action_lower or "format" in action_lower or "sudo" in action_lower

        return {
            "preconditions": preconditions,
            "timeout_ms": timeout_ms,
            "rollback_hint": rollback_hint,
            "expected_ui_change": expected_ui_change,
            "verification_query": verification,
            "retry_count": 2 if critical else 1,
            "critical": critical,
        }
