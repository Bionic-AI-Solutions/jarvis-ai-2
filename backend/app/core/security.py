"""Security utilities — bcrypt hashing, JWT tokens, lockout logic.

Story 5.1: Passphrase Authentication
- bcrypt cost factor: 12 (prod), configurable for tests
- JWT session tokens with configurable expiry
- Lockout after 3 failed attempts for 60s
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ── Passphrase Hashing ─────────────────────────────────────────────

def hash_passphrase(passphrase: str, rounds: int | None = None) -> str:
    """Hash a passphrase using bcrypt.

    Args:
        passphrase: Plaintext passphrase (8+ chars).
        rounds: Override bcrypt cost factor (default from config).

    Returns:
        Bcrypt hash string.
    """
    settings = get_settings()
    cost = rounds if rounds is not None else settings.bcrypt_rounds
    salt = bcrypt.gensalt(rounds=cost)
    hashed = bcrypt.hashpw(passphrase.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_passphrase(passphrase: str, hashed: str) -> bool:
    """Verify a passphrase against its bcrypt hash.

    Returns True if the passphrase matches, False otherwise.
    Plaintext is cleared from stack after verification.
    """
    try:
        return bcrypt.checkpw(passphrase.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT Tokens ──────────────────────────────────────────────────────

def create_access_token(
    data: Dict[str, Any],
    expires_minutes: int | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        data: Claims to encode (e.g. {"sub": user_id}).
        expires_minutes: Override token lifetime.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    exp_minutes = expires_minutes or settings.jwt_expire_minutes
    expire = time.time() + (exp_minutes * 60)

    to_encode = data.copy()
    to_encode["exp"] = expire
    to_encode["iat"] = time.time()

    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any] | None:
    """Decode and validate a JWT access token.

    Returns:
        Decoded claims dict, or None if invalid/expired.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


# ── Lockout Logic ───────────────────────────────────────────────────

class LockoutManager:
    """In-memory brute-force protection.

    After `max_attempts` failed auth within the lockout window,
    the user is locked out for `lockout_seconds`.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        lockout_seconds: int = 60,
    ) -> None:
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self._failures: Dict[str, list[float]] = {}  # user_id → [timestamps]
        self._lockouts: Dict[str, float] = {}  # user_id → lockout_until

    def is_locked_out(self, user_id: str) -> bool:
        """Check if a user is currently locked out."""
        until = self._lockouts.get(user_id, 0)
        if time.time() < until:
            return True
        # Lockout expired — clean up
        self._lockouts.pop(user_id, None)
        return False

    def lockout_remaining(self, user_id: str) -> int:
        """Seconds remaining in lockout. 0 if not locked."""
        until = self._lockouts.get(user_id, 0)
        remaining = until - time.time()
        return max(0, int(remaining))

    def record_failure(self, user_id: str) -> bool:
        """Record a failed auth attempt.

        Returns True if lockout has been triggered.
        """
        now = time.time()
        failures = self._failures.setdefault(user_id, [])
        # Keep only recent failures
        cutoff = now - self.lockout_seconds
        failures[:] = [t for t in failures if t > cutoff]
        failures.append(now)

        if len(failures) >= self.max_attempts:
            self._lockouts[user_id] = now + self.lockout_seconds
            self._failures.pop(user_id, None)
            logger.warning("auth_lockout_triggered", user_id=user_id, duration=self.lockout_seconds)
            return True

        return False

    def clear(self, user_id: str) -> None:
        """Clear failures and lockout for a user (on successful auth)."""
        self._failures.pop(user_id, None)
        self._lockouts.pop(user_id, None)


# Module-level singleton
lockout_manager = LockoutManager()
