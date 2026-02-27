"""Agent Registry — Manages local BaseAgent instances for in-process dispatch.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 12
Role: Agent registration, discovery, and health monitoring
Approach: All agents run in-process; registry stores live BaseAgent instances.

This replaces the HTTP microservice approach with direct local dispatch:
  - register_instance(agent) stores a BaseAgent reference
  - get(name) returns the BaseAgent for direct .process() calls
  - health checks call agent.health_check() locally (no HTTP)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from app.core.logging_config import get_logger

if TYPE_CHECKING:
    from app.agents.protocol import BaseAgent

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
    agent_type: str = "general"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.REGISTERED
    last_health_check: float = 0.0
    consecutive_failures: int = 0
    instance: Any = None  # BaseAgent instance (Any to avoid circular import)


class AgentRegistry:
    """In-memory registry of local BaseAgent instances.

    Provides registration, discovery, and health monitoring for agents
    running in the same process (no HTTP needed).
    """

    def __init__(self) -> None:
        self._agents: Dict[str, AgentInfo] = {}
        self._health_task: Optional[asyncio.Task] = None

    @property
    def agents(self) -> Dict[str, AgentInfo]:
        return dict(self._agents)

    # ── Registration ────────────────────────────────────────

    def register_instance(self, agent: "BaseAgent", capabilities: List[str] | None = None) -> AgentInfo:
        """Register a live BaseAgent instance.
        
        Args:
            agent: A BaseAgent subclass instance (RAGAgent, SafetyAgent, etc.)
            capabilities: Optional list of capability tags for discovery
            
        Returns:
            AgentInfo record for the registered agent
        """
        info = AgentInfo(
            name=agent.agent_name,
            agent_type=agent.agent_type,
            description=agent.description,
            capabilities=capabilities or [],
            status=AgentStatus.REGISTERED,
            instance=agent,
        )
        self._agents[agent.agent_name] = info
        logger.info(
            "agent_registered",
            name=agent.agent_name,
            agent_type=agent.agent_type,
            capabilities=capabilities,
        )
        return info

    def register(
        self,
        name: str,
        host: str = "127.0.0.1",
        port: int | None = None,
        capabilities: list[str] | None = None,
    ) -> AgentInfo:
        """Legacy registration by name (backward compatibility).
        
        Prefer register_instance() for new code.
        """
        info = AgentInfo(
            name=name,
            capabilities=capabilities or [],
        )
        self._agents[name] = info
        logger.info("agent_registered_legacy", name=name, capabilities=capabilities)
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

    def get_instance(self, name: str) -> Optional["BaseAgent"]:
        """Get the live BaseAgent instance by name.
        
        Returns None if agent not registered or has no instance.
        """
        info = self._agents.get(name)
        if info and info.instance:
            return info.instance
        return None

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

    def list_all(self) -> List[Dict[str, Any]]:
        """Return summary of all registered agents."""
        return [
            {
                "name": info.name,
                "agent_type": info.agent_type,
                "status": info.status.value,
                "capabilities": info.capabilities,
                "has_instance": info.instance is not None,
            }
            for info in self._agents.values()
        ]

    # ── Health Monitoring ───────────────────────────────────

    async def check_health(self, name: str) -> AgentStatus:
        """Check a single agent's health by calling its health_check() method."""
        info = self._agents.get(name)
        if info is None:
            return AgentStatus.OFFLINE

        if info.instance is None:
            info.status = AgentStatus.OFFLINE
            return AgentStatus.OFFLINE

        try:
            health = await info.instance.health_check()
            info.last_health_check = time.time()

            if health.get("healthy", False):
                info.status = AgentStatus.HEALTHY
                info.consecutive_failures = 0
            else:
                info.status = AgentStatus.DEGRADED
                info.consecutive_failures += 1

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
        """Check health of all registered agents concurrently."""
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
        logger.info("agent_health_monitor_stopped")


# Singleton registry
agent_registry = AgentRegistry()
