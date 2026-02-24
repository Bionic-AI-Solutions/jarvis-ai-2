"""Execution-related models: WorkflowExecution, ExecutionLog, ContextSnapshot."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utcnow


class WorkflowExecution(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Single execution run of a workflow."""

    __tablename__ = "workflow_executions"

    workflow_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    session_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending | running | completed | failed | cancelled
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    logs: Mapped[list["ExecutionLog"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    snapshots: Mapped[list["ContextSnapshot"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ExecutionLog(Base, UUIDPrimaryKeyMixin):
    """Granular log entry for an execution step."""

    __tablename__ = "execution_logs"

    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success | failed | skipped
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    screenshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    execution: Mapped["WorkflowExecution"] = relationship(back_populates="logs")


class ContextSnapshot(Base, UUIDPrimaryKeyMixin):
    """Stores a JSON snapshot of app context at a given execution point."""

    __tablename__ = "context_snapshots"

    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    execution: Mapped["WorkflowExecution"] = relationship(back_populates="snapshots")
