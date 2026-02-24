"""Chat service — business logic for sessions and messages."""

from __future__ import annotations

import json
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ErrorCode
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging_config import get_logger
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import (
    ChatMessageCreate,
    ChatSessionCreate,
    ChatSessionUpdate,
)

logger = get_logger(__name__)


class ChatService:
    """Encapsulates all chat-related database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Sessions ────────────────────────────────────────────

    async def list_sessions(self, *, active_only: bool = False) -> Sequence[ChatSession]:
        """Return all chat sessions, optionally filtered."""
        stmt = (
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .order_by(ChatSession.updated_at.desc())
        )
        if active_only:
            stmt = stmt.where(ChatSession.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_session(self, session_id: str) -> ChatSession:
        """Fetch a single session by ID or raise NotFoundError."""
        stmt = (
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id)
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if session is None:
            raise NotFoundError("ChatSession", session_id)
        return session

    async def create_session(self, data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(title=data.title, mode=data.mode)
        self.db.add(session)
        await self.db.flush()
        # Eagerly load messages to avoid MissingGreenlet in response serialization
        await self.db.refresh(session, attribute_names=["messages"])
        logger.info("chat_session_created", session_id=session.id, title=data.title)
        return session

    async def update_session(self, session_id: str, data: ChatSessionUpdate) -> ChatSession:
        """Update session fields."""
        session = await self.get_session(session_id)
        if data.title is not None:
            session.title = data.title
        if data.mode is not None:
            session.mode = data.mode
        await self.db.flush()
        await self.db.refresh(session, attribute_names=["messages"])
        logger.info("chat_session_updated", session_id=session_id)
        return session

    async def delete_session(self, session_id: str) -> None:
        """Soft-delete or hard-delete a chat session."""
        session = await self.get_session(session_id)
        await self.db.delete(session)
        logger.info("chat_session_deleted", session_id=session_id)

    # ── Messages ────────────────────────────────────────────

    async def add_message(self, session_id: str, data: ChatMessageCreate) -> ChatMessage:
        """Append a message to a session."""
        # Validate session exists
        session = await self.get_session(session_id)

        # Determine next sequence number
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        last_msg = result.scalar_one_or_none()
        next_seq = (last_msg.sequence + 1) if last_msg else 1

        msg = ChatMessage(
            session_id=session_id,
            role=data.role,
            content=data.content,
            sequence=next_seq,
            token_count=len(data.content.split()),  # rough estimate
        )
        self.db.add(msg)
        await self.db.flush()
        logger.info("chat_message_added", session_id=session_id, message_id=msg.id, seq=next_seq)
        return msg

    async def get_messages(self, session_id: str) -> Sequence[ChatMessage]:
        """Return all messages for a session in order."""
        # Validate session exists
        await self.get_session(session_id)
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
