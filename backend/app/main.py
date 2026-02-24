"""JARVIS AI Backend - FastAPI application entry point.

Wires up all routes, middleware, lifecycle events, and error handlers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.middleware import setup_middleware
from app.db.init_db import init_db
from app.db.session import close_engine
from app.routes import agents, auth, chats, execution, health, settings, voice, workflows, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown lifecycle."""
    cfg = get_settings()
    setup_logging(cfg.log_level)

    # Startup
    await init_db()

    yield

    # Shutdown
    await close_engine()


def create_app() -> FastAPI:
    """Application factory."""
    cfg = get_settings()

    app = FastAPI(
        title="JARVIS AI Backend",
        version=cfg.version,
        docs_url="/docs" if cfg.debug else None,
        redoc_url="/redoc" if cfg.debug else None,
        lifespan=lifespan,
    )

    # Middleware
    setup_middleware(app, cfg)

    # Exception handlers
    register_exception_handlers(app)

    # Routes
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(chats.router)
    app.include_router(workflows.router)
    app.include_router(execution.router)
    app.include_router(settings.router)
    app.include_router(agents.router)
    app.include_router(voice.router)
    app.include_router(ws.router)

    return app


app = create_app()
