"""Workflow API routes — CRUD, templates, search, export, execution.

Sprint 1: Basic CRUD & revision history.
Sprint 7 Stories 4.1-4.7: Save-from-execution, execute, search, clone templates,
    seed templates, export, parameter handling.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import SuccessResponse
from app.schemas.workflow import (
    WorkflowCloneRequest,
    WorkflowCreate,
    WorkflowExecuteRequest,
    WorkflowExportRequest,
    WorkflowExportResponse,
    WorkflowListItem,
    WorkflowResponse,
    WorkflowRevisionResponse,
    WorkflowSaveAfterExecution,
    WorkflowSearchRequest,
    WorkflowUpdate,
)
from app.services.execution_service import ExecutionService
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


def _svc(db: AsyncSession = Depends(get_db)) -> WorkflowService:
    return WorkflowService(db)


def _exe_svc(db: AsyncSession = Depends(get_db)) -> ExecutionService:
    return ExecutionService(db)


# ── Templates (must precede /{workflow_id} to avoid capture) ───────────

@router.get("/templates", response_model=list[WorkflowListItem])
async def list_templates(
    svc: WorkflowService = Depends(_svc),
):
    """List all workflow templates."""
    return await svc.list_workflows(templates_only=True)


@router.post("/templates/seed", response_model=SuccessResponse)
async def seed_templates(
    svc: WorkflowService = Depends(_svc),
):
    """Seed the database with built-in workflow templates."""
    count = await svc.seed_templates()
    return SuccessResponse(message=f"Seeded {count} templates")


# ── Search ──────────────────────────────────────────────────

@router.post("/search", response_model=list[WorkflowListItem])
async def search_workflows(
    data: WorkflowSearchRequest,
    svc: WorkflowService = Depends(_svc),
):
    """Search workflows by query text, tags, or template flag."""
    return await svc.search_workflows(
        query=data.query,
        tags=data.tags,
        templates_only=data.templates_only,
    )


# ── Save from Execution (Story 4.1) ────────────────────────

@router.post("/save-from-execution", response_model=WorkflowResponse, status_code=201)
async def save_from_execution(
    data: WorkflowSaveAfterExecution,
    svc: WorkflowService = Depends(_svc),
):
    """Save a completed execution as a reusable workflow."""
    return await svc.save_after_execution(data)


# ── Basic CRUD ──────────────────────────────────────────────

@router.get("", response_model=list[WorkflowListItem])
async def list_workflows(
    active_only: bool = Query(False),
    templates_only: bool = Query(False),
    svc: WorkflowService = Depends(_svc),
):
    """List all workflow templates."""
    return await svc.list_workflows(active_only=active_only, templates_only=templates_only)


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


# ── Revisions ───────────────────────────────────────────────

@router.get("/{workflow_id}/revisions", response_model=list[WorkflowRevisionResponse])
async def list_revisions(
    workflow_id: str,
    svc: WorkflowService = Depends(_svc),
):
    """List all revisions for a workflow."""
    return await svc.get_revisions(workflow_id)


# ── Clone Template (Story 4.5) ──────────────────────────────

@router.post("/{workflow_id}/clone", response_model=WorkflowResponse, status_code=201)
async def clone_template(
    workflow_id: str,
    data: WorkflowCloneRequest,
    svc: WorkflowService = Depends(_svc),
):
    """Clone a workflow template into a personal workflow."""
    return await svc.clone_template(
        template_id=workflow_id,
        new_name=data.new_name,
        description=data.description,
        tags=data.tags,
    )


# ── Execute (Story 4.2) ─────────────────────────────────────

@router.post("/{workflow_id}/execute", response_model=dict, status_code=202)
async def execute_workflow(
    workflow_id: str,
    data: WorkflowExecuteRequest,
    svc: WorkflowService = Depends(_svc),
    exe_svc: ExecutionService = Depends(_exe_svc),
):
    """Start executing a workflow with optional parameter substitution.

    Creates an execution record, substitutes parameter values into steps,
    and kicks off the orchestrator (fire-and-forget via background task).
    Returns the execution record immediately.
    """
    from app.agents.orchestrator import WorkflowOrchestrator

    wf = await svc.get_workflow(workflow_id)
    steps = json.loads(wf.steps_json)

    # Substitute parameter placeholders
    if data.parameter_values:
        steps = _substitute_parameters(steps, data.parameter_values)

    exe = await exe_svc.create_execution(
        workflow_id=wf.id,
        total_steps=len(steps),
        session_id=data.session_id,
    )
    exe = await exe_svc.start_execution(exe.id)

    # Fire-and-forget orchestration
    import asyncio

    orchestrator = WorkflowOrchestrator()

    async def _run() -> None:
        result = await orchestrator.execute_workflow(exe.id, steps, data.session_id)
        # Update execution stats on workflow
        success = result.get("status") == "completed"
        try:
            await svc.update_execution_stats(wf.id, success)
        except Exception:
            pass  # best effort

    asyncio.create_task(_run())

    return {
        "execution_id": exe.id,
        "workflow_id": wf.id,
        "status": exe.status,
        "total_steps": len(steps),
    }


# ── Export (Story 4.7) ──────────────────────────────────────

@router.post("/{workflow_id}/export", response_model=WorkflowExportResponse)
async def export_workflow(
    workflow_id: str,
    data: WorkflowExportRequest,
    svc: WorkflowService = Depends(_svc),
):
    """Export a workflow in JSON or CSV format."""
    return await svc.export_workflow(workflow_id, fmt=data.format)


# ── Helpers ──────────────────────────────────────────────────

def _substitute_parameters(steps: list[dict], values: dict[str, str]) -> list[dict]:
    """Replace {placeholder} tokens in step parameters with provided values."""
    import copy
    substituted = copy.deepcopy(steps)
    for step in substituted:
        params = step.get("parameters", {})
        for key, val in params.items():
            if isinstance(val, str):
                for pname, pval in values.items():
                    val = val.replace(f"{{{pname}}}", str(pval))
                params[key] = val
        step["parameters"] = params
    return substituted
