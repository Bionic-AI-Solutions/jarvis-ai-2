"""Tests for Sprint 2 — Agent registry, routes, orchestrator, and Ollama service."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.agents.orchestrator import WorkflowOrchestrator
from app.agents.protocol import AgentMessageType, AgentMessage, AgentExecutePayload, AgentResultPayload
from app.agents.registry import AgentInfo, AgentRegistry, AgentStatus, agent_registry
from app.main import create_app


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_agent_registry():
    """Ensure clean agent registry for each test."""
    agent_registry._agents.clear()
    yield
    agent_registry._agents.clear()


@pytest.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── Protocol Tests ────────────────────────────────────────────────────

class TestAgentProtocol:
    """Verify protocol data classes and enums."""

    def test_message_types(self):
        assert AgentMessageType.EXECUTE.value == "execute"
        assert AgentMessageType.RESULT.value == "result"
        assert AgentMessageType.HEALTH_CHECK.value == "health_check"
        assert AgentMessageType.CANCEL.value == "cancel"
        assert AgentMessageType.ERROR.value == "error"

    def test_agent_message_serialization(self):
        msg = AgentMessage(
            type=AgentMessageType.EXECUTE,
            agent_name="test-agent",
            payload={"action": "click", "target": "button"},
        )
        assert msg.type == AgentMessageType.EXECUTE
        assert msg.agent_name == "test-agent"
        assert msg.payload["action"] == "click"
        assert msg.timestamp > 0

    def test_execute_payload(self):
        payload = AgentExecutePayload(
            action="type_text",
            parameters={"text": "hello", "target": "#input"},
            timeout_seconds=30,
        )
        assert payload.action == "type_text"
        assert payload.parameters["text"] == "hello"
        assert payload.timeout_seconds == 30

    def test_result_payload_success(self):
        result = AgentResultPayload(
            success=True,
            data={"typed": True},
            duration_ms=150.0,
        )
        assert result.success is True
        assert result.data["typed"] is True
        assert result.duration_ms == 150.0

    def test_result_payload_failure(self):
        result = AgentResultPayload(
            success=False,
            error_message="Element not found",
        )
        assert result.success is False
        assert result.error_message == "Element not found"


# ── Registry Tests ────────────────────────────────────────────────────

class TestAgentRegistry:
    """Unit tests for AgentRegistry."""

    def test_register_agent(self):
        info = agent_registry.register(name="browser", host="127.0.0.1", port=9100, capabilities=["navigate", "click"])
        assert info.name == "browser"
        assert info.port == 9100
        assert info.status == AgentStatus.REGISTERED
        assert "navigate" in info.capabilities

    def test_register_assigns_port(self):
        info = agent_registry.register(name="auto-port", host="127.0.0.1")
        assert info.port >= 9100

    def test_register_duplicate_updates(self):
        agent_registry.register(name="dup", host="127.0.0.1", port=9100)
        agent_registry.register(name="dup", host="127.0.0.1", port=9101, capabilities=["new"])
        info = agent_registry.get("dup")
        assert info.port == 9101
        assert "new" in info.capabilities

    def test_unregister_agent(self):
        agent_registry.register(name="removeme", host="127.0.0.1", port=9100)
        assert agent_registry.unregister("removeme") is True
        assert agent_registry.get("removeme") is None

    def test_unregister_nonexistent(self):
        assert agent_registry.unregister("ghost") is False

    def test_get_agent(self):
        agent_registry.register(name="finder", host="127.0.0.1", port=9100)
        found = agent_registry.get("finder")
        assert found is not None
        assert found.name == "finder"

    def test_get_nonexistent(self):
        assert agent_registry.get("nope") is None

    def test_get_by_capability(self):
        agent_registry.register(name="a1", host="127.0.0.1", port=9100, capabilities=["click", "type"])
        agent_registry.register(name="a2", host="127.0.0.1", port=9101, capabilities=["navigate"])
        result = agent_registry.get_by_capability("click")
        assert len(result) == 1
        assert result[0].name == "a1"

    def test_list_healthy(self):
        agent_registry.register(name="h1", host="127.0.0.1", port=9100)
        agent_registry.register(name="h2", host="127.0.0.1", port=9101)
        # Mark one as unhealthy via internal dict
        agent_registry._agents["h2"].status = AgentStatus.UNHEALTHY
        healthy = agent_registry.list_healthy()
        names = [a.name for a in healthy]
        assert "h1" in names
        assert "h2" not in names

    @pytest.mark.asyncio
    async def test_check_health_unreachable(self):
        """Agent on a port nothing listens on -> DEGRADED on first failure."""
        agent_registry.register(name="dead", host="127.0.0.1", port=19999)
        status = await agent_registry.check_health("dead")
        # First failure -> degraded (needs 3 consecutive for unhealthy)
        assert status in (AgentStatus.DEGRADED, AgentStatus.UNHEALTHY)

    @pytest.mark.asyncio
    async def test_check_health_nonexistent(self):
        status = await agent_registry.check_health("nonexistent")
        assert status == AgentStatus.OFFLINE


# ── Agent Routes Tests ────────────────────────────────────────────────

class TestAgentRoutes:
    """Integration tests for /api/agents endpoints."""

    @pytest.mark.asyncio
    async def test_list_agents_empty(self, client):
        resp = await client.get("/api/agents")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_register_agent_via_api(self, client):
        resp = await client.post("/api/agents", json={
            "name": "browser",
            "host": "127.0.0.1",
            "port": 9100,
            "capabilities": ["navigate", "click"],
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "browser"
        assert body["port"] == 9100
        assert body["status"] == "registered"

    @pytest.mark.asyncio
    async def test_list_after_register(self, client):
        await client.post("/api/agents", json={"name": "a1", "port": 9100})
        resp = await client.get("/api/agents")
        assert resp.status_code == 200
        agents = resp.json()
        names = [a["name"] for a in agents]
        assert "a1" in names

    @pytest.mark.asyncio
    async def test_unregister_agent(self, client):
        await client.post("/api/agents", json={"name": "bye", "port": 9100})
        resp = await client.delete("/api/agents/bye")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True

    @pytest.mark.asyncio
    async def test_unregister_nonexistent(self, client):
        resp = await client.delete("/api/agents/ghost")
        body = resp.json()
        assert body["ok"] is False

    @pytest.mark.asyncio
    async def test_health_check_all(self, client):
        resp = await client.post("/api/agents/health-check")
        assert resp.status_code == 200
        assert isinstance(resp.json()["results"], dict)

    @pytest.mark.asyncio
    async def test_single_health_check(self, client):
        await client.post("/api/agents", json={"name": "sick", "port": 19999})
        resp = await client.post("/api/agents/sick/health-check")
        assert resp.status_code == 200
        # On first failure, status will be degraded (needs 3 for unhealthy)
        assert resp.json()["status"] in ("degraded", "unhealthy")


# ── Orchestrator Tests ────────────────────────────────────────────────

class TestWorkflowOrchestrator:
    """Unit tests for the workflow orchestrator with mocked agent dispatch."""

    @pytest.fixture
    def orchestrator(self):
        from app.services.recovery_engine import (
            RecoveryAttempt,
            RecoveryEngine,
            RecoveryLevel as RLevel,
        )

        class _FastRecoveryEngine(RecoveryEngine):
            """Recovery engine that auto-skips L5 instead of blocking on user."""

            async def _l5_user_confirm(self, ctx):
                if ctx.skippable:
                    return RecoveryAttempt(
                        RLevel.L5_USER_CONFIRM, "auto-skip", True, 0,
                        details={"user_choice": "skip"},
                    )
                return RecoveryAttempt(
                    RLevel.L5_USER_CONFIRM, "auto-fail", False, 0,
                    error="Step not skippable",
                )

        return WorkflowOrchestrator(
            base_backoff_seconds=0.01,
            recovery=_FastRecoveryEngine(),
        )

    @pytest.mark.asyncio
    async def test_dispatch_to_agent_success(self, orchestrator):
        """Mock a successful agent response."""
        agent_registry.register(name="browser", host="127.0.0.1", port=9100, capabilities=["click"])

        mock_resp = httpx.Response(
            200,
            json={
                "success": True,
                "data": {"done": True},
                "duration_ms": 50,
            },
        )
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await orchestrator._dispatch_to_agent("browser", "click", {"target": "#btn"})

        assert result["success"] is True
        assert result["data"]["done"] is True

    @pytest.mark.asyncio
    async def test_dispatch_to_agent_not_found(self, orchestrator):
        """Agent not in registry -> error result."""
        result = await orchestrator._dispatch_to_agent("ghost", "click", {})
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_dispatch_to_agent_connection_error(self, orchestrator):
        """Agent unreachable -> error result (not an exception)."""
        agent_registry.register(name="dead", host="127.0.0.1", port=9100, capabilities=[])
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")):
            result = await orchestrator._dispatch_to_agent("dead", "click", {})
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_execute_step_l1_retry(self, orchestrator):
        """L1 recovery: first call fails, retry succeeds."""
        call_count = 0

        async def mock_dispatch(agent_name, action, params):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"success": False, "error": "transient", "duration_ms": 0}
            return {"success": True, "data": {}, "duration_ms": 10}

        orchestrator._dispatch_to_agent = mock_dispatch

        result = await orchestrator._execute_step_with_recovery(
            execution_id="exec-1",
            step_index=0,
            agent_name="retried",
            action="click",
            parameters={},
            skippable=False,
        )

        assert result["success"] is True
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_execute_step_l2_skip(self, orchestrator):
        """Recovery chain: all levels fail -> skippable step auto-skips at L5."""

        async def always_fail(agent_name, action, params):
            return {"success": False, "error": "persistent", "duration_ms": 0}

        orchestrator._dispatch_to_agent = always_fail

        result = await orchestrator._execute_step_with_recovery(
            execution_id="exec-1",
            step_index=0,
            agent_name="failing",
            action="click",
            parameters={},
            skippable=True,
        )

        assert result["success"] is False
        assert result.get("skipped") is True

    @pytest.mark.asyncio
    async def test_execute_step_not_skippable(self, orchestrator):
        """Recovery chain: all levels fail -> non-skippable step marked impossible."""

        async def always_fail(agent_name, action, params):
            return {"success": False, "error": "fatal", "duration_ms": 0}

        orchestrator._dispatch_to_agent = always_fail

        result = await orchestrator._execute_step_with_recovery(
            execution_id="exec-1",
            step_index=0,
            agent_name="failing",
            action="click",
            parameters={},
            skippable=False,
        )

        assert result["success"] is False
        assert result.get("skipped") is False


# ── Ollama Service Tests ──────────────────────────────────────────────

class TestOllamaService:
    """Test OllamaService methods with mocked HTTP."""

    @pytest.fixture
    def svc(self):
        from app.services.ollama_service import OllamaService
        return OllamaService()

    @pytest.mark.asyncio
    async def test_generate_success(self, svc):
        mock_resp = httpx.Response(200, json={"response": "Hello, I'm Jarvis."})
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await svc.generate("Hi")
        assert result == "Hello, I'm Jarvis."

    @pytest.mark.asyncio
    async def test_generate_connect_error(self, svc):
        from app.core.exceptions import JarvisError
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=httpx.ConnectError("refused")):
            with pytest.raises(JarvisError):
                await svc.generate("Hi")

    @pytest.mark.asyncio
    async def test_generate_timeout(self, svc):
        from app.core.exceptions import JarvisError
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=httpx.TimeoutException("timeout")):
            with pytest.raises(JarvisError):
                await svc.generate("Hi")

    @pytest.mark.asyncio
    async def test_generate_bad_status(self, svc):
        from app.core.exceptions import JarvisError
        mock_resp = httpx.Response(500, text="Internal error")
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            with pytest.raises(JarvisError):
                await svc.generate("Hi")

    @pytest.mark.asyncio
    async def test_chat_success(self, svc):
        mock_resp = httpx.Response(200, json={"message": {"role": "assistant", "content": "I can help."}})
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await svc.chat([{"role": "user", "content": "Hello"}])
        assert result == "I can help."

    @pytest.mark.asyncio
    async def test_list_models_success(self, svc):
        mock_resp = httpx.Response(200, json={"models": [{"name": "qwen2.5:3b"}, {"name": "llama3:8b"}]})
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            models = await svc.list_models()
        assert len(models) == 2
        assert models[0]["name"] == "qwen2.5:3b"

    @pytest.mark.asyncio
    async def test_list_models_failure(self, svc):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, side_effect=httpx.ConnectError("down")):
            models = await svc.list_models()
        assert models == []

    @pytest.mark.asyncio
    async def test_is_available_true(self, svc):
        mock_resp = httpx.Response(200, json={"version": "0.1.0"})
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            assert await svc.is_available() is True

    @pytest.mark.asyncio
    async def test_is_available_false(self, svc):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, side_effect=httpx.ConnectError("nope")):
            assert await svc.is_available() is False
