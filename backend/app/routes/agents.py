"""Agent management API routes — Sprint 2."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.registry import AgentInfo, AgentStatus, agent_registry

router = APIRouter(prefix="/api/agents", tags=["Agents"])


# ── Schemas ─────────────────────────────────────────────────

class AgentRegisterRequest(BaseModel):
    name: str
    host: str = "127.0.0.1"
    port: int | None = None
    capabilities: list[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    name: str
    host: str
    port: int
    capabilities: list[str]
    status: str
    version: str
    last_health_check: float


class AgentHealthResponse(BaseModel):
    results: Dict[str, str]


# ── Routes ──────────────────────────────────────────────────

@router.get("", response_model=list[AgentResponse])
async def list_agents():
    """List all registered agents."""
    return [
        AgentResponse(
            name=a.name,
            host=a.host,
            port=a.port,
            capabilities=a.capabilities,
            status=a.status.value,
            version=a.version,
            last_health_check=a.last_health_check,
        )
        for a in agent_registry.agents.values()
    ]


@router.post("", response_model=AgentResponse, status_code=201)
async def register_agent(data: AgentRegisterRequest):
    """Register a new agent in the registry."""
    info = agent_registry.register(
        name=data.name,
        host=data.host,
        port=data.port,
        capabilities=data.capabilities,
    )
    return AgentResponse(
        name=info.name,
        host=info.host,
        port=info.port,
        capabilities=info.capabilities,
        status=info.status.value,
        version=info.version,
        last_health_check=info.last_health_check,
    )


@router.delete("/{agent_name}")
async def unregister_agent(agent_name: str):
    """Remove an agent from the registry."""
    removed = agent_registry.unregister(agent_name)
    return {"ok": removed, "message": f"Agent '{agent_name}' {'removed' if removed else 'not found'}"}


@router.post("/health-check", response_model=AgentHealthResponse)
async def check_all_agents():
    """Trigger health checks on all registered agents."""
    results = await agent_registry.check_all_health()
    return AgentHealthResponse(results={k: v.value for k, v in results.items()})


@router.post("/{agent_name}/health-check")
async def check_agent_health(agent_name: str):
    """Check health of a specific agent."""
    status = await agent_registry.check_health(agent_name)
    return {"name": agent_name, "status": status.value}
