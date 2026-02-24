"""Sprint 7 backend tests — Workflow Execution, Pause/Resume, Error Context, AI Suggestions.

Covers:
  4.1  Save workflow after execution
  4.2  Workflow execute with parameter substitution
  4.3  Workflow parameter handling (via create/update)
  4.4  Workflow search & tag filtering
  4.5  Template clone & seed
  4.6  Workflow versioning (existing — no change)
  4.7  Workflow export (JSON + CSV)
  2.6  Pause & Resume execution
  3.7  Error context capture
  3.8  AI recovery suggestions
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError, WorkflowError
from app.models.execution import ContextSnapshot, ExecutionLog, WorkflowExecution
from app.models.workflow import Workflow
from app.services.workflow_service import WorkflowService, WORKFLOW_TEMPLATES
from app.services.error_context_service import ErrorContextService
from app.services.recovery_suggestion_service import (
    RecoverySuggestionService,
    RecoverySuggestionResult,
    RecoverySuggestion,
)
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowSaveAfterExecution,
    WorkflowSearchRequest,
    WorkflowCloneRequest,
    WorkflowExportRequest,
)


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

async def _create_test_workflow(db: AsyncSession, **overrides) -> Workflow:
    """Create a workflow for testing."""
    defaults = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "steps_json": json.dumps([
            {"agent": "file_agent", "action": "read", "parameters": {"path": "/tmp/test.txt"}},
            {"agent": "web_agent", "action": "fetch", "parameters": {"url": "http://example.com"}},
        ]),
        "is_active": True,
        "tags": None,
        "is_template": False,
        "template_category": None,
        "success_rate": 0.0,
        "execution_count": 0,
        "confidence": 0.0,
    }
    defaults.update(overrides)
    wf = Workflow(**defaults)
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return wf


async def _create_test_execution(
    db: AsyncSession, workflow_id: str, *, status: str = "completed"
) -> WorkflowExecution:
    """Create an execution record."""
    exe = WorkflowExecution(
        workflow_id=workflow_id,
        status=status,
        total_steps=2,
        current_step=2 if status == "completed" else 0,
    )
    db.add(exe)
    await db.commit()
    await db.refresh(exe)
    return exe


async def _create_test_logs(db: AsyncSession, execution_id: str) -> None:
    """Add execution logs for steps."""
    for i in range(2):
        log = ExecutionLog(
            execution_id=execution_id,
            step_index=i,
            agent_name=f"agent_{i}",
            action=f"action_{i}",
            status="success",
            duration_ms=100 + i * 50,
            detail=f"Step {i} completed OK",
        )
        db.add(log)
    await db.commit()


# ═══════════════════════════════════════════════════════════════
# Story 4.1: Save Workflow After Execution
# ═══════════════════════════════════════════════════════════════

class TestSaveAfterExecution:

    @pytest.mark.asyncio
    async def test_save_from_completed_execution(self, db_session: AsyncSession):
        """Save a workflow from a completed execution creates workflow + steps."""
        wf = await _create_test_workflow(db_session, name="Source WF")
        exe = await _create_test_execution(db_session, wf.id, status="completed")
        await _create_test_logs(db_session, exe.id)

        svc = WorkflowService(db_session)
        data = WorkflowSaveAfterExecution(
            name="Saved Workflow",
            description="From execution",
            tags=["auto", "test"],
            execution_id=exe.id,
        )
        result = await svc.save_after_execution(data)
        assert result.name == "Saved Workflow"
        assert result.description == "From execution"
        assert result.tags == "auto,test"
        steps = json.loads(result.steps_json)
        assert len(steps) == 2
        assert steps[0]["agent"] == "agent_0"

    @pytest.mark.asyncio
    async def test_save_from_incomplete_execution_raises(self, db_session: AsyncSession):
        """Cannot save from a non-completed execution."""
        wf = await _create_test_workflow(db_session, name="Src")
        exe = await _create_test_execution(db_session, wf.id, status="running")

        svc = WorkflowService(db_session)
        data = WorkflowSaveAfterExecution(
            name="Bad Save", execution_id=exe.id
        )
        with pytest.raises(JarvisError) as exc_info:
            await svc.save_after_execution(data)
        assert exc_info.value.code == ErrorCode.WORKFLOW_SAVE_INCOMPLETE

    @pytest.mark.asyncio
    async def test_save_auto_versions_duplicate_name(self, db_session: AsyncSession):
        """If name exists, auto-appends (2), (3), etc."""
        wf = await _create_test_workflow(db_session, name="Dup Name")
        exe = await _create_test_execution(db_session, wf.id, status="completed")
        await _create_test_logs(db_session, exe.id)

        svc = WorkflowService(db_session)
        # Save once
        data1 = WorkflowSaveAfterExecution(name="Dup Name", execution_id=exe.id)
        r1 = await svc.save_after_execution(data1)
        # Save again — should increment name
        data2 = WorkflowSaveAfterExecution(name="Dup Name", execution_id=exe.id)
        r2 = await svc.save_after_execution(data2)
        assert "Dup Name" in r2.name
        assert r1.name != r2.name


# ═══════════════════════════════════════════════════════════════
# Story 4.3: Workflow Parameters via Create/Update
# ═══════════════════════════════════════════════════════════════

class TestWorkflowParameters:

    @pytest.mark.asyncio
    async def test_create_workflow_with_tags_and_params(self, db_session: AsyncSession):
        """Create with tags and parameters stores them correctly."""
        svc = WorkflowService(db_session)
        data = WorkflowCreate(
            name="Parameterized WF",
            description="Test",
            steps_json=json.dumps([{"agent": "a", "action": "do", "parameters": {"p": "{val}"}}]),
            tags=["dev", "ci"],
            parameters={"val": {"type": "string", "description": "A value"}},
            is_template=True,
            template_category="development",
        )
        wf = await svc.create_workflow(data)
        assert wf.tags == "dev,ci"
        assert wf.is_template is True
        assert wf.template_category == "development"
        params = json.loads(wf.parameters_json) if wf.parameters_json else None
        assert params is not None
        assert "val" in params

    @pytest.mark.asyncio
    async def test_update_workflow_tags(self, db_session: AsyncSession):
        """Update can change tags."""
        wf = await _create_test_workflow(db_session, tags="old")
        svc = WorkflowService(db_session)
        updated = await svc.update_workflow(wf.id, WorkflowUpdate(tags=["new1", "new2"]))
        assert updated.tags == "new1,new2"


# ═══════════════════════════════════════════════════════════════
# Story 4.4: Search & Tags
# ═══════════════════════════════════════════════════════════════

class TestWorkflowSearch:

    @pytest.mark.asyncio
    async def test_search_by_name(self, db_session: AsyncSession):
        """Search matches workflow name."""
        await _create_test_workflow(db_session, name="Daily Report")
        await _create_test_workflow(db_session, name="Monthly Backup")

        svc = WorkflowService(db_session)
        results = await svc.search_workflows(query="daily")
        assert len(results) == 1
        assert results[0].name == "Daily Report"

    @pytest.mark.asyncio
    async def test_search_by_description(self, db_session: AsyncSession):
        """Search matches workflow description."""
        await _create_test_workflow(db_session, name="WF1", description="Uses python scripts")
        await _create_test_workflow(db_session, name="WF2", description="Uses shell commands")

        svc = WorkflowService(db_session)
        results = await svc.search_workflows(query="python")
        assert len(results) == 1
        assert results[0].name == "WF1"

    @pytest.mark.asyncio
    async def test_search_by_tags(self, db_session: AsyncSession):
        """Search filters by tags."""
        await _create_test_workflow(db_session, name="A", tags="dev,ci")
        await _create_test_workflow(db_session, name="B", tags="prod,deploy")

        svc = WorkflowService(db_session)
        results = await svc.search_workflows(tags=["dev"])
        assert len(results) == 1
        assert results[0].name == "A"

    @pytest.mark.asyncio
    async def test_search_templates_only(self, db_session: AsyncSession):
        """Search with templates_only=True returns only templates."""
        await _create_test_workflow(db_session, name="User WF", is_template=False)
        await _create_test_workflow(db_session, name="Template WF", is_template=True)

        svc = WorkflowService(db_session)
        results = await svc.search_workflows(templates_only=True)
        assert len(results) == 1
        assert results[0].name == "Template WF"

    @pytest.mark.asyncio
    async def test_search_no_results(self, db_session: AsyncSession):
        """Search with no match returns empty list."""
        svc = WorkflowService(db_session)
        results = await svc.search_workflows(query="nonexistent_xyz")
        assert results == []


# ═══════════════════════════════════════════════════════════════
# Story 4.5: Templates & Clone
# ═══════════════════════════════════════════════════════════════

class TestWorkflowTemplates:

    @pytest.mark.asyncio
    async def test_seed_templates(self, db_session: AsyncSession):
        """Seed inserts WORKFLOW_TEMPLATES into the DB."""
        svc = WorkflowService(db_session)
        count = await svc.seed_templates()
        assert count == len(WORKFLOW_TEMPLATES)

        # Second seed is idempotent
        count2 = await svc.seed_templates()
        assert count2 == 0

    @pytest.mark.asyncio
    async def test_list_templates_only(self, db_session: AsyncSession):
        """list_workflows(templates_only=True) returns only templates."""
        await _create_test_workflow(db_session, name="User", is_template=False)
        await _create_test_workflow(db_session, name="Tmpl", is_template=True)

        svc = WorkflowService(db_session)
        results = await svc.list_workflows(templates_only=True)
        assert all(r.is_template for r in results)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_clone_template(self, db_session: AsyncSession):
        """Cloning a template creates a non-template copy."""
        template = await _create_test_workflow(
            db_session, name="My Template", is_template=True, tags="orig"
        )
        svc = WorkflowService(db_session)
        clone = await svc.clone_template(
            template_id=template.id,
            new_name="My Clone",
            description="Cloned",
            tags=["personal"],
        )
        assert clone.name == "My Clone"
        assert clone.is_template is False
        assert clone.tags == "personal"
        assert json.loads(clone.steps_json) == json.loads(template.steps_json)

    @pytest.mark.asyncio
    async def test_clone_non_template_raises(self, db_session: AsyncSession):
        """Cannot clone a non-template workflow."""
        wf = await _create_test_workflow(db_session, is_template=False)
        svc = WorkflowService(db_session)
        with pytest.raises(JarvisError) as exc_info:
            await svc.clone_template(wf.id, "Copy")
        assert exc_info.value.code == ErrorCode.WORKFLOW_NOT_TEMPLATE

    @pytest.mark.asyncio
    async def test_clone_duplicate_name_raises(self, db_session: AsyncSession):
        """Cannot clone to a name that already exists."""
        tpl = await _create_test_workflow(db_session, name="Tpl", is_template=True)
        await _create_test_workflow(db_session, name="Existing")
        svc = WorkflowService(db_session)
        with pytest.raises(JarvisError) as exc_info:
            await svc.clone_template(tpl.id, "Existing")
        assert exc_info.value.code == ErrorCode.WORKFLOW_DUPLICATE_NAME


# ═══════════════════════════════════════════════════════════════
# Story 4.7: Export
# ═══════════════════════════════════════════════════════════════

class TestWorkflowExport:

    @pytest.mark.asyncio
    async def test_export_json(self, db_session: AsyncSession):
        """Export as JSON returns full workflow dict."""
        wf = await _create_test_workflow(db_session, name="Export Me")
        svc = WorkflowService(db_session)
        result = await svc.export_workflow(wf.id, fmt="json")
        assert result["format"] == "json"
        assert result["workflow"]["name"] == "Export Me"
        assert "steps" in result["workflow"]

    @pytest.mark.asyncio
    async def test_export_csv(self, db_session: AsyncSession):
        """Export as CSV returns a string with headers and rows."""
        wf = await _create_test_workflow(db_session, name="CSV WF")
        svc = WorkflowService(db_session)
        result = await svc.export_workflow(wf.id, fmt="csv")
        assert result["format"] == "csv"
        csv_str = result["workflow"]
        assert isinstance(csv_str, str)
        assert "step_index" in csv_str
        assert "agent" in csv_str
        assert result["exported_at"] is not None


# ═══════════════════════════════════════════════════════════════
# Story 4.2: Workflow Execute Stats Update
# ═══════════════════════════════════════════════════════════════

class TestExecutionStats:

    @pytest.mark.asyncio
    async def test_update_execution_stats_success(self, db_session: AsyncSession):
        """Successful execution updates count and success rate."""
        wf = await _create_test_workflow(db_session)
        svc = WorkflowService(db_session)

        await svc.update_execution_stats(wf.id, success=True)
        await db_session.refresh(wf)
        assert wf.execution_count == 1
        assert wf.success_rate > 0

    @pytest.mark.asyncio
    async def test_update_execution_stats_failure(self, db_session: AsyncSession):
        """Failed execution updates count, lowers success_rate."""
        wf = await _create_test_workflow(db_session, success_rate=1.0, execution_count=5)
        svc = WorkflowService(db_session)

        await svc.update_execution_stats(wf.id, success=False)
        await db_session.refresh(wf)
        assert wf.execution_count == 6
        assert wf.success_rate < 1.0

    @pytest.mark.asyncio
    async def test_update_execution_stats_multiple(self, db_session: AsyncSession):
        """Multiple updates accumulate correctly."""
        wf = await _create_test_workflow(db_session)
        svc = WorkflowService(db_session)

        for _ in range(5):
            await svc.update_execution_stats(wf.id, success=True)
        await svc.update_execution_stats(wf.id, success=False)

        await db_session.refresh(wf)
        assert wf.execution_count == 6
        assert 0 < wf.success_rate < 1.0


# ═══════════════════════════════════════════════════════════════
# Story 2.6: Pause & Resume (Orchestrator)
# ═══════════════════════════════════════════════════════════════

class TestPauseResume:

    @pytest.mark.asyncio
    async def test_pause_sets_event(self):
        """Calling pause creates an unset event for the execution."""
        from app.agents.orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        orch._running_executions["exec-1"] = True

        await orch.pause("exec-1")
        assert orch.is_paused("exec-1")

    @pytest.mark.asyncio
    async def test_resume_clears_event(self):
        """Resume sets the event, unblocking the loop."""
        from app.agents.orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        orch._running_executions["exec-1"] = True
        await orch.pause("exec-1")
        assert orch.is_paused("exec-1")

        await orch.resume("exec-1")
        assert not orch.is_paused("exec-1")

    @pytest.mark.asyncio
    async def test_pause_nonexistent_raises(self):
        """Cannot pause an execution that isn't running."""
        from app.agents.orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        with pytest.raises(WorkflowError):
            await orch.pause("nonexistent")

    @pytest.mark.asyncio
    async def test_resume_not_paused_raises(self):
        """Cannot resume an execution that isn't paused."""
        from app.agents.orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        with pytest.raises(WorkflowError):
            await orch.resume("not-paused")

    @pytest.mark.asyncio
    async def test_double_pause_raises(self):
        """Pausing an already-paused execution raises."""
        from app.agents.orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        orch._running_executions["exec-1"] = True
        await orch.pause("exec-1")
        with pytest.raises(WorkflowError):
            await orch.pause("exec-1")

    @pytest.mark.asyncio
    async def test_cancel_wakes_paused(self):
        """Cancelling a paused execution wakes the event."""
        from app.agents.orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        orch._running_executions["exec-1"] = True
        await orch.pause("exec-1")
        assert orch.is_paused("exec-1")

        await orch.cancel("exec-1")
        # Event was set by cancel
        assert "exec-1" not in orch._paused_executions

    @pytest.mark.asyncio
    async def test_pause_blocks_execution_loop(self):
        """Pausing before step execution delays until resume."""
        from app.agents.orchestrator import WorkflowOrchestrator
        from app.agents.registry import AgentInfo, AgentStatus

        orch = WorkflowOrchestrator()
        # Mock the agent dispatch to succeed immediately
        orch._dispatch_to_agent = AsyncMock(return_value={"success": True, "data": None, "duration_ms": 10})
        # Mock WS manager
        with patch("app.agents.orchestrator.ws_manager") as mock_ws:
            mock_ws.broadcast_to_execution = AsyncMock()

            steps = [{"agent": "a", "action": "do", "parameters": {}}]

            # Pause before execution starts
            orch._running_executions["e1"] = True
            await orch.pause("e1")

            # Run in background
            task = asyncio.create_task(orch.execute_workflow("e1", steps))

            # Wait a bit - should be blocked
            await asyncio.sleep(0.1)
            assert not task.done()

            # Resume
            await orch.resume("e1")
            result = await asyncio.wait_for(task, timeout=5)
            assert result["status"] == "completed"


# ═══════════════════════════════════════════════════════════════
# Story 3.7: Error Context Capture
# ═══════════════════════════════════════════════════════════════

class TestErrorContextCapture:

    @pytest.mark.asyncio
    async def test_capture_creates_snapshot(self, db_session: AsyncSession):
        """Capturing error context creates a ContextSnapshot."""
        wf = await _create_test_workflow(db_session, name="Ctx WF")
        exe = await _create_test_execution(db_session, wf.id, status="failed")

        svc = ErrorContextService(db_session)
        cs = await svc.capture_error_context(
            execution_id=exe.id,
            step_index=1,
            error="Agent timed out",
            error_type="timeout",
            agent_name="web_agent",
            action="fetch",
            parameters={"url": "http://example.com"},
        )
        assert cs.id is not None
        assert cs.execution_id == exe.id
        assert cs.step_index == 1

        data = json.loads(cs.snapshot_json)
        assert data["error"]["message"] == "Agent timed out"
        assert data["error"]["type"] == "timeout"
        assert data["step"]["agent"] == "web_agent"
        assert "system" in data

    @pytest.mark.asyncio
    async def test_capture_redacts_sensitive_params(self, db_session: AsyncSession):
        """Sensitive parameters are redacted in the snapshot."""
        wf = await _create_test_workflow(db_session, name="Redact WF")
        exe = await _create_test_execution(db_session, wf.id, status="failed")

        svc = ErrorContextService(db_session)
        cs = await svc.capture_error_context(
            execution_id=exe.id,
            step_index=0,
            error="Auth failed",
            parameters={"api_key": "secret-123", "url": "http://safe.com"},
        )
        data = json.loads(cs.snapshot_json)
        assert data["step"]["parameters"]["api_key"] == "***REDACTED***"
        assert data["step"]["parameters"]["url"] == "http://safe.com"

    @pytest.mark.asyncio
    async def test_get_execution_snapshots(self, db_session: AsyncSession):
        """Lists all snapshots for an execution."""
        wf = await _create_test_workflow(db_session, name="Multi Snap WF")
        exe = await _create_test_execution(db_session, wf.id, status="failed")

        svc = ErrorContextService(db_session)
        await svc.capture_error_context(exe.id, 0, "Error 1")
        await svc.capture_error_context(exe.id, 1, "Error 2")

        snapshots = await svc.get_execution_snapshots(exe.id)
        assert len(snapshots) == 2
        assert snapshots[0].step_index == 0
        assert snapshots[1].step_index == 1

    @pytest.mark.asyncio
    async def test_get_snapshot_data_returns_dict(self, db_session: AsyncSession):
        """get_snapshot_data returns parsed JSON."""
        wf = await _create_test_workflow(db_session, name="Parsed WF")
        exe = await _create_test_execution(db_session, wf.id, status="failed")

        svc = ErrorContextService(db_session)
        cs = await svc.capture_error_context(exe.id, 0, "Test error")
        data = await svc.get_snapshot_data(cs.id)
        assert isinstance(data, dict)
        assert data["error"]["message"] == "Test error"

    @pytest.mark.asyncio
    async def test_get_snapshot_data_not_found(self, db_session: AsyncSession):
        """Returns None for nonexistent snapshot."""
        svc = ErrorContextService(db_session)
        result = await svc.get_snapshot_data("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_capture_includes_execution_history(self, db_session: AsyncSession):
        """Snapshot includes recent execution logs."""
        wf = await _create_test_workflow(db_session, name="History WF")
        exe = await _create_test_execution(db_session, wf.id, status="failed")
        await _create_test_logs(db_session, exe.id)

        svc = ErrorContextService(db_session)
        cs = await svc.capture_error_context(exe.id, 1, "Step 1 failed")
        data = json.loads(cs.snapshot_json)
        assert "execution_history" in data
        assert len(data["execution_history"]) == 2

    @pytest.mark.asyncio
    async def test_capture_includes_system_info(self, db_session: AsyncSession):
        """Snapshot includes platform and Python version."""
        wf = await _create_test_workflow(db_session, name="SysInfo WF")
        exe = await _create_test_execution(db_session, wf.id, status="failed")

        svc = ErrorContextService(db_session)
        cs = await svc.capture_error_context(exe.id, 0, "Err")
        data = json.loads(cs.snapshot_json)
        assert "platform" in data["system"]
        assert "python_version" in data["system"]
        assert "pid" in data["system"]

    @pytest.mark.asyncio
    async def test_capture_with_extra_data(self, db_session: AsyncSession):
        """Extra context data is included in snapshot."""
        wf = await _create_test_workflow(db_session, name="Extra WF")
        exe = await _create_test_execution(db_session, wf.id, status="failed")

        svc = ErrorContextService(db_session)
        cs = await svc.capture_error_context(
            exe.id, 0, "Err", extra={"retry_count": 3, "last_output": "partial"}
        )
        data = json.loads(cs.snapshot_json)
        assert data["extra"]["retry_count"] == 3


# ═══════════════════════════════════════════════════════════════
# Story 3.8: AI Recovery Suggestions
# ═══════════════════════════════════════════════════════════════

class TestRecoverySuggestions:

    @pytest.mark.asyncio
    async def test_fallback_for_timeout(self):
        """Fallback suggestions for timeout error."""
        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=False)

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {
            "error": {"message": "Agent timed out after 30s", "type": "timeout"},
            "step": {"agent": "web_agent", "action": "fetch", "parameters": {}},
            "system": {},
        }
        result = await svc.suggest(ctx)
        assert result.model_used == "fallback"
        assert len(result.suggestions) > 0
        actions = [s.action for s in result.suggestions]
        assert "increase_timeout" in actions

    @pytest.mark.asyncio
    async def test_fallback_for_not_found(self):
        """Fallback suggestions for not-found error."""
        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=False)

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {
            "error": {"message": "Agent 'unknown' not found in registry", "type": "runtime"},
            "step": {},
            "system": {},
        }
        result = await svc.suggest(ctx)
        actions = [s.action for s in result.suggestions]
        assert "verify_agent" in actions

    @pytest.mark.asyncio
    async def test_fallback_for_unhealthy(self):
        """Fallback suggestions for unhealthy agent."""
        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=False)

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {
            "error": {"message": "Agent 'file_agent' is unhealthy", "type": "runtime"},
            "step": {},
            "system": {},
        }
        result = await svc.suggest(ctx)
        actions = [s.action for s in result.suggestions]
        assert "restart_agent" in actions

    @pytest.mark.asyncio
    async def test_fallback_generic(self):
        """Fallback suggestions for generic error."""
        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=False)

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {
            "error": {"message": "Something went wrong", "type": "runtime"},
            "step": {},
            "system": {},
        }
        result = await svc.suggest(ctx)
        actions = [s.action for s in result.suggestions]
        assert "retry" in actions

    @pytest.mark.asyncio
    async def test_ai_suggestion_success(self):
        """When Ollama is available, parses AI response."""
        ai_response = json.dumps({
            "diagnosis": "The agent is overloaded",
            "suggestions": [
                {"action": "scale_up", "description": "Increase resources", "confidence": 0.8},
                {"action": "retry_later", "description": "Wait and retry", "confidence": 0.6},
            ],
            "can_auto_recover": True,
            "auto_recovery_action": "retry_later",
        })

        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=True)
        mock_ollama.generate = AsyncMock(return_value=ai_response)
        mock_ollama._model = "qwen2.5:3b"

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {
            "error": {"message": "Overloaded", "type": "runtime"},
            "step": {"agent": "compute", "action": "run", "parameters": {}},
            "system": {"platform": "test"},
        }
        result = await svc.suggest(ctx)
        assert result.diagnosis == "The agent is overloaded"
        assert len(result.suggestions) == 2
        assert result.can_auto_recover is True
        assert result.auto_recovery_action == "retry_later"
        assert result.model_used == "qwen2.5:3b"

    @pytest.mark.asyncio
    async def test_ai_suggestion_parse_failure_fallback(self):
        """If AI returns invalid JSON, falls back to parse error result."""
        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=True)
        mock_ollama.generate = AsyncMock(return_value="This is not JSON at all!")
        mock_ollama._model = "qwen2.5:3b"

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {
            "error": {"message": "Test", "type": "runtime"},
            "step": {},
            "system": {},
        }
        result = await svc.suggest(ctx)
        assert "Failed to parse" in result.diagnosis
        assert len(result.suggestions) >= 1

    @pytest.mark.asyncio
    async def test_ai_suggestion_handles_markdown_fences(self):
        """AI response wrapped in markdown code fences is still parsed."""
        inner = json.dumps({
            "diagnosis": "Disk full",
            "suggestions": [{"action": "free_space", "description": "Delete temp files", "confidence": 0.9}],
            "can_auto_recover": False,
        })
        response = f"```json\n{inner}\n```"

        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=True)
        mock_ollama.generate = AsyncMock(return_value=response)
        mock_ollama._model = "test-model"

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {"error": {"message": "No space left"}, "step": {}, "system": {}}
        result = await svc.suggest(ctx)
        assert result.diagnosis == "Disk full"
        assert result.suggestions[0].action == "free_space"

    @pytest.mark.asyncio
    async def test_ai_exception_falls_back(self):
        """If Ollama raises, falls back to rule-based."""
        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=True)
        mock_ollama.generate = AsyncMock(side_effect=RuntimeError("Connection reset"))
        mock_ollama._model = "test"

        svc = RecoverySuggestionService(ollama=mock_ollama)
        ctx = {
            "error": {"message": "timeout error", "type": "timeout"},
            "step": {},
            "system": {},
        }
        result = await svc.suggest(ctx)
        assert result.model_used == "fallback"

    @pytest.mark.asyncio
    async def test_suggest_from_snapshot_json(self):
        """suggest_from_snapshot parses JSON string."""
        mock_ollama = AsyncMock()
        mock_ollama.is_available = AsyncMock(return_value=False)

        svc = RecoverySuggestionService(ollama=mock_ollama)
        snapshot_json = json.dumps({
            "error": {"message": "test", "type": "runtime"},
            "step": {},
            "system": {},
        })
        result = await svc.suggest_from_snapshot(snapshot_json)
        assert result is not None
        assert len(result.suggestions) > 0

    def test_suggestion_result_to_dict(self):
        """RecoverySuggestionResult serializes correctly."""
        result = RecoverySuggestionResult(
            diagnosis="Test",
            suggestions=[RecoverySuggestion("act", "desc", 0.7)],
            can_auto_recover=False,
            auto_recovery_action=None,
            generated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            model_used="test",
        )
        d = result.to_dict()
        assert d["diagnosis"] == "Test"
        assert d["suggestions"][0]["action"] == "act"
        assert d["suggestions"][0]["confidence"] == 0.7
        assert d["model_used"] == "test"

    def test_build_prompt(self):
        """Prompt builder includes all context sections."""
        svc = RecoverySuggestionService(ollama=MagicMock())
        ctx = {
            "error": {"message": "timeout", "type": "timeout", "timestamp": "2024-01-01"},
            "step": {"agent": "a", "action": "b", "parameters": {"x": 1}},
            "system": {"platform": "Linux", "memory": {"available_mb": 4000, "total_mb": 8000, "percent_used": 50}},
            "execution_history": [
                {"step_index": 0, "agent_name": "a", "action": "b", "status": "success", "duration_ms": 100},
            ],
        }
        prompt = svc._build_prompt(ctx)
        assert "timeout" in prompt
        assert "Linux" in prompt
        assert "4000" in prompt
        assert "Recent Execution History" in prompt


# ═══════════════════════════════════════════════════════════════
# Parameter Substitution Helper
# ═══════════════════════════════════════════════════════════════

class TestParameterSubstitution:

    def test_substitute_replaces_placeholders(self):
        """_substitute_parameters replaces {placeholder} tokens."""
        from app.routes.workflows import _substitute_parameters

        steps = [
            {"agent": "file_agent", "action": "read", "parameters": {"path": "/data/{filename}"}},
            {"agent": "web_agent", "action": "post", "parameters": {"url": "{base_url}/api", "body": "hello"}},
        ]
        values = {"filename": "report.txt", "base_url": "http://localhost:8080"}
        result = _substitute_parameters(steps, values)

        assert result[0]["parameters"]["path"] == "/data/report.txt"
        assert result[1]["parameters"]["url"] == "http://localhost:8080/api"
        assert result[1]["parameters"]["body"] == "hello"  # unchanged

    def test_substitute_does_not_mutate_original(self):
        """Substitution creates a deep copy."""
        from app.routes.workflows import _substitute_parameters

        original = [{"agent": "a", "action": "b", "parameters": {"p": "{val}"}}]
        _substitute_parameters(original, {"val": "replaced"})
        assert original[0]["parameters"]["p"] == "{val}"


# ═══════════════════════════════════════════════════════════════
# API Route Tests
# ═══════════════════════════════════════════════════════════════

class TestWorkflowRoutes:

    @pytest.mark.asyncio
    async def test_list_templates_route(self, client):
        """GET /api/workflows/templates returns only templates."""
        resp = await client.get("/api/workflows/templates")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_seed_templates_route(self, client):
        """POST /api/workflows/templates/seed populates templates."""
        resp = await client.post("/api/workflows/templates/seed")
        assert resp.status_code == 200
        data = resp.json()
        assert "Seeded" in data["message"]

    @pytest.mark.asyncio
    async def test_search_route(self, client):
        """POST /api/workflows/search works."""
        # Seed first
        await client.post("/api/workflows/templates/seed")
        resp = await client.post("/api/workflows/search", json={"query": "daily"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_create_with_tags(self, client):
        """POST /api/workflows with tags stores them."""
        resp = await client.post("/api/workflows", json={
            "name": "Tagged WF",
            "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
            "tags": ["dev", "test"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["tags"] == "dev,test"

    @pytest.mark.asyncio
    async def test_clone_route(self, client):
        """POST /api/workflows/{id}/clone creates a clone."""
        # Create template
        resp = await client.post("/api/workflows", json={
            "name": "Clone Source",
            "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
            "is_template": True,
        })
        template_id = resp.json()["id"]

        # Clone
        resp = await client.post(f"/api/workflows/{template_id}/clone", json={
            "new_name": "My Clone",
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "My Clone"
        assert resp.json()["is_template"] is False

    @pytest.mark.asyncio
    async def test_export_json_route(self, client):
        """POST /api/workflows/{id}/export with json format."""
        resp = await client.post("/api/workflows", json={
            "name": "Export Route WF",
            "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
        })
        wf_id = resp.json()["id"]

        resp = await client.post(f"/api/workflows/{wf_id}/export", json={"format": "json"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "json"

    @pytest.mark.asyncio
    async def test_export_csv_route(self, client):
        """POST /api/workflows/{id}/export with csv format."""
        resp = await client.post("/api/workflows", json={
            "name": "CSV Route WF",
            "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
        })
        wf_id = resp.json()["id"]

        resp = await client.post(f"/api/workflows/{wf_id}/export", json={"format": "csv"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "csv"

    @pytest.mark.asyncio
    async def test_list_with_templates_only_param(self, client):
        """GET /api/workflows?templates_only=true filters results."""
        resp = await client.get("/api/workflows?templates_only=true")
        assert resp.status_code == 200


class TestExecutionRoutes:

    @pytest.mark.asyncio
    async def test_pause_status_route(self, client):
        """GET /api/executions/{id}/pause-status returns status."""
        resp = await client.get("/api/executions/fake-id/pause-status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["paused"] is False

    @pytest.mark.asyncio
    async def test_context_snapshots_route(self, client):
        """GET /api/executions/{id}/context-snapshots returns list."""
        resp = await client.get("/api/executions/fake-id/context-snapshots")
        assert resp.status_code == 200
        data = resp.json()
        assert "snapshots" in data
