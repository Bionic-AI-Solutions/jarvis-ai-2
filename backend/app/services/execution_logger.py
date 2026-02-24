"""
JARVIS AI — Step Execution Logger.

Story 2.3: Step Execution Logging
- Each step logs: Timestamp, Agent, Action, Input, Output, Duration, Exit Code
- Structured JSON + plaintext
- Log rotation: Daily / 50MB, keep 30 days
- Sensitive data redaction
"""

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from app.config import get_settings

# Patterns to redact from logs
REDACT_PATTERNS = [
    re.compile(r'Bearer\s+\S+', re.IGNORECASE),
    re.compile(r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'),  # JWT tokens
    re.compile(r'(password|passphrase|secret|token|api_key|apikey|authorization)\s*[:=]\s*\S+', re.IGNORECASE),
]


def redact_sensitive(text: str) -> str:
    """Remove sensitive data (passwords, tokens, API keys) from log text."""
    result = text
    for pattern in REDACT_PATTERNS:
        result = pattern.sub('[REDACTED]', result)
    return result


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Deep-redact sensitive values from a dictionary."""
    sensitive_keys = {'password', 'passphrase', 'secret', 'token', 'api_key', 'apikey', 'authorization'}
    result = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            result[key] = '[REDACTED]'
        elif isinstance(value, dict):
            result[key] = redact_dict(value)
        elif isinstance(value, str):
            result[key] = redact_sensitive(value)
        else:
            result[key] = value
    return result


class StepLogEntry:
    """Represents a single step execution log entry."""

    def __init__(
        self,
        execution_id: str,
        step_index: int,
        agent_name: str,
        action: str,
        input_data: dict[str, Any] | None = None,
        workflow_id: str | None = None,
    ):
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self.step_index = step_index
        self.agent_name = agent_name
        self.action = action
        self.input_data = input_data or {}
        self.output_data: dict[str, Any] = {}
        self.status: str = 'started'
        self.exit_code: int | None = None
        self.error: str | None = None
        self.confidence: float | None = None
        self.started_at: datetime = datetime.now(timezone.utc)
        self.completed_at: datetime | None = None
        self.duration_ms: float | None = None

    def complete(
        self,
        output_data: dict[str, Any] | None = None,
        status: str = 'success',
        exit_code: int = 0,
        error: str | None = None,
        confidence: float | None = None,
    ) -> None:
        """Mark step as completed."""
        self.completed_at = datetime.now(timezone.utc)
        self.duration_ms = (self.completed_at - self.started_at).total_seconds() * 1000
        self.output_data = output_data or {}
        self.status = status
        self.exit_code = exit_code
        self.error = error
        self.confidence = confidence

    def to_json(self) -> dict[str, Any]:
        """Serialize to JSON-safe dictionary with redaction."""
        entry = {
            'timestamp': self.started_at.isoformat(),
            'execution_id': self.execution_id,
            'workflow_id': self.workflow_id,
            'step_index': self.step_index,
            'agent': self.agent_name,
            'action': self.action,
            'input': redact_dict(self.input_data),
            'output': redact_dict(self.output_data),
            'status': self.status,
            'exit_code': self.exit_code,
            'duration_ms': self.duration_ms,
            'confidence': self.confidence,
            'error': redact_sensitive(self.error) if self.error else None,
        }
        if self.completed_at:
            entry['completed_at'] = self.completed_at.isoformat()
        return entry

    def to_plaintext(self) -> str:
        """Human-readable log line."""
        ts = self.started_at.strftime('%Y-%m-%d %H:%M:%S')
        duration = f'{self.duration_ms:.0f}ms' if self.duration_ms else 'N/A'
        confidence = f'{self.confidence:.0%}' if self.confidence is not None else 'N/A'
        line = (
            f'[{ts}] Step {self.step_index} | {self.agent_name}.{self.action} '
            f'| Status: {self.status} | Duration: {duration} | Confidence: {confidence}'
        )
        if self.error:
            line += f' | Error: {redact_sensitive(self.error)}'
        return line


class ExecutionLogger:
    """
    Manages execution logging with structured JSON and plaintext formats.

    Storage: [DATA_PATH]/logs/execution_[workflowID].log
    Rotation: 50MB per file, keep 30 files (≈30 days)
    """

    def __init__(self, log_dir: str | None = None):
        settings = get_settings()
        self.log_dir = Path(log_dir) if log_dir else Path(settings.data_path) / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._loggers: dict[str, logging.Logger] = {}
        self._entries: dict[str, list[StepLogEntry]] = {}

    def _get_logger(self, execution_id: str, workflow_id: str | None = None) -> logging.Logger:
        """Get or create a logger for a specific execution."""
        if execution_id in self._loggers:
            return self._loggers[execution_id]

        logger_name = f'jarvis.execution.{execution_id}'
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        # JSON log file
        wf_id = workflow_id or 'unknown'
        json_path = self.log_dir / f'execution_{wf_id}_{execution_id[:8]}.json.log'
        json_handler = RotatingFileHandler(
            str(json_path),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=30,
            encoding='utf-8',
        )
        json_handler.setFormatter(logging.Formatter('%(message)s'))
        json_handler.set_name('json')
        logger.addHandler(json_handler)

        # Plaintext log file
        text_path = self.log_dir / f'execution_{wf_id}_{execution_id[:8]}.log'
        text_handler = RotatingFileHandler(
            str(text_path),
            maxBytes=50 * 1024 * 1024,
            backupCount=30,
            encoding='utf-8',
        )
        text_handler.setFormatter(logging.Formatter('%(message)s'))
        text_handler.set_name('text')
        logger.addHandler(text_handler)

        self._loggers[execution_id] = logger
        return logger

    def start_step(
        self,
        execution_id: str,
        step_index: int,
        agent_name: str,
        action: str,
        input_data: dict[str, Any] | None = None,
        workflow_id: str | None = None,
    ) -> StepLogEntry:
        """Create and log a step start event."""
        entry = StepLogEntry(
            execution_id=execution_id,
            step_index=step_index,
            agent_name=agent_name,
            action=action,
            input_data=input_data,
            workflow_id=workflow_id,
        )

        # Store entry
        if execution_id not in self._entries:
            self._entries[execution_id] = []
        self._entries[execution_id].append(entry)

        # Log start event
        logger = self._get_logger(execution_id, workflow_id)
        start_event = {
            'event': 'step_started',
            'timestamp': entry.started_at.isoformat(),
            'execution_id': execution_id,
            'step_index': step_index,
            'agent': agent_name,
            'action': action,
            'input': redact_dict(entry.input_data),
        }

        # Write to JSON handler
        for handler in logger.handlers:
            if handler.name == 'json':
                handler.emit(logging.LogRecord(
                    name=logger.name, level=logging.INFO, pathname='', lineno=0,
                    msg=json.dumps(start_event), args=(), exc_info=None,
                ))
            elif handler.name == 'text':
                ts = entry.started_at.strftime('%Y-%m-%d %H:%M:%S')
                handler.emit(logging.LogRecord(
                    name=logger.name, level=logging.INFO, pathname='', lineno=0,
                    msg=f'[{ts}] Step {step_index} STARTED | {agent_name}.{action}',
                    args=(), exc_info=None,
                ))

        return entry

    def complete_step(
        self,
        entry: StepLogEntry,
        output_data: dict[str, Any] | None = None,
        status: str = 'success',
        exit_code: int = 0,
        error: str | None = None,
        confidence: float | None = None,
    ) -> None:
        """Log a step completion event."""
        entry.complete(
            output_data=output_data,
            status=status,
            exit_code=exit_code,
            error=error,
            confidence=confidence,
        )

        logger = self._get_logger(entry.execution_id, entry.workflow_id)

        # Write JSON
        for handler in logger.handlers:
            if handler.name == 'json':
                handler.emit(logging.LogRecord(
                    name=logger.name, level=logging.INFO, pathname='', lineno=0,
                    msg=json.dumps(entry.to_json()), args=(), exc_info=None,
                ))
            elif handler.name == 'text':
                handler.emit(logging.LogRecord(
                    name=logger.name, level=logging.INFO, pathname='', lineno=0,
                    msg=entry.to_plaintext(), args=(), exc_info=None,
                ))

    def get_entries(
        self,
        execution_id: str,
        step_index: int | None = None,
        agent: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query logged entries with optional filters.

        Filters: step_index, agent, status (success/failure/started).
        """
        entries = self._entries.get(execution_id, [])
        result = []
        for e in entries:
            if step_index is not None and e.step_index != step_index:
                continue
            if agent is not None and e.agent_name != agent:
                continue
            if status is not None and e.status != status:
                continue
            result.append(e.to_json())
        return result

    def cleanup(self, execution_id: str) -> None:
        """Remove logger and cached entries for a finished execution."""
        if execution_id in self._loggers:
            logger = self._loggers[execution_id]
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            del self._loggers[execution_id]
        self._entries.pop(execution_id, None)


# Singleton
execution_logger = ExecutionLogger()
