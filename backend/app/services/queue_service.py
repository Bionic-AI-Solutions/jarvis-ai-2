"""Request queue service — queue requests while system is locked.

Sprint 8 Story 5.4: Request Queue While Locked
- Requests queued while locked
- Executed in order after unlock
"""

from __future__ import annotations

import json
from typing import Any, Dict, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.models.security import PendingRequest

logger = get_logger(__name__)


class RequestQueueService:
    """Manages the pending request queue for locked-mode operation."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def enqueue(
        self,
        *,
        request_type: str,
        payload: Dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> PendingRequest:
        """Add a request to the queue."""
        req = PendingRequest(
            session_id=session_id,
            request_type=request_type,
            payload_json=json.dumps(payload or {}),
            status="pending",
        )
        self.db.add(req)
        await self.db.flush()
        logger.info("request_queued", request_id=req.id, request_type=request_type)
        return req

    async def list_pending(self) -> Sequence[PendingRequest]:
        """List all pending requests in queue order."""
        stmt = (
            select(PendingRequest)
            .where(PendingRequest.status == "pending")
            .order_by(PendingRequest.timestamp.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_pending(self) -> int:
        """Return the number of pending requests."""
        from sqlalchemy import func

        result = await self.db.execute(
            select(func.count(PendingRequest.id)).where(
                PendingRequest.status == "pending"
            )
        )
        return result.scalar_one()

    async def drain(self) -> list[Dict[str, Any]]:
        """Mark all pending requests as approved and return their payloads.

        Called on system unlock to process queued work.
        """
        pending = await self.list_pending()
        drained: list[Dict[str, Any]] = []
        for req in pending:
            req.status = "approved"
            drained.append({
                "id": req.id,
                "request_type": req.request_type,
                "payload": json.loads(req.payload_json),
            })
        await self.db.flush()
        logger.info("queue_drained", count=len(drained))
        return drained

    async def reject(self, request_id: str) -> bool:
        """Reject a pending request."""
        stmt = (
            select(PendingRequest)
            .where(PendingRequest.id == request_id, PendingRequest.status == "pending")
        )
        result = await self.db.execute(stmt)
        req = result.scalar_one_or_none()
        if req is None:
            return False
        req.status = "rejected"
        await self.db.flush()
        return True

    async def clear_expired(self, max_age_hours: int = 24) -> int:
        """Remove old expired requests."""
        from datetime import datetime, timezone, timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        stmt = (
            update(PendingRequest)
            .where(
                PendingRequest.status == "pending",
                PendingRequest.timestamp < cutoff,
            )
            .values(status="expired")
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
