"""Agent communication protocol — BaseAgent interface and message types.

All agents inherit from BaseAgent and implement async process().
The orchestrator calls agents directly via agent.process(input_data).

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4
"""

from __future__ import annotations

import abc
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── BaseAgent Abstract Class ────────────────────────────────


class BaseAgent(abc.ABC):
    """Abstract base class for all JARVIS agents.

    Every agent in the 13-agent mesh MUST inherit from this class
    and implement the async process() method.

    Architecture V3, Part 4: All agents share a unified interface:
      - process(input_data) → dict with status, result, context_updates
      - agent_name: unique identifier
      - agent_type: category (planning, execution, support)
      - health_check(): returns agent health status
    """

    def __init__(self, agent_name: str, agent_type: str = "general", description: str = ""):
        self._agent_name = agent_name
        self._agent_type = agent_type
        self._description = description
        self._initialized = True
        self._call_count = 0
        self._total_duration_ms = 0.0

    @property
    def agent_name(self) -> str:
        """Unique name for this agent."""
        return self._agent_name

    @property
    def agent_type(self) -> str:
        """Agent category: planning, execution, observation, safety, support."""
        return self._agent_type

    @property
    def description(self) -> str:
        """Human-readable description of what this agent does."""
        return self._description

    @abc.abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result.

        This is the ONLY method the orchestrator calls. All agent-specific
        logic must be reachable through this single entry point.

        Args:
            input_data: Dict with agent-specific input fields.

        Returns:
            Dict with at minimum:
                - status: "success" | "failure" | "needs_clarification"
                - result: agent-specific output
                - context_updates: dict of context changes for CMA
        """
        ...

    async def health_check(self) -> Dict[str, Any]:
        """Return agent health status."""
        return {
            "agent_name": self._agent_name,
            "agent_type": self._agent_type,
            "healthy": self._initialized,
            "call_count": self._call_count,
            "avg_duration_ms": (
                round(self._total_duration_ms / self._call_count, 2)
                if self._call_count > 0
                else 0.0
            ),
        }

    def _record_call(self, duration_ms: float) -> None:
        """Track call metrics."""
        self._call_count += 1
        self._total_duration_ms += duration_ms


# ── Message Types (kept for backward compat + WebSocket) ────


class AgentMessageType(str, Enum):
    """Types of messages exchanged with agents."""

    # Orchestrator → Agent
    EXECUTE = "execute"
    CANCEL = "cancel"
    HEALTH_CHECK = "health_check"

    # Agent → Orchestrator (response)
    RESULT = "result"
    ERROR = "error"
    PROGRESS = "progress"
    ACK = "ack"


class AgentMessage(BaseModel):
    """Standard envelope for orchestrator ↔ agent communication."""

    type: AgentMessageType
    agent_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class AgentExecutePayload(BaseModel):
    """Payload sent when requesting an agent to execute a step."""

    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 30
    execution_id: Optional[str] = None
    step_index: Optional[int] = None


class AgentResultPayload(BaseModel):
    """Payload returned by an agent after execution."""

    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0
    screenshot_path: Optional[str] = None
    error_message: Optional[str] = None


class AgentHealthPayload(BaseModel):
    """Payload for agent health check responses."""

    healthy: bool
    agent_version: str = "unknown"
    capabilities: list[str] = Field(default_factory=list)
    current_load: float = 0.0  # 0.0 to 1.0
