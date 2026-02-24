"""Tests for Sprint 3 — Authentication, Monitoring/Logging, CI."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from app.core.security import (
    LockoutManager,
    create_access_token,
    decode_access_token,
    hash_passphrase,
    lockout_manager,
    verify_passphrase,
)


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_lockout():
    """Reset the global lockout manager between tests."""
    lockout_manager._failures.clear()
    lockout_manager._lockouts.clear()
    yield
    lockout_manager._failures.clear()
    lockout_manager._lockouts.clear()


# Use the shared `client` fixture from conftest.py (has DB overrides)


# ── Bcrypt Hashing Tests ─────────────────────────────────────────────

class TestBcryptHashing:
    """Verify bcrypt passphrase hashing."""

    def test_hash_passphrase(self):
        hashed = hash_passphrase("my-secret-phrase", rounds=4)
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

    def test_verify_correct_passphrase(self):
        hashed = hash_passphrase("correcthorse", rounds=4)
        assert verify_passphrase("correcthorse", hashed) is True

    def test_verify_wrong_passphrase(self):
        hashed = hash_passphrase("correcthorse", rounds=4)
        assert verify_passphrase("wronghorse", hashed) is False

    def test_verify_invalid_hash(self):
        assert verify_passphrase("anything", "not-a-hash") is False

    def test_cost_factor_embedded_in_hash(self):
        hashed = hash_passphrase("test", rounds=4)
        assert "$2b$04$" in hashed

    def test_different_hashes_for_same_input(self):
        """Bcrypt uses random salt, so same input → different hashes."""
        h1 = hash_passphrase("same", rounds=4)
        h2 = hash_passphrase("same", rounds=4)
        assert h1 != h2
        assert verify_passphrase("same", h1) is True
        assert verify_passphrase("same", h2) is True


# ── JWT Token Tests ───────────────────────────────────────────────────

class TestJwtTokens:
    """Verify JWT creation and decoding."""

    def test_create_and_decode(self):
        token = create_access_token({"sub": "user-1", "role": "admin"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user-1"
        assert payload["role"] == "admin"
        assert "exp" in payload
        assert "iat" in payload

    def test_expired_token(self):
        token = create_access_token({"sub": "user-1"}, expires_minutes=-1)
        payload = decode_access_token(token)
        assert payload is None

    def test_invalid_token(self):
        payload = decode_access_token("completely.invalid.token")
        assert payload is None

    def test_tampered_token(self):
        token = create_access_token({"sub": "user-1"})
        # Tamper with the payload
        parts = token.split(".")
        parts[1] = parts[1] + "x"
        tampered = ".".join(parts)
        assert decode_access_token(tampered) is None


# ── Lockout Tests ─────────────────────────────────────────────────────

class TestLockoutManager:
    """Verify brute-force protection logic."""

    def test_not_locked_initially(self):
        mgr = LockoutManager(max_attempts=3, lockout_seconds=60)
        assert mgr.is_locked_out("user1") is False

    def test_single_failure_no_lockout(self):
        mgr = LockoutManager(max_attempts=3, lockout_seconds=60)
        locked = mgr.record_failure("user1")
        assert locked is False
        assert mgr.is_locked_out("user1") is False

    def test_lockout_after_max_attempts(self):
        mgr = LockoutManager(max_attempts=3, lockout_seconds=60)
        mgr.record_failure("user1")
        mgr.record_failure("user1")
        locked = mgr.record_failure("user1")
        assert locked is True
        assert mgr.is_locked_out("user1") is True

    def test_lockout_remaining(self):
        mgr = LockoutManager(max_attempts=3, lockout_seconds=60)
        for _ in range(3):
            mgr.record_failure("user1")
        remaining = mgr.lockout_remaining("user1")
        assert remaining > 0
        assert remaining <= 60

    def test_clear_resets_everything(self):
        mgr = LockoutManager(max_attempts=3, lockout_seconds=60)
        for _ in range(3):
            mgr.record_failure("user1")
        mgr.clear("user1")
        assert mgr.is_locked_out("user1") is False

    def test_lockout_expires(self):
        mgr = LockoutManager(max_attempts=3, lockout_seconds=1)  # 1 second lockout
        for _ in range(3):
            mgr.record_failure("user1")
        assert mgr.is_locked_out("user1") is True
        time.sleep(1.1)
        assert mgr.is_locked_out("user1") is False

    def test_lockout_remaining_when_not_locked(self):
        mgr = LockoutManager()
        assert mgr.lockout_remaining("nobody") == 0


# ── Auth Routes Tests ─────────────────────────────────────────────────

class TestAuthRoutes:
    """Integration tests for /api/auth endpoints."""

    @pytest.mark.asyncio
    async def test_status_initial(self, client):
        resp = await client.get("/api/auth/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["is_locked"] is False
        assert body["has_passphrase"] is False

    @pytest.mark.asyncio
    async def test_set_passphrase(self, client):
        resp = await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})
        assert resp.status_code == 201
        assert resp.json()["ok"] is True

    @pytest.mark.asyncio
    async def test_set_passphrase_too_short(self, client):
        resp = await client.post("/api/auth/passphrase", json={"passphrase": "short"})
        assert resp.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_verify_correct_passphrase(self, client):
        await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})
        resp = await client.post("/api/auth/verify", json={"passphrase": "my-secret-pass"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["authenticated"] is True
        assert body["token"] is not None

    @pytest.mark.asyncio
    async def test_verify_wrong_passphrase(self, client):
        await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})
        resp = await client.post("/api/auth/verify", json={"passphrase": "wrong-pass"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["authenticated"] is False

    @pytest.mark.asyncio
    async def test_verify_no_passphrase_set(self, client):
        resp = await client.post("/api/auth/verify", json={"passphrase": "anything"})
        body = resp.json()
        assert body["authenticated"] is False

    @pytest.mark.asyncio
    async def test_lock_and_unlock(self, client):
        # Set passphrase first
        await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})

        # Lock
        resp = await client.post("/api/auth/lock")
        assert resp.json()["is_locked"] is True

        # Status should show locked
        resp = await client.get("/api/auth/status")
        assert resp.json()["is_locked"] is True

        # Unlock with correct passphrase
        resp = await client.post("/api/auth/unlock", json={"passphrase": "my-secret-pass"})
        assert resp.json()["ok"] is True
        assert resp.json()["is_locked"] is False

    @pytest.mark.asyncio
    async def test_unlock_wrong_passphrase(self, client):
        await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})
        await client.post("/api/auth/lock")

        resp = await client.post("/api/auth/unlock", json={"passphrase": "wrong"})
        assert resp.json()["ok"] is False
        assert resp.json()["is_locked"] is True

    @pytest.mark.asyncio
    async def test_brute_force_lockout(self, client):
        await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})

        # 3 failed attempts
        for _ in range(3):
            await client.post("/api/auth/verify", json={"passphrase": "wrong"})

        # Status should show locked out
        resp = await client.get("/api/auth/status")
        body = resp.json()
        assert body["locked_out"] is True
        assert body["lockout_remaining_seconds"] > 0

    @pytest.mark.asyncio
    async def test_status_has_passphrase(self, client):
        await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})
        resp = await client.get("/api/auth/status")
        assert resp.json()["has_passphrase"] is True

    @pytest.mark.asyncio
    async def test_token_valid_after_auth(self, client):
        """Verify the returned JWT token is valid."""
        await client.post("/api/auth/passphrase", json={"passphrase": "my-secret-pass"})
        resp = await client.post("/api/auth/verify", json={"passphrase": "my-secret-pass"})
        token = resp.json()["token"]
        payload = decode_access_token(token)
        assert payload is not None
        assert "sub" in payload


# ── Logging Config Tests ──────────────────────────────────────────────

class TestLoggingConfig:
    """Verify logging configuration."""

    def test_setup_logging_creates_log_dir(self, tmp_path):
        from app.core.logging_config import setup_logging
        log_dir = tmp_path / "test_logs"
        setup_logging("DEBUG", log_dir=str(log_dir))
        assert log_dir.exists()
        assert (log_dir / "jarvis.log").exists()
        assert (log_dir / "jarvis_errors.log").exists()

    def test_get_logger(self):
        from app.core.logging_config import get_logger
        log = get_logger("test_module")
        assert log is not None
