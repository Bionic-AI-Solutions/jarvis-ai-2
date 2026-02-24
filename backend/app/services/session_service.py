"""Session management service — track and manage active sessions.

Sprint 8 Story 5.6: Session Management
- Track active sessions with JTI
- List/revoke sessions
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError
from app.core.logging_config import get_logger
from app.core.security import create_access_token, decode_access_token
from app.models.security import ActiveSession

logger = get_logger(__name__)


class SessionService:
    """Manages active sessions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(
        self,
        *,
        user_id: str,
        ip_address: str = "127.0.0.1",
        user_agent: str | None = None,
    ) -> Dict[str, Any]:
        """Create a new tracked session with JTI."""
        jti = str(uuid.uuid4())

        token = create_access_token({"sub": user_id, "jti": jti})

        session = ActiveSession(
            user_id=user_id,
            token_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
        )
        self.db.add(session)
        await self.db.flush()

        logger.info("session_created", session_id=session.id, jti=jti[:8])
        return {
            "session_id": session.id,
            "token": token,
            "jti": jti,
        }

    async def list_sessions(
        self,
        user_id: str,
        *,
        active_only: bool = True,
    ) -> Sequence[ActiveSession]:
        """List sessions for a user."""
        stmt = select(ActiveSession).where(ActiveSession.user_id == user_id)
        if active_only:
            stmt = stmt.where(ActiveSession.is_active.is_(True))
        stmt = stmt.order_by(ActiveSession.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a session by marking it inactive."""
        stmt = select(ActiveSession).where(ActiveSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if session is None:
            raise JarvisError(ErrorCode.SESSION_NOT_FOUND, detail=f"Session {session_id}")
        if not session.is_active:
            raise JarvisError(ErrorCode.SESSION_ALREADY_REVOKED)
        session.is_active = False
        await self.db.flush()
        logger.info("session_revoked", session_id=session_id)
        return True

    async def revoke_all(self, user_id: str) -> int:
        """Revoke all active sessions for a user."""
        stmt = (
            update(ActiveSession)
            .where(ActiveSession.user_id == user_id, ActiveSession.is_active.is_(True))
            .values(is_active=False)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        count = result.rowcount
        logger.info("all_sessions_revoked", user_id=user_id, count=count)
        return count

    async def validate_jti(self, jti: str) -> bool:
        """Check if a JTI belongs to an active session."""
        stmt = select(ActiveSession).where(
            ActiveSession.token_jti == jti,
            ActiveSession.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if session is None:
            return False
        session.last_activity = datetime.now(timezone.utc)
        await self.db.flush()
        return True

    async def touch(self, jti: str) -> None:
        """Update last_activity for a session (heartbeat)."""
        stmt = (
            update(ActiveSession)
            .where(ActiveSession.token_jti == jti, ActiveSession.is_active.is_(True))
            .values(last_activity=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
        await self.db.flush()
