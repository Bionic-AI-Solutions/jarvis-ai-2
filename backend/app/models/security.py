"""Security-related models: AuthLog, FailureHistory, PendingRequest."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin, utcnow


class AuthLog(Base, UUIDPrimaryKeyMixin):
    """Audit log for authentication attempts."""

    __tablename__ = "auth_log"

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    event: Mapped[str] = mapped_column(String(50), nullable=False)  # login_success | login_failed | lockout | unlock
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, default="127.0.0.1")
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class FailureHistory(Base, UUIDPrimaryKeyMixin):
    """Record of execution / agent failures for recovery analysis."""

    __tablename__ = "failure_history"

    execution_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("workflow_executions.id", ondelete="SET NULL"),
        nullable=True,
    )
    error_code: Mapped[str] = mapped_column(String(20), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    recovery_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resolved: Mapped[bool] = mapped_column(default=False, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class PendingRequest(Base, UUIDPrimaryKeyMixin):
    """Requests queued when the system is in locked / supervised mode."""

    __tablename__ = "pending_requests"

    session_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending | approved | rejected | expired
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
