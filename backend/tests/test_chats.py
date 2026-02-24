"""Tests for /api/chats endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_sessions_empty(client: AsyncClient):
    """Initially there should be no sessions."""
    resp = await client.get("/api/chats")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_session_defaults(client: AsyncClient):
    """Create a session with default values."""
    resp = await client.post("/api/chats", json={})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "New Chat"
    assert body["mode"] == "auto"
    assert body["is_active"] is True
    assert "id" in body


@pytest.mark.asyncio
async def test_create_session_custom(client: AsyncClient):
    """Create a session with custom title and mode."""
    resp = await client.post("/api/chats", json={"title": "My Chat", "mode": "supervised"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "My Chat"
    assert body["mode"] == "supervised"


@pytest.mark.asyncio
async def test_get_session(client: AsyncClient):
    """Retrieve a session by ID."""
    create = await client.post("/api/chats", json={"title": "Fetch Me"})
    sid = create.json()["id"]

    resp = await client.get(f"/api/chats/{sid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sid
    assert resp.json()["title"] == "Fetch Me"


@pytest.mark.asyncio
async def test_get_session_not_found(client: AsyncClient):
    """404 for non-existent session."""
    resp = await client.get("/api/chats/00000000-0000-0000-0000-000000000099")
    assert resp.status_code == 404
    assert "error_code" in resp.json()


@pytest.mark.asyncio
async def test_update_session(client: AsyncClient):
    """Update a session title."""
    create = await client.post("/api/chats", json={"title": "Original"})
    sid = create.json()["id"]

    resp = await client.put(f"/api/chats/{sid}", json={"title": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_delete_session(client: AsyncClient):
    """Delete a session and verify it's gone."""
    create = await client.post("/api/chats", json={"title": "Delete Me"})
    sid = create.json()["id"]

    resp = await client.delete(f"/api/chats/{sid}")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    resp = await client.get(f"/api/chats/{sid}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_message(client: AsyncClient):
    """Add a user message to a session."""
    create = await client.post("/api/chats", json={})
    sid = create.json()["id"]

    resp = await client.post(
        f"/api/chats/{sid}/messages",
        json={"content": "Hello, Jarvis!", "role": "user"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["content"] == "Hello, Jarvis!"
    assert body["role"] == "user"
    assert body["sequence"] == 1


@pytest.mark.asyncio
async def test_message_sequence_increments(client: AsyncClient):
    """Messages in the same session should have incrementing sequence."""
    create = await client.post("/api/chats", json={})
    sid = create.json()["id"]

    await client.post(f"/api/chats/{sid}/messages", json={"content": "First"})
    resp = await client.post(f"/api/chats/{sid}/messages", json={"content": "Second"})
    assert resp.json()["sequence"] == 2


@pytest.mark.asyncio
async def test_list_messages(client: AsyncClient):
    """List all messages in a session."""
    create = await client.post("/api/chats", json={})
    sid = create.json()["id"]

    await client.post(f"/api/chats/{sid}/messages", json={"content": "Msg 1"})
    await client.post(f"/api/chats/{sid}/messages", json={"content": "Msg 2"})

    resp = await client.get(f"/api/chats/{sid}/messages")
    assert resp.status_code == 200
    msgs = resp.json()
    assert len(msgs) == 2
    assert msgs[0]["sequence"] == 1
    assert msgs[1]["sequence"] == 2


@pytest.mark.asyncio
async def test_add_message_to_nonexistent_session(client: AsyncClient):
    """Adding a message to a bad session ID returns 404."""
    resp = await client.post(
        "/api/chats/bad-session-id/messages",
        json={"content": "Orphan message"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_session_invalid_mode(client: AsyncClient):
    """Invalid mode value should fail validation (422)."""
    resp = await client.post("/api/chats", json={"mode": "invalid_mode"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_sessions_active_only(client: AsyncClient):
    """Filter sessions by active status."""
    await client.post("/api/chats", json={"title": "Active Chat"})
    resp = await client.get("/api/chats", params={"active_only": True})
    assert resp.status_code == 200
    sessions = resp.json()
    assert all(s["is_active"] for s in sessions)
