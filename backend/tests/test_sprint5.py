"""
Sprint 5 Backend Tests — Execution Logger + Execution Log Route.

Story 2.3: Step Execution Logging
"""

import json
import os
import tempfile
from datetime import datetime, timezone

import pytest

from app.services.execution_logger import (
    ExecutionLogger,
    StepLogEntry,
    redact_sensitive,
    redact_dict,
)


# ── Redaction Tests ─────────────────────────────────────

class TestRedaction:
    """Tests for sensitive data redaction."""

    def test_redact_password_in_text(self):
        text = "password: my_secret_123"
        result = redact_sensitive(text)
        assert "my_secret_123" not in result
        assert "[REDACTED]" in result

    def test_redact_bearer_token(self):
        text = "Authorization: Bearer abc123xyz"
        result = redact_sensitive(text)
        assert "abc123xyz" not in result

    def test_redact_jwt_token(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = redact_sensitive(jwt)
        assert "eyJ" not in result

    def test_redact_api_key_in_text(self):
        text = "api_key=sk-12345abcdef"
        result = redact_sensitive(text)
        assert "sk-12345" not in result

    def test_redact_dict_sensitive_keys(self):
        data = {
            "username": "admin",
            "password": "secret123",
            "token": "jwt-token-here",
            "api_key": "sk-key",
            "action": "login",
        }
        result = redact_dict(data)
        assert result["username"] == "admin"
        assert result["password"] == "[REDACTED]"
        assert result["token"] == "[REDACTED]"
        assert result["api_key"] == "[REDACTED]"
        assert result["action"] == "login"

    def test_redact_nested_dict(self):
        data = {
            "config": {
                "secret": "hidden_value",
                "name": "test",
            },
        }
        result = redact_dict(data)
        assert result["config"]["secret"] == "[REDACTED]"
        assert result["config"]["name"] == "test"

    def test_safe_text_unchanged(self):
        text = "This is a normal log message with no secrets."
        assert redact_sensitive(text) == text


# ── StepLogEntry Tests ──────────────────────────────────

class TestStepLogEntry:
    """Tests for StepLogEntry model."""

    def test_create_entry(self):
        entry = StepLogEntry(
            execution_id="exec-1",
            step_index=0,
            agent_name="analyzer",
            action="analyze",
            input_data={"text": "hello"},
        )
        assert entry.execution_id == "exec-1"
        assert entry.step_index == 0
        assert entry.agent_name == "analyzer"
        assert entry.status == "started"
        assert entry.exit_code is None

    def test_complete_entry(self):
        entry = StepLogEntry(
            execution_id="exec-2",
            step_index=1,
            agent_name="generator",
            action="generate",
        )
        entry.complete(
            output_data={"result": "done"},
            status="success",
            exit_code=0,
            confidence=0.87,
        )
        assert entry.status == "success"
        assert entry.exit_code == 0
        assert entry.confidence == 0.87
        assert entry.duration_ms is not None
        assert entry.duration_ms >= 0

    def test_to_json(self):
        entry = StepLogEntry(
            execution_id="exec-3",
            step_index=0,
            agent_name="test-agent",
            action="test",
            input_data={"password": "secret"},
        )
        entry.complete(output_data={"token": "abc"}, status="success")
        data = entry.to_json()

        assert data["agent"] == "test-agent"
        assert data["input"]["password"] == "[REDACTED]"
        assert data["output"]["token"] == "[REDACTED]"
        assert data["status"] == "success"
        assert "completed_at" in data

    def test_to_plaintext(self):
        entry = StepLogEntry(
            execution_id="exec-4",
            step_index=2,
            agent_name="runner",
            action="execute",
        )
        entry.complete(status="success", confidence=0.92)
        text = entry.to_plaintext()

        assert "Step 2" in text
        assert "runner.execute" in text
        assert "success" in text
        assert "92%" in text

    def test_plaintext_with_error(self):
        entry = StepLogEntry(
            execution_id="exec-5",
            step_index=0,
            agent_name="agent",
            action="run",
        )
        entry.complete(status="failure", error="Connection failed")
        text = entry.to_plaintext()
        assert "Connection failed" in text


# ── ExecutionLogger Tests ───────────────────────────────

class TestExecutionLogger:
    """Tests for ExecutionLogger (file-based logging)."""

    def test_start_and_complete_step(self, tmp_path):
        logger = ExecutionLogger(log_dir=str(tmp_path))

        entry = logger.start_step(
            execution_id="exec-test-1",
            step_index=0,
            agent_name="analyzer",
            action="analyze",
            input_data={"query": "test"},
            workflow_id="wf-1",
        )

        assert entry.status == "started"

        logger.complete_step(
            entry,
            output_data={"result": "analyzed"},
            status="success",
            confidence=0.95,
        )

        assert entry.status == "success"
        assert entry.confidence == 0.95

        # Check log files were created
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 1

        # Cleanup
        logger.cleanup("exec-test-1")

    def test_get_entries(self, tmp_path):
        logger = ExecutionLogger(log_dir=str(tmp_path))

        e1 = logger.start_step("exec-q", 0, "agent-a", "act-1", workflow_id="wf-q")
        logger.complete_step(e1, status="success")

        e2 = logger.start_step("exec-q", 1, "agent-b", "act-2", workflow_id="wf-q")
        logger.complete_step(e2, status="failure", error="timeout")

        entries = logger.get_entries("exec-q")
        assert len(entries) == 2

    def test_filter_by_step_index(self, tmp_path):
        logger = ExecutionLogger(log_dir=str(tmp_path))
        e1 = logger.start_step("exec-f", 0, "a", "run", workflow_id="wf-f")
        logger.complete_step(e1, status="success")
        e2 = logger.start_step("exec-f", 1, "b", "run", workflow_id="wf-f")
        logger.complete_step(e2, status="success")

        filtered = logger.get_entries("exec-f", step_index=1)
        assert len(filtered) == 1
        assert filtered[0]["step_index"] == 1

    def test_filter_by_agent(self, tmp_path):
        logger = ExecutionLogger(log_dir=str(tmp_path))
        e1 = logger.start_step("exec-g", 0, "agent-x", "run", workflow_id="wf-g")
        logger.complete_step(e1, status="success")
        e2 = logger.start_step("exec-g", 1, "agent-y", "run", workflow_id="wf-g")
        logger.complete_step(e2, status="success")

        filtered = logger.get_entries("exec-g", agent="agent-x")
        assert len(filtered) == 1
        assert filtered[0]["agent"] == "agent-x"

    def test_filter_by_status(self, tmp_path):
        logger = ExecutionLogger(log_dir=str(tmp_path))
        e1 = logger.start_step("exec-h", 0, "a", "run", workflow_id="wf-h")
        logger.complete_step(e1, status="success")
        e2 = logger.start_step("exec-h", 1, "b", "run", workflow_id="wf-h")
        logger.complete_step(e2, status="failure", error="boom")

        failed = logger.get_entries("exec-h", status="failure")
        assert len(failed) == 1
        assert failed[0]["status"] == "failure"

    def test_cleanup_removes_logger(self, tmp_path):
        logger = ExecutionLogger(log_dir=str(tmp_path))
        logger.start_step("exec-cl", 0, "a", "run", workflow_id="wf-cl")
        logger.cleanup("exec-cl")

        assert "exec-cl" not in logger._loggers
        assert "exec-cl" not in logger._entries


# ── Execution Logs Route Test ───────────────────────────

@pytest.mark.asyncio
async def test_execution_logs_route(client):
    """Test GET /api/executions/{id}/logs returns log entries."""
    response = await client.get("/api/executions/nonexistent/logs")
    assert response.status_code == 200
    data = response.json()
    assert data["execution_id"] == "nonexistent"
    assert data["entries"] == []
    assert data["count"] == 0


@pytest.mark.asyncio
async def test_execution_logs_route_with_filters(client):
    """Test GET /api/executions/{id}/logs with query params."""
    response = await client.get(
        "/api/executions/test-exec/logs",
        params={"step_index": 0, "agent": "test-agent", "status": "success"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
