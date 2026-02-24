# JARVIS AI

An intelligent desktop automation assistant powered by local LLMs via Ollama. JARVIS observes, learns, and executes multi-step workflows on your desktop — with voice input, visual feedback, and a learning engine that improves over time.

## Features

- **Chat Interface** — Natural language conversation with context-aware responses
- **Workflow Engine** — Create, edit, execute, and schedule multi-step automations
- **13-Agent Architecture** — Specialized agents for browsing, file management, code, and more
- **Voice Input** — Speech-to-text transcription with silence detection
- **Learning Engine** — Learns execution patterns and suggests automations
- **Security** — Passphrase auth, JWT sessions, AES-256 encryption, audit trail with hash-chain integrity
- **Recovery** — Multi-strategy error recovery with context snapshots and suggestions
- **Local-First** — All data stays on your machine; LLM inference runs via Ollama

## Architecture

```
┌─────────────────────────────────────────┐
│             Electron + React            │ ← Desktop UI
│  (Chat, Workflows, Settings, Voice)     │
└───────────────┬─────────────────────────┘
                │ HTTP / WebSocket
┌───────────────▼─────────────────────────┐
│           FastAPI Backend               │ ← localhost:9000
│  88 REST endpoints + 1 WebSocket        │
│  17 services • 20+ DB tables            │
└──────┬──────────────┬───────────────────┘
       │              │
  ┌────▼────┐   ┌─────▼─────┐
  │ SQLite  │   │  Ollama   │ ← localhost:11434
  │  (async)│   │ (qwen2.5) │
  └─────────┘   └───────────┘
```

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| Ollama | latest | Local LLM inference |

### Install Ollama

1. Download from [ollama.com](https://ollama.com)
2. Pull a model: `ollama pull qwen2.5:3b`
3. Verify: `ollama list`

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Bionic-AI-Solutions/jarvis-ai-2.git
cd jarvis-ai-2
```

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

Create `backend/.env` (or set environment variables):

```env
JARVIS_DB_URL=sqlite+aiosqlite:///./data/jarvis.db
JARVIS_SECRET_KEY=your-secret-key-here
JARVIS_DEBUG=true
JARVIS_LOG_LEVEL=INFO
JARVIS_OLLAMA_HOST=http://localhost:11434
JARVIS_OLLAMA_MODELS_PATH=F:/models
JARVIS_OLLAMA_DEFAULT_MODEL=qwen2.5:3b
JARVIS_BCRYPT_ROUNDS=12
```

### 4. Start the backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

The API is now available at `http://localhost:9000`. Interactive docs at `/docs` (debug mode).

### 5. Frontend setup

```bash
cd frontend
npm install
```

### 6. Start the frontend (development)

```bash
npm run dev
```

### 7. Build the desktop app

```bash
npm run build
npm run electron:build
```

## Project Structure

```
jarvis-ai-2/
├── backend/
│   ├── app/
│   │   ├── config.py              # Pydantic Settings (env vars)
│   │   ├── main.py                # FastAPI app factory
│   │   ├── core/                  # Errors, logging, middleware, exceptions
│   │   ├── db/                    # Engine, session, init_db
│   │   ├── models/                # SQLAlchemy models (10 files, 20+ tables)
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── routes/                # 13 routers (88 endpoints + WebSocket)
│   │   └── services/              # 17 business logic services
│   ├── tests/                     # pytest test suites
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/            # React components (20+)
│   │   ├── services/              # API client
│   │   ├── store/                 # Zustand state stores
│   │   └── App.tsx                # Router + layout
│   ├── electron/                  # Electron main process
│   └── package.json
├── Jarvis_Final_Documents/        # Architecture, implementation plans, API docs
├── CHANGELOG.md
└── README.md
```

## Testing

### Backend tests

```bash
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v --tb=short
```

Coverage target: **≥ 80%** (currently ~87% on unit tests).

Test suites:
- **Unit tests** — Sprint 0–8 (340 tests across 12 files)
- **Integration tests** — 18 cross-service tests
- **E2E tests** — 12 full user-journey tests
- **Performance tests** — 12 latency/throughput tests
- **Error edge cases** — 72 validation, 404, and business-logic tests

### Frontend tests

```bash
cd frontend
npx vitest run
```

167 component/integration tests across 5 test files.

## Configuration Reference

All configuration is via environment variables (prefixed `JARVIS_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `JARVIS_DB_URL` | `sqlite+aiosqlite:///./data/jarvis.db` | Database connection string |
| `JARVIS_SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `JARVIS_DEBUG` | `false` | Enable debug mode (Swagger UI) |
| `JARVIS_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `JARVIS_OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `JARVIS_OLLAMA_MODELS_PATH` | `F:/models` | Ollama models directory |
| `JARVIS_OLLAMA_DEFAULT_MODEL` | `qwen2.5:3b` | Default LLM model |
| `JARVIS_OLLAMA_TIMEOUT` | `120` | Ollama request timeout (seconds) |
| `JARVIS_BCRYPT_ROUNDS` | `12` | Bcrypt cost factor |
| `JARVIS_HOST` | `0.0.0.0` | Server bind address |
| `JARVIS_PORT` | `9000` | Server port |
| `JARVIS_VERSION` | `1.0.0` | Application version |

## API Documentation

See [Jarvis_Final_Documents/API_REFERENCE.md](Jarvis_Final_Documents/API_REFERENCE.md) for the complete API reference (88 endpoints).

Interactive Swagger UI is available at `http://localhost:9000/docs` when running in debug mode.

## Development

### Adding a new service

1. Create `backend/app/services/my_service.py`
2. Create schemas in `backend/app/schemas/my_schema.py`
3. Create routes in `backend/app/routes/my_route.py`
4. Register the router in `backend/app/main.py`
5. Add tests in `backend/tests/test_my_feature.py`

### Adding a new agent

1. Implement the agent protocol (REST on ports 9100–9199)
2. Register via `POST /api/agents`
3. The orchestrator will route tasks based on declared capabilities

## License

Proprietary — Bionic AI Solutions. All rights reserved.
