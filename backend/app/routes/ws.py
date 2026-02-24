"""WebSocket endpoint — real-time execution streaming (Story 7.3).

Protocol:
  Client → Server:  {"type": "subscribe", "execution_id": "<uuid>"}
  Server → Client:  {"type": "plan_ready"|"step_started"|"step_complete"|"workflow_complete"|"error", ...}
  Heartbeat:        Server sends {"type": "ping"} every ws_heartbeat_seconds
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

# ── Connection Manager ──────────────────────────────────────


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""

    def __init__(self) -> None:
        # ws → set of execution_ids
        self._subscriptions: Dict[WebSocket, Set[str]] = {}
        # execution_id → set of ws
        self._execution_subs: Dict[str, Set[WebSocket]] = {}

    @property
    def active_count(self) -> int:
        return len(self._subscriptions)

    async def connect(self, ws: WebSocket) -> None:
        """Accept a WebSocket connection."""
        await ws.accept()
        self._subscriptions[ws] = set()
        logger.info("ws_connected", active=self.active_count)

    def disconnect(self, ws: WebSocket) -> None:
        """Clean up on disconnect."""
        subs = self._subscriptions.pop(ws, set())
        for eid in subs:
            self._execution_subs.get(eid, set()).discard(ws)
        logger.info("ws_disconnected", active=self.active_count)

    def subscribe(self, ws: WebSocket, execution_id: str) -> None:
        """Subscribe a connection to execution updates."""
        self._subscriptions.setdefault(ws, set()).add(execution_id)
        self._execution_subs.setdefault(execution_id, set()).add(ws)
        logger.info("ws_subscribed", execution_id=execution_id)

    async def broadcast_to_execution(self, execution_id: str, message: dict) -> None:
        """Send a JSON message to all subscribers of an execution."""
        subs = self._execution_subs.get(execution_id, set()).copy()
        disconnected: list[WebSocket] = []
        for ws in subs:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_all(self, message: dict) -> None:
        """Send a message to ALL connected clients."""
        disconnected: list[WebSocket] = []
        for ws in list(self._subscriptions.keys()):
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    async def send_personal(self, ws: WebSocket, message: dict) -> None:
        """Send a message to a single connection."""
        try:
            await ws.send_json(message)
        except Exception:
            self.disconnect(ws)


# Singleton manager
manager = ConnectionManager()


# ── Heartbeat task ──────────────────────────────────────────

async def _heartbeat(ws: WebSocket, interval: int) -> None:
    """Send periodic pings to keep the connection alive."""
    try:
        while True:
            await asyncio.sleep(interval)
            await ws.send_json({"type": "ping", "ts": time.time()})
    except Exception:
        pass  # connection closed — task ends


# ── WebSocket Route ─────────────────────────────────────────

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """Main WebSocket entry point."""
    settings = get_settings()
    await manager.connect(ws)

    heartbeat_task = asyncio.create_task(
        _heartbeat(ws, settings.ws_heartbeat_seconds)
    )

    try:
        while True:
            raw = await asyncio.wait_for(
                ws.receive_text(),
                timeout=settings.ws_idle_timeout_seconds,
            )
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await manager.send_personal(ws, {
                    "type": "error",
                    "message": "Invalid JSON",
                })
                continue

            msg_type = data.get("type")

            if msg_type == "subscribe":
                eid = data.get("execution_id")
                if eid:
                    manager.subscribe(ws, eid)
                    await manager.send_personal(ws, {
                        "type": "subscribed",
                        "execution_id": eid,
                    })
                else:
                    await manager.send_personal(ws, {
                        "type": "error",
                        "message": "Missing execution_id",
                    })

            elif msg_type == "pong":
                pass  # heartbeat ack — no action needed

            else:
                await manager.send_personal(ws, {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        heartbeat_task.cancel()
        manager.disconnect(ws)
