"""Auth schemas — request/response models for authentication."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PassphraseSetRequest(BaseModel):
    """Set or update the system passphrase."""

    passphrase: str = Field(..., min_length=8, description="Passphrase (8+ characters)")


class PassphraseVerifyRequest(BaseModel):
    """Verify the system passphrase to unlock."""

    passphrase: str = Field(..., min_length=1, description="Passphrase to verify")


class AuthResponse(BaseModel):
    """Response after successful authentication."""

    authenticated: bool
    token: str | None = None
    message: str = ""


class LockStatusResponse(BaseModel):
    """Current lock state of the system."""

    is_locked: bool
    locked_out: bool = False
    lockout_remaining_seconds: int = 0
    has_passphrase: bool = False
    auto_lock_timeout_mins: int = 30


class AuthFailureResponse(BaseModel):
    """Response after a failed authentication attempt."""

    authenticated: bool = False
    attempts_remaining: int
    locked_out: bool = False
    lockout_remaining_seconds: int = 0
    message: str = ""


class PassphraseStrengthResponse(BaseModel):
    """Passphrase strength evaluation result."""

    strong: bool
    score: int = Field(..., ge=0, le=4)
    feedback: list[str] = Field(default_factory=list)


class AutoLockTimeoutRequest(BaseModel):
    """Request to update auto-lock timeout."""

    minutes: int = Field(..., ge=0, le=1440, description="Auto-lock timeout in minutes (0 = disabled)")

