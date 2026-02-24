"""JARVIS AI Backend - Middleware stack."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def setup_cors(app: FastAPI, settings: Settings) -> None:
    """Add CORS middleware based on configuration."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log request duration for every HTTP call."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=elapsed_ms,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter.

    Tracks requests per client IP in a rolling window.
    Configurable via settings; defaults to 100 req / 60 s.
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Prune old entries
        self._hits[client_ip] = [
            t for t in self._hits[client_ip] if t > now - self.window_seconds
        ]

        if len(self._hits[client_ip]) >= self.max_requests:
            from app.core.errors import ErrorCode, error_response_body
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429,
                content=error_response_body(ErrorCode.RATE_LIMITED),
            )

        self._hits[client_ip].append(now)
        return await call_next(request)


def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """Register all middleware on the FastAPI application."""
    setup_cors(app, settings)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
