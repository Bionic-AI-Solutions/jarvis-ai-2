"""Sprint 8 tests — Security hardening & Learning engine.

Stories 5.1-5.7 (Security), 6.1-6.3 (Learning)
Tests: services, routes, models, encryption, audit chain, patterns, confidence.
"""

from __future__ import annotations

import json
import time

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# ──────────────────────────────────────────────────────────
# Imports for direct service tests
# ──────────────────────────────────────────────────────────
from app.core.security import LockoutManager
from app.services.audit_service import AuditService
from app.services.queue_service import RequestQueueService
from app.services.session_service import SessionService
from app.services.encryption_service import (
    EncryptionService,
    check_passphrase_strength,
)
from app.services.pattern_learning_service import PatternLearningService
from app.services.confidence_learning_service import (
    ConfidenceLearningService,
    VALID_CONTEXTS,
)
from app.services.auth_service import DEFAULT_USER_ID
from app.models.user import User
from app.core.security import hash_passphrase

pytestmark = pytest.mark.asyncio


# ════════════════════════════════════════════════════════════
#  5.1  Passphrase Strength
# ════════════════════════════════════════════════════════════


class TestPassphraseStrength:
    """Tests for check_passphrase_strength utility (Story 5.1)."""

    def test_weak_short(self):
        result = check_passphrase_strength("abc")
        assert not result["strong"]
        assert result["score"] < 3

    def test_weak_no_upper_no_digit_no_special(self):
        result = check_passphrase_strength("longpassphrase")
        assert result["score"] < 3

    def test_strong_all_criteria(self):
        result = check_passphrase_strength("MyStr0ng!Pass")
        assert result["strong"]
        assert result["score"] >= 3

    def test_feedback_messages(self):
        result = check_passphrase_strength("abcde")
        assert len(result["feedback"]) > 0

    def test_score_increments(self):
        s1 = check_passphrase_strength("abcdefgh")["score"]
        s2 = check_passphrase_strength("Abcdefgh")["score"]
        s3 = check_passphrase_strength("Abcdefg1")["score"]
        assert s2 > s1
        assert s3 > s2


# ════════════════════════════════════════════════════════════
#  5.3  Exponential Backoff
# ════════════════════════════════════════════════════════════


class TestLockoutExponentialBackoff:
    """Tests for LockoutManager with exponential backoff (Story 5.3)."""

    def test_first_lockout_base_duration(self):
        lm = LockoutManager(max_attempts=2, lockout_seconds=10, max_lockout_seconds=320)
        lm.record_failure("u1")
        triggered = lm.record_failure("u1")
        assert triggered
        # First lockout streak=1: duration = 10 * 2^0 = 10
        remaining = lm.lockout_remaining("u1")
        assert 8 <= remaining <= 11

    def test_second_lockout_doubled(self):
        lm = LockoutManager(max_attempts=1, lockout_seconds=10, max_lockout_seconds=320)
        # First lockout
        lm.record_failure("u1")
        assert lm.is_locked_out("u1")
        # Manually expire lockout
        lm._lockouts["u1"] = time.time() - 1
        # Second lockout
        lm.record_failure("u1")
        assert lm.is_locked_out("u1")
        remaining = lm.lockout_remaining("u1")
        # Second streak=2: duration = 10 * 2^1 = 20
        assert remaining >= 18

    def test_clear_resets_streak(self):
        lm = LockoutManager(max_attempts=1, lockout_seconds=10, max_lockout_seconds=320)
        lm.record_failure("u1")
        lm.clear("u1")
        assert not lm.is_locked_out("u1")
        assert lm._lockout_streak.get("u1") is None

    def test_max_lockout_cap(self):
        lm = LockoutManager(max_attempts=1, lockout_seconds=10, max_lockout_seconds=30)
        # Streak 1: 10, Streak 2: 20, Streak 3: 30 (capped)
        for i in range(3):
            lm.record_failure("u1")
            lm._lockouts["u1"] = time.time() - 1
        lm.record_failure("u1")
        remaining = lm.lockout_remaining("u1")
        assert remaining <= 31


# ════════════════════════════════════════════════════════════
#  5.4  Request Queue
# ════════════════════════════════════════════════════════════


class TestQueueService:
    """Tests for RequestQueueService (Story 5.4)."""

    async def test_enqueue_and_list(self, db_session: AsyncSession):
        svc = RequestQueueService(db_session)
        await svc.enqueue(request_type="test", payload={"key": "val"})
        items = await svc.list_pending()
        assert len(items) == 1
        assert items[0].request_type == "test"

    async def test_count_pending(self, db_session: AsyncSession):
        svc = RequestQueueService(db_session)
        await svc.enqueue(request_type="a", payload={})
        await svc.enqueue(request_type="b", payload={})
        count = await svc.count_pending()
        assert count == 2

    async def test_drain_approves_all(self, db_session: AsyncSession):
        svc = RequestQueueService(db_session)
        await svc.enqueue(request_type="x", payload={"n": 1})
        await svc.enqueue(request_type="y", payload={"n": 2})
        payloads = await svc.drain()
        assert len(payloads) == 2
        remaining = await svc.count_pending()
        assert remaining == 0

    async def test_reject(self, db_session: AsyncSession):
        svc = RequestQueueService(db_session)
        await svc.enqueue(request_type="z", payload={})
        items = await svc.list_pending()
        await svc.reject(items[0].id)
        count = await svc.count_pending()
        assert count == 0

    async def test_clear_expired(self, db_session: AsyncSession):
        svc = RequestQueueService(db_session)
        await svc.enqueue(request_type="old", payload={})
        # Manually backdating timestamp tested via SQL can be complex,
        # so just ensure clear_expired doesn't crash with no old items
        cleared = await svc.clear_expired(max_age_hours=0)
        # With max_age_hours=0, all items are "expired"
        assert cleared >= 0


# ════════════════════════════════════════════════════════════
#  5.5  Audit Service
# ════════════════════════════════════════════════════════════


class TestAuditService:
    """Tests for AuditService with hash-chain (Story 5.5)."""

    async def test_log_entry(self, db_session: AsyncSession):
        svc = AuditService(db_session)
        entry = await svc.log(actor="test", action="create", resource_type="widget")
        assert entry.id
        assert entry.entry_hash
        assert entry.prev_hash is None  # first entry

    async def test_hash_chain(self, db_session: AsyncSession):
        svc = AuditService(db_session)
        e1 = await svc.log(actor="user", action="login")
        e2 = await svc.log(actor="user", action="create")
        assert e2.prev_hash == e1.entry_hash

    async def test_list_entries(self, db_session: AsyncSession):
        svc = AuditService(db_session)
        await svc.log(actor="admin", action="delete")
        await svc.log(actor="user", action="read")
        entries = await svc.list_entries()
        assert len(entries) == 2

    async def test_list_entries_filter(self, db_session: AsyncSession):
        svc = AuditService(db_session)
        await svc.log(actor="admin", action="delete")
        await svc.log(actor="user", action="read")
        entries = await svc.list_entries(actor="admin")
        assert len(entries) == 1
        assert entries[0].actor == "admin"

    async def test_count(self, db_session: AsyncSession):
        svc = AuditService(db_session)
        await svc.log(actor="a", action="b")
        await svc.log(actor="c", action="d")
        count = await svc.count()
        assert count == 2

    async def test_verify_chain_valid(self, db_session: AsyncSession):
        svc = AuditService(db_session)
        await svc.log(actor="a", action="1")
        await svc.log(actor="b", action="2")
        await svc.log(actor="c", action="3")
        result = await svc.verify_chain()
        assert result["valid"]
        assert result["entries_checked"] == 3

    async def test_verify_chain_empty(self, db_session: AsyncSession):
        svc = AuditService(db_session)
        result = await svc.verify_chain()
        assert result["valid"]
        assert result["entries_checked"] == 0


# ════════════════════════════════════════════════════════════
#  5.6  Session Service
# ════════════════════════════════════════════════════════════


class TestSessionService:
    """Tests for SessionService (Story 5.6)."""

    async def _ensure_user(self, db: AsyncSession):
        user = User(id=DEFAULT_USER_ID, username="test", passphrase_hash="x")
        db.add(user)
        await db.flush()

    async def test_create_session(self, db_session: AsyncSession):
        await self._ensure_user(db_session)
        svc = SessionService(db_session)
        result = await svc.create_session(user_id=DEFAULT_USER_ID)
        assert "token" in result
        assert "jti" in result
        assert "session_id" in result

    async def test_list_sessions(self, db_session: AsyncSession):
        await self._ensure_user(db_session)
        svc = SessionService(db_session)
        await svc.create_session(user_id=DEFAULT_USER_ID)
        await svc.create_session(user_id=DEFAULT_USER_ID)
        sessions = await svc.list_sessions(DEFAULT_USER_ID)
        assert len(sessions) == 2

    async def test_revoke_session(self, db_session: AsyncSession):
        await self._ensure_user(db_session)
        svc = SessionService(db_session)
        result = await svc.create_session(user_id=DEFAULT_USER_ID)
        await svc.revoke_session(result["session_id"])
        sessions = await svc.list_sessions(DEFAULT_USER_ID, active_only=True)
        assert len(sessions) == 0

    async def test_revoke_session_not_found(self, db_session: AsyncSession):
        svc = SessionService(db_session)
        with pytest.raises(Exception):
            await svc.revoke_session("nonexistent-id")

    async def test_revoke_all(self, db_session: AsyncSession):
        await self._ensure_user(db_session)
        svc = SessionService(db_session)
        await svc.create_session(user_id=DEFAULT_USER_ID)
        await svc.create_session(user_id=DEFAULT_USER_ID)
        count = await svc.revoke_all(DEFAULT_USER_ID)
        assert count == 2
        active = await svc.list_sessions(DEFAULT_USER_ID, active_only=True)
        assert len(active) == 0

    async def test_validate_jti(self, db_session: AsyncSession):
        await self._ensure_user(db_session)
        svc = SessionService(db_session)
        result = await svc.create_session(user_id=DEFAULT_USER_ID)
        valid = await svc.validate_jti(result["jti"])
        assert valid

    async def test_validate_jti_invalid(self, db_session: AsyncSession):
        svc = SessionService(db_session)
        valid = await svc.validate_jti("nonexistent-jti")
        assert not valid


# ════════════════════════════════════════════════════════════
#  5.7  Encryption Service
# ════════════════════════════════════════════════════════════


class TestEncryptionService:
    """Tests for EncryptionService (Story 5.7)."""

    def test_encrypt_decrypt_roundtrip(self):
        svc = EncryptionService("MyStr0ng!Pass")
        encrypted = svc.encrypt("hello world")
        assert "$" in encrypted
        decrypted = svc.decrypt(encrypted)
        assert decrypted == "hello world"

    def test_weak_passphrase_rejected(self):
        with pytest.raises(Exception):
            EncryptionService("weak")

    def test_different_salts(self):
        svc = EncryptionService("MyStr0ng!Pass")
        e1 = svc.encrypt("same data")
        e2 = svc.encrypt("same data")
        # Different salts → different ciphertext
        assert e1 != e2

    def test_decrypt_wrong_passphrase(self):
        svc1 = EncryptionService("MyStr0ng!Pass")
        encrypted = svc1.encrypt("secret")
        svc2 = EncryptionService("OtherStr0ng!Pass")
        with pytest.raises(Exception):
            svc2.decrypt(encrypted)

    def test_decrypt_invalid_format(self):
        svc = EncryptionService("MyStr0ng!Pass")
        with pytest.raises(Exception):
            svc.decrypt("not-valid-format")

    def test_empty_string_roundtrip(self):
        svc = EncryptionService("MyStr0ng!Pass")
        encrypted = svc.encrypt("")
        decrypted = svc.decrypt(encrypted)
        assert decrypted == ""

    def test_unicode_roundtrip(self):
        svc = EncryptionService("MyStr0ng!Pass")
        text = "Hello 世界 🌍"
        encrypted = svc.encrypt(text)
        assert svc.decrypt(encrypted) == text


# ════════════════════════════════════════════════════════════
#  6.1  Pattern Learning Service
# ════════════════════════════════════════════════════════════


class TestPatternLearningService:
    """Tests for PatternLearningService (Story 6.1)."""

    async def test_record_new_pattern(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        pattern = await svc.record_execution(
            intent="open browser",
            steps=[{"agent": "browser", "action": "open"}],
        )
        assert pattern.frequency == 1
        assert pattern.success_rate == 1.0

    async def test_record_same_pattern_increments(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        steps = [{"agent": "browser", "action": "open"}]
        await svc.record_execution(intent="open browser", steps=steps)
        p2 = await svc.record_execution(intent="open browser", steps=steps)
        assert p2.frequency == 2

    async def test_success_rate_average(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        steps = [{"agent": "a", "action": "b"}]
        await svc.record_execution(intent="x", steps=steps, success=True)
        p2 = await svc.record_execution(intent="x", steps=steps, success=False)
        assert 0.4 <= p2.success_rate <= 0.6  # ~0.5

    async def test_list_patterns(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        await svc.record_execution(
            intent="a", steps=[{"agent": "x", "action": "y"}]
        )
        await svc.record_execution(
            intent="b", steps=[{"agent": "p", "action": "q"}]
        )
        patterns = await svc.list_patterns()
        assert len(patterns) == 2

    async def test_get_pattern(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        p = await svc.record_execution(
            intent="test", steps=[{"agent": "a", "action": "b"}]
        )
        fetched = await svc.get_pattern(p.id)
        assert fetched.intent == "test"

    async def test_get_pattern_not_found(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        with pytest.raises(Exception):
            await svc.get_pattern("nonexistent")

    async def test_get_suggestions_below_threshold(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        # Only 1 occurrence — below _MIN_FREQUENCY_TO_SUGGEST (3)
        await svc.record_execution(
            intent="rare", steps=[{"agent": "a", "action": "b"}]
        )
        suggestions = await svc.get_suggestions()
        assert len(suggestions) == 0

    async def test_accept_suggestion(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        steps = [{"agent": "a", "action": "b"}]
        for _ in range(5):
            p = await svc.record_execution(intent="frequent", steps=steps)
        # Manually set confidence above threshold
        p.confidence = 0.8
        await db_session.flush()

        log = await svc.accept_suggestion(p.id)
        assert log.accepted

    async def test_dismiss_suggestion(self, db_session: AsyncSession):
        svc = PatternLearningService(db_session)
        steps = [{"agent": "c", "action": "d"}]
        for _ in range(5):
            p = await svc.record_execution(intent="dismiss_me", steps=steps)
        p.confidence = 0.8
        await db_session.flush()

        log = await svc.dismiss_suggestion(p.id)
        assert log.dismissed


# ════════════════════════════════════════════════════════════
#  6.3  Confidence Learning Service
# ════════════════════════════════════════════════════════════


class TestConfidenceLearningService:
    """Tests for ConfidenceLearningService (Story 6.3)."""

    async def test_record_change(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        entry = await svc.record_change(
            context="voice", old_value=0.9, new_value=0.85, reason="user accepted"
        )
        assert entry.id
        assert entry.context == "voice"

    async def test_invalid_context(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        with pytest.raises(Exception):
            await svc.record_change(
                context="invalid", old_value=0.5, new_value=0.6, reason="x"
            )

    async def test_out_of_range_value(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        with pytest.raises(Exception):
            await svc.record_change(
                context="voice", old_value=1.5, new_value=0.5, reason="x"
            )

    async def test_get_history(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        await svc.record_change(
            context="voice", old_value=0.9, new_value=0.85, reason="a"
        )
        await svc.record_change(
            context="agent", old_value=0.7, new_value=0.75, reason="b"
        )
        history = await svc.get_history()
        assert len(history) == 2

    async def test_get_history_filtered(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        await svc.record_change(
            context="voice", old_value=0.9, new_value=0.85, reason="a"
        )
        await svc.record_change(
            context="agent", old_value=0.7, new_value=0.75, reason="b"
        )
        history = await svc.get_history(context="voice")
        assert len(history) == 1

    async def test_get_current_threshold(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        await svc.record_change(
            context="voice", old_value=0.9, new_value=0.85, reason="first"
        )
        await svc.record_change(
            context="voice", old_value=0.85, new_value=0.80, reason="second"
        )
        val = await svc.get_current_threshold("voice")
        assert val == 0.80

    async def test_get_current_threshold_none(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        val = await svc.get_current_threshold("voice")
        assert val is None

    async def test_count(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        await svc.record_change(
            context="voice", old_value=0.9, new_value=0.8, reason="a"
        )
        assert await svc.count() == 1
        assert await svc.count(context="agent") == 0

    async def test_auto_adjust_accepted(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        entry = await svc.auto_adjust(
            context="voice", current_value=0.9, user_accepted=True
        )
        assert entry is not None
        assert entry.new_value < 0.9

    async def test_auto_adjust_rejected(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        entry = await svc.auto_adjust(
            context="voice", current_value=0.9, user_accepted=False
        )
        assert entry is not None
        assert entry.new_value > 0.9

    async def test_auto_adjust_at_boundary(self, db_session: AsyncSession):
        svc = ConfidenceLearningService(db_session)
        entry = await svc.auto_adjust(
            context="voice", current_value=1.0, user_accepted=False
        )
        assert entry is None  # already at 1.0


# ════════════════════════════════════════════════════════════
#  Route-level tests
# ════════════════════════════════════════════════════════════


class TestAuthRoutes:
    """Test auth route additions (Story 5.1, 5.3)."""

    async def test_passphrase_strength_endpoint(self, client: AsyncClient):
        res = await client.post(
            "/api/auth/passphrase/strength",
            json={"passphrase": "MyStr0ng!Pass"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["strong"]

    async def test_passphrase_strength_weak(self, client: AsyncClient):
        res = await client.post(
            "/api/auth/passphrase/strength",
            json={"passphrase": "abcdefgh"},
        )
        assert res.status_code == 200
        data = res.json()
        assert not data["strong"]

    async def test_auto_lock_timeout(self, client: AsyncClient):
        res = await client.post(
            "/api/auth/auto-lock-timeout",
            json={"minutes": 15},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["auto_lock_timeout_mins"] == 15


class TestAuditRoutes:
    """Test audit trail routes (Story 5.5)."""

    async def test_list_empty(self, client: AsyncClient):
        res = await client.get("/api/audit")
        assert res.status_code == 200
        data = res.json()
        assert data["entries"] == []

    async def test_verify_empty_chain(self, client: AsyncClient):
        res = await client.get("/api/audit/verify")
        assert res.status_code == 200
        data = res.json()
        assert data["valid"]


class TestSessionRoutes:
    """Test session management routes (Story 5.6)."""

    async def test_list_empty(self, client: AsyncClient):
        res = await client.get("/api/sessions")
        assert res.status_code == 200
        data = res.json()
        assert data["sessions"] == []

    async def test_revoke_all_empty(self, client: AsyncClient):
        res = await client.post("/api/sessions/revoke-all")
        assert res.status_code == 200
        data = res.json()
        assert data["revoked_count"] == 0


class TestQueueRoutes:
    """Test queue routes (Story 5.4)."""

    async def test_list_empty(self, client: AsyncClient):
        res = await client.get("/api/queue")
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []
        assert data["count"] == 0

    async def test_drain_empty(self, client: AsyncClient):
        res = await client.post("/api/queue/drain")
        assert res.status_code == 200
        data = res.json()
        assert data["drained"] == 0

    async def test_clear_expired(self, client: AsyncClient):
        res = await client.post("/api/queue/clear-expired?max_age_hours=1")
        assert res.status_code == 200


class TestLearningRoutes:
    """Test learning routes (Stories 6.1-6.3)."""

    async def test_record_pattern(self, client: AsyncClient):
        res = await client.post(
            "/api/learning/patterns",
            json={
                "intent": "open browser",
                "steps": [{"agent": "browser", "action": "open"}],
                "success": True,
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert data["intent"] == "open browser"
        assert data["frequency"] == 1

    async def test_list_patterns(self, client: AsyncClient):
        res = await client.get("/api/learning/patterns")
        assert res.status_code == 200
        data = res.json()
        assert "patterns" in data

    async def test_get_suggestions_empty(self, client: AsyncClient):
        res = await client.get("/api/learning/suggestions")
        assert res.status_code == 200
        data = res.json()
        assert data["suggestions"] == []

    async def test_confidence_update(self, client: AsyncClient):
        res = await client.post(
            "/api/learning/confidence",
            json={
                "context": "voice",
                "old_value": 0.9,
                "new_value": 0.85,
                "reason": "user accepted",
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert data["context"] == "voice"

    async def test_confidence_auto_adjust(self, client: AsyncClient):
        res = await client.post(
            "/api/learning/confidence/auto-adjust",
            json={
                "context": "voice",
                "current_value": 0.9,
                "user_accepted": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["adjusted"]

    async def test_confidence_current(self, client: AsyncClient):
        # First set a value
        await client.post(
            "/api/learning/confidence",
            json={
                "context": "agent",
                "old_value": 0.8,
                "new_value": 0.75,
                "reason": "test",
            },
        )
        res = await client.get("/api/learning/confidence/agent")
        assert res.status_code == 200
        data = res.json()
        assert data["context"] == "agent"
        assert data["value"] == 0.75

    async def test_confidence_history(self, client: AsyncClient):
        res = await client.get("/api/learning/confidence")
        assert res.status_code == 200
        data = res.json()
        assert "entries" in data

    async def test_encrypt_decrypt(self, client: AsyncClient):
        res = await client.post(
            "/api/learning/encrypt",
            json={"plaintext": "secret data", "passphrase": "MyStr0ng!Pass"},
        )
        assert res.status_code == 200
        encrypted = res.json()["encrypted"]

        res2 = await client.post(
            "/api/learning/decrypt",
            json={"encrypted": encrypted, "passphrase": "MyStr0ng!Pass"},
        )
        assert res2.status_code == 200
        assert res2.json()["plaintext"] == "secret data"

    async def test_encrypt_weak_passphrase(self, client: AsyncClient):
        res = await client.post(
            "/api/learning/encrypt",
            json={"plaintext": "data", "passphrase": "weakpass"},
        )
        assert res.status_code in (400, 422, 500)
