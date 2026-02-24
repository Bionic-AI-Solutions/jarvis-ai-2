"""AI-powered recovery suggestions — uses Ollama to generate fix suggestions.

Story 3.8: AI Recovery Suggestions
Analyzes error context snapshots and produces actionable recovery steps
using a local LLM via Ollama.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger
from app.services.ollama_service import ollama_service

logger = get_logger(__name__)

# System prompt for the recovery suggestion LLM
_RECOVERY_SYSTEM_PROMPT = """\
You are Jarvis AI's recovery assistant. Given an error context from a failed
workflow step, produce a JSON object with:
{
  "diagnosis": "Brief root-cause analysis (1-2 sentences)",
  "suggestions": [
    {"action": "short action label", "description": "how to implement", "confidence": 0.0-1.0},
    ...
  ],
  "can_auto_recover": true/false,
  "auto_recovery_action": "action to take if can_auto_recover is true, else null"
}

Rules:
- Provide 1-5 suggestions ordered by likelihood of success.
- Confidence is your estimate that the suggestion resolves the issue.
- Be specific: include commands, file paths, or parameter changes.
- If the error is a timeout, suggest increasing timeout or checking network.
- If the error is an agent failure, suggest checking agent health or restarting.
- If the error relates to missing resources, suggest creating or downloading them.
- Only set can_auto_recover=true if a simple retry or parameter change can fix it.
- Respond ONLY with valid JSON, no markdown fences or extra text.
"""


class RecoverySuggestion:
    """Structured recovery suggestion from the AI."""

    def __init__(
        self,
        action: str,
        description: str,
        confidence: float,
    ) -> None:
        self.action = action
        self.description = description
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "description": self.description,
            "confidence": self.confidence,
        }


class RecoverySuggestionResult:
    """Full result from the suggestion engine."""

    def __init__(
        self,
        diagnosis: str,
        suggestions: List[RecoverySuggestion],
        can_auto_recover: bool,
        auto_recovery_action: str | None,
        generated_at: datetime,
        model_used: str,
    ) -> None:
        self.diagnosis = diagnosis
        self.suggestions = suggestions
        self.can_auto_recover = can_auto_recover
        self.auto_recovery_action = auto_recovery_action
        self.generated_at = generated_at
        self.model_used = model_used

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diagnosis": self.diagnosis,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "can_auto_recover": self.can_auto_recover,
            "auto_recovery_action": self.auto_recovery_action,
            "generated_at": self.generated_at.isoformat(),
            "model_used": self.model_used,
        }


class RecoverySuggestionService:
    """Uses Ollama LLM to generate recovery suggestions from error context."""

    def __init__(self, ollama=None) -> None:
        self._ollama = ollama or ollama_service

    async def suggest(
        self,
        error_context: Dict[str, Any],
        model: str | None = None,
    ) -> RecoverySuggestionResult:
        """Generate recovery suggestions from an error context snapshot.

        Args:
            error_context: Parsed ContextSnapshot JSON data.
            model: Optional model override for Ollama.

        Returns:
            RecoverySuggestionResult with diagnosis and suggestions.
        """
        prompt = self._build_prompt(error_context)

        try:
            available = await self._ollama.is_available()
            if not available:
                logger.warning("ollama_unavailable_for_suggestions")
                return self._fallback_suggestions(error_context)

            raw = await self._ollama.generate(
                prompt=prompt,
                system=_RECOVERY_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1024,
                model=model,
            )

            result = self._parse_response(raw, model or self._ollama._model)
            logger.info(
                "recovery_suggestions_generated",
                diagnosis=result.diagnosis[:80],
                suggestion_count=len(result.suggestions),
                can_auto_recover=result.can_auto_recover,
            )
            return result

        except Exception as exc:
            logger.error("recovery_suggestion_error", error=str(exc))
            return self._fallback_suggestions(error_context)

    async def suggest_from_snapshot(
        self,
        snapshot_json: str,
        model: str | None = None,
    ) -> RecoverySuggestionResult:
        """Convenience method: parse snapshot JSON and generate suggestions."""
        context = json.loads(snapshot_json)
        return await self.suggest(context, model=model)

    def _build_prompt(self, ctx: Dict[str, Any]) -> str:
        """Build the user prompt from error context."""
        error_info = ctx.get("error", {})
        step_info = ctx.get("step", {})
        system_info = ctx.get("system", {})
        history = ctx.get("execution_history", [])

        parts = [
            "## Error Details",
            f"- Message: {error_info.get('message', 'Unknown')}",
            f"- Type: {error_info.get('type', 'Unknown')}",
            f"- Timestamp: {error_info.get('timestamp', 'N/A')}",
            "",
            "## Failed Step",
            f"- Agent: {step_info.get('agent', 'Unknown')}",
            f"- Action: {step_info.get('action', 'Unknown')}",
            f"- Parameters: {json.dumps(step_info.get('parameters', {}), default=str)}",
            "",
            "## System State",
            f"- Platform: {system_info.get('platform', 'Unknown')}",
        ]

        mem = system_info.get("memory")
        if mem:
            parts.append(f"- Memory: {mem.get('available_mb', '?')}MB available / "
                        f"{mem.get('total_mb', '?')}MB total ({mem.get('percent_used', '?')}% used)")

        if history:
            parts.append("")
            parts.append("## Recent Execution History")
            for entry in history[-5:]:
                parts.append(
                    f"- Step {entry.get('step_index')}: "
                    f"{entry.get('agent_name', '?')}/{entry.get('action', '?')} "
                    f"→ {entry.get('status', '?')} ({entry.get('duration_ms', 0)}ms)"
                )

        parts.append("")
        parts.append("Generate recovery suggestions as JSON:")

        return "\n".join(parts)

    def _parse_response(self, raw: str, model: str) -> RecoverySuggestionResult:
        """Parse the LLM JSON response into a structured result."""
        # Strip any markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last fence lines
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("recovery_suggestion_parse_failed", raw_length=len(raw))
            return RecoverySuggestionResult(
                diagnosis="Failed to parse AI response",
                suggestions=[
                    RecoverySuggestion("retry", "Retry the failed step", 0.5),
                ],
                can_auto_recover=False,
                auto_recovery_action=None,
                generated_at=datetime.now(timezone.utc),
                model_used=model,
            )

        suggestions = []
        for s in data.get("suggestions", []):
            suggestions.append(RecoverySuggestion(
                action=s.get("action", "unknown"),
                description=s.get("description", ""),
                confidence=float(s.get("confidence", 0.5)),
            ))

        return RecoverySuggestionResult(
            diagnosis=data.get("diagnosis", "No diagnosis provided"),
            suggestions=suggestions,
            can_auto_recover=data.get("can_auto_recover", False),
            auto_recovery_action=data.get("auto_recovery_action"),
            generated_at=datetime.now(timezone.utc),
            model_used=model,
        )

    def _fallback_suggestions(self, ctx: Dict[str, Any]) -> RecoverySuggestionResult:
        """Generate rule-based suggestions when Ollama is unavailable."""
        error_msg = ctx.get("error", {}).get("message", "").lower()
        error_type = ctx.get("error", {}).get("type", "").lower()
        suggestions: list[RecoverySuggestion] = []

        if "timeout" in error_msg or error_type == "timeout":
            suggestions.append(RecoverySuggestion(
                "increase_timeout", "Increase agent timeout in settings", 0.7,
            ))
            suggestions.append(RecoverySuggestion(
                "check_network", "Verify network connectivity to the agent", 0.5,
            ))
        elif "not found" in error_msg:
            suggestions.append(RecoverySuggestion(
                "verify_agent", "Check that the agent is registered and running", 0.8,
            ))
        elif "unhealthy" in error_msg:
            suggestions.append(RecoverySuggestion(
                "restart_agent", "Restart the agent process", 0.7,
            ))
            suggestions.append(RecoverySuggestion(
                "check_resources", "Verify system resources (memory, disk)", 0.5,
            ))
        else:
            suggestions.append(RecoverySuggestion(
                "retry", "Retry the failed step", 0.5,
            ))
            suggestions.append(RecoverySuggestion(
                "skip", "Skip this step if it is not critical", 0.3,
            ))

        return RecoverySuggestionResult(
            diagnosis="AI suggestions unavailable — using rule-based fallback",
            suggestions=suggestions,
            can_auto_recover=False,
            auto_recovery_action=None,
            generated_at=datetime.now(timezone.utc),
            model_used="fallback",
        )


# Module-level singleton
recovery_suggestion_service = RecoverySuggestionService()
