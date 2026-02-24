"""Metrics model — stores performance and usage telemetry."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin, utcnow


class Metric(Base, UUIDPrimaryKeyMixin):
    """Time-series metric data point."""

    __tablename__ = "metrics"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    tags_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )
