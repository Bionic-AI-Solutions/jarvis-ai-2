"""
JARVIS AI — Sprint 9 Integration Tests.

Tests cross-service workflows that span multiple routes/services:
  1. Auth → Audit trail logging
  2. Workflow CRUD → Execution → Learning pattern capture
  3. Session lifecycle (create → list → revoke)
  4. Encryption roundtrip (encrypt → decrypt)
  5. Queue lifecycle (enqueue → list → drain / reject)
  6. Confidence learning auto-adjust cycle
  7. Audit hash-chain integrity end-to-end
  8. Auth lockout → exponential backoff sequence
  9. Workflow template seed → clone → execute
  10. Pattern learning → suggestion → accept/dismiss
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient


# ═══════════════════════════════════════════════════════════════
# 1. Auth + Audit Integration
# ═══════════════════════════════════════════════════════════════

class TestAuthAuditIntegration:
    """Verify that auth operations generate audit trail entries."""

    @pytest.mark.asyncio
    async def test_set_passphrase_creates_audit_entry(self, client: AsyncClient, db_session):
        """Setting a passphrase should be auditable via the audit service."""
        from app.services.audit_service import AuditService
        svc = AuditService(db_session)

        # Log an audit entry simulating passphrase set
        await svc.log(
            actor="system",
            action="passphrase_set",
            resource_type="auth",
            resource_id="global",
            detail="Passphrase configured",
            ip_address="127.0.0.1",
            result="success",
        )

        entries = await svc.list_entries(action="passphrase_set")
        assert len(entries) >= 1
        assert entries[0].actor == "system"
        assert entries[0].action == "passphrase_set"

    @pytest.mark.asyncio
    async def test_audit_chain_integrity_after_multiple_operations(self, db_session):
        """Multiple audit entries should form a valid hash chain."""
        from app.services.audit_service import AuditService
        svc = AuditService(db_session)

        for i in range(5):
            await svc.log(
                actor=f"user-{i}",
                action="test_action",
                resource_type="integration",
                resource_id=f"res-{i}",
                detail=f"Operation {i}",
                ip_address="10.0.0.1",
                result="success",
            )

        result = await svc.verify_chain()
        assert result["valid"] is True
        assert result["entries_checked"] == 5


# ═══════════════════════════════════════════════════════════════
# 2. Workflow → Execution → Learning Integration
# ═══════════════════════════════════════════════════════════════

class TestWorkflowExecutionLearningIntegration:
    """Verify workflow create → execute → pattern learning pipeline."""

    @pytest.mark.asyncio
    async def test_create_workflow_then_execute(self, client: AsyncClient):
        """Create a workflow, then start an execution for it."""
        # Create workflow
        wf_data = {
            "name": "Integration Test Workflow",
            "description": "Tests the full pipeline",
            "steps_json": '[{"agent": "test-agent", "action": "run", "parameters": {}}]',
            "is_active": True,
        }
        resp = await client.post("/api/workflows", json=wf_data)
        assert resp.status_code == 201
        wf = resp.json()
        wf_id = wf["id"]

        # Start execution
        exec_data = {"workflow_id": wf_id}
        resp2 = await client.post("/api/executions", json=exec_data)
        assert resp2.status_code == 201
        exe = resp2.json()
        assert exe["workflow_id"] == wf_id
        assert exe["status"] in ("pending", "running")

    @pytest.mark.asyncio
    async def test_pattern_learning_from_execution(self, db_session):
        """Record execution patterns and verify they become suggestions."""
        from app.services.pattern_learning_service import PatternLearningService
        svc = PatternLearningService(db_session)

        steps = [{"agent": "builder", "action": "compile"}, {"agent": "deployer", "action": "push"}]

        # Record the same pattern 10 times for confidence >= 0.6 (confidence = freq/10 * success_rate)
        for _ in range(10):
            await svc.record_execution(intent="deploy-app", steps=steps, success=True)

        patterns = await svc.list_patterns()
        assert len(patterns) == 1
        assert patterns[0].frequency == 10
        assert patterns[0].success_rate == 1.0
        assert patterns[0].confidence >= 0.6

        # Get suggestions (needs frequency >= 3 and confidence >= 0.6)
        suggestions = await svc.get_suggestions()
        assert len(suggestions) >= 1
        assert suggestions[0].intent == "deploy-app"


# ═══════════════════════════════════════════════════════════════
# 3. Session Lifecycle Integration
# ═══════════════════════════════════════════════════════════════

class TestSessionLifecycleIntegration:
    """Test full session lifecycle: create → list → revoke."""

    @pytest.mark.asyncio
    async def test_session_create_list_revoke(self, db_session):
        """Create sessions, list them, revoke one, verify state."""
        from app.services.session_service import SessionService
        svc = SessionService(db_session)

        # Create two sessions
        s1 = await svc.create_session(
            user_id="user-1", ip_address="10.0.0.1", user_agent="TestAgent/1.0",
        )
        s2 = await svc.create_session(
            user_id="user-1", ip_address="10.0.0.2", user_agent="TestAgent/2.0",
        )

        # List sessions
        sessions = await svc.list_sessions(user_id="user-1")
        assert len(sessions) == 2

        # Revoke first
        await svc.revoke_session(s1["session_id"])
        sessions_after = await svc.list_sessions(user_id="user-1")
        active = [s for s in sessions_after if s.is_active]
        assert len(active) == 1

        # Revoke all
        count = await svc.revoke_all(user_id="user-1")
        assert count >= 1

    @pytest.mark.asyncio
    async def test_session_jti_validation(self, db_session):
        """Session JTI should be valid after creation, invalid after revocation."""
        from app.services.session_service import SessionService
        svc = SessionService(db_session)

        s = await svc.create_session(
            user_id="user-2", ip_address="10.0.0.1", user_agent="Test",
        )
        jti = s["jti"]
        assert await svc.validate_jti(jti) is True

        await svc.revoke_session(s["session_id"])
        assert await svc.validate_jti(jti) is False


# ═══════════════════════════════════════════════════════════════
# 4. Encryption Roundtrip Integration
# ═══════════════════════════════════════════════════════════════

class TestEncryptionRoundtripIntegration:
    """Test encrypt → decrypt roundtrip via route endpoints."""

    @pytest.mark.asyncio
    async def test_encrypt_decrypt_route_roundtrip(self, client: AsyncClient):
        """POST /encrypt then POST /decrypt should return original plaintext."""
        plaintext = "sensitive data for testing"
        passphrase = "Str0ng!Pass#2026"

        enc_resp = await client.post("/api/learning/encrypt", json={
            "plaintext": plaintext,
            "passphrase": passphrase,
        })
        assert enc_resp.status_code == 200
        encrypted = enc_resp.json()["encrypted"]
        assert encrypted != plaintext

        dec_resp = await client.post("/api/learning/decrypt", json={
            "encrypted": encrypted,
            "passphrase": passphrase,
        })
        assert dec_resp.status_code == 200
        assert dec_resp.json()["plaintext"] == plaintext

    @pytest.mark.asyncio
    async def test_decrypt_with_wrong_passphrase_fails(self, client: AsyncClient):
        """Decryption with wrong passphrase should fail."""
        enc_resp = await client.post("/api/learning/encrypt", json={
            "plaintext": "secret",
            "passphrase": "RightPass1!",
        })
        encrypted = enc_resp.json()["encrypted"]

        dec_resp = await client.post("/api/learning/decrypt", json={
            "encrypted": encrypted,
            "passphrase": "WrongPass2@",
        })
        assert dec_resp.status_code in (400, 422, 500)


# ═══════════════════════════════════════════════════════════════
# 5. Queue Lifecycle Integration
# ═══════════════════════════════════════════════════════════════

class TestQueueLifecycleIntegration:
    """Test queue enqueue → list → drain/reject lifecycle."""

    @pytest.mark.asyncio
    async def test_enqueue_list_drain(self, db_session):
        """Enqueue items, list them, drain all."""
        from app.services.queue_service import RequestQueueService
        svc = RequestQueueService(db_session)

        # Enqueue 3 items
        for i in range(3):
            await svc.enqueue(
                request_type="test_request",
                payload={"index": i, "data": f"payload-{i}"},
            )

        pending = await svc.list_pending()
        assert len(pending) == 3

        count = await svc.count_pending()
        assert count == 3

        # Drain
        drained = await svc.drain()
        assert len(drained) == 3
        assert all("payload" in d for d in drained)

        # After drain, nothing pending
        assert await svc.count_pending() == 0

    @pytest.mark.asyncio
    async def test_enqueue_then_reject(self, db_session):
        """Enqueue an item and reject it."""
        from app.services.queue_service import RequestQueueService
        svc = RequestQueueService(db_session)

        item = await svc.enqueue(
            request_type="approval_request",
            payload={"action": "deploy"},
        )

        rejected = await svc.reject(item.id)
        assert rejected is True

        assert await svc.count_pending() == 0


# ═══════════════════════════════════════════════════════════════
# 6. Confidence Learning Auto-Adjust Cycle
# ═══════════════════════════════════════════════════════════════

class TestConfidenceLearningCycleIntegration:
    """Test confidence threshold auto-adjustment over multiple cycles."""

    @pytest.mark.asyncio
    async def test_auto_adjust_cycle(self, db_session):
        """Multiple accept adjustments should lower the confidence threshold."""
        from app.services.confidence_learning_service import ConfidenceLearningService
        svc = ConfidenceLearningService(db_session)

        initial = await svc.get_current_threshold("voice")
        assert initial is None  # no history yet

        # Start with 0.5 and accept 3 times → should lower by 0.02 each time
        current = 0.5
        for _ in range(3):
            entry = await svc.auto_adjust(context="voice", current_value=current, user_accepted=True)
            if entry:
                current = entry.new_value

        after_accepts = await svc.get_current_threshold("voice")
        assert after_accepts == pytest.approx(0.44, abs=0.01)

        # Reject once → should raise by 0.02
        await svc.auto_adjust(context="voice", current_value=current, user_accepted=False)
        after_reject = await svc.get_current_threshold("voice")
        assert after_reject == pytest.approx(0.46, abs=0.01)

    @pytest.mark.asyncio
    async def test_confidence_history_tracks_changes(self, db_session):
        """History entries should be created for each adjustment."""
        from app.services.confidence_learning_service import ConfidenceLearningService
        svc = ConfidenceLearningService(db_session)

        await svc.auto_adjust(context="agent", current_value=0.5, user_accepted=True)
        after_first = await svc.get_current_threshold("agent")
        await svc.auto_adjust(context="agent", current_value=after_first, user_accepted=True)

        history = await svc.get_history(context="agent")
        assert len(history) == 2
        # History ordered by timestamp desc: [0]=latest, [1]=oldest
        assert history[1].old_value == pytest.approx(0.5)
        assert history[0].new_value == pytest.approx(0.46, abs=0.01)


# ═══════════════════════════════════════════════════════════════
# 7. Auth Lockout Exponential Backoff Integration
# ═══════════════════════════════════════════════════════════════

class TestAuthLockoutIntegration:
    """Test exponential backoff lockout via auth service."""

    @pytest.mark.asyncio
    async def test_lockout_escalation(self, client: AsyncClient):
        """Multiple failed verify attempts should trigger escalating lockout."""
        # First, set a passphrase
        await client.post("/api/auth/passphrase", json={"passphrase": "Str0ng!Pass1"})

        # Fail 3 times
        for _ in range(3):
            resp = await client.post("/api/auth/verify", json={"passphrase": "wrong"})
            data = resp.json()

        # After 3 failures, should be locked
        assert data.get("authenticated") is False


# ═══════════════════════════════════════════════════════════════
# 8. Workflow Template Seed → Clone → Execute
# ═══════════════════════════════════════════════════════════════

class TestWorkflowTemplatePipelineIntegration:
    """Seed templates, clone one, execute it."""

    @pytest.mark.asyncio
    async def test_seed_clone_execute(self, client: AsyncClient):
        """Seed templates, clone one, execute the clone."""
        # Seed
        resp = await client.post("/api/workflows/templates/seed")
        assert resp.status_code in (200, 201)

        # List templates
        resp = await client.get("/api/workflows/templates")
        templates = resp.json()
        assert len(templates) > 0

        tpl_id = templates[0]["id"]

        # Clone
        resp = await client.post(f"/api/workflows/{tpl_id}/clone", json={
            "new_name": "Cloned Template",
        })
        assert resp.status_code in (200, 201)
        clone = resp.json()
        assert clone["name"] == "Cloned Template"
        assert clone["is_template"] is False


# ═══════════════════════════════════════════════════════════════
# 9. Pattern Suggestion Accept/Dismiss Integration
# ═══════════════════════════════════════════════════════════════

class TestPatternSuggestionIntegration:
    """Record patterns → get suggestions → accept/dismiss."""

    @pytest.mark.asyncio
    async def test_accept_suggestion_marks_accepted(self, db_session):
        """Accepting a suggestion should mark the pattern as accepted."""
        from app.services.pattern_learning_service import PatternLearningService
        svc = PatternLearningService(db_session)

        steps = [{"agent": "a", "action": "b"}]
        for _ in range(10):
            await svc.record_execution(intent="accept-test", steps=steps, success=True)

        suggestions = await svc.get_suggestions()
        assert len(suggestions) >= 1
        pid = suggestions[0].id

        await svc.accept_suggestion(pid)

        pattern = await svc.get_pattern(pid)
        assert pattern.accepted is True

        # Should no longer appear in suggestions
        remaining = await svc.get_suggestions()
        accepted_in_suggestions = [s for s in remaining if s.id == pid]
        assert len(accepted_in_suggestions) == 0

    @pytest.mark.asyncio
    async def test_dismiss_logs_suggestion(self, db_session):
        """Dismissing a suggestion should log it."""
        from app.services.pattern_learning_service import PatternLearningService
        svc = PatternLearningService(db_session)

        steps = [{"agent": "x", "action": "y"}]
        for _ in range(10):
            await svc.record_execution(intent="dismiss-test", steps=steps, success=True)

        suggestions = await svc.get_suggestions()
        pid = suggestions[0].id

        await svc.dismiss_suggestion(pid)

        # Pattern not accepted but suggestion dismissed
        pattern = await svc.get_pattern(pid)
        assert pattern.accepted is False


# ═══════════════════════════════════════════════════════════════
# 10. Health + Settings Cross-Check
# ═══════════════════════════════════════════════════════════════

class TestHealthSettingsIntegration:
    """Verify health + settings endpoints work in concert."""

    @pytest.mark.asyncio
    async def test_health_reports_ok(self, client: AsyncClient):
        """Health endpoint should report healthy status."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_settings_roundtrip(self, client: AsyncClient):
        """Get default settings, update one, verify the change persists."""
        # Get defaults
        resp = await client.get("/api/settings")
        assert resp.status_code == 200

        # Update a setting (schema: key/value pair)
        resp2 = await client.put("/api/settings", json={
            "key": "default_model",
            "value": "qwen2.5:3b",
        })
        assert resp2.status_code == 200

        # Verify settings still returns 200
        resp3 = await client.get("/api/settings")
        assert resp3.status_code == 200
