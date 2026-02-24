"""Additional coverage tests for Sprint 2 — edge cases and uncovered paths."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.agents.registry import AgentStatus, agent_registry
from app.services.ollama_service import OllamaService
from app.core.exceptions import JarvisError


@pytest.fixture(autouse=True)
def clean_registry():
    agent_registry._agents.clear()
    yield
    agent_registry._agents.clear()


class TestRegistryEdgeCases:
    """Extra coverage for registry paths."""

    @pytest.mark.asyncio
    async def test_check_all_health_concurrent(self):
        """Register multiple agents, check all → all degraded (unreachable)."""
        for i in range(3):
            agent_registry.register(name=f"agent-{i}", host="127.0.0.1", port=19990 + i)

        results = await agent_registry.check_all_health()
        assert len(results) == 3
        for status in results.values():
            assert status in (AgentStatus.DEGRADED, AgentStatus.UNHEALTHY)

    @pytest.mark.asyncio
    async def test_health_degraded_to_unhealthy_after_3_failures(self):
        """After 3 consecutive failures, agent becomes UNHEALTHY."""
        agent_registry.register(name="flaky", host="127.0.0.1", port=19999)

        for _ in range(3):
            await agent_registry.check_health("flaky")

        status = await agent_registry.check_health("flaky")
        assert status == AgentStatus.UNHEALTHY

    def test_agent_info_urls(self):
        info = agent_registry.register(name="url-test", host="127.0.0.1", port=9100)
        assert info.base_url == "http://127.0.0.1:9100"
        assert info.health_url == "http://127.0.0.1:9100/health"
        assert info.execute_url == "http://127.0.0.1:9100/execute"


class TestOllamaServiceChat:
    """Extra coverage for Ollama chat paths."""

    @pytest.fixture
    def svc(self):
        return OllamaService()

    @pytest.mark.asyncio
    async def test_chat_connect_error(self, svc):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=httpx.ConnectError("down")):
            with pytest.raises(JarvisError):
                await svc.chat([{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_chat_timeout(self, svc):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=httpx.TimeoutException("slow")):
            with pytest.raises(JarvisError):
                await svc.chat([{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_chat_bad_status(self, svc):
        mock_resp = httpx.Response(503, text="Service Unavailable")
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            with pytest.raises(JarvisError):
                await svc.chat([{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_generate_custom_params(self, svc):
        """Generate with custom model, system prompt, temperature, max_tokens."""
        mock_resp = httpx.Response(200, json={"response": "custom output"})
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp) as mock_post:
            result = await svc.generate(
                "test", model="llama3:8b", system="You are a test bot",
                temperature=0.3, max_tokens=256,
            )
        assert result == "custom output"
