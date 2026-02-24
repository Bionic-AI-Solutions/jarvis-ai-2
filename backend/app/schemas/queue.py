"""Queue schemas — request/response models for request queue endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueueItemResponse(BaseModel):
    """Single queued request."""

    id: str
    session_id: Optional[str] = None
    request_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    timestamp: datetime

    model_config = {"from_attributes": True}


class QueueListResponse(BaseModel):
    """List of queued requests."""

    items: List[QueueItemResponse]
    count: int


class QueueDrainResponse(BaseModel):
    """Result of draining the queue."""

    drained: int
    payloads: List[Dict[str, Any]]


class QueueRejectResponse(BaseModel):
    """Result of rejecting a queue item."""

    rejected: bool = True
    item_id: str
