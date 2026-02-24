"""Shared test fixtures — async client, in-memory database, settings overrides."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.db.session import get_db
from app.models.base import Base

# ── In-memory SQLite for tests ─────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(TEST_DB_URL, echo=False)
_test_session_factory = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def _get_test_settings() -> Settings:
    """Return test-specific settings (all configurable, nothing hardcoded)."""
    return Settings(
        JARVIS_DB_URL=TEST_DB_URL,
        JARVIS_DEBUG=True,
        JARVIS_LOG_LEVEL="WARNING",
        JARVIS_OLLAMA_HOST="http://localhost:11434",
        JARVIS_OLLAMA_MODELS_PATH="F:/models",
        JARVIS_SECRET_KEY="test-secret-key",
        JARVIS_BCRYPT_ROUNDS=4,  # fast for tests
    )


# ── Override dependencies ───────────────────────────────────

async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Fixtures ────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for all async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create / drop tables before each test for isolation."""
    # Import all models so metadata is populated
    import app.models  # noqa: F401

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a raw async DB session for service-level tests."""
    async with _test_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx AsyncClient bound to the JARVIS FastAPI app."""
    from app.config import get_settings
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_settings] = _get_test_settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
