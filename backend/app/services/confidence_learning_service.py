"""Confidence learning service — track and adjust confidence thresholds.

Sprint 8 Story 6.3: Confidence Learning
- Record confidence changes with reason
- Query history by context
- Auto-adjust thresholds based on user feedback
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError
from app.core.logging_config import get_logger
from app.models.learning import ConfidenceHistory

logger = get_logger(__name__)

# Valid context names
VALID_CONTEXTS = {"voice", "agent", "workflow", "pattern"}


class ConfidenceLearningService:
    """Tracks and adjusts confidence thresholds across contexts."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record_change(
        self,
        *,
        context: str,
        old_value: float,
        new_value: float,
        reason: str,
    ) -> ConfidenceHistory:
        """Record a confidence threshold change.

        Args:
            context: Domain context (voice, agent, workflow, pattern).
            old_value: Previous confidence value (0.0-1.0).
            new_value: New confidence value (0.0-1.0).
            reason: Why the change was made.

        Returns:
            The created ConfidenceHistory entry.
        """
        if context not in VALID_CONTEXTS:
            raise JarvisError(
                ErrorCode.CONFIDENCE_OUT_OF_RANGE,
                detail=f"Invalid context '{context}'. Must be one of: {', '.join(sorted(VALID_CONTEXTS))}",
            )
        if not (0.0 <= old_value <= 1.0 and 0.0 <= new_value <= 1.0):
            raise JarvisError(
                ErrorCode.CONFIDENCE_OUT_OF_RANGE,
                detail=f"Values must be between 0.0 and 1.0: old={old_value}, new={new_value}",
            )

        entry = ConfidenceHistory(
            context=context,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
        )
        self.db.add(entry)
        await self.db.flush()

        logger.info(
            "confidence_changed",
            context=context,
            old=round(old_value, 3),
            new=round(new_value, 3),
            reason=reason,
        )
        return entry

    async def get_history(
        self,
        *,
        context: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[ConfidenceHistory]:
        """Get confidence change history, optionally filtered by context."""
        stmt = select(ConfidenceHistory).order_by(
            ConfidenceHistory.timestamp.desc()
        )
        if context is not None:
            stmt = stmt.where(ConfidenceHistory.context == context)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_current_threshold(self, context: str) -> float | None:
        """Get the most recent threshold value for a context.

        Returns None if no history exists.
        """
        stmt = (
            select(ConfidenceHistory)
            .where(ConfidenceHistory.context == context)
            .order_by(ConfidenceHistory.timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        entry = result.scalar_one_or_none()
        return entry.new_value if entry is not None else None

    async def count(self, context: str | None = None) -> int:
        """Count confidence history entries."""
        stmt = select(func.count(ConfidenceHistory.id))
        if context is not None:
            stmt = stmt.where(ConfidenceHistory.context == context)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def auto_adjust(
        self,
        *,
        context: str,
        current_value: float,
        user_accepted: bool,
        step: float = 0.02,
    ) -> ConfidenceHistory | None:
        """Auto-adjust confidence based on user feedback.

        If user accepted, slightly lower threshold (easier acceptance next time).
        If user rejected, slightly raise threshold (stricter next time).

        Args:
            context: Domain context.
            current_value: Current threshold value.
            user_accepted: Whether user accepted the result.
            step: Adjustment step size.

        Returns:
            ConfidenceHistory entry if adjustment made, None if threshold at boundary.
        """
        if user_accepted:
            new_value = max(0.0, current_value - step)
            reason = "User accepted result; lowering threshold"
        else:
            new_value = min(1.0, current_value + step)
            reason = "User rejected result; raising threshold"

        # Don't record if no change
        if abs(new_value - current_value) < 0.001:
            return None

        return await self.record_change(
            context=context,
            old_value=current_value,
            new_value=round(new_value, 4),
            reason=reason,
        )
