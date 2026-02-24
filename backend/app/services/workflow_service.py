"""Workflow service — CRUD, versioning, templates, search, export.

Stories 4.1-4.7: Save, Load & Execute, Parameters, Tags, Templates, Versioning, Export.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError, NotFoundError
from app.core.logging_config import get_logger
from app.models.execution import WorkflowExecution
from app.models.workflow import Workflow, WorkflowRevision
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowSaveAfterExecution,
    WorkflowUpdate,
)

logger = get_logger(__name__)


# Pre-built workflow templates (Story 4.5)
WORKFLOW_TEMPLATES: list[dict[str, Any]] = [
    {
        "name": "Daily Report Generator",
        "description": "Generate and send a daily status report",
        "category": "productivity",
        "steps": [
            {"agent": "browser", "action": "open", "parameters": {"url": "{report_url}"}, "skippable": False},
            {"agent": "browser", "action": "screenshot", "parameters": {}, "skippable": True},
            {"agent": "file_manager", "action": "save", "parameters": {"path": "{output_path}"}, "skippable": False},
        ],
        "parameters": {
            "report_url": {"type": "string", "description": "URL of the report dashboard", "required": True},
            "output_path": {"type": "string", "description": "Path to save the report", "default": "./reports/daily_{date}.pdf"},
        },
    },
    {
        "name": "Backup Files",
        "description": "Backup specified files to a target directory",
        "category": "system",
        "steps": [
            {"agent": "file_manager", "action": "list", "parameters": {"path": "{source_dir}"}, "skippable": False},
            {"agent": "file_manager", "action": "copy", "parameters": {"source": "{source_dir}", "target": "{backup_dir}"}, "skippable": False},
            {"agent": "file_manager", "action": "verify", "parameters": {"path": "{backup_dir}"}, "skippable": True},
        ],
        "parameters": {
            "source_dir": {"type": "string", "description": "Source directory to backup", "required": True},
            "backup_dir": {"type": "string", "description": "Backup destination", "default": "./backups/{date}"},
        },
    },
    {
        "name": "Web Scrape & Save",
        "description": "Navigate to a URL, extract content, and save locally",
        "category": "data",
        "steps": [
            {"agent": "browser", "action": "navigate", "parameters": {"url": "{target_url}"}, "skippable": False},
            {"agent": "browser", "action": "extract", "parameters": {"selector": "{css_selector}"}, "skippable": False},
            {"agent": "file_manager", "action": "save", "parameters": {"path": "{output_file}"}, "skippable": False},
        ],
        "parameters": {
            "target_url": {"type": "string", "description": "URL to scrape", "required": True},
            "css_selector": {"type": "string", "description": "CSS selector for content", "default": "body"},
            "output_file": {"type": "string", "description": "Output file path", "default": "./scraped_{date}.txt"},
        },
    },
    {
        "name": "Git Commit & Push",
        "description": "Stage, commit, and push changes to Git",
        "category": "development",
        "steps": [
            {"agent": "terminal", "action": "run", "parameters": {"command": "git add -A"}, "skippable": False},
            {"agent": "terminal", "action": "run", "parameters": {"command": "git commit -m \"{commit_message}\""}, "skippable": False},
            {"agent": "terminal", "action": "run", "parameters": {"command": "git push origin {branch}"}, "skippable": True},
        ],
        "parameters": {
            "commit_message": {"type": "string", "description": "Commit message", "required": True},
            "branch": {"type": "string", "description": "Branch name", "default": "main"},
        },
    },
]


class WorkflowService:
    """Encapsulates workflow template operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── List / Get ──────────────────────────────────────────

    async def list_workflows(
        self,
        *,
        active_only: bool = False,
        templates_only: bool = False,
    ) -> Sequence[Workflow]:
        """Return all workflows, optionally filtered."""
        stmt = select(Workflow).order_by(Workflow.updated_at.desc())
        if active_only:
            stmt = stmt.where(Workflow.is_active.is_(True))
        if templates_only:
            stmt = stmt.where(Workflow.is_template.is_(True))
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

    # ── Create / Update / Delete ────────────────────────────

    async def create_workflow(self, data: WorkflowCreate) -> Workflow:
        """Create a new workflow template."""
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
            tags=",".join(data.tags) if data.tags else None,
            parameters_json=json.dumps(data.parameters) if data.parameters else None,
            is_template=data.is_template,
            template_category=data.template_category,
        )
        self.db.add(wf)
        await self.db.flush()
        logger.info("workflow_created", workflow_id=wf.id, name=data.name)
        return wf

    async def update_workflow(self, workflow_id: str, data: WorkflowUpdate) -> Workflow:
        """Update an existing workflow. Creates a revision snapshot first."""
        wf = await self.get_workflow(workflow_id)

        revision = WorkflowRevision(
            workflow_id=wf.id,
            version=wf.version,
            steps_json=wf.steps_json,
            change_reason="auto-snapshot before update",
        )
        self.db.add(revision)

        if data.name is not None:
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
        if data.tags is not None:
            wf.tags = ",".join(data.tags) if data.tags else None
        if data.parameters is not None:
            wf.parameters_json = json.dumps(data.parameters)

        wf.version += 1
        await self.db.flush()
        logger.info("workflow_updated", workflow_id=workflow_id, new_version=wf.version)
        return wf

    async def delete_workflow(self, workflow_id: str) -> None:
        """Delete a workflow and its revisions."""
        wf = await self.get_workflow(workflow_id)
        await self.db.delete(wf)
        logger.info("workflow_deleted", workflow_id=workflow_id)

    # ── Revisions ───────────────────────────────────────────

    async def get_revisions(self, workflow_id: str) -> Sequence[WorkflowRevision]:
        """Return all revisions for a workflow."""
        await self.get_workflow(workflow_id)
        stmt = (
            select(WorkflowRevision)
            .where(WorkflowRevision.workflow_id == workflow_id)
            .order_by(WorkflowRevision.version.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ── Save After Execution (Story 4.1) ────────────────────

    async def save_after_execution(self, data: WorkflowSaveAfterExecution) -> Workflow:
        """Save a workflow from a completed execution."""
        # Verify execution exists and is completed
        exec_stmt = select(WorkflowExecution).where(
            WorkflowExecution.id == data.execution_id
        )
        result = await self.db.execute(exec_stmt)
        execution = result.scalar_one_or_none()
        if execution is None:
            raise NotFoundError("Execution", data.execution_id)
        if execution.status != "completed":
            raise JarvisError(
                ErrorCode.WORKFLOW_SAVE_INCOMPLETE,
                detail="Cannot save workflow from incomplete execution",
            )

        # Auto-version on duplicate name
        name = data.name
        counter = 1
        while True:
            existing = await self.db.execute(
                select(Workflow).where(Workflow.name == name)
            )
            if existing.scalar_one_or_none() is None:
                break
            counter += 1
            name = f"{data.name} ({counter})"

        # Query logs directly to avoid identity-map stale cache
        from app.models.execution import ExecutionLog

        log_stmt = (
            select(ExecutionLog)
            .where(ExecutionLog.execution_id == data.execution_id)
            .order_by(ExecutionLog.step_index)
        )
        log_result = await self.db.execute(log_stmt)
        exec_logs = log_result.scalars().all()

        # Build steps from execution logs (if available, else empty)
        steps: list[dict[str, Any]] = []
        for log in exec_logs:
            params: dict[str, Any] = {}
            if log.detail:
                try:
                    parsed = json.loads(log.detail)
                    if isinstance(parsed, dict):
                        params = parsed
                except (json.JSONDecodeError, TypeError):
                    pass
            steps.append({
                "agent": log.agent_name,
                "action": log.action,
                "parameters": params,
                "skippable": log.status == "skipped",
            })

        wf = Workflow(
            name=name,
            description=data.description,
            steps_json=json.dumps(steps),
            trigger_type="manual",
            tags=",".join(data.tags) if data.tags else None,
            execution_count=1,
            success_rate=1.0,
        )
        self.db.add(wf)
        await self.db.flush()
        logger.info("workflow_saved_from_execution", workflow_id=wf.id, execution_id=data.execution_id)
        return wf

    # ── Search (Story 4.4) ──────────────────────────────────

    async def search_workflows(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        templates_only: bool = False,
    ) -> Sequence[Workflow]:
        """Search workflows by name/description text or tags."""
        stmt = select(Workflow).where(Workflow.is_active.is_(True))

        if templates_only:
            stmt = stmt.where(Workflow.is_template.is_(True))

        if query:
            pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Workflow.name.ilike(pattern),
                    Workflow.description.ilike(pattern),
                )
            )

        if tags:
            for tag in tags:
                stmt = stmt.where(Workflow.tags.ilike(f"%{tag}%"))

        stmt = stmt.order_by(Workflow.updated_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ── Clone Template (Story 4.5) ──────────────────────────

    async def clone_template(self, template_id: str, new_name: str, description: str | None = None, tags: list[str] | None = None) -> Workflow:
        """Clone a template workflow into a user's workflow."""
        template = await self.get_workflow(template_id)
        if not template.is_template:
            raise JarvisError(ErrorCode.WORKFLOW_NOT_TEMPLATE, detail="Source workflow is not a template")

        # Check name uniqueness
        existing = await self.db.execute(
            select(Workflow).where(Workflow.name == new_name)
        )
        if existing.scalar_one_or_none() is not None:
            raise JarvisError(ErrorCode.WORKFLOW_DUPLICATE_NAME, detail=f"Name '{new_name}' already exists")

        wf = Workflow(
            name=new_name,
            description=description or template.description,
            steps_json=template.steps_json,
            trigger_type=template.trigger_type,
            tags=",".join(tags) if tags else template.tags,
            parameters_json=template.parameters_json,
            is_template=False,
        )
        self.db.add(wf)
        await self.db.flush()
        logger.info("template_cloned", template_id=template_id, new_id=wf.id)
        return wf

    # ── Seed Templates (Story 4.5) ──────────────────────────

    async def seed_templates(self) -> int:
        """Insert pre-built workflow templates if they don't exist.

        Returns:
            Number of templates newly created.
        """
        created = 0
        for tpl in WORKFLOW_TEMPLATES:
            existing = await self.db.execute(
                select(Workflow).where(Workflow.name == tpl["name"])
            )
            if existing.scalar_one_or_none() is not None:
                continue
            wf = Workflow(
                name=tpl["name"],
                description=tpl["description"],
                steps_json=json.dumps(tpl["steps"]),
                trigger_type="manual",
                is_template=True,
                template_category=tpl["category"],
                parameters_json=json.dumps(tpl["parameters"]),
            )
            self.db.add(wf)
            created += 1
        if created:
            await self.db.flush()
            logger.info("templates_seeded", count=created)
        return created

    # ── Update Execution Stats ──────────────────────────────

    async def update_execution_stats(self, workflow_id: str, success: bool) -> Workflow:
        """Update workflow success rate and execution count after a run."""
        wf = await self.get_workflow(workflow_id)
        total = wf.execution_count
        wf.execution_count = total + 1
        # Weighted running average
        wf.success_rate = ((wf.success_rate * total) + (1.0 if success else 0.0)) / (total + 1)
        await self.db.flush()
        return wf

    # ── Export (Story 4.7) ──────────────────────────────────

    async def export_workflow(self, workflow_id: str, fmt: str = "json") -> dict[str, Any]:
        """Export workflow data as JSON or CSV dict."""
        wf = await self.get_workflow(workflow_id)
        steps = json.loads(wf.steps_json)
        params = json.loads(wf.parameters_json) if wf.parameters_json else None
        tags = wf.tags.split(",") if wf.tags else []

        data: dict[str, Any] = {
            "name": wf.name,
            "description": wf.description,
            "version": wf.version,
            "trigger_type": wf.trigger_type,
            "tags": tags,
            "steps": steps,
            "parameters": params,
            "success_rate": wf.success_rate,
            "execution_count": wf.execution_count,
            "is_template": wf.is_template,
            "template_category": wf.template_category,
            "created_at": wf.created_at.isoformat() if wf.created_at else None,
            "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
        }

        now = datetime.now(timezone.utc).isoformat()

        if fmt == "csv":
            # Build CSV string
            import csv
            import io

            output = io.StringIO()
            fieldnames = ["step_index", "agent", "action", "parameters", "skippable"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for i, step in enumerate(steps):
                writer.writerow({
                    "step_index": i,
                    "agent": step.get("agent", ""),
                    "action": step.get("action", ""),
                    "parameters": json.dumps(step.get("parameters", {})),
                    "skippable": step.get("skippable", False),
                })
            return {"workflow": output.getvalue(), "format": "csv", "exported_at": now}

        return {"workflow": data, "format": "json", "exported_at": now}
