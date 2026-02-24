"""Tests for WebSocket /ws endpoint (Story 7.3)."""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from app.db.session import get_db
from app.config import get_settings


def _get_test_app():
    """Create a test app with overrides."""
    from tests.conftest import _override_get_db, _get_test_settings
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_settings] = _get_test_settings
    return app


@pytest.mark.asyncio
async def test_websocket_connect():
    """Client should be able to connect to /ws."""
    app = _get_test_app()
    sync_client = TestClient(app)
    with sync_client.websocket_connect("/ws") as ws:
        # Send a subscribe message
        ws.send_json({"type": "subscribe", "execution_id": "test-exec-123"})
        data = ws.receive_json()
        assert data["type"] == "subscribed"
        assert data["execution_id"] == "test-exec-123"


@pytest.mark.asyncio
async def test_websocket_invalid_json():
    """Server should handle invalid JSON gracefully."""
    app = _get_test_app()
    sync_client = TestClient(app)
    with sync_client.websocket_connect("/ws") as ws:
        ws.send_text("not valid json {{{")
        data = ws.receive_json()
        assert data["type"] == "error"
        assert "Invalid JSON" in data["message"]


@pytest.mark.asyncio
async def test_websocket_unknown_type():
    """Server should report unknown message types."""
    app = _get_test_app()
    sync_client = TestClient(app)
    with sync_client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "foobar"})
        data = ws.receive_json()
        assert data["type"] == "error"
        assert "Unknown" in data["message"]


@pytest.mark.asyncio
async def test_websocket_subscribe_missing_id():
    """Subscribe without execution_id should return error."""
    app = _get_test_app()
    sync_client = TestClient(app)
    with sync_client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "subscribe"})
        data = ws.receive_json()
        assert data["type"] == "error"
        assert "execution_id" in data["message"].lower() or "Missing" in data["message"]
