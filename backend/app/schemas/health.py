"""Health check schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ComponentHealth(BaseModel):
    """Health status of one backend component."""

    name: str
    status: str  # healthy | degraded | unhealthy
    latency_ms: Optional[float] = None
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Aggregated health check response."""

    status: str  # healthy | degraded | unhealthy
    version: str
    uptime_seconds: float
    timestamp: datetime
    components: list[ComponentHealth] = []
