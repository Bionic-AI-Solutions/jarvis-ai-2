"""Execution service — manages workflow execution lifecycle."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError, NotFoundError
from app.core.logging_config import get_logger
from app.models.execution import ContextSnapshot, ExecutionLog, WorkflowExecution

logger = get_logger(__name__)


class ExecutionService:
    """Manages the lifecycle of workflow executions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_executions(self, *, workflow_id: str | None = None) -> Sequence[WorkflowExecution]:
        """List executions, optionally filtered by workflow."""
        stmt = select(WorkflowExecution).order_by(WorkflowExecution.created_at.desc())
        if workflow_id:
            stmt = stmt.where(WorkflowExecution.workflow_id == workflow_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_execution(self, execution_id: str) -> WorkflowExecution:
        """Fetch a single execution by ID."""
        stmt = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        result = await self.db.execute(stmt)
        exe = result.scalar_one_or_none()
        if exe is None:
            raise NotFoundError("WorkflowExecution", execution_id)
        return exe

    async def create_execution(
        self,
        workflow_id: str,
        total_steps: int,
        session_id: str | None = None,
    ) -> WorkflowExecution:
        """Create a new pending execution record."""
        exe = WorkflowExecution(
            workflow_id=workflow_id,
            session_id=session_id,
            status="pending",
            total_steps=total_steps,
        )
        self.db.add(exe)
        await self.db.flush()
        logger.info("execution_created", execution_id=exe.id, workflow_id=workflow_id)
        return exe

    async def start_execution(self, execution_id: str) -> WorkflowExecution:
        """Transition execution from pending → running."""
        exe = await self.get_execution(execution_id)
        if exe.status != "pending":
            raise JarvisError(
                ErrorCode.WORKFLOW_ALREADY_RUNNING,
                detail=f"Execution is in '{exe.status}' state",
            )
        exe.status = "running"
        exe.started_at = datetime.now(timezone.utc)
        await self.db.flush()
        logger.info("execution_started", execution_id=execution_id)
        return exe

    async def advance_step(
        self,
        execution_id: str,
        step_index: int,
        agent_name: str,
        action: str,
        status: str,
        duration_ms: float,
        detail: str | None = None,
        screenshot_path: str | None = None,
    ) -> ExecutionLog:
        """Log a completed step and advance the current_step counter."""
        exe = await self.get_execution(execution_id)

        log = ExecutionLog(
            execution_id=execution_id,
            step_index=step_index,
            agent_name=agent_name,
            action=action,
            status=status,
            duration_ms=duration_ms,
            detail=detail,
            screenshot_path=screenshot_path,
        )
        self.db.add(log)

        if status == "success":
            exe.current_step = step_index + 1

        await self.db.flush()
        logger.info(
            "execution_step",
            execution_id=execution_id,
            step=step_index,
            status=status,
        )
        return log

    async def complete_execution(
        self,
        execution_id: str,
        status: str = "completed",
        error_code: str | None = None,
        error_detail: str | None = None,
    ) -> WorkflowExecution:
        """Mark an execution as completed or failed."""
        exe = await self.get_execution(execution_id)
        exe.status = status
        exe.completed_at = datetime.now(timezone.utc)
        exe.error_code = error_code
        exe.error_detail = error_detail
        await self.db.flush()
        logger.info("execution_completed", execution_id=execution_id, status=status)
        return exe

    async def cancel_execution(self, execution_id: str, reason: str | None = None) -> WorkflowExecution:
        """Cancel a running or pending execution."""
        exe = await self.get_execution(execution_id)
        if exe.status not in ("pending", "running"):
            raise JarvisError(
                ErrorCode.EXECUTION_ALREADY_COMPLETE,
                detail=f"Cannot cancel — execution is '{exe.status}'",
            )
        exe.status = "cancelled"
        exe.completed_at = datetime.now(timezone.utc)
        exe.error_detail = reason
        await self.db.flush()
        logger.info("execution_cancelled", execution_id=execution_id, reason=reason)
        return exe

    async def save_snapshot(
        self,
        execution_id: str,
        step_index: int,
        snapshot_data: dict,
    ) -> ContextSnapshot:
        """Persist a context snapshot for an execution step."""
        snap = ContextSnapshot(
            execution_id=execution_id,
            step_index=step_index,
            snapshot_json=json.dumps(snapshot_data),
        )
        self.db.add(snap)
        await self.db.flush()
        return snap
