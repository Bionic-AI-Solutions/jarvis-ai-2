"""Tests for /health endpoint (Story 7.4)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    """Health endpoint should always return 200 with status field."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
    assert body["status"] in ("healthy", "degraded", "unhealthy")


@pytest.mark.asyncio
async def test_health_contains_version(client: AsyncClient):
    """Health response must include the app version."""
    resp = await client.get("/health")
    body = resp.json()
    assert "version" in body
    assert isinstance(body["version"], str)


@pytest.mark.asyncio
async def test_health_contains_uptime(client: AsyncClient):
    """Health response must include uptime_seconds."""
    resp = await client.get("/health")
    body = resp.json()
    assert "uptime_seconds" in body
    assert body["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_health_contains_components(client: AsyncClient):
    """Health response must list component checks."""
    resp = await client.get("/health")
    body = resp.json()
    assert "components" in body
    assert isinstance(body["components"], list)
    names = [c["name"] for c in body["components"]]
    assert "database" in names


@pytest.mark.asyncio
async def test_health_database_healthy(client: AsyncClient):
    """Database component should be healthy in test env."""
    resp = await client.get("/health")
    body = resp.json()
    db_comp = next(c for c in body["components"] if c["name"] == "database")
    assert db_comp["status"] == "healthy"
    assert db_comp["latency_ms"] >= 0
