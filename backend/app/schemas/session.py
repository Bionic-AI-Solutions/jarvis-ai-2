"""Session schemas — request/response models for session management endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SessionResponse(BaseModel):
    """Single active session."""

    id: str
    user_id: str
    token_jti: str
    ip_address: str = "127.0.0.1"
    user_agent: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_activity: datetime

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    """List of sessions."""

    sessions: List[SessionResponse]
    total: int


class SessionRevokeResponse(BaseModel):
    """Result of session revocation."""

    revoked: bool = True
    session_id: str


class SessionRevokeAllResponse(BaseModel):
    """Result of revoking all sessions."""

    revoked_count: int
