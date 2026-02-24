"""Error context capture service — captures system/execution state on failure.

Story 3.7: Rich Error Context Capture
Captures environment, memory usage, recent logs, and error details
into a ContextSnapshot for post-mortem analysis.
"""

from __future__ import annotations

import json
import os
import platform
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.models.execution import ContextSnapshot, ExecutionLog, WorkflowExecution
from app.services.execution_logger import execution_logger

logger = get_logger(__name__)


class ErrorContextService:
    """Captures and stores rich error context snapshots."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def capture_error_context(
        self,
        execution_id: str,
        step_index: int,
        error: str,
        error_type: str = "runtime",
        agent_name: str | None = None,
        action: str | None = None,
        parameters: dict | None = None,
        extra: dict | None = None,
    ) -> ContextSnapshot:
        """Capture full error context and persist as a ContextSnapshot.

        Args:
            execution_id: The execution that encountered the error.
            step_index: Which step failed.
            error: Error message string.
            error_type: Category (runtime, timeout, agent, validation, etc.).
            agent_name: Name of the agent that failed.
            action: The action that was attempted.
            parameters: Parameters passed to the agent.
            extra: Any additional context to include.

        Returns:
            The created ContextSnapshot model instance.
        """
        snapshot_data: Dict[str, Any] = {
            "error": {
                "message": error,
                "type": error_type,
                "traceback": traceback.format_exc() if error_type == "runtime" else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "step": {
                "index": step_index,
                "agent": agent_name,
                "action": action,
                "parameters": _redact_sensitive(parameters or {}),
            },
            "system": _capture_system_info(),
            "execution_history": await self._get_recent_logs(execution_id, limit=10),
        }

        if extra:
            snapshot_data["extra"] = extra

        cs = ContextSnapshot(
            execution_id=execution_id,
            step_index=step_index,
            snapshot_json=json.dumps(snapshot_data, default=str),
        )
        self.db.add(cs)
        await self.db.commit()
        await self.db.refresh(cs)

        logger.info(
            "error_context_captured",
            execution_id=execution_id,
            step_index=step_index,
            error_type=error_type,
            snapshot_id=cs.id,
        )
        return cs

    async def get_context_snapshot(self, snapshot_id: str) -> ContextSnapshot | None:
        """Retrieve a single snapshot by ID."""
        result = await self.db.execute(
            select(ContextSnapshot).where(ContextSnapshot.id == snapshot_id)
        )
        return result.scalar_one_or_none()

    async def get_execution_snapshots(self, execution_id: str) -> list[ContextSnapshot]:
        """Retrieve all snapshots for an execution."""
        result = await self.db.execute(
            select(ContextSnapshot)
            .where(ContextSnapshot.execution_id == execution_id)
            .order_by(ContextSnapshot.step_index)
        )
        return list(result.scalars().all())

    async def get_snapshot_data(self, snapshot_id: str) -> dict | None:
        """Get parsed JSON data from a snapshot."""
        cs = await self.get_context_snapshot(snapshot_id)
        if cs is None:
            return None
        return json.loads(cs.snapshot_json)

    async def _get_recent_logs(self, execution_id: str, limit: int = 10) -> list[dict]:
        """Fetch recent execution log entries for context."""
        result = await self.db.execute(
            select(ExecutionLog)
            .where(ExecutionLog.execution_id == execution_id)
            .order_by(ExecutionLog.step_index.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            {
                "step_index": log.step_index,
                "agent_name": log.agent_name,
                "action": log.action,
                "status": log.status,
                "duration_ms": log.duration_ms,
                "detail": log.detail[:200] if log.detail else None,
            }
            for log in reversed(list(logs))
        ]


def _capture_system_info() -> Dict[str, Any]:
    """Capture basic system information for error context."""
    info: Dict[str, Any] = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "pid": os.getpid(),
    }
    try:
        import psutil
        mem = psutil.virtual_memory()
        info["memory"] = {
            "total_mb": round(mem.total / (1024 * 1024), 1),
            "available_mb": round(mem.available / (1024 * 1024), 1),
            "percent_used": mem.percent,
        }
        info["cpu_percent"] = psutil.cpu_percent(interval=0)
    except ImportError:
        # psutil not installed — provide basic info only
        pass
    return info


def _redact_sensitive(params: dict) -> dict:
    """Redact potentially sensitive parameter values."""
    sensitive_keys = {"password", "secret", "token", "api_key", "passphrase", "credential"}
    redacted = {}
    for k, v in params.items():
        if any(sk in k.lower() for sk in sensitive_keys):
            redacted[k] = "***REDACTED***"
        else:
            redacted[k] = v
    return redacted
