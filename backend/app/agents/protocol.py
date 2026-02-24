"""Agent communication protocol — message types and transport layer.

Agents communicate via local REST endpoints on localhost:91XX.
Each message follows a strict JSON envelope format.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


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
