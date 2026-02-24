"""Settings-related schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import OrmBase


class SettingUpdate(BaseModel):
    """Update a single setting."""

    key: str = Field(..., max_length=100)
    value: str


class SettingResponse(OrmBase):
    """Single user setting."""

    id: str
    user_id: str
    key: str
    value: str


class ModeSetRequest(BaseModel):
    """Set operational mode of the system."""

    mode: str = Field(..., pattern="^(auto|supervised|locked)$")
    passphrase: Optional[str] = None


class ModeResponse(BaseModel):
    """Current operational mode."""

    mode: str
    changed_at: Optional[str] = None
