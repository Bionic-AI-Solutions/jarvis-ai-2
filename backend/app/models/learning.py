"""Pattern learning models — execution patterns, suggestions, confidence tracking.

Sprint 8 Stories:
  6.1: Workflow Pattern Learning
  6.2: Suggest Workflows
  6.3: Confidence Learning
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, utcnow


class ExecutionPattern(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Detected execution pattern extracted from workflow runs (Story 6.1).

    Tracks recurring sequences of agent+action pairs along with their
    frequency, success rate, and whether they have been suggested to the user.
    """

    __tablename__ = "execution_patterns"

    pattern_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    intent: Mapped[str] = mapped_column(String(200), nullable=False)
    steps_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    suggested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False,
    )


class SuggestionLog(Base, UUIDPrimaryKeyMixin):
    """Log of workflow suggestions shown to the user (Story 6.2)."""

    __tablename__ = "suggestion_logs"

    pattern_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("execution_patterns.id", ondelete="CASCADE"),
        nullable=False,
    )
    suggestion_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="workflow",
    )
    accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False,
    )


class ConfidenceHistory(Base, UUIDPrimaryKeyMixin):
    """Tracks confidence threshold adjustments over time (Story 6.3)."""

    __tablename__ = "confidence_history"

    context: Mapped[str] = mapped_column(String(100), nullable=False)  # voice | agent | workflow
    old_value: Mapped[float] = mapped_column(Float, nullable=False)
    new_value: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False,
    )
