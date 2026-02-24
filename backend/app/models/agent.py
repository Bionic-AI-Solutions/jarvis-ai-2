"""Application registry model — tracks external apps available on the machine."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ApplicationRegistry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Registry of desktop applications known to JARVIS."""

    __tablename__ = "application_registry"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    exe_path: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    icon_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    launch_args: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
