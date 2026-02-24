"""Settings and mode API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.settings import ModeResponse, ModeSetRequest, SettingResponse, SettingUpdate
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/api/settings", tags=["Settings"])

# Default user ID for the local single-user desktop app
_DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def _svc(db: AsyncSession = Depends(get_db)) -> SettingsService:
    return SettingsService(db)


@router.get("", response_model=list[SettingResponse])
async def list_settings(svc: SettingsService = Depends(_svc)):
    """Get all user settings."""
    return await svc.get_all(_DEFAULT_USER_ID)


@router.put("", response_model=SettingResponse)
async def upsert_setting(
    data: SettingUpdate,
    svc: SettingsService = Depends(_svc),
):
    """Create or update a setting."""
    return await svc.upsert(_DEFAULT_USER_ID, data.key, data.value)


@router.get("/mode", response_model=ModeResponse)
async def get_mode():
    """Get current operational mode."""
    return ModeResponse(mode=SettingsService.get_mode())


@router.post("/mode", response_model=ModeResponse)
async def set_mode(data: ModeSetRequest):
    """Set operational mode (auto | supervised | locked)."""
    new_mode = SettingsService.set_mode(data.mode)
    return ModeResponse(mode=new_mode)
