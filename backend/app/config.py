"""JARVIS AI Backend - Application configuration.

Loads all settings from environment variables with sensible defaults.
No hardcoded values — everything is configurable via .env file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="JARVIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Server ──────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 9000
    debug: bool = False
    log_level: str = "INFO"
    version: str = "1.0.0"

    # ── Database ────────────────────────────────────────────
    db_url: str = "sqlite+aiosqlite:///./data/jarvis.db"
    data_path: str = "./data"

    # ── Ollama ──────────────────────────────────────────────
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_models_path: str = "F:/models"

    # ── Security ────────────────────────────────────────────
    secret_key: str = "change-me-in-production"
    bcrypt_rounds: int = 12
    auth_lockout_seconds: int = 60
    auth_max_attempts: int = 3
    session_timeout_minutes: int = 30
    jwt_secret: str = "jarvis-jwt-secret-change-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # ── CORS ────────────────────────────────────────────────
    cors_origins: str = '["http://localhost:3000","http://localhost:9000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        return json.loads(self.cors_origins)

    # ── Agent Protocol ──────────────────────────────────────
    agent_base_port: int = 9100
    agent_timeout_seconds: int = 30
    agent_max_concurrent: int = 5

    # ── Screenshots ─────────────────────────────────────────
    screenshot_quality: int = 80
    screenshot_retention_days: int = 30

    # ── Voice ───────────────────────────────────────────────
    voice_model: str = "whisper"
    voice_confidence_threshold: float = 0.90
    voice_silence_db: float = 5.0
    voice_silence_duration: float = 1.5
    voice_max_duration: int = 30
    voice_auto_accept_threshold: float = 0.90
    voice_re_speak_threshold: float = 0.80

    # ── WebSocket ───────────────────────────────────────────
    ws_heartbeat_seconds: int = 30
    ws_idle_timeout_seconds: int = 300

    @property
    def data_dir(self) -> Path:
        """Return the data directory path, creating it if needed."""
        path = Path("./data")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def screenshots_dir(self) -> Path:
        """Return the screenshots directory path."""
        path = self.data_dir / "screenshots"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        """Return the logs directory path."""
        path = self.data_dir / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path


def get_settings() -> Settings:
    """Factory function for Settings — enables dependency injection."""
    return Settings()
