"""JARVIS AI Backend - Structured logging configuration.

Story 7.7: Monitoring & Logging
- Console output (dev mode, coloured)
- File output (structured JSON, rotating)
- Centralized error log
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog


def setup_logging(log_level: str = "INFO", log_dir: str | None = None) -> None:
    """Configure structured logging for the application.

    Uses structlog for JSON-friendly log output in production
    and human-readable coloured output in development.
    Logs to both console and rotating file.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Ensure log directory
    if log_dir is None:
        log_path = Path("./data/logs")
    else:
        log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # structlog processors
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Console handler (coloured dev output)
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(),
        ],
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    # File handler (JSON structured, rotating 10MB x 5 files)
    json_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )
    file_handler = RotatingFileHandler(
        log_path / "jarvis.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(json_formatter)

    # Error-only file handler (for easy error triage)
    error_handler = RotatingFileHandler(
        log_path / "jarvis_errors.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)
    root.addHandler(error_handler)
    root.setLevel(numeric_level)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)
