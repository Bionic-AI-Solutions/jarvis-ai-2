"""
Sprint 9 — Error handling edge-case tests.

Covers: validation (422), not-found (404), business-logic conflicts,
structural edge cases (empty body, wrong method, unicode, null fields).
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Validation edge cases (422)
# ---------------------------------------------------------------------------

class TestChatValidation:
    """Pydantic validation for chat endpoints."""

    @pytest.mark.asyncio
    async def test_create_chat_invalid_mode(self, client: AsyncClient):
        resp = await client.post("/api/chats", json={"mode": "invalid"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_chat_title_too_long(self, client: AsyncClient):
        resp = await client.post("/api/chats", json={"title": "x" * 256})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_empty_content(self, client: AsyncClient):
        session = await client.post("/api/chats", json={"title": "test"})
        sid = session.json()["id"]
        resp = await client.post(
            f"/api/chats/{sid}/messages", json={"content": ""}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_content_too_long(self, client: AsyncClient):
        session = await client.post("/api/chats", json={"title": "test"})
        sid = session.json()["id"]
        resp = await client.post(
            f"/api/chats/{sid}/messages", json={"content": "x" * 10_001}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_invalid_role(self, client: AsyncClient):
        session = await client.post("/api/chats", json={"title": "test"})
        sid = session.json()["id"]
        resp = await client.post(
            f"/api/chats/{sid}/messages",
            json={"content": "hello", "role": "admin"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_update_chat_invalid_mode(self, client: AsyncClient):
        session = await client.post("/api/chats", json={"title": "test"})
        sid = session.json()["id"]
        resp = await client.put(
            f"/api/chats/{sid}", json={"mode": "unknown"}
        )
        assert resp.status_code == 422


class TestWorkflowValidation:
    """Pydantic validation for workflow endpoints."""

    @pytest.mark.asyncio
    async def test_create_workflow_empty_name(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows", json={"name": "", "steps": []}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_workflow_name_too_long(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows", json={"name": "w" * 256, "steps": []}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_workflow_invalid_trigger(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows",
            json={"name": "test", "steps": [], "trigger_type": "invalid"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_clone_empty_name(self, client: AsyncClient):
        wf = await client.post(
            "/api/workflows", json={"name": "src", "steps": []}
        )
        wid = wf.json()["id"]
        resp = await client.post(
            f"/api/workflows/{wid}/clone", json={"new_name": ""}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_export_invalid_format(self, client: AsyncClient):
        wf = await client.post(
            "/api/workflows", json={"name": "src", "steps": []}
        )
        wid = wf.json()["id"]
        resp = await client.post(
            f"/api/workflows/{wid}/export", json={"format": "xml"}
        )
        assert resp.status_code == 422


class TestAuthValidation:
    """Pydantic validation for auth endpoints."""

    @pytest.mark.asyncio
    async def test_set_passphrase_too_short(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/passphrase", json={"passphrase": "short"}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_empty_passphrase(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/verify", json={"passphrase": ""}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_auto_lock_timeout_negative(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/auto-lock-timeout", json={"minutes": -1}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_auto_lock_timeout_too_large(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/auto-lock-timeout", json={"minutes": 1441}
        )
        assert resp.status_code == 422


class TestSettingsValidation:
    """Pydantic validation for settings endpoints."""

    @pytest.mark.asyncio
    async def test_set_setting_key_too_long(self, client: AsyncClient):
        resp = await client.put(
            "/api/settings", json={"key": "k" * 101, "value": "v"}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_set_mode_invalid(self, client: AsyncClient):
        resp = await client.post(
            "/api/settings/mode", json={"mode": "turbo"}
        )
        assert resp.status_code == 422


class TestLearningValidation:
    """Pydantic validation for learning endpoints."""

    @pytest.mark.asyncio
    async def test_record_pattern_empty_intent(self, client: AsyncClient):
        resp = await client.post(
            "/api/learning/patterns", json={"intent": "", "steps": [{"a": 1}]}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_confidence_update_out_of_range(self, client: AsyncClient):
        resp = await client.post(
            "/api/learning/confidence",
            json={
                "context": "test",
                "old_value": 0.5,
                "new_value": 1.5,
                "reason": "test",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_confidence_auto_adjust_out_of_range(
        self, client: AsyncClient
    ):
        resp = await client.post(
            "/api/learning/confidence/auto-adjust",
            json={"context": "x", "current_value": -0.1, "user_accepted": True},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_encrypt_passphrase_too_short(self, client: AsyncClient):
        resp = await client.post(
            "/api/learning/encrypt",
            json={"plaintext": "secret", "passphrase": "short"},
        )
        assert resp.status_code == 422


class TestVoiceValidation:
    """Pydantic validation for voice endpoints."""

    @pytest.mark.asyncio
    async def test_silence_sample_rate_too_low(self, client: AsyncClient):
        resp = await client.post(
            "/api/voice/silence",
            json={"audio_b64": "AAAA", "sample_rate": 4000},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_silence_sample_rate_too_high(self, client: AsyncClient):
        resp = await client.post(
            "/api/voice/silence",
            json={"audio_b64": "AAAA", "sample_rate": 96000},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_voice_config_threshold_out_of_range(
        self, client: AsyncClient
    ):
        resp = await client.put(
            "/api/voice/config", json={"confidence_threshold": 2.0}
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Not-found edge cases (404)
# ---------------------------------------------------------------------------

class TestNotFound:
    """Resource-not-found for every router that takes a path param."""

    @pytest.mark.asyncio
    async def test_get_chat_not_found(self, client: AsyncClient):
        resp = await client.get("/api/chats/nonexistent-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_chat_not_found(self, client: AsyncClient):
        resp = await client.put(
            "/api/chats/nonexistent-id", json={"title": "x"}
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_chat_not_found(self, client: AsyncClient):
        resp = await client.delete("/api/chats/nonexistent-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_chat_messages_not_found(self, client: AsyncClient):
        resp = await client.get("/api/chats/nonexistent-id/messages")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_send_message_to_missing_chat(self, client: AsyncClient):
        resp = await client.post(
            "/api/chats/nonexistent-id/messages",
            json={"content": "hello"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, client: AsyncClient):
        resp = await client.get("/api/workflows/nonexistent-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_workflow_not_found(self, client: AsyncClient):
        resp = await client.put(
            "/api/workflows/nonexistent-id", json={"name": "x"}
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(self, client: AsyncClient):
        resp = await client.delete("/api/workflows/nonexistent-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_clone_workflow_not_found(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows/nonexistent-id/clone",
            json={"new_name": "copy"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows/nonexistent-id/execute", json={}
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_export_workflow_not_found(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows/nonexistent-id/export", json={"format": "json"}
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_workflow_revisions_not_found(self, client: AsyncClient):
        resp = await client.get("/api/workflows/nonexistent-id/revisions")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_execution_not_found(self, client: AsyncClient):
        resp = await client.get("/api/executions/nonexistent-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_execution_not_found(self, client: AsyncClient):
        resp = await client.post(
            "/api/executions/nonexistent-id/cancel",
            json={"reason": "abort"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_agent_not_found(self, client: AsyncClient):
        resp = await client.delete("/api/agents/nonexistent-agent")
        # Agent delete is idempotent — returns 200 even if not found
        assert resp.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_reject_queue_item_not_found(self, client: AsyncClient):
        resp = await client.post("/api/queue/999/reject")
        # Queue reject is idempotent — returns 200 even if not found
        assert resp.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_accept_suggestion_not_found(self, client: AsyncClient):
        resp = await client.post(
            "/api/learning/suggestions/999/accept"
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_dismiss_suggestion_not_found(self, client: AsyncClient):
        resp = await client.post(
            "/api/learning/suggestions/999/dismiss"
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, client: AsyncClient):
        resp = await client.delete("/api/sessions/nonexistent-jti")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_confidence_context_not_found(self, client: AsyncClient):
        """GET on non-existent context should return null or empty, not crash."""
        resp = await client.get("/api/learning/confidence/no-such-ctx")
        # Should return 200 with null threshold (graceful), or 404
        assert resp.status_code in (200, 404)


# ---------------------------------------------------------------------------
# Structural / empty-body edge cases
# ---------------------------------------------------------------------------

class TestStructuralEdgeCases:
    """Wrong methods, empty bodies, null fields, unicode, unknown fields."""

    @pytest.mark.asyncio
    async def test_wrong_method_on_health(self, client: AsyncClient):
        resp = await client.post("/health")
        assert resp.status_code == 405

    @pytest.mark.asyncio
    async def test_wrong_method_on_chats_get(self, client: AsyncClient):
        resp = await client.patch("/api/chats")
        assert resp.status_code == 405

    @pytest.mark.asyncio
    async def test_empty_body_create_workflow(self, client: AsyncClient):
        resp = await client.post("/api/workflows", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_null_required_field_workflow(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows", json={"name": None, "steps": []}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_extra_fields_ignored(self, client: AsyncClient):
        """Extra unknown fields should be silently ignored by Pydantic."""
        resp = await client.post(
            "/api/chats",
            json={"title": "ok", "totally_unknown_field": 999},
        )
        assert resp.status_code in (200, 201)
        assert "totally_unknown_field" not in resp.json()

    @pytest.mark.asyncio
    async def test_unicode_in_chat_title(self, client: AsyncClient):
        """Unicode / emoji should be accepted in string fields."""
        resp = await client.post(
            "/api/chats", json={"title": "Test \u2728\U0001F680 Session"}
        )
        assert resp.status_code in (200, 201)
        assert "\u2728" in resp.json()["title"]

    @pytest.mark.asyncio
    async def test_unicode_in_workflow_name(self, client: AsyncClient):
        resp = await client.post(
            "/api/workflows",
            json={"name": "\u00e9\u00e0\u00fc workflow", "steps": []},
        )
        assert resp.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_unicode_in_message_content(self, client: AsyncClient):
        session = await client.post("/api/chats", json={"title": "test"})
        sid = session.json()["id"]
        resp = await client.post(
            f"/api/chats/{sid}/messages",
            json={"content": "\u4f60\u597d\u4e16\u754c\U0001F600"},
        )
        assert resp.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_empty_json_body_auth(self, client: AsyncClient):
        resp = await client.post("/api/auth/passphrase", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_nonexistent_route_404(self, client: AsyncClient):
        resp = await client.get("/api/does-not-exist")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_sql_injection_in_name(self, client: AsyncClient):
        """SQL injection in string fields should be treated as plain text."""
        resp = await client.post(
            "/api/workflows",
            json={
                "name": "'; DROP TABLE workflows; --",
                "steps": [],
            },
        )
        # Should succeed (ORM parameterises queries)
        assert resp.status_code in (200, 201)
        assert "DROP TABLE" in resp.json()["name"]

    @pytest.mark.asyncio
    async def test_very_long_path_parameter(self, client: AsyncClient):
        """Very long path parameter should not crash the server."""
        resp = await client.get(f"/api/workflows/{'x' * 5000}")
        assert resp.status_code in (404, 422)


# ---------------------------------------------------------------------------
# Business-logic edge cases
# ---------------------------------------------------------------------------

class TestBusinessLogicEdgeCases:
    """Duplicate names, double actions, boundary conditions."""

    @pytest.mark.asyncio
    async def test_passphrase_boundary_exactly_8_chars(
        self, client: AsyncClient
    ):
        """Passphrase of exactly 8 chars should be accepted."""
        resp = await client.post(
            "/api/auth/passphrase", json={"passphrase": "12345678"}
        )
        # Should not return 422 — 8 chars meets min_length=8
        assert resp.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_set_passphrase_twice_overwrites(self, client: AsyncClient):
        """Setting passphrase a second time should overwrite (or fail gracefully)."""
        await client.post(
            "/api/auth/passphrase", json={"passphrase": "FirstPass123"}
        )
        resp = await client.post(
            "/api/auth/passphrase", json={"passphrase": "SecondPass456"}
        )
        # Either succeeds (overwrite) or returns a handled error
        assert resp.status_code in (200, 201, 409)

    @pytest.mark.asyncio
    async def test_verify_before_set_passphrase(self, client: AsyncClient):
        """Verifying before any passphrase is set should NOT succeed."""
        resp = await client.post(
            "/api/auth/verify", json={"passphrase": "anything123"}
        )
        # May return 200 with verified=false/None, or 401/404
        assert resp.status_code in (200, 401, 404, 400)
        if resp.status_code == 200:
            # verified should NOT be True
            assert resp.json().get("verified") is not True

    @pytest.mark.asyncio
    async def test_delete_workflow_twice(self, client: AsyncClient):
        """Deleting the same workflow twice: second should 404."""
        wf = await client.post(
            "/api/workflows", json={"name": "temp", "steps": []}
        )
        wid = wf.json()["id"]
        r1 = await client.delete(f"/api/workflows/{wid}")
        assert r1.status_code in (200, 204)
        r2 = await client.delete(f"/api/workflows/{wid}")
        assert r2.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_chat_twice(self, client: AsyncClient):
        """Deleting the same chat twice: second should 404."""
        ch = await client.post("/api/chats", json={"title": "temp"})
        cid = ch.json()["id"]
        r1 = await client.delete(f"/api/chats/{cid}")
        assert r1.status_code in (200, 204)
        r2 = await client.delete(f"/api/chats/{cid}")
        assert r2.status_code == 404

    @pytest.mark.asyncio
    async def test_update_after_delete_workflow(self, client: AsyncClient):
        """Updating a deleted workflow should 404."""
        wf = await client.post(
            "/api/workflows", json={"name": "temp", "steps": []}
        )
        wid = wf.json()["id"]
        await client.delete(f"/api/workflows/{wid}")
        resp = await client.put(
            f"/api/workflows/{wid}", json={"name": "renamed"}
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_auto_lock_boundary_zero(self, client: AsyncClient):
        """auto-lock timeout of 0 should be accepted (disable auto-lock)."""
        resp = await client.post(
            "/api/auth/auto-lock-timeout", json={"minutes": 0}
        )
        assert resp.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_auto_lock_boundary_max(self, client: AsyncClient):
        """auto-lock timeout of 1440 should be accepted (max value)."""
        resp = await client.post(
            "/api/auth/auto-lock-timeout", json={"minutes": 1440}
        )
        assert resp.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_settings_mode_roundtrip(self, client: AsyncClient):
        """Setting mode then reading it should return the same value."""
        await client.post(
            "/api/settings/mode", json={"mode": "supervised"}
        )
        resp = await client.get("/api/settings/mode")
        assert resp.status_code == 200
        assert resp.json()["mode"] == "supervised"
        # Reset to default so other tests aren't affected (global state)
        await client.post("/api/settings/mode", json={"mode": "auto"})

    @pytest.mark.asyncio
    async def test_workflow_search_no_results(self, client: AsyncClient):
        """Search with a query that matches nothing should return empty list."""
        resp = await client.post(
            "/api/workflows/search",
            json={"query": "zzz_no_match_xyz_123"},
        )
        assert resp.status_code == 200
        body = resp.json()
        # Should be a list (possibly wrapped)
        results = body if isinstance(body, list) else body.get("results", body.get("workflows", []))
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_confidence_boundary_zero(self, client: AsyncClient):
        """Confidence value of exactly 0.0 should pass schema validation."""
        resp = await client.post(
            "/api/learning/confidence",
            json={
                "context": "boundary",
                "old_value": 0.0,
                "new_value": 0.0,
                "reason": "testing boundary",
            },
        )
        # 200 if accepted, 400 if business rule rejects same-value update
        assert resp.status_code in (200, 400)
        # Must NOT be 422 (schema validation should pass)
        assert resp.status_code != 422

    @pytest.mark.asyncio
    async def test_confidence_boundary_one(self, client: AsyncClient):
        """Confidence value of exactly 1.0 should pass schema validation."""
        resp = await client.post(
            "/api/learning/confidence",
            json={
                "context": "boundary",
                "old_value": 1.0,
                "new_value": 1.0,
                "reason": "testing boundary",
            },
        )
        # 200 if accepted, 400 if business rule rejects same-value update
        assert resp.status_code in (200, 400)
        # Must NOT be 422 (schema validation should pass)
        assert resp.status_code != 422

    @pytest.mark.asyncio
    async def test_decrypt_with_wrong_passphrase(self, client: AsyncClient):
        """Decrypting with wrong passphrase should fail, not crash."""
        enc = await client.post(
            "/api/learning/encrypt",
            json={"plaintext": "secret data", "passphrase": "CorrectPass1"},
        )
        assert enc.status_code == 200
        encrypted = enc.json()["encrypted"]

        resp = await client.post(
            "/api/learning/decrypt",
            json={"encrypted": encrypted, "passphrase": "WrongPass99"},
        )
        # Should return an error (400/500) not crash
        assert resp.status_code in (400, 500)

    @pytest.mark.asyncio
    async def test_decrypt_corrupt_data(self, client: AsyncClient):
        """Decrypting garbage should return error, not crash."""
        resp = await client.post(
            "/api/learning/decrypt",
            json={"encrypted": "not-valid-base64-ciphertext", "passphrase": "SomePass123"},
        )
        assert resp.status_code in (400, 500)

    @pytest.mark.asyncio
    async def test_empty_workflow_list(self, client: AsyncClient):
        """Listing workflows when none exist should return empty list."""
        resp = await client.get("/api/workflows")
        assert resp.status_code == 200
        body = resp.json()
        results = body if isinstance(body, list) else body.get("workflows", [])
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_empty_chat_list(self, client: AsyncClient):
        """Listing chats when none exist should return empty list."""
        resp = await client.get("/api/chats")
        assert resp.status_code == 200
        body = resp.json()
        results = body if isinstance(body, list) else body.get("sessions", [])
        assert len(results) == 0
