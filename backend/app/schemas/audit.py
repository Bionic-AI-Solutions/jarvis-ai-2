"""Audit schemas — request/response models for audit trail endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class AuditEntryResponse(BaseModel):
    """Single audit trail entry."""

    id: str
    actor: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    detail: Optional[str] = None
    ip_address: str = "127.0.0.1"
    result: str = "success"
    entry_hash: str
    prev_hash: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditListResponse(BaseModel):
    """Paginated list of audit entries."""

    entries: List[AuditEntryResponse]
    total: int
    limit: int
    offset: int


class AuditVerifyResponse(BaseModel):
    """Result of audit chain verification."""

    valid: bool
    entries_checked: int
    first_broken_id: Optional[str] = None
    message: str
