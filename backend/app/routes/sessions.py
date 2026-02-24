"""Session routes — list and revoke active sessions.

Sprint 8 Story 5.6: Session Management
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.session import (
    SessionListResponse,
    SessionResponse,
    SessionRevokeAllResponse,
    SessionRevokeResponse,
)
from app.services.auth_service import DEFAULT_USER_ID
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


def _session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    return SessionService(db)


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    active_only: bool = True,
    svc: SessionService = Depends(_session_service),
):
    """List active sessions for the current user."""
    sessions = await svc.list_sessions(DEFAULT_USER_ID, active_only=active_only)
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=len(sessions),
    )


@router.delete("/{session_id}", response_model=SessionRevokeResponse)
async def revoke_session(
    session_id: str,
    svc: SessionService = Depends(_session_service),
):
    """Revoke a specific session."""
    await svc.revoke_session(session_id)
    return SessionRevokeResponse(session_id=session_id)


@router.post("/revoke-all", response_model=SessionRevokeAllResponse)
async def revoke_all_sessions(
    svc: SessionService = Depends(_session_service),
):
    """Revoke all active sessions for the current user."""
    count = await svc.revoke_all(DEFAULT_USER_ID)
    return SessionRevokeAllResponse(revoked_count=count)
