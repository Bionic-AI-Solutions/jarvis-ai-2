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
    """Add a user message and receive an assistant response from the pipeline.

    The endpoint now processes user messages through the agent pipeline and
    returns the assistant reply (not the user's original message).
    """
    create = await client.post("/api/chats", json={})
    sid = create.json()["id"]

    resp = await client.post(
        f"/api/chats/{sid}/messages",
        json={"content": "Hello, Jarvis!", "role": "user"},
    )
    assert resp.status_code == 201
    body = resp.json()
    # Pipeline returns assistant response, not the user message echo
    assert body["role"] == "assistant"
    assert isinstance(body["content"], str) and len(body["content"]) > 0
    # User message is seq 1, assistant is seq 2
    assert body["sequence"] == 2


@pytest.mark.asyncio
async def test_message_sequence_increments(client: AsyncClient):
    """Messages in the same session should have incrementing sequence.

    Each user message creates TWO DB records (user + assistant), so:
      - 1st POST: user (seq 1) + assistant (seq 2) → returns seq 2
      - 2nd POST: user (seq 3) + assistant (seq 4) → returns seq 4
    """
    create = await client.post("/api/chats", json={})
    sid = create.json()["id"]

    resp1 = await client.post(f"/api/chats/{sid}/messages", json={"content": "First"})
    assert resp1.json()["sequence"] == 2  # assistant response for "First"

    resp2 = await client.post(f"/api/chats/{sid}/messages", json={"content": "Second"})
    assert resp2.json()["sequence"] == 4  # assistant response for "Second"


@pytest.mark.asyncio
async def test_list_messages(client: AsyncClient):
    """List all messages in a session.

    Each user POST creates user + assistant messages, so 2 POSTs → 4 messages.
    """
    create = await client.post("/api/chats", json={})
    sid = create.json()["id"]

    await client.post(f"/api/chats/{sid}/messages", json={"content": "Msg 1"})
    await client.post(f"/api/chats/{sid}/messages", json={"content": "Msg 2"})

    resp = await client.get(f"/api/chats/{sid}/messages")
    assert resp.status_code == 200
    msgs = resp.json()
    # 2 user messages + 2 assistant responses = 4 total messages
    assert len(msgs) == 4
    assert msgs[0]["sequence"] == 1  # user Msg 1
    assert msgs[1]["sequence"] == 2  # assistant response 1
    assert msgs[2]["sequence"] == 3  # user Msg 2
    assert msgs[3]["sequence"] == 4  # assistant response 2


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
