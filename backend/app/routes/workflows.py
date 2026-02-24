"""Workflow API routes — CRUD for workflow templates."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import SuccessResponse
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowListItem,
    WorkflowResponse,
    WorkflowRevisionResponse,
    WorkflowUpdate,
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


def _svc(db: AsyncSession = Depends(get_db)) -> WorkflowService:
    return WorkflowService(db)


@router.get("", response_model=list[WorkflowListItem])
async def list_workflows(
    active_only: bool = Query(False),
    svc: WorkflowService = Depends(_svc),
):
    """List all workflow templates."""
    return await svc.list_workflows(active_only=active_only)


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    data: WorkflowCreate,
    svc: WorkflowService = Depends(_svc),
):
    """Create a new workflow template."""
    return await svc.create_workflow(data)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    svc: WorkflowService = Depends(_svc),
):
    """Get a workflow by ID."""
    return await svc.get_workflow(workflow_id)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    data: WorkflowUpdate,
    svc: WorkflowService = Depends(_svc),
):
    """Update a workflow template (creates a revision snapshot)."""
    return await svc.update_workflow(workflow_id, data)


@router.delete("/{workflow_id}", response_model=SuccessResponse)
async def delete_workflow(
    workflow_id: str,
    svc: WorkflowService = Depends(_svc),
):
    """Delete a workflow template."""
    await svc.delete_workflow(workflow_id)
    return SuccessResponse(message=f"Workflow {workflow_id} deleted")


@router.get("/{workflow_id}/revisions", response_model=list[WorkflowRevisionResponse])
async def list_revisions(
    workflow_id: str,
    svc: WorkflowService = Depends(_svc),
):
    """List all revisions for a workflow."""
    return await svc.get_revisions(workflow_id)
