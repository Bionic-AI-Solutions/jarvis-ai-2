"""Execution API routes — run, cancel, and query workflow executions."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import SuccessResponse
from app.schemas.execution import (
    ExecutionCancel,
    ExecutionCreate,
    ExecutionListItem,
    ExecutionResponse,
)
from app.services.execution_service import ExecutionService
from app.services.execution_logger import execution_logger
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/executions", tags=["Executions"])


def _exe_svc(db: AsyncSession = Depends(get_db)) -> ExecutionService:
    return ExecutionService(db)


def _wf_svc(db: AsyncSession = Depends(get_db)) -> WorkflowService:
    return WorkflowService(db)


@router.get("", response_model=list[ExecutionListItem])
async def list_executions(
    workflow_id: str | None = Query(None),
    svc: ExecutionService = Depends(_exe_svc),
):
    """List executions, optionally filtered by workflow."""
    return await svc.list_executions(workflow_id=workflow_id)


@router.post("", response_model=ExecutionResponse, status_code=201)
async def start_execution(
    data: ExecutionCreate,
    exe_svc: ExecutionService = Depends(_exe_svc),
    wf_svc: WorkflowService = Depends(_wf_svc),
):
    """Create and start a new workflow execution."""
    wf = await wf_svc.get_workflow(data.workflow_id)
    steps = json.loads(wf.steps_json)
    exe = await exe_svc.create_execution(
        workflow_id=wf.id,
        total_steps=len(steps),
        session_id=data.session_id,
    )
    exe = await exe_svc.start_execution(exe.id)
    return exe


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    svc: ExecutionService = Depends(_exe_svc),
):
    """Get execution details including step logs."""
    return await svc.get_execution(execution_id)


@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
async def cancel_execution(
    execution_id: str,
    data: ExecutionCancel,
    svc: ExecutionService = Depends(_exe_svc),
):
    """Cancel a running or pending execution."""
    return await svc.cancel_execution(execution_id, reason=data.reason)


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    step_index: int | None = Query(None),
    agent: str | None = Query(None),
    status: str | None = Query(None),
):
    """Query step execution logs with optional filters."""
    entries = execution_logger.get_entries(
        execution_id=execution_id,
        step_index=step_index,
        agent=agent,
        status=status,
    )
    return {"execution_id": execution_id, "entries": entries, "count": len(entries)}
