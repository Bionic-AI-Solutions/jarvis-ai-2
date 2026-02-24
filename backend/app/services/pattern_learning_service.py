"""Pattern learning service — detect recurring execution patterns.

Sprint 8 Story 6.1: Workflow Pattern Learning
- Extract patterns from execution history
- Compute pattern hashes for deduplication
- Track frequency, success rate, confidence
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError
from app.core.logging_config import get_logger
from app.models.learning import ExecutionPattern, SuggestionLog

logger = get_logger(__name__)

# Minimum occurrences before a pattern is suggested
_MIN_FREQUENCY_TO_SUGGEST = 3
_SUGGESTION_CONFIDENCE_THRESHOLD = 0.6


def _compute_pattern_hash(steps: List[Dict[str, Any]]) -> str:
    """Create a deterministic hash for a sequence of steps."""
    normalized = json.dumps(
        [{"agent": s.get("agent", ""), "action": s.get("action", "")} for s in steps],
        sort_keys=True,
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class PatternLearningService:
    """Detects and tracks recurring execution patterns."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record_execution(
        self,
        *,
        intent: str,
        steps: List[Dict[str, Any]],
        success: bool = True,
    ) -> ExecutionPattern:
        """Record an execution and update or create a pattern.

        Args:
            intent: The user intent / command.
            steps: List of step dicts with 'agent' and 'action' keys.
            success: Whether the execution succeeded.

        Returns:
            The created or updated ExecutionPattern.
        """
        pattern_hash = _compute_pattern_hash(steps)

        stmt = select(ExecutionPattern).where(
            ExecutionPattern.pattern_hash == pattern_hash
        )
        result = await self.db.execute(stmt)
        pattern = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if pattern is None:
            pattern = ExecutionPattern(
                pattern_hash=pattern_hash,
                intent=intent,
                steps_json=json.dumps(steps),
                frequency=1,
                success_rate=1.0 if success else 0.0,
                confidence=0.0,
                last_seen=now,
            )
            self.db.add(pattern)
        else:
            # Update frequency and success rate (running average)
            pattern.frequency += 1
            old_rate = pattern.success_rate
            n = pattern.frequency
            pattern.success_rate = old_rate + (
                (1.0 if success else 0.0) - old_rate
            ) / n
            pattern.last_seen = now
            # Recompute confidence = f(frequency, success_rate)
            pattern.confidence = min(
                1.0,
                (pattern.frequency / 10.0) * pattern.success_rate,
            )

        await self.db.flush()
        logger.info(
            "pattern_recorded",
            pattern_hash=pattern_hash[:12],
            frequency=pattern.frequency,
            confidence=round(pattern.confidence, 3),
        )
        return pattern

    async def list_patterns(
        self,
        *,
        min_frequency: int = 1,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[ExecutionPattern]:
        """List patterns ordered by frequency descending."""
        stmt = (
            select(ExecutionPattern)
            .where(ExecutionPattern.frequency >= min_frequency)
            .order_by(ExecutionPattern.frequency.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_pattern(self, pattern_id: str) -> ExecutionPattern:
        """Get a single pattern by ID."""
        stmt = select(ExecutionPattern).where(ExecutionPattern.id == pattern_id)
        result = await self.db.execute(stmt)
        pattern = result.scalar_one_or_none()
        if pattern is None:
            raise JarvisError(ErrorCode.PATTERN_NOT_FOUND, detail=pattern_id)
        return pattern

    async def get_suggestions(
        self,
        *,
        limit: int = 5,
    ) -> Sequence[ExecutionPattern]:
        """Get patterns eligible for suggestion (high frequency + confidence, not yet accepted)."""
        stmt = (
            select(ExecutionPattern)
            .where(
                ExecutionPattern.frequency >= _MIN_FREQUENCY_TO_SUGGEST,
                ExecutionPattern.confidence >= _SUGGESTION_CONFIDENCE_THRESHOLD,
                ExecutionPattern.accepted.is_(False),
            )
            .order_by(ExecutionPattern.confidence.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def accept_suggestion(self, pattern_id: str) -> SuggestionLog:
        """Mark a pattern as accepted and log the action."""
        pattern = await self.get_pattern(pattern_id)

        # Check if already handled
        stmt = select(SuggestionLog).where(
            SuggestionLog.pattern_id == pattern_id,
            (SuggestionLog.accepted.is_(True) | SuggestionLog.dismissed.is_(True)),
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing is not None:
            raise JarvisError(ErrorCode.SUGGESTION_ALREADY_HANDLED)

        pattern.accepted = True
        pattern.suggested = True

        log_entry = SuggestionLog(
            pattern_id=pattern_id,
            suggestion_type="workflow",
            accepted=True,
            dismissed=False,
        )
        self.db.add(log_entry)
        await self.db.flush()

        logger.info("suggestion_accepted", pattern_id=pattern_id)
        return log_entry

    async def dismiss_suggestion(self, pattern_id: str) -> SuggestionLog:
        """Dismiss a pattern suggestion."""
        pattern = await self.get_pattern(pattern_id)

        stmt = select(SuggestionLog).where(
            SuggestionLog.pattern_id == pattern_id,
            (SuggestionLog.accepted.is_(True) | SuggestionLog.dismissed.is_(True)),
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing is not None:
            raise JarvisError(ErrorCode.SUGGESTION_ALREADY_HANDLED)

        pattern.suggested = True

        log_entry = SuggestionLog(
            pattern_id=pattern_id,
            suggestion_type="workflow",
            accepted=False,
            dismissed=True,
        )
        self.db.add(log_entry)
        await self.db.flush()

        logger.info("suggestion_dismissed", pattern_id=pattern_id)
        return log_entry
