"""Chat API routes — CRUD for sessions and messages, with agent pipeline integration.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 5
When a user sends a message, it flows through the agent pipeline:
  User message → RAG → Safety → EA → OA → Assistant response
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.pipeline import AgentPipeline
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
    """Add a user message and process it through the agent pipeline.
    
    Flow:
      1. Store user message in DB
      2. Run through agent pipeline (RAG → Safety → EA → OA)
      3. Store assistant response in DB
      4. Return the assistant response
    """
    # 1. Store the user message
    user_msg = await svc.add_message(session_id, data)

    # 2. If this is a user message, process through agent pipeline
    if data.role == "user":
        # Load chat history to provide context
        chat_history = await svc.get_messages(session_id)
        context = {
            "chat_history": [
                {"role": m.role, "content": m.content}
                for m in chat_history[:-1]  # Exclude current message (already in user_message)
            ]
        }
        
        pipeline = AgentPipeline()
        pipeline_result = await pipeline.process_message(
            user_message=data.content,
            session_id=session_id,
            context=context,
        )

        # 3. Store the assistant response with pipeline metadata
        assistant_data = ChatMessageCreate(
            content=pipeline_result["response"],
            role="assistant",
        )
        assistant_msg = await svc.add_message(session_id, assistant_data)

        # Attach pipeline metadata to the response (not persisted in DB,
        # but returned to the frontend for UI differentiation)
        response_dict = assistant_msg
        if hasattr(assistant_msg, "__dict__"):
            # SQLAlchemy model — convert to dict-like for schema
            pass

        # Build metadata dict for frontend consumption
        metadata = {
            "message_type": pipeline_result.get("message_type", "chat"),
            "pipeline_stages": pipeline_result.get("pipeline_stages", []),
            "duration_ms": pipeline_result.get("duration_ms", 0),
        }
        if pipeline_result.get("plan"):
            plan = pipeline_result["plan"]
            metadata["plan"] = {
                "steps": [
                    {
                        "action": s.get("action", ""),
                        "description": s.get("description", s.get("action", "")),
                    }
                    for s in plan.get("steps", [])
                ],
                "confidence": plan.get("confidence", 0),
            }
        if pipeline_result.get("execution"):
            ex = pipeline_result["execution"]
            metadata["execution"] = {
                "success": ex.get("success", False),
                "steps_executed": ex.get("steps_executed", 0),
                "steps_total": ex.get("steps_total", 0),
                "duration_ms": ex.get("duration_ms", 0),
                "step_results": [
                    {
                        "success": r.get("success", False),
                        "description": r.get("description", r.get("step", {}).get("action", "")),
                        "error": r.get("error"),
                        "duration_ms": r.get("duration_ms", 0),
                    }
                    for r in ex.get("step_results", [])
                ],
            }
        if pipeline_result.get("observation"):
            metadata["observation"] = pipeline_result["observation"]

        # Return response with metadata injected
        return ChatMessageResponse(
            id=assistant_msg.id if hasattr(assistant_msg, "id") else assistant_msg["id"],
            session_id=assistant_msg.session_id if hasattr(assistant_msg, "session_id") else assistant_msg["session_id"],
            role="assistant",
            content=pipeline_result["response"],
            sequence=assistant_msg.sequence if hasattr(assistant_msg, "sequence") else assistant_msg.get("sequence", 0),
            token_count=assistant_msg.token_count if hasattr(assistant_msg, "token_count") else assistant_msg.get("token_count", 0),
            created_at=assistant_msg.created_at if hasattr(assistant_msg, "created_at") else assistant_msg["created_at"],
            metadata=metadata,
        )

    # For non-user messages (system, assistant), just store as-is
    return user_msg
