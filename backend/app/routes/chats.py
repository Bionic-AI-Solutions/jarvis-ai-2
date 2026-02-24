"""Chat API routes — CRUD for sessions and messages."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionListItem,
    ChatSessionResponse,
    ChatSessionUpdate,
)
from app.schemas.common import SuccessResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chats", tags=["Chats"])


def _svc(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)


# ── Sessions ────────────────────────────────────────────────

@router.get("", response_model=list[ChatSessionListItem])
async def list_sessions(
    active_only: bool = Query(False),
    svc: ChatService = Depends(_svc),
):
    """List all chat sessions."""
    return await svc.list_sessions(active_only=active_only)


@router.post("", response_model=ChatSessionResponse, status_code=201)
async def create_session(
    data: ChatSessionCreate,
    svc: ChatService = Depends(_svc),
):
    """Create a new chat session."""
    return await svc.create_session(data)


@router.get("/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: str,
    svc: ChatService = Depends(_svc),
):
    """Get a chat session by ID, including messages."""
    return await svc.get_session(session_id)


@router.put("/{session_id}", response_model=ChatSessionResponse)
async def update_session(
    session_id: str,
    data: ChatSessionUpdate,
    svc: ChatService = Depends(_svc),
):
    """Update a chat session."""
    return await svc.update_session(session_id, data)


@router.delete("/{session_id}", response_model=SuccessResponse)
async def delete_session(
    session_id: str,
    svc: ChatService = Depends(_svc),
):
    """Delete a chat session and all its messages."""
    await svc.delete_session(session_id)
    return SuccessResponse(message=f"Session {session_id} deleted")


# ── Messages ────────────────────────────────────────────────

@router.get("/{session_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(
    session_id: str,
    svc: ChatService = Depends(_svc),
):
    """List all messages in a session."""
    return await svc.get_messages(session_id)


@router.post("/{session_id}/messages", response_model=ChatMessageResponse, status_code=201)
async def create_message(
    session_id: str,
    data: ChatMessageCreate,
    svc: ChatService = Depends(_svc),
):
    """Add a message to a chat session."""
    return await svc.add_message(session_id, data)
