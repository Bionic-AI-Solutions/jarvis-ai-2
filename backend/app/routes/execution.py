"""Execution API routes — run, cancel, pause/resume, and query workflow executions.

Sprint 1: Basic create/cancel/list.
Sprint 7 Story 2.6: Pause & Resume execution.
Sprint 7 Story 3.7: Error context snapshots.
Sprint 7 Story 3.8: AI recovery suggestions.
"""

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
from app.services.error_context_service import ErrorContextService
from app.services.recovery_suggestion_service import recovery_suggestion_service
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/executions", tags=["Executions"])

# Shared orchestrator singleton for pause/resume/cancel across requests
_orchestrator = None


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from app.agents.orchestrator import WorkflowOrchestrator
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator


def _exe_svc(db: AsyncSession = Depends(get_db)) -> ExecutionService:
    return ExecutionService(db)


def _wf_svc(db: AsyncSession = Depends(get_db)) -> WorkflowService:
    return WorkflowService(db)


def _ctx_svc(db: AsyncSession = Depends(get_db)) -> ErrorContextService:
    return ErrorContextService(db)


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


# ── Pause & Resume (Story 2.6) ─────────────────────────────

@router.post("/{execution_id}/pause", response_model=SuccessResponse)
async def pause_execution(execution_id: str):
    """Pause a running execution at the next step boundary."""
    orch = _get_orchestrator()
    await orch.pause(execution_id)
    return SuccessResponse(message=f"Execution {execution_id} paused")


@router.post("/{execution_id}/resume", response_model=SuccessResponse)
async def resume_execution(execution_id: str):
    """Resume a paused execution."""
    orch = _get_orchestrator()
    await orch.resume(execution_id)
    return SuccessResponse(message=f"Execution {execution_id} resumed")


@router.get("/{execution_id}/pause-status")
async def get_pause_status(execution_id: str):
    """Check whether an execution is paused."""
    orch = _get_orchestrator()
    return {"execution_id": execution_id, "paused": orch.is_paused(execution_id)}


# ── Error Context Snapshots (Story 3.7) ─────────────────────

@router.get("/{execution_id}/context-snapshots")
async def list_context_snapshots(
    execution_id: str,
    svc: ErrorContextService = Depends(_ctx_svc),
):
    """List all error context snapshots for an execution."""
    snapshots = await svc.get_execution_snapshots(execution_id)
    return {
        "execution_id": execution_id,
        "snapshots": [
            {
                "id": s.id,
                "step_index": s.step_index,
                "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            }
            for s in snapshots
        ],
    }


@router.get("/{execution_id}/context-snapshots/{snapshot_id}")
async def get_context_snapshot(
    execution_id: str,
    snapshot_id: str,
    svc: ErrorContextService = Depends(_ctx_svc),
):
    """Get full error context data for a snapshot."""
    data = await svc.get_snapshot_data(snapshot_id)
    if data is None:
        from app.core.errors import ErrorCode
        from app.core.exceptions import NotFoundError
        raise NotFoundError(ErrorCode.EXECUTION_NOT_FOUND, detail=f"Snapshot {snapshot_id} not found")
    return {"snapshot_id": snapshot_id, "execution_id": execution_id, "data": data}


# ── AI Recovery Suggestions (Story 3.8) ─────────────────────

@router.post("/{execution_id}/context-snapshots/{snapshot_id}/suggestions")
async def get_recovery_suggestions(
    execution_id: str,
    snapshot_id: str,
    svc: ErrorContextService = Depends(_ctx_svc),
):
    """Generate AI-powered recovery suggestions from an error snapshot."""
    data = await svc.get_snapshot_data(snapshot_id)
    if data is None:
        from app.core.errors import ErrorCode
        from app.core.exceptions import NotFoundError
        raise NotFoundError(ErrorCode.EXECUTION_NOT_FOUND, detail=f"Snapshot {snapshot_id} not found")

    result = await recovery_suggestion_service.suggest(data)
    return result.to_dict()
