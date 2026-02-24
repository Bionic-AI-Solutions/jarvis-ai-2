"""Workflow and workflow revision models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Workflow(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Reusable workflow template."""

    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    trigger_type: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    revisions: Mapped[list["WorkflowRevision"]] = relationship(
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class WorkflowRevision(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit trail for workflow edits — stores previous version snapshots."""

    __tablename__ = "workflow_revisions"

    workflow_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    steps_json: Mapped[str] = mapped_column(Text, nullable=False)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="revisions")
