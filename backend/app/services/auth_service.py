"""Auth service — passphrase management and session authentication.

Story 5.1: Passphrase Authentication
- Set / verify passphrase (bcrypt cost 12)
- Lock / unlock system
- Session token creation (JWT)
- Brute-force lockout (3 attempts → 60s)
- Auto-lock timeout (configurable, default 30 min)
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging_config import get_logger
from app.core.security import (
    LockoutManager,
    create_access_token,
    hash_passphrase,
    lockout_manager,
    verify_passphrase,
)
from app.models.security import AuthLog
from app.models.user import User

logger = get_logger(__name__)

# In-memory lock state (single-user desktop app)
_lock_state: Dict[str, Any] = {
    "is_locked": False,
    "last_activity": time.time(),
    "auto_lock_timeout_mins": 30,
}

# Default user ID for single-user desktop app
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


class AuthService:
    """Handles passphrase authentication for the single-user system."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Passphrase Management ───────────────────────────────

    async def set_passphrase(self, passphrase: str) -> bool:
        """Set or update the system passphrase.

        Args:
            passphrase: Plaintext passphrase (8+ chars).

        Returns:
            True if successful.
        """
        hashed = hash_passphrase(passphrase)

        # Upsert the default user
        result = await self.db.execute(
            select(User).where(User.id == DEFAULT_USER_ID)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(id=DEFAULT_USER_ID, username="jarvis_user", passphrase_hash=hashed)
            self.db.add(user)
        else:
            user.passphrase_hash = hashed
            user.failed_attempts = 0

        await self.db.commit()

        # Log the event
        await self._log_event("passphrase_set")
        logger.info("passphrase_set", user_id=DEFAULT_USER_ID)
        return True

    async def has_passphrase(self) -> bool:
        """Check if a passphrase has been configured."""
        result = await self.db.execute(
            select(User).where(User.id == DEFAULT_USER_ID)
        )
        user = result.scalar_one_or_none()
        return user is not None and user.passphrase_hash is not None

    async def verify(self, passphrase: str) -> Dict[str, Any]:
        """Verify a passphrase and return auth result.

        Implements:
        - Lockout check (3 failures → 60s)
        - bcrypt verification
        - JWT token creation on success
        - Failure recording with attempt counting

        Returns:
            Dict with authenticated, token, message, attempts_remaining, etc.
        """
        settings = get_settings()

        # Check lockout
        if lockout_manager.is_locked_out(DEFAULT_USER_ID):
            remaining = lockout_manager.lockout_remaining(DEFAULT_USER_ID)
            await self._log_event("auth_locked_out")
            return {
                "authenticated": False,
                "locked_out": True,
                "lockout_remaining_seconds": remaining,
                "attempts_remaining": 0,
                "message": f"Locked out. Try again in {remaining} seconds.",
            }

        # Fetch user
        result = await self.db.execute(
            select(User).where(User.id == DEFAULT_USER_ID)
        )
        user = result.scalar_one_or_none()

        if user is None or user.passphrase_hash is None:
            return {
                "authenticated": False,
                "locked_out": False,
                "attempts_remaining": lockout_manager.max_attempts,
                "message": "No passphrase configured. Please set one first.",
            }

        # Verify
        if verify_passphrase(passphrase, user.passphrase_hash):
            # Success
            lockout_manager.clear(DEFAULT_USER_ID)
            user.failed_attempts = 0
            await self.db.commit()

            token = create_access_token({"sub": DEFAULT_USER_ID, "username": user.username})
            _lock_state["is_locked"] = False
            _lock_state["last_activity"] = time.time()

            await self._log_event("auth_success")
            logger.info("auth_success", user_id=DEFAULT_USER_ID)

            return {
                "authenticated": True,
                "token": token,
                "message": "Welcome back!",
                "attempts_remaining": lockout_manager.max_attempts,
            }
        else:
            # Failure
            locked_out = lockout_manager.record_failure(DEFAULT_USER_ID)
            user.failed_attempts = (user.failed_attempts or 0) + 1
            await self.db.commit()

            remaining_attempts = max(0, lockout_manager.max_attempts - user.failed_attempts)
            await self._log_event("auth_failure")

            if locked_out:
                lockout_secs = lockout_manager.lockout_remaining(DEFAULT_USER_ID)
                return {
                    "authenticated": False,
                    "locked_out": True,
                    "lockout_remaining_seconds": lockout_secs,
                    "attempts_remaining": 0,
                    "message": f"Authentication failed after {lockout_manager.max_attempts} attempts. Locked for {lockout_secs}s.",
                }

            return {
                "authenticated": False,
                "locked_out": False,
                "attempts_remaining": remaining_attempts,
                "message": f"Incorrect passphrase. {remaining_attempts} attempt(s) remaining.",
            }

    # ── Lock State ──────────────────────────────────────────

    def lock(self) -> None:
        """Engage the system lock."""
        _lock_state["is_locked"] = True
        logger.info("system_locked")

    def unlock(self) -> None:
        """Disengage the system lock."""
        _lock_state["is_locked"] = False
        _lock_state["last_activity"] = time.time()
        logger.info("system_unlocked")

    @staticmethod
    def get_lock_status() -> Dict[str, Any]:
        """Return current lock state."""
        return {
            "is_locked": _lock_state["is_locked"],
            "locked_out": lockout_manager.is_locked_out(DEFAULT_USER_ID),
            "lockout_remaining_seconds": lockout_manager.lockout_remaining(DEFAULT_USER_ID),
            "auto_lock_timeout_mins": _lock_state["auto_lock_timeout_mins"],
        }

    @staticmethod
    def set_auto_lock_timeout(minutes: int) -> None:
        """Configure auto-lock timeout."""
        _lock_state["auto_lock_timeout_mins"] = minutes

    def check_auto_lock(self) -> bool:
        """Check if auto-lock should engage due to inactivity.

        Returns True if lock was triggered.
        """
        timeout = _lock_state["auto_lock_timeout_mins"] * 60
        if timeout > 0 and not _lock_state["is_locked"]:
            elapsed = time.time() - _lock_state["last_activity"]
            if elapsed > timeout:
                self.lock()
                return True
        return False

    @staticmethod
    def touch_activity() -> None:
        """Record user activity (resets auto-lock timer)."""
        _lock_state["last_activity"] = time.time()

    # ── Audit Log ───────────────────────────────────────────

    async def _log_event(self, event: str, ip_address: str = "127.0.0.1") -> None:
        """Write an auth event to the audit log."""
        log = AuthLog(user_id=DEFAULT_USER_ID, event=event, ip_address=ip_address)
        self.db.add(log)
        await self.db.commit()
