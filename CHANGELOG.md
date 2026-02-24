# Changelog

All notable changes to JARVIS AI are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2025-01-21

### Added

#### Core Platform (Sprint 0)
- FastAPI application factory with async lifespan (startup/shutdown)
- Centralized `Settings` configuration via environment variables (Pydantic)
- Structured logging with `structlog` (ConsoleRenderer + RotatingFileHandler, 50 MB × 30)
- 60+ categorized error codes with structured JSON error responses
- CORS middleware, request-ID injection, request logging middleware
- SQLAlchemy async engine with `aiosqlite` (dev) and auto-migration on startup

#### Chat & Conversations (Sprint 1)
- 14 SQLAlchemy models: ChatSession, ChatMessage, Workflow, WorkflowStep, Execution, ExecutionLog, Agent, Settings, User, Metrics, and more
- Full CRUD for chat sessions with message threading
- Pydantic v2 schemas with field validation (min/max length, regex patterns)
- WebSocket endpoint (`/ws`) for real-time execution updates

#### Workflow Engine (Sprint 1–2)
- Workflow CRUD with revision history, clone, export (JSON/CSV), and search
- Built-in template seeding and cloning
- Workflow execution with step-by-step logging and cancel support
- Agent protocol (REST on ports 9100–9199) with registry, orchestrator, and health checks
- Ollama LLM integration (localhost:11434, configurable model directory)

#### Security & Auth (Sprint 3)
- Passphrase-based auth with bcrypt (cost 12 prod, 4 tests) + JWT (HS256, 60 min)
- Account lockout with exponential backoff (3 attempts → max 3600 s)
- Passphrase strength scoring (0–4 scale)
- CI pipeline with GitHub Actions

#### Desktop UI (Sprint 4)
- Electron 33 + React 18 + Vite 6 + TypeScript 5.7 desktop application
- Chat interface, workflow builder, settings page, status bar
- React Router v6 navigation with sidebar layout
- Zustand-based state management

#### Execution Monitoring (Sprint 5)
- Execution logger service with structured step recording
- ExecutionTimeline, StepConfidence, and FallbackTextInput UI components
- Real-time confidence display per step

#### Recovery & Voice (Sprint 6)
- Recovery engine with multi-strategy fallback and error context analysis
- Voice service with transcription, silence detection, and configurable thresholds
- VoiceButton, VoiceIndicator, VoiceSettings, RecoveryDialog UI components

#### Advanced Workflows (Sprint 7)
- Extended Workflow model (8 new columns: `retry_count`, `max_retries`, `timeout_seconds`, `priority`, `schedule_cron`, `error_handling_strategy`, `last_error_message`, `average_duration`)
- Pause / resume support for workflow executions
- Error context service and recovery suggestion service
- Ollama proxy service for model management
- WorkflowStats, WorkflowErrorBanner, PauseResumeControls, RecoverySuggestionPanel, OllamaModelSelector UI

#### Security Hardening & Learning Engine (Sprint 8)
- Audit trail with hash-chain integrity verification (SHA-256)
- Active session management (list, revoke, revoke-all)
- Request queue with drain, reject, and expiry cleanup
- AES-256 encryption service (Fernet + PBKDF2HMAC, 100 K iterations)
- Pattern learning engine: record execution patterns → frequency/confidence scoring → suggestions
- Confidence learning engine: manual and auto-adjust thresholds with history tracking
- LockScreen, PassphraseStrengthMeter, AuditLogViewer, PatternSuggestion UI
- LockoutManager with exponential backoff (3 attempts → max 3600 s)

#### QA, Hardening & Release (Sprint 9)
- Integration test suite: 18 cross-service tests
- End-to-end test suite: 12 user-journey tests
- Performance test suite: 12 latency/throughput/load tests
- Error edge-case test suite: 72 tests (validation, 404s, business logic, structural)
- API reference documentation (88 HTTP endpoints + 1 WebSocket)
- CHANGELOG and updated README
- Electron + Python backend installer scripts

### Infrastructure
- **Backend:** FastAPI 0.115.6, Python 3.12, SQLAlchemy[asyncio] 2.0.36, aiosqlite 0.20.0
- **Frontend:** Electron 33.2.0, React 18.3.1, Vite 6.0.3, TypeScript 5.7.2
- **Testing:** pytest 8.3.4 + pytest-asyncio 0.25.0 (backend), vitest 2.1.9 (frontend)
- **CI/CD:** GitHub Actions with lint, type-check, and test stages
- **LLM:** Ollama (localhost:11434) with configurable model path (default: `F:/models`)

### Bug Fixes
- **BUG-001:** Bcrypt version incompatibility — pinned bcrypt==4.2.1
- **BUG-002:** Pydantic V1-style `orm_mode` — migrated to `from_attributes`
- **BUG-003:** SQLAlchemy expired-instance on lazy access — set `expire_on_commit=False`
- **BUG-004:** Stale `Settings` import — switched to `get_settings()` dependency
- **BUG-005:** `ChatMessage.role` default `"user"` → Pydantic `default=...` instead of SA `server_default`
- **BUG-006:** `event_loop` fixture scope — set `scope="session"` for pytest-asyncio
- **BUG-007:** Missing `__all__` in `models/__init__.py` — SA `create_all` now sees every table
- **BUG-008:** `httpx.AsyncClient` transport — switched to `ASGITransport`
- **BUG-009:** `recovery_engine.py` import of non-existent `notify_ui` — guarded with try/except
- **BUG-010:** `voice_service.py` unresolved `np`/`io`/`sf` — added conditional imports
- **BUG-011:** `OllamaProxy.generate()` passed `options` to httpx JSON — serialize properly
- **BUG-012:** Frontend `zustand` TypeScript strict-mode errors — typed store creators
- **BUG-013:** `audit_service.verify_chain` returned wrong key names — aligned to schema
- **BUG-014:** Audit hash failed after SQLite datetime round-trip — fixed `_format_ts()` with `strftime`

---

[1.0.0]: https://github.com/Bionic-AI-Solutions/jarvis-ai-2/releases/tag/v1.0.0
