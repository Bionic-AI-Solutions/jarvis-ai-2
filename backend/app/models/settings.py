"""User settings model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserSetting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Key-value user preferences."""

    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")

    __table_args__ = (
        # Enforce uniqueness per user + key
        {"sqlite_autoincrement": False},
    )
