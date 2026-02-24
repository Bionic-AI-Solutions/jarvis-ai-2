"""
JARVIS AI — Sprint 9 End-to-End Tests.

10+ user-journey scenarios covering the full stack.
Each test simulates a real user workflow through the HTTP API.
"""

import json
import pytest
from httpx import AsyncClient


class TestE2EUserJourney01_HealthCheck:
    """Journey: User opens app → verifies backend is alive."""

    @pytest.mark.asyncio
    async def test_health_check_returns_all_fields(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data or "timestamp" in data


class TestE2EUserJourney02_AuthFlow:
    """Journey: User sets passphrase → verifies it → checks lock status."""

    @pytest.mark.asyncio
    async def test_full_auth_flow(self, client: AsyncClient):
        # Step 1: Set passphrase
        resp = await client.post("/api/auth/passphrase", json={
            "passphrase": "MyStr0ng!Pass",
        })
        assert resp.status_code == 201
        assert resp.json()["ok"] is True

        # Step 2: Verify with correct passphrase
        resp = await client.post("/api/auth/verify", json={
            "passphrase": "MyStr0ng!Pass",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
        assert "token" in data

        # Step 3: Check status
        resp = await client.get("/api/auth/status")
        assert resp.status_code == 200


class TestE2EUserJourney03_ChatSession:
    """Journey: User creates a chat → sends a message → reads history."""

    @pytest.mark.asyncio
    async def test_chat_lifecycle(self, client: AsyncClient):
        # Create chat
        resp = await client.post("/api/chats", json={
            "title": "Test Chat Session",
        })
        assert resp.status_code == 201
        chat = resp.json()
        chat_id = chat["id"]

        # Send a message
        resp = await client.post(f"/api/chats/{chat_id}/messages", json={
            "role": "user",
            "content": "Hello JARVIS, run a test workflow",
        })
        assert resp.status_code == 201

        # Read messages
        resp = await client.get(f"/api/chats/{chat_id}/messages")
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) >= 1
        assert messages[0]["content"] == "Hello JARVIS, run a test workflow"


class TestE2EUserJourney04_WorkflowCRUD:
    """Journey: Create → Read → Update → Delete a workflow."""

    @pytest.mark.asyncio
    async def test_workflow_crud(self, client: AsyncClient):
        # Create
        resp = await client.post("/api/workflows", json={
            "name": "E2E Test Workflow",
            "description": "Full CRUD test",
            "steps_json": json.dumps([{"agent": "test", "action": "run", "parameters": {}}]),
            "is_active": True,
        })
        assert resp.status_code == 201
        wf = resp.json()
        wf_id = wf["id"]

        # Read
        resp = await client.get(f"/api/workflows/{wf_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "E2E Test Workflow"

        # Update
        resp = await client.put(f"/api/workflows/{wf_id}", json={
            "name": "Updated E2E Workflow",
            "description": "Updated description",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated E2E Workflow"

        # Delete
        resp = await client.delete(f"/api/workflows/{wf_id}")
        assert resp.status_code == 200

        # Verify deleted
        resp = await client.get(f"/api/workflows/{wf_id}")
        assert resp.status_code == 404


class TestE2EUserJourney05_WorkflowExecute:
    """Journey: Create workflow → execute → check status + logs."""

    @pytest.mark.asyncio
    async def test_create_and_execute(self, client: AsyncClient):
        # Create
        resp = await client.post("/api/workflows", json={
            "name": "Exec Workflow",
            "steps_json": json.dumps([{"agent": "a1", "action": "do", "parameters": {}}]),
            "is_active": True,
        })
        assert resp.status_code == 201
        wf_id = resp.json()["id"]

        # Execute
        resp = await client.post("/api/executions", json={
            "workflow_id": wf_id,
        })
        assert resp.status_code == 201
        exe = resp.json()
        exe_id = exe["id"]

        # Check execution
        resp = await client.get(f"/api/executions/{exe_id}")
        assert resp.status_code == 200

        # Check execution logs
        resp = await client.get(f"/api/executions/{exe_id}/logs")
        assert resp.status_code == 200


class TestE2EUserJourney06_TemplateSeedAndClone:
    """Journey: Seed templates → list → clone → verify clone."""

    @pytest.mark.asyncio
    async def test_seed_and_clone(self, client: AsyncClient):
        # Seed
        resp = await client.post("/api/workflows/templates/seed")
        assert resp.status_code in (200, 201)

        # List templates
        resp = await client.get("/api/workflows/templates")
        assert resp.status_code == 200
        templates = resp.json()
        assert len(templates) >= 1

        # Clone first template
        tpl_id = templates[0]["id"]
        resp = await client.post(f"/api/workflows/{tpl_id}/clone", json={
            "new_name": "E2E Cloned Workflow",
        })
        assert resp.status_code in (200, 201)
        clone = resp.json()
        assert clone["name"] == "E2E Cloned Workflow"
        assert clone["is_template"] is False


class TestE2EUserJourney07_EncryptDecrypt:
    """Journey: Check passphrase strength → encrypt → decrypt."""

    @pytest.mark.asyncio
    async def test_strength_encrypt_decrypt(self, client: AsyncClient):
        passphrase = "Str0ng!SecureP@ss"

        # Check strength
        resp = await client.post("/api/auth/passphrase/strength", json={
            "passphrase": passphrase,
        })
        assert resp.status_code == 200
        strength = resp.json()
        assert strength["strong"] is True

        # Encrypt
        resp = await client.post("/api/learning/encrypt", json={
            "plaintext": "JARVIS secret configuration",
            "passphrase": passphrase,
        })
        assert resp.status_code == 200
        encrypted = resp.json()["encrypted"]

        # Decrypt
        resp = await client.post("/api/learning/decrypt", json={
            "encrypted": encrypted,
            "passphrase": passphrase,
        })
        assert resp.status_code == 200
        assert resp.json()["plaintext"] == "JARVIS secret configuration"


class TestE2EUserJourney08_AuditTrail:
    """Journey: Perform operations → check audit trail → verify chain."""

    @pytest.mark.asyncio
    async def test_audit_trail_flow(self, client: AsyncClient, db_session):
        from app.services.audit_service import AuditService
        svc = AuditService(db_session)

        # Create some audit entries
        for i in range(3):
            await svc.log(
                actor="e2e-user",
                action=f"action_{i}",
                resource_type="e2e",
                resource_id=f"res-{i}",
                ip_address="127.0.0.1",
                result="success",
            )

        # List entries via route
        resp = await client.get("/api/audit?actor=e2e-user")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 3

        # Verify chain
        resp = await client.get("/api/audit/verify")
        assert resp.status_code == 200
        verify = resp.json()
        assert verify["valid"] is True


class TestE2EUserJourney09_AgentManagement:
    """Journey: Register agent → list agents → health-check."""

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, client: AsyncClient):
        # Register agent
        resp = await client.post("/api/agents", json={
            "name": "e2e-test-agent",
            "host": "http://localhost",
            "port": 9100,
            "capabilities": ["test"],
        })
        assert resp.status_code in (200, 201)

        # List agents
        resp = await client.get("/api/agents")
        assert resp.status_code == 200
        agents = resp.json()
        assert len(agents) >= 1
        assert any(a["name"] == "e2e-test-agent" for a in agents)


class TestE2EUserJourney10_LearningAndSuggestions:
    """Journey: Record pattern → get suggestions → accept."""

    @pytest.mark.asyncio
    async def test_learning_flow(self, client: AsyncClient):
        # Record patterns (10 times for confidence >= 0.6)
        for _ in range(10):
            resp = await client.post("/api/learning/patterns", json={
                "intent": "e2e-deploy",
                "steps": [{"agent": "build", "action": "compile"}, {"agent": "deploy", "action": "ship"}],
                "success": True,
            })
            assert resp.status_code in (200, 201)

        # Get suggestions
        resp = await client.get("/api/learning/suggestions")
        assert resp.status_code == 200
        data = resp.json()
        suggestions = data.get("suggestions", [])
        assert len(suggestions) >= 1

        # Accept first suggestion
        pid = suggestions[0]["id"]
        resp = await client.post(f"/api/learning/suggestions/{pid}/accept")
        assert resp.status_code == 200


class TestE2EUserJourney11_SettingsManagement:
    """Journey: Get settings → update mode."""

    @pytest.mark.asyncio
    async def test_settings_and_mode(self, client: AsyncClient):
        # Get settings
        resp = await client.get("/api/settings")
        assert resp.status_code == 200

        # Get current mode
        resp = await client.get("/api/settings/mode")
        assert resp.status_code == 200

        # Set mode to supervised
        resp = await client.post("/api/settings/mode", json={
            "mode": "supervised",
        })
        assert resp.status_code == 200
        assert resp.json()["mode"] == "supervised"


class TestE2EUserJourney12_WorkflowSearch:
    """Journey: Create workflows → search by name."""

    @pytest.mark.asyncio
    async def test_workflow_search(self, client: AsyncClient):
        # Create two workflows
        for name in ["Alpha Deployment", "Beta Testing"]:
            await client.post("/api/workflows", json={
                "name": name,
                "steps_json": json.dumps([{"agent": "a", "action": "r", "parameters": {}}]),
                "is_active": True,
            })

        # Search for 'Alpha'
        resp = await client.post("/api/workflows/search", json={
            "query": "Alpha",
        })
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) >= 1
        assert any("Alpha" in r["name"] for r in results)
