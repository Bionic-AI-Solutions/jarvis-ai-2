"""Settings service — manages user preferences and system mode."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.models.settings import UserSetting

logger = get_logger(__name__)

# In-memory mode state (single-user desktop app)
_current_mode: str = "auto"


class SettingsService:
    """Manages user settings CRUD and system mode."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── User Settings ───────────────────────────────────────

    async def get_all(self, user_id: str) -> Sequence[UserSetting]:
        """Return all settings for a user."""
        stmt = (
            select(UserSetting)
            .where(UserSetting.user_id == user_id)
            .order_by(UserSetting.key)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get(self, user_id: str, key: str) -> UserSetting | None:
        """Get a single setting by key."""
        stmt = select(UserSetting).where(
            UserSetting.user_id == user_id,
            UserSetting.key == key,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, user_id: str, key: str, value: str) -> UserSetting:
        """Create or update a setting."""
        existing = await self.get(user_id, key)
        if existing:
            existing.value = value
            await self.db.flush()
            logger.info("setting_updated", user_id=user_id, key=key)
            return existing

        setting = UserSetting(user_id=user_id, key=key, value=value)
        self.db.add(setting)
        await self.db.flush()
        logger.info("setting_created", user_id=user_id, key=key)
        return setting

    async def delete(self, user_id: str, key: str) -> None:
        """Delete a setting."""
        existing = await self.get(user_id, key)
        if existing:
            await self.db.delete(existing)
            logger.info("setting_deleted", user_id=user_id, key=key)

    # ── System Mode ─────────────────────────────────────────

    @staticmethod
    def get_mode() -> str:
        """Return current operational mode."""
        return _current_mode

    @staticmethod
    def set_mode(mode: str) -> str:
        """Set operational mode (auto | supervised | locked)."""
        global _current_mode
        _current_mode = mode
        logger.info("mode_changed", mode=mode)
        return _current_mode
