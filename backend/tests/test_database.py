"""Tests for database models — verify table creation and basic CRUD."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatSession
from app.models.workflow import Workflow, WorkflowRevision
from app.models.execution import WorkflowExecution, ExecutionLog
from app.models.security import AuthLog, FailureHistory, PendingRequest
from app.models.agent import ApplicationRegistry
from app.models.metrics import Metric
from app.models.settings import UserSetting
from app.models.user import User


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Can insert and read a User row."""
    user = User(username="testuser", passphrase_hash="fakehash")
    db_session.add(user)
    await db_session.flush()

    result = await db_session.execute(select(User).where(User.username == "testuser"))
    found = result.scalar_one()
    assert found.username == "testuser"
    assert found.failed_attempts == 0
    assert found.is_active is True


@pytest.mark.asyncio
async def test_create_chat_session_with_messages(db_session: AsyncSession):
    """Chat session + messages cascade correctly."""
    session = ChatSession(title="Test Chat")
    db_session.add(session)
    await db_session.flush()

    msg = ChatMessage(
        session_id=session.id,
        role="user",
        content="Hello",
        sequence=1,
    )
    db_session.add(msg)
    await db_session.flush()

    result = await db_session.execute(
        select(ChatMessage).where(ChatMessage.session_id == session.id)
    )
    messages = result.scalars().all()
    assert len(messages) == 1
    assert messages[0].content == "Hello"


@pytest.mark.asyncio
async def test_workflow_with_revision(db_session: AsyncSession):
    """Workflow revision snapshot creation."""
    wf = Workflow(name="Test WF", steps_json="[]")
    db_session.add(wf)
    await db_session.flush()

    rev = WorkflowRevision(
        workflow_id=wf.id,
        version=1,
        steps_json="[]",
        change_reason="initial",
    )
    db_session.add(rev)
    await db_session.flush()

    result = await db_session.execute(
        select(WorkflowRevision).where(WorkflowRevision.workflow_id == wf.id)
    )
    revisions = result.scalars().all()
    assert len(revisions) == 1


@pytest.mark.asyncio
async def test_execution_with_logs(db_session: AsyncSession):
    """Execution + log entry creation."""
    wf = Workflow(name="Exec WF", steps_json="[]")
    db_session.add(wf)
    await db_session.flush()

    exe = WorkflowExecution(workflow_id=wf.id, total_steps=2)
    db_session.add(exe)
    await db_session.flush()

    log = ExecutionLog(
        execution_id=exe.id,
        step_index=0,
        agent_name="test_agent",
        action="noop",
        status="success",
        duration_ms=42.5,
    )
    db_session.add(log)
    await db_session.flush()

    result = await db_session.execute(
        select(ExecutionLog).where(ExecutionLog.execution_id == exe.id)
    )
    logs = result.scalars().all()
    assert len(logs) == 1
    assert logs[0].duration_ms == 42.5


@pytest.mark.asyncio
async def test_auth_log_creation(db_session: AsyncSession):
    """AuthLog row insertion."""
    entry = AuthLog(event="login_failed", ip_address="127.0.0.1", detail="bad passphrase")
    db_session.add(entry)
    await db_session.flush()

    result = await db_session.execute(select(AuthLog))
    assert len(result.scalars().all()) == 1


@pytest.mark.asyncio
async def test_application_registry(db_session: AsyncSession):
    """Register an application."""
    app = ApplicationRegistry(
        name="Notepad",
        exe_path="C:\\Windows\\System32\\notepad.exe",
        category="editor",
    )
    db_session.add(app)
    await db_session.flush()

    result = await db_session.execute(
        select(ApplicationRegistry).where(ApplicationRegistry.name == "Notepad")
    )
    found = result.scalar_one()
    assert found.is_available is True


@pytest.mark.asyncio
async def test_metric_insertion(db_session: AsyncSession):
    """Insert a metric data point."""
    m = Metric(name="api_latency", value=12.5, unit="ms")
    db_session.add(m)
    await db_session.flush()

    result = await db_session.execute(select(Metric).where(Metric.name == "api_latency"))
    found = result.scalar_one()
    assert found.value == 12.5


@pytest.mark.asyncio
async def test_user_setting(db_session: AsyncSession):
    """User setting key-value pair."""
    user = User(username="settingsuser", passphrase_hash="hash")
    db_session.add(user)
    await db_session.flush()

    s = UserSetting(user_id=user.id, key="theme", value="dark")
    db_session.add(s)
    await db_session.flush()

    result = await db_session.execute(
        select(UserSetting).where(UserSetting.user_id == user.id)
    )
    settings = result.scalars().all()
    assert len(settings) == 1
    assert settings[0].value == "dark"
