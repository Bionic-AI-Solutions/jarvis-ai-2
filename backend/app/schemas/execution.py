"""Execution-related request / response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import OrmBase


# ── Requests ────────────────────────────────────────────────

class ExecutionCreate(BaseModel):
    """Start a new workflow execution."""

    workflow_id: str
    session_id: Optional[str] = None


class ExecutionCancel(BaseModel):
    """Cancel a running execution."""

    reason: Optional[str] = None


# ── Responses ───────────────────────────────────────────────

class ExecutionLogResponse(OrmBase):
    """Single execution step log entry."""

    id: str
    execution_id: str
    step_index: int
    agent_name: str
    action: str
    status: str
    duration_ms: float
    screenshot_path: Optional[str]
    detail: Optional[str]
    timestamp: datetime


class ExecutionResponse(OrmBase):
    """Workflow execution detail."""

    id: str
    workflow_id: Optional[str]
    session_id: Optional[str]
    status: str
    current_step: int
    total_steps: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_code: Optional[str]
    error_detail: Optional[str]
    created_at: datetime
    updated_at: datetime
    logs: list[ExecutionLogResponse] = []


class ExecutionListItem(OrmBase):
    """Lightweight execution for list endpoints."""

    id: str
    workflow_id: Optional[str]
    status: str
    current_step: int
    total_steps: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
