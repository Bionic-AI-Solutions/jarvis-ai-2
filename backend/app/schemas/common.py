"""Common / shared Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class OrmBase(BaseModel):
    """Base schema that reads from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standard JSON error payload."""

    error_code: str
    message: str
    detail: Optional[str] = None
    ux_action: str
    retry_allowed: bool


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list results."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    pages: int


class SuccessResponse(BaseModel):
    """Generic success payload."""

    ok: bool = True
    message: str = "success"
