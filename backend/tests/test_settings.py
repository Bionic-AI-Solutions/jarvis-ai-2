"""Tests for /api/settings and /api/settings/mode endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_settings_empty(client: AsyncClient):
    """Initially no user settings exist."""
    resp = await client.get("/api/settings")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_upsert_setting(client: AsyncClient):
    """Create a new setting via upsert."""
    resp = await client.put("/api/settings", json={"key": "theme", "value": "dark"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["key"] == "theme"
    assert body["value"] == "dark"


@pytest.mark.asyncio
async def test_upsert_updates_existing(client: AsyncClient):
    """Upsert an existing key should update the value."""
    await client.put("/api/settings", json={"key": "theme", "value": "dark"})
    resp = await client.put("/api/settings", json={"key": "theme", "value": "light"})
    assert resp.status_code == 200
    assert resp.json()["value"] == "light"


@pytest.mark.asyncio
async def test_list_settings_after_insert(client: AsyncClient):
    """After inserting, settings list should be non-empty."""
    await client.put("/api/settings", json={"key": "lang", "value": "en"})
    resp = await client.get("/api/settings")
    settings = resp.json()
    assert len(settings) >= 1
    assert any(s["key"] == "lang" for s in settings)


@pytest.mark.asyncio
async def test_get_mode_default(client: AsyncClient):
    """Default mode should be 'auto'."""
    resp = await client.get("/api/settings/mode")
    assert resp.status_code == 200
    assert resp.json()["mode"] == "auto"


@pytest.mark.asyncio
async def test_set_mode(client: AsyncClient):
    """Set mode to supervised."""
    resp = await client.post("/api/settings/mode", json={"mode": "supervised"})
    assert resp.status_code == 200
    assert resp.json()["mode"] == "supervised"


@pytest.mark.asyncio
async def test_set_mode_invalid(client: AsyncClient):
    """Invalid mode should return 422."""
    resp = await client.post("/api/settings/mode", json={"mode": "turbo"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_mode_round_trip(client: AsyncClient):
    """Set mode and verify via GET."""
    await client.post("/api/settings/mode", json={"mode": "locked"})
    resp = await client.get("/api/settings/mode")
    assert resp.json()["mode"] == "locked"
