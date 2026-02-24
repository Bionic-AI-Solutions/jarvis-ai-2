"""Queue routes — manage request queue for locked mode.

Sprint 8 Story 5.4: Request Queue
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.queue import (
    QueueDrainResponse,
    QueueItemResponse,
    QueueListResponse,
    QueueRejectResponse,
)
from app.services.queue_service import RequestQueueService

router = APIRouter(prefix="/api/queue", tags=["Queue"])


def _queue_service(db: AsyncSession = Depends(get_db)) -> RequestQueueService:
    return RequestQueueService(db)


@router.get("", response_model=QueueListResponse)
async def list_queue(
    svc: RequestQueueService = Depends(_queue_service),
):
    """List pending requests in the queue."""
    items = await svc.list_pending()
    count = await svc.count_pending()
    result_items = []
    for item in items:
        try:
            payload = json.loads(item.payload_json)
        except (json.JSONDecodeError, TypeError):
            payload = {}
        result_items.append(
            QueueItemResponse(
                id=item.id,
                session_id=item.session_id,
                request_type=item.request_type,
                payload=payload,
                status=item.status,
                timestamp=item.timestamp,
            )
        )
    return QueueListResponse(items=result_items, count=count)


@router.post("/drain", response_model=QueueDrainResponse)
async def drain_queue(
    svc: RequestQueueService = Depends(_queue_service),
):
    """Drain the queue — approve all pending requests."""
    payloads = await svc.drain()
    return QueueDrainResponse(drained=len(payloads), payloads=payloads)


@router.post("/{item_id}/reject", response_model=QueueRejectResponse)
async def reject_queue_item(
    item_id: str,
    svc: RequestQueueService = Depends(_queue_service),
):
    """Reject a specific queue item."""
    await svc.reject(item_id)
    return QueueRejectResponse(item_id=item_id)


@router.post("/clear-expired")
async def clear_expired(
    max_age_hours: int = Query(24, ge=1, le=720),
    svc: RequestQueueService = Depends(_queue_service),
):
    """Clear expired requests older than max_age_hours."""
    count = await svc.clear_expired(max_age_hours=max_age_hours)
    return {"cleared": count}
