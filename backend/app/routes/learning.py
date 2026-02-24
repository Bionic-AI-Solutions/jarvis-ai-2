"""Learning routes — pattern learning, suggestions, confidence tuning, encryption.

Sprint 8 Stories:
  6.1: Workflow Pattern Learning
  6.2: Suggest Workflows
  6.3: Confidence Learning
  5.7: Data Encryption helpers
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.learning import (
    ConfidenceAutoAdjustRequest,
    ConfidenceCurrentResponse,
    ConfidenceHistoryListResponse,
    ConfidenceHistoryResponse,
    ConfidenceUpdateRequest,
    DecryptRequest,
    DecryptResponse,
    EncryptRequest,
    EncryptResponse,
    PatternListResponse,
    PatternRecordRequest,
    PatternResponse,
    SuggestionListResponse,
    SuggestionResponse,
)
from app.services.confidence_learning_service import ConfidenceLearningService
from app.services.encryption_service import EncryptionService
from app.services.pattern_learning_service import PatternLearningService

router = APIRouter(prefix="/api/learning", tags=["Learning"])


# ── Dependency factories ────────────────────────────────────

def _pattern_service(db: AsyncSession = Depends(get_db)) -> PatternLearningService:
    return PatternLearningService(db)


def _confidence_service(db: AsyncSession = Depends(get_db)) -> ConfidenceLearningService:
    return ConfidenceLearningService(db)


# ── Pattern Learning (6.1) ──────────────────────────────────

@router.post("/patterns", status_code=201)
async def record_pattern(
    data: PatternRecordRequest,
    svc: PatternLearningService = Depends(_pattern_service),
):
    """Record an execution pattern."""
    pattern = await svc.record_execution(
        intent=data.intent,
        steps=data.steps,
        success=data.success,
    )
    steps = json.loads(pattern.steps_json) if pattern.steps_json else []
    return PatternResponse(
        id=pattern.id,
        pattern_hash=pattern.pattern_hash,
        intent=pattern.intent,
        steps=steps,
        frequency=pattern.frequency,
        success_rate=pattern.success_rate,
        confidence=pattern.confidence,
        suggested=pattern.suggested,
        accepted=pattern.accepted,
        last_seen=pattern.last_seen,
    )


@router.get("/patterns", response_model=PatternListResponse)
async def list_patterns(
    min_frequency: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: PatternLearningService = Depends(_pattern_service),
):
    """List execution patterns."""
    patterns = await svc.list_patterns(
        min_frequency=min_frequency, limit=limit, offset=offset
    )
    items = []
    for p in patterns:
        steps = json.loads(p.steps_json) if p.steps_json else []
        items.append(
            PatternResponse(
                id=p.id,
                pattern_hash=p.pattern_hash,
                intent=p.intent,
                steps=steps,
                frequency=p.frequency,
                success_rate=p.success_rate,
                confidence=p.confidence,
                suggested=p.suggested,
                accepted=p.accepted,
                last_seen=p.last_seen,
            )
        )
    return PatternListResponse(patterns=items, total=len(items))


# ── Suggestions (6.2) ──────────────────────────────────────

@router.get("/suggestions", response_model=SuggestionListResponse)
async def get_suggestions(
    limit: int = Query(5, ge=1, le=20),
    svc: PatternLearningService = Depends(_pattern_service),
):
    """Get suggested patterns based on learned execution patterns."""
    patterns = await svc.get_suggestions(limit=limit)
    items = []
    for p in patterns:
        steps = json.loads(p.steps_json) if p.steps_json else []
        items.append(
            PatternResponse(
                id=p.id,
                pattern_hash=p.pattern_hash,
                intent=p.intent,
                steps=steps,
                frequency=p.frequency,
                success_rate=p.success_rate,
                confidence=p.confidence,
                suggested=p.suggested,
                accepted=p.accepted,
                last_seen=p.last_seen,
            )
        )
    return SuggestionListResponse(suggestions=items)


@router.post("/suggestions/{pattern_id}/accept")
async def accept_suggestion(
    pattern_id: str,
    svc: PatternLearningService = Depends(_pattern_service),
):
    """Accept a workflow suggestion."""
    log = await svc.accept_suggestion(pattern_id)
    return SuggestionResponse.model_validate(log)


@router.post("/suggestions/{pattern_id}/dismiss")
async def dismiss_suggestion(
    pattern_id: str,
    svc: PatternLearningService = Depends(_pattern_service),
):
    """Dismiss a workflow suggestion."""
    log = await svc.dismiss_suggestion(pattern_id)
    return SuggestionResponse.model_validate(log)


# ── Confidence Learning (6.3) ──────────────────────────────

@router.post("/confidence", status_code=201)
async def update_confidence(
    data: ConfidenceUpdateRequest,
    svc: ConfidenceLearningService = Depends(_confidence_service),
):
    """Record a confidence threshold change."""
    entry = await svc.record_change(
        context=data.context,
        old_value=data.old_value,
        new_value=data.new_value,
        reason=data.reason,
    )
    return ConfidenceHistoryResponse.model_validate(entry)


@router.post("/confidence/auto-adjust")
async def auto_adjust_confidence(
    data: ConfidenceAutoAdjustRequest,
    svc: ConfidenceLearningService = Depends(_confidence_service),
):
    """Auto-adjust confidence threshold based on user feedback."""
    entry = await svc.auto_adjust(
        context=data.context,
        current_value=data.current_value,
        user_accepted=data.user_accepted,
    )
    if entry is None:
        return {"adjusted": False, "message": "Threshold already at boundary."}
    return {
        "adjusted": True,
        "entry": ConfidenceHistoryResponse.model_validate(entry),
    }


@router.get("/confidence/{context}", response_model=ConfidenceCurrentResponse)
async def get_current_confidence(
    context: str,
    svc: ConfidenceLearningService = Depends(_confidence_service),
):
    """Get the current confidence threshold for a context."""
    value = await svc.get_current_threshold(context)
    return ConfidenceCurrentResponse(context=context, value=value)


@router.get("/confidence", response_model=ConfidenceHistoryListResponse)
async def list_confidence_history(
    context: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: ConfidenceLearningService = Depends(_confidence_service),
):
    """List confidence threshold change history."""
    entries = await svc.get_history(context=context, limit=limit, offset=offset)
    total = await svc.count(context=context)
    return ConfidenceHistoryListResponse(
        entries=[ConfidenceHistoryResponse.model_validate(e) for e in entries],
        total=total,
    )


# ── Encryption helpers (5.7) ───────────────────────────────

@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt_data(data: EncryptRequest):
    """Encrypt plaintext data."""
    svc = EncryptionService(data.passphrase)
    encrypted = svc.encrypt(data.plaintext)
    return EncryptResponse(encrypted=encrypted)


@router.post("/decrypt", response_model=DecryptResponse)
async def decrypt_data(data: DecryptRequest):
    """Decrypt encrypted data."""
    svc = EncryptionService(data.passphrase)
    plaintext = svc.decrypt(data.encrypted)
    return DecryptResponse(plaintext=plaintext)
