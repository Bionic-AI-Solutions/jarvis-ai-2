"""Workflow-related request / response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.common import OrmBase


# ── Requests ────────────────────────────────────────────────

class WorkflowCreate(BaseModel):
    """Create a new workflow template."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    steps: list[dict[str, Any]] = Field(default_factory=list)
    trigger_type: str = Field(default="manual", pattern="^(manual|hotkey|schedule|event)$")


class WorkflowUpdate(BaseModel):
    """Update an existing workflow."""

    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    steps: Optional[list[dict[str, Any]]] = None
    trigger_type: Optional[str] = Field(default=None, pattern="^(manual|hotkey|schedule|event)$")
    is_active: Optional[bool] = None


# ── Responses ───────────────────────────────────────────────

class WorkflowResponse(OrmBase):
    """Full workflow detail."""

    id: str
    name: str
    description: Optional[str]
    steps_json: str
    trigger_type: str
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime


class WorkflowListItem(OrmBase):
    """Lightweight workflow for list endpoints."""

    id: str
    name: str
    trigger_type: str
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime


class WorkflowRevisionResponse(OrmBase):
    """Workflow revision history entry."""

    id: str
    workflow_id: str
    version: int
    steps_json: str
    change_reason: Optional[str]
    created_at: datetime
