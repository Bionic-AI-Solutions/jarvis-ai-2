"""JARVIS AI Backend - Custom exception classes and error handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import ErrorCode, error_response_body, get_error


class JarvisError(Exception):
    """Base exception for all JARVIS application errors."""

    def __init__(self, code: ErrorCode, detail: str | None = None) -> None:
        self.code = code
        self.detail = detail
        err = get_error(code)
        self.http_status = err.http_status
        super().__init__(err.message)


class NotFoundError(JarvisError):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            ErrorCode.NOT_FOUND,
            detail=f"{resource} with id '{resource_id}' not found",
        )


class AuthenticationError(JarvisError):
    """Authentication failure."""

    def __init__(self, code: ErrorCode = ErrorCode.AUTH_REQUIRED, detail: str | None = None) -> None:
        super().__init__(code, detail)


class WorkflowError(JarvisError):
    """Workflow-specific error."""

    pass


class AgentError(JarvisError):
    """Agent communication error."""

    pass


class ValidationError(JarvisError):
    """Input validation error."""

    def __init__(self, detail: str) -> None:
        super().__init__(ErrorCode.VALIDATION_FAILED, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI app."""

    @app.exception_handler(JarvisError)
    async def jarvis_error_handler(_request: Request, exc: JarvisError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=error_response_body(exc.code, exc.detail),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_response_body(
                ErrorCode.INTERNAL_ERROR,
                detail=str(exc) if exc.args else None,
            ),
        )
