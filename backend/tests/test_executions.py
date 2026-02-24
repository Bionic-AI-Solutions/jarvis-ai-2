"""Tests for /api/executions endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _create_workflow(client: AsyncClient, name: str = "Test WF") -> str:
    """Helper: create a workflow and return its ID."""
    resp = await client.post(
        "/api/workflows",
        json={
            "name": name,
            "steps": [
                {"agent": "app_launcher", "action": "open", "target": "notepad.exe"},
                {"agent": "keyboard", "action": "type", "text": "hello"},
            ],
        },
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_executions_empty(client: AsyncClient):
    """Initially no executions exist."""
    resp = await client.get("/api/executions")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_start_execution(client: AsyncClient):
    """Start a workflow execution."""
    wf_id = await _create_workflow(client)
    resp = await client.post("/api/executions", json={"workflow_id": wf_id})
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "running"
    assert body["total_steps"] == 2
    assert body["current_step"] == 0
    assert body["workflow_id"] == wf_id


@pytest.mark.asyncio
async def test_get_execution(client: AsyncClient):
    """Get execution details."""
    wf_id = await _create_workflow(client, "Get Exec WF")
    create = await client.post("/api/executions", json={"workflow_id": wf_id})
    exe_id = create.json()["id"]

    resp = await client.get(f"/api/executions/{exe_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == exe_id


@pytest.mark.asyncio
async def test_get_execution_not_found(client: AsyncClient):
    """404 for non-existent execution."""
    resp = await client.get("/api/executions/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_execution(client: AsyncClient):
    """Cancel a running execution."""
    wf_id = await _create_workflow(client, "Cancel WF")
    create = await client.post("/api/executions", json={"workflow_id": wf_id})
    exe_id = create.json()["id"]

    resp = await client.post(
        f"/api/executions/{exe_id}/cancel",
        json={"reason": "User requested"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_completed_execution_fails(client: AsyncClient):
    """Cannot cancel an already-completed execution."""
    wf_id = await _create_workflow(client, "Complete WF")
    create = await client.post("/api/executions", json={"workflow_id": wf_id})
    exe_id = create.json()["id"]

    # Cancel first
    await client.post(f"/api/executions/{exe_id}/cancel", json={})

    # Try to cancel again — should fail
    resp = await client.post(f"/api/executions/{exe_id}/cancel", json={})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_start_execution_bad_workflow(client: AsyncClient):
    """Starting execution for a non-existent workflow returns 404."""
    resp = await client.post(
        "/api/executions",
        json={"workflow_id": "nonexistent-workflow-id"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_executions_filter_by_workflow(client: AsyncClient):
    """Filter executions by workflow_id."""
    wf_id = await _create_workflow(client, "Filter WF")
    await client.post("/api/executions", json={"workflow_id": wf_id})

    resp = await client.get("/api/executions", params={"workflow_id": wf_id})
    assert resp.status_code == 200
    exes = resp.json()
    assert len(exes) >= 1
    assert all(e["workflow_id"] == wf_id for e in exes)
