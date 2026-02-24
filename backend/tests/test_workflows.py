"""Tests for /api/workflows endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_workflows_empty(client: AsyncClient):
    """Initially no workflows exist."""
    resp = await client.get("/api/workflows")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_workflow(client: AsyncClient):
    """Create a basic workflow."""
    payload = {
        "name": "Open Notepad",
        "description": "Simple test workflow",
        "steps": [
            {"agent": "app_launcher", "action": "open", "target": "notepad.exe"}
        ],
        "trigger_type": "manual",
    }
    resp = await client.post("/api/workflows", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Open Notepad"
    assert body["version"] == 1
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_create_workflow_duplicate_name(client: AsyncClient):
    """Creating two workflows with the same name should fail."""
    payload = {"name": "Duplicate Test", "steps": []}
    await client.post("/api/workflows", json=payload)
    resp = await client.post("/api/workflows", json=payload)
    assert resp.status_code == 409
    assert resp.json()["error_code"] == "WF_008"


@pytest.mark.asyncio
async def test_get_workflow(client: AsyncClient):
    """Retrieve a workflow by ID."""
    create = await client.post("/api/workflows", json={"name": "My WF", "steps": []})
    wf_id = create.json()["id"]

    resp = await client.get(f"/api/workflows/{wf_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == wf_id


@pytest.mark.asyncio
async def test_get_workflow_not_found(client: AsyncClient):
    """404 for non-existent workflow."""
    resp = await client.get("/api/workflows/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_workflow(client: AsyncClient):
    """Update a workflow and check version increments."""
    create = await client.post("/api/workflows", json={"name": "v1 WF", "steps": []})
    wf_id = create.json()["id"]

    resp = await client.put(
        f"/api/workflows/{wf_id}",
        json={"name": "v2 WF", "steps": [{"agent": "test", "action": "noop"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "v2 WF"
    assert body["version"] == 2


@pytest.mark.asyncio
async def test_update_creates_revision(client: AsyncClient):
    """Updating a workflow should create a revision snapshot."""
    create = await client.post("/api/workflows", json={"name": "Rev Test", "steps": []})
    wf_id = create.json()["id"]

    await client.put(f"/api/workflows/{wf_id}", json={"description": "updated desc"})

    resp = await client.get(f"/api/workflows/{wf_id}/revisions")
    assert resp.status_code == 200
    revisions = resp.json()
    assert len(revisions) >= 1
    assert revisions[0]["version"] == 1


@pytest.mark.asyncio
async def test_delete_workflow(client: AsyncClient):
    """Delete a workflow."""
    create = await client.post("/api/workflows", json={"name": "Delete Me WF", "steps": []})
    wf_id = create.json()["id"]

    resp = await client.delete(f"/api/workflows/{wf_id}")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    resp = await client.get(f"/api/workflows/{wf_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_workflow_missing_name(client: AsyncClient):
    """Name is required — should fail validation."""
    resp = await client.post("/api/workflows", json={"steps": []})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_workflows_active_only(client: AsyncClient):
    """Filter workflows by active status."""
    await client.post("/api/workflows", json={"name": "Active WF", "steps": []})
    resp = await client.get("/api/workflows", params={"active_only": True})
    assert resp.status_code == 200
    wfs = resp.json()
    assert all(w["is_active"] for w in wfs)
