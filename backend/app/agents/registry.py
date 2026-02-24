"""Agent registry — manages registered agents and their health.

Story 2.1: Agent Registration & Discovery
Story 2.2: Agent Health Monitoring

Each agent is a lightweight REST service on localhost:91XX.
The registry tracks their endpoints, status, and capabilities.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import httpx

from app.agents.protocol import (
    AgentHealthPayload,
    AgentMessage,
    AgentMessageType,
)
from app.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AgentStatus(str, Enum):
    """Current lifecycle status of an agent."""

    REGISTERED = "registered"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


@dataclass
class AgentInfo:
    """Runtime information about a registered agent."""

    name: str
    host: str
    port: int
    capabilities: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.REGISTERED
    last_health_check: float = 0.0
    consecutive_failures: int = 0
    version: str = "unknown"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        return f"{self.base_url}/health"

    @property
    def execute_url(self) -> str:
        return f"{self.base_url}/execute"


class AgentRegistry:
    """In-memory registry of available agents.

    Provides registration, discovery, and periodic health monitoring.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, AgentInfo] = {}
        self._health_task: Optional[asyncio.Task] = None
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def agents(self) -> Dict[str, AgentInfo]:
        return dict(self._agents)

    # ── Registration ────────────────────────────────────────

    def register(
        self,
        name: str,
        host: str = "127.0.0.1",
        port: int | None = None,
        capabilities: list[str] | None = None,
    ) -> AgentInfo:
        """Register a new agent or update an existing one."""
        settings = get_settings()
        if port is None:
            port = settings.agent_base_port + len(self._agents)

        info = AgentInfo(
            name=name,
            host=host,
            port=port,
            capabilities=capabilities or [],
        )
        self._agents[name] = info
        logger.info("agent_registered", name=name, port=port, capabilities=capabilities)
        return info

    def unregister(self, name: str) -> bool:
        """Remove an agent from the registry."""
        if name in self._agents:
            del self._agents[name]
            logger.info("agent_unregistered", name=name)
            return True
        return False

    def get(self, name: str) -> AgentInfo | None:
        """Look up an agent by name."""
        return self._agents.get(name)

    def get_by_capability(self, capability: str) -> List[AgentInfo]:
        """Find all agents that support a given capability."""
        return [
            a for a in self._agents.values()
            if capability in a.capabilities and a.status in (AgentStatus.HEALTHY, AgentStatus.REGISTERED)
        ]

    def list_healthy(self) -> List[AgentInfo]:
        """Return all healthy agents."""
        return [
            a for a in self._agents.values()
            if a.status in (AgentStatus.HEALTHY, AgentStatus.REGISTERED)
        ]

    # ── Health Monitoring ───────────────────────────────────

    async def check_health(self, name: str) -> AgentStatus:
        """Probe a single agent's health endpoint."""
        info = self._agents.get(name)
        if info is None:
            return AgentStatus.OFFLINE

        settings = get_settings()
        timeout = httpx.Timeout(settings.agent_timeout_seconds)

        try:
            if self._http_client is None:
                self._http_client = httpx.AsyncClient(timeout=timeout)

            resp = await self._http_client.get(info.health_url)
            info.last_health_check = time.time()

            if resp.status_code == 200:
                data = AgentHealthPayload.model_validate(resp.json())
                info.status = AgentStatus.HEALTHY if data.healthy else AgentStatus.DEGRADED
                info.version = data.agent_version
                info.capabilities = data.capabilities or info.capabilities
                info.consecutive_failures = 0
            else:
                info.consecutive_failures += 1
                info.status = AgentStatus.DEGRADED

        except Exception as exc:
            info.consecutive_failures += 1
            if info.consecutive_failures >= 3:
                info.status = AgentStatus.UNHEALTHY
            else:
                info.status = AgentStatus.DEGRADED
            logger.warning(
                "agent_health_check_failed",
                name=name,
                error=str(exc),
                failures=info.consecutive_failures,
            )

        return info.status

    async def check_all_health(self) -> Dict[str, AgentStatus]:
        """Probe all registered agents concurrently."""
        results: Dict[str, AgentStatus] = {}
        tasks = {
            name: asyncio.create_task(self.check_health(name))
            for name in self._agents
        }
        for name, task in tasks.items():
            results[name] = await task
        return results

    async def start_health_monitor(self, interval_seconds: int = 30) -> None:
        """Start a background task that periodically checks all agents."""
        async def _loop():
            while True:
                await asyncio.sleep(interval_seconds)
                await self.check_all_health()

        self._health_task = asyncio.create_task(_loop())
        logger.info("agent_health_monitor_started", interval=interval_seconds)

    async def stop_health_monitor(self) -> None:
        """Stop the background health monitor."""
        if self._health_task:
            self._health_task.cancel()
            self._health_task = None
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        logger.info("agent_health_monitor_stopped")


# Singleton registry
agent_registry = AgentRegistry()
