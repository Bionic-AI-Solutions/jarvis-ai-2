"""Chat session and message models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single chat conversation."""

    __tablename__ = "chat_sessions"

    title: Mapped[str] = mapped_column(String(255), default="New Chat", nullable=False)
    mode: Mapped[str] = mapped_column(String(20), default="auto", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.sequence",
        lazy="selectin",
    )


class ChatMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual message within a chat session."""

    __tablename__ = "chat_messages"

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user | assistant | system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
