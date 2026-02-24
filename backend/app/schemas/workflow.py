"""Workflow-related request / response schemas.

Stories 4.1-4.7: Save, Load, Parameters, Tags, Templates, Versioning, Export.
"""

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
    tags: Optional[list[str]] = None
    parameters: Optional[dict[str, Any]] = None
    is_template: bool = False
    template_category: Optional[str] = None


class WorkflowUpdate(BaseModel):
    """Update an existing workflow."""

    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    steps: Optional[list[dict[str, Any]]] = None
    trigger_type: Optional[str] = Field(default=None, pattern="^(manual|hotkey|schedule|event)$")
    is_active: Optional[bool] = None
    tags: Optional[list[str]] = None
    parameters: Optional[dict[str, Any]] = None


class WorkflowSaveAfterExecution(BaseModel):
    """Save a workflow after successful execution (Story 4.1)."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    execution_id: str


class WorkflowExecuteRequest(BaseModel):
    """Execute a saved workflow (Story 4.2)."""

    parameter_values: Optional[dict[str, Any]] = None
    session_id: Optional[str] = None


class WorkflowCloneRequest(BaseModel):
    """Clone a template workflow (Story 4.5)."""

    new_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[list[str]] = None


class WorkflowSearchRequest(BaseModel):
    """Search workflows by name/tags (Story 4.4)."""

    query: Optional[str] = None
    tags: Optional[list[str]] = None
    templates_only: bool = False


class WorkflowExportRequest(BaseModel):
    """Export a workflow (Story 4.7)."""

    format: str = Field(default="json", pattern="^(json|csv)$")


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
    tags: Optional[str]
    parameters_json: Optional[str]
    success_rate: float
    execution_count: int
    confidence: float
    is_template: bool
    template_category: Optional[str]
    created_at: datetime
    updated_at: datetime


class WorkflowListItem(OrmBase):
    """Lightweight workflow for list endpoints."""

    id: str
    name: str
    trigger_type: str
    is_active: bool
    version: int
    tags: Optional[str]
    success_rate: float
    execution_count: int
    is_template: bool
    template_category: Optional[str]
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


class WorkflowExportResponse(BaseModel):
    """Exported workflow data."""

    workflow: Any  # dict for JSON, string for CSV
    format: str
    exported_at: str
