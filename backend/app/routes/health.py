"""Health check endpoint — Story 7.4."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.health import ComponentHealth, HealthResponse

router = APIRouter(tags=["Health"])

_startup_time: float = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Deep health check that probes all backend components.

    Returns:
        - overall status (healthy / degraded / unhealthy)
        - per-component status (database, Ollama)
        - uptime and version
    """
    components: list[ComponentHealth] = []

    # 1. Database health
    db_health = await _check_database(db)
    components.append(db_health)

    # 2. Ollama health
    ollama_health = await _check_ollama(settings.ollama_host)
    components.append(ollama_health)

    # Overall status: unhealthy if any unhealthy, degraded if any degraded
    statuses = [c.status for c in components]
    if "unhealthy" in statuses:
        overall = "unhealthy"
    elif "degraded" in statuses:
        overall = "degraded"
    else:
        overall = "healthy"

    return HealthResponse(
        status=overall,
        version=settings.version,
        uptime_seconds=round(time.time() - _startup_time, 2),
        timestamp=datetime.now(timezone.utc),
        components=components,
    )


async def _check_database(db: AsyncSession) -> ComponentHealth:
    """Probe the database with a trivial query."""
    start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        latency = round((time.perf_counter() - start) * 1000, 2)
        return ComponentHealth(name="database", status="healthy", latency_ms=latency)
    except Exception as exc:
        latency = round((time.perf_counter() - start) * 1000, 2)
        return ComponentHealth(
            name="database", status="unhealthy", latency_ms=latency, detail=str(exc)
        )


async def _check_ollama(ollama_host: str) -> ComponentHealth:
    """Ping the Ollama API."""
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{ollama_host}/api/version")
            latency = round((time.perf_counter() - start) * 1000, 2)
            if resp.status_code == 200:
                return ComponentHealth(
                    name="ollama", status="healthy", latency_ms=latency,
                    detail=resp.json().get("version", "unknown"),
                )
            return ComponentHealth(
                name="ollama", status="degraded", latency_ms=latency,
                detail=f"HTTP {resp.status_code}",
            )
    except Exception as exc:
        latency = round((time.perf_counter() - start) * 1000, 2)
        return ComponentHealth(
            name="ollama", status="unhealthy", latency_ms=latency, detail=str(exc)
        )
