"""Audit service — immutable audit trail with hash-chain verification.

Sprint 8 Story 5.5: Audit Logging
- Log all actions: Who, What, When, Result
- Immutable audit trail (hash-chain)
- Verify integrity of audit chain
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError
from app.core.logging_config import get_logger
from app.models.security import AuditEntry

logger = get_logger(__name__)


class AuditService:
    """Immutable audit trail with hash-chain integrity."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _compute_hash(
        actor: str,
        action: str,
        resource_type: str | None,
        resource_id: str | None,
        detail: str | None,
        result: str,
        timestamp: str,
        prev_hash: str | None,
    ) -> str:
        """Compute SHA-256 hash of an audit entry."""
        payload = json.dumps(
            {
                "actor": actor,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "detail": detail,
                "result": result,
                "timestamp": timestamp,
                "prev_hash": prev_hash or "",
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _format_ts(dt: datetime) -> str:
        """Normalize datetime to a consistent string format for hashing."""
        # Always format as UTC with microseconds to avoid SQLite round-trip issues
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")

    async def _get_last_hash(self) -> str | None:
        """Retrieve the hash of the most recent audit entry."""
        stmt = (
            select(AuditEntry.entry_hash)
            .order_by(AuditEntry.timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return row

    async def log(
        self,
        *,
        actor: str = "system",
        action: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        detail: str | None = None,
        ip_address: str = "127.0.0.1",
        result: str = "success",
    ) -> AuditEntry:
        """Create a new immutable audit entry."""
        prev_hash = await self._get_last_hash()
        now = datetime.now(timezone.utc)
        ts_str = self._format_ts(now)

        entry_hash = self._compute_hash(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            result=result,
            timestamp=ts_str,
            prev_hash=prev_hash,
        )

        entry = AuditEntry(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip_address,
            result=result,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            timestamp=now,
        )
        self.db.add(entry)
        await self.db.flush()

        logger.info(
            "audit_entry_created",
            action=action,
            actor=actor,
            entry_hash=entry_hash[:12],
        )
        return entry

    async def list_entries(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        actor: str | None = None,
        action: str | None = None,
    ) -> Sequence[AuditEntry]:
        """List audit entries with optional filtering."""
        stmt = select(AuditEntry).order_by(AuditEntry.timestamp.desc())
        if actor:
            stmt = stmt.where(AuditEntry.actor == actor)
        if action:
            stmt = stmt.where(AuditEntry.action == action)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Return total number of audit entries."""
        result = await self.db.execute(select(func.count(AuditEntry.id)))
        return result.scalar_one()

    async def verify_chain(self, *, limit: int = 100) -> Dict[str, Any]:
        """Verify the integrity of the audit hash chain.

        Returns a dict with 'valid', 'entries_checked', 'first_broken_id', 'message'.
        """
        stmt = (
            select(AuditEntry)
            .order_by(AuditEntry.timestamp.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        entries = list(result.scalars().all())

        if not entries:
            return {
                "valid": True,
                "entries_checked": 0,
                "first_broken_id": None,
                "message": "No entries to verify.",
            }

        for i, entry in enumerate(entries):
            expected_prev = entries[i - 1].entry_hash if i > 0 else None
            if entry.prev_hash != expected_prev:
                logger.warning(
                    "audit_chain_broken",
                    index=i,
                    entry_id=entry.id,
                )
                return {
                    "valid": False,
                    "entries_checked": i + 1,
                    "first_broken_id": entry.id,
                    "message": f"Chain broken at entry {entry.id} (index {i}): prev_hash mismatch.",
                }

            # Verify the entry's own hash
            expected_hash = self._compute_hash(
                actor=entry.actor,
                action=entry.action,
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                detail=entry.detail,
                result=entry.result,
                timestamp=self._format_ts(entry.timestamp) if entry.timestamp else "",
                prev_hash=entry.prev_hash,
            )
            if entry.entry_hash != expected_hash:
                logger.warning(
                    "audit_hash_mismatch",
                    index=i,
                    entry_id=entry.id,
                )
                return {
                    "valid": False,
                    "entries_checked": i + 1,
                    "first_broken_id": entry.id,
                    "message": f"Hash mismatch at entry {entry.id} (index {i}).",
                }

        return {
            "valid": True,
            "entries_checked": len(entries),
            "first_broken_id": None,
            "message": f"All {len(entries)} entries verified successfully.",
        }
