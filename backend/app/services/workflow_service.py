"""Workflow service — CRUD and versioning for workflow templates."""

from __future__ import annotations

import json
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError, NotFoundError
from app.core.logging_config import get_logger
from app.models.workflow import Workflow, WorkflowRevision
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate

logger = get_logger(__name__)


class WorkflowService:
    """Encapsulates workflow template operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_workflows(self, *, active_only: bool = False) -> Sequence[Workflow]:
        """Return all workflows, optionally active-only."""
        stmt = select(Workflow).order_by(Workflow.updated_at.desc())
        if active_only:
            stmt = stmt.where(Workflow.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_workflow(self, workflow_id: str) -> Workflow:
        """Fetch workflow by ID or raise NotFoundError."""
        stmt = select(Workflow).where(Workflow.id == workflow_id)
        result = await self.db.execute(stmt)
        wf = result.scalar_one_or_none()
        if wf is None:
            raise NotFoundError("Workflow", workflow_id)
        return wf

    async def create_workflow(self, data: WorkflowCreate) -> Workflow:
        """Create a new workflow template."""
        # Check for duplicate name
        existing = await self.db.execute(
            select(Workflow).where(Workflow.name == data.name)
        )
        if existing.scalar_one_or_none() is not None:
            raise JarvisError(ErrorCode.WORKFLOW_DUPLICATE_NAME, detail=f"Name '{data.name}' already exists")

        wf = Workflow(
            name=data.name,
            description=data.description,
            steps_json=json.dumps(data.steps),
            trigger_type=data.trigger_type,
        )
        self.db.add(wf)
        await self.db.flush()
        logger.info("workflow_created", workflow_id=wf.id, name=data.name)
        return wf

    async def update_workflow(self, workflow_id: str, data: WorkflowUpdate) -> Workflow:
        """Update an existing workflow. Creates a revision snapshot first."""
        wf = await self.get_workflow(workflow_id)

        # Snapshot current version before mutation
        revision = WorkflowRevision(
            workflow_id=wf.id,
            version=wf.version,
            steps_json=wf.steps_json,
            change_reason="auto-snapshot before update",
        )
        self.db.add(revision)

        if data.name is not None:
            # check duplicate for new name
            dup = await self.db.execute(
                select(Workflow).where(Workflow.name == data.name, Workflow.id != workflow_id)
            )
            if dup.scalar_one_or_none() is not None:
                raise JarvisError(ErrorCode.WORKFLOW_DUPLICATE_NAME, detail=f"Name '{data.name}' already exists")
            wf.name = data.name
        if data.description is not None:
            wf.description = data.description
        if data.steps is not None:
            wf.steps_json = json.dumps(data.steps)
        if data.trigger_type is not None:
            wf.trigger_type = data.trigger_type
        if data.is_active is not None:
            wf.is_active = data.is_active

        wf.version += 1
        await self.db.flush()
        logger.info("workflow_updated", workflow_id=workflow_id, new_version=wf.version)
        return wf

    async def delete_workflow(self, workflow_id: str) -> None:
        """Delete a workflow and its revisions."""
        wf = await self.get_workflow(workflow_id)
        await self.db.delete(wf)
        logger.info("workflow_deleted", workflow_id=workflow_id)

    async def get_revisions(self, workflow_id: str) -> Sequence[WorkflowRevision]:
        """Return all revisions for a workflow."""
        await self.get_workflow(workflow_id)  # ensure exists
        stmt = (
            select(WorkflowRevision)
            .where(WorkflowRevision.workflow_id == workflow_id)
            .order_by(WorkflowRevision.version.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
