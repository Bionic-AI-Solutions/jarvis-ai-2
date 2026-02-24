"""Chat-related request / response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import OrmBase


# ── Requests ────────────────────────────────────────────────

class ChatSessionCreate(BaseModel):
    """Create a new chat session."""

    title: str = Field(default="New Chat", max_length=255)
    mode: str = Field(default="auto", pattern="^(auto|supervised|locked)$")


class ChatSessionUpdate(BaseModel):
    """Update an existing chat session."""

    title: Optional[str] = Field(default=None, max_length=255)
    mode: Optional[str] = Field(default=None, pattern="^(auto|supervised|locked)$")


class ChatMessageCreate(BaseModel):
    """Send a new message in a session."""

    content: str = Field(..., min_length=1, max_length=10_000)
    role: str = Field(default="user", pattern="^(user|assistant|system)$")


# ── Responses ───────────────────────────────────────────────

class ChatMessageResponse(OrmBase):
    """Single chat message."""

    id: str
    session_id: str
    role: str
    content: str
    sequence: int
    token_count: int
    created_at: datetime


class ChatSessionResponse(OrmBase):
    """Chat session with embedded messages."""

    id: str
    title: str
    mode: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = []


class ChatSessionListItem(OrmBase):
    """Lightweight session summary for list endpoints."""

    id: str
    title: str
    mode: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
