"""Audit routes — immutable audit trail with hash-chain verification.

Sprint 8 Story 5.5: Audit Logging
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.audit import (
    AuditEntryResponse,
    AuditListResponse,
    AuditVerifyResponse,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["Audit"])


def _audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)


@router.get("", response_model=AuditListResponse)
async def list_audit_entries(
    actor: str | None = Query(None),
    action: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: AuditService = Depends(_audit_service),
):
    """List audit trail entries with optional filters."""
    entries = await svc.list_entries(
        actor=actor, action=action, limit=limit, offset=offset
    )
    total = await svc.count()
    return AuditListResponse(
        entries=[AuditEntryResponse.model_validate(e) for e in entries],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/verify", response_model=AuditVerifyResponse)
async def verify_audit_chain(
    svc: AuditService = Depends(_audit_service),
):
    """Verify the integrity of the audit hash chain."""
    result = await svc.verify_chain()
    return AuditVerifyResponse(**result)
