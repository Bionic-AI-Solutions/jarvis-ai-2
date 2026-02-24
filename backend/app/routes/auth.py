"""Auth routes — passphrase setup, lock/unlock, verification, strength check.

Story 5.1: Passphrase Authentication
Story 5.3: Brute-Force (exponential backoff)
Story 5.7: Data Encryption helpers
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    AuthResponse,
    AutoLockTimeoutRequest,
    LockStatusResponse,
    PassphraseSetRequest,
    PassphraseStrengthResponse,
    PassphraseVerifyRequest,
)
from app.services.auth_service import AuthService
from app.services.encryption_service import check_passphrase_strength

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ── Helpers ─────────────────────────────────────────────────

def _auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


# ── Routes ──────────────────────────────────────────────────

@router.post("/passphrase", status_code=201)
async def set_passphrase(
    data: PassphraseSetRequest,
    svc: AuthService = Depends(_auth_service),
):
    """Set or update the system passphrase."""
    await svc.set_passphrase(data.passphrase)
    return {"ok": True, "message": "Passphrase set successfully."}


@router.post("/verify", response_model=AuthResponse)
async def verify_passphrase(
    data: PassphraseVerifyRequest,
    svc: AuthService = Depends(_auth_service),
):
    """Verify passphrase and receive a session token."""
    result = await svc.verify(data.passphrase)
    return AuthResponse(
        authenticated=result["authenticated"],
        token=result.get("token"),
        message=result.get("message", ""),
    )


@router.get("/status", response_model=LockStatusResponse)
async def lock_status(svc: AuthService = Depends(_auth_service)):
    """Get current lock state."""
    status = svc.get_lock_status()
    has_pp = await svc.has_passphrase()
    return LockStatusResponse(
        is_locked=status["is_locked"],
        locked_out=status["locked_out"],
        lockout_remaining_seconds=status["lockout_remaining_seconds"],
        has_passphrase=has_pp,
        auto_lock_timeout_mins=status["auto_lock_timeout_mins"],
    )


@router.post("/lock")
async def lock_system(svc: AuthService = Depends(_auth_service)):
    """Engage the system lock."""
    svc.lock()
    return {"ok": True, "is_locked": True}


@router.post("/unlock")
async def unlock_system(
    data: PassphraseVerifyRequest,
    svc: AuthService = Depends(_auth_service),
):
    """Unlock the system by verifying the passphrase."""
    result = await svc.verify(data.passphrase)
    if result["authenticated"]:
        svc.unlock()
        return {
            "ok": True,
            "is_locked": False,
            "token": result.get("token"),
            "message": "Welcome back!",
        }
    return {
        "ok": False,
        "is_locked": True,
        "message": result.get("message", "Authentication failed."),
        "attempts_remaining": result.get("attempts_remaining", 0),
        "locked_out": result.get("locked_out", False),
    }


@router.post("/passphrase/strength", response_model=PassphraseStrengthResponse)
async def check_strength(data: PassphraseSetRequest):
    """Check passphrase strength without setting it."""
    result = check_passphrase_strength(data.passphrase)
    return PassphraseStrengthResponse(**result)


@router.post("/auto-lock-timeout")
async def set_auto_lock_timeout(
    data: AutoLockTimeoutRequest,
    svc: AuthService = Depends(_auth_service),
):
    """Configure auto-lock timeout (in minutes, 0=disabled)."""
    svc.set_auto_lock_timeout(data.minutes)
    return {"ok": True, "auto_lock_timeout_mins": data.minutes}
