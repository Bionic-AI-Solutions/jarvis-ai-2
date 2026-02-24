"""Database initialisation — create all tables on startup."""

from __future__ import annotations

from app.core.logging_config import get_logger
from app.db.session import get_engine
from app.models.base import Base

# Side-effect import: ensure all models are registered with the Base metadata
import app.models  # noqa: F401

logger = get_logger(__name__)


async def init_db() -> None:
    """Create database tables if they don't exist.

    Uses SQLAlchemy's ``create_all`` for dev convenience.
    Production should rely on Alembic migrations.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized", tables=list(Base.metadata.tables.keys()))
