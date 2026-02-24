# JARVIS AI — COMPREHENSIVE SPRINT PLANNING

**Version:** 1.0  
**Date:** February 24, 2026  
**Source:** JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md + JARVIS_AI_EPICS_AND_USER_STORIES.md  
**Status:** Ready for Implementation  

---

## TABLE OF CONTENTS

1. [Sprint Overview](#sprint-overview)
2. [Timeline & Milestones](#timeline--milestones)
3. [Team Roster & Capacity](#team-roster--capacity)
4. [Sprint Details](#sprint-details)
   - [Sprint 0: Phase 0 Blockers (Gate)](#sprint-0-phase-0-blockers-gate)
   - [Sprint 1: API Contract & Backend Scaffold](#sprint-1-api-contract--backend-scaffold)
   - [Sprint 2: Backend Core Implementation](#sprint-2-backend-core-implementation)
   - [Sprint 3: Backend Services & Integrations](#sprint-3-backend-services--integrations)
   - [Sprint 4: Frontend Shell & IPC](#sprint-4-frontend-shell--ipc)
   - [Sprint 5: Frontend Features & Integration](#sprint-5-frontend-features--integration)
   - [Sprint 6: Voice & Error Recovery (Epic 1 & 3)](#sprint-6-voice--error-recovery-epic-1--3)
   - [Sprint 7: Workflow Execution (Epic 2 & 4)](#sprint-7-workflow-execution-epic-2--4)
   - [Sprint 8: Security & Learning (Epic 5 & 6)](#sprint-8-security--learning-epic-5--6)
   - [Sprint 9: QA, Hardening & Release](#sprint-9-qa-hardening--release)
5. [Dependencies & Critical Path](#dependencies--critical-path)
6. [Risk Register](#risk-register)
7. [Success Criteria](#success-criteria)

---

## SPRINT OVERVIEW

### Summary Table

| Sprint | Duration | Goal | Epics | Stories | Pts | Owner(s) | Status |
|--------|----------|------|-------|---------|-----|---------|--------|
| **0** | Week 1 | Phase 0 blockers | (Setup) | 0 | 0 | Amelia | Not Started |
| **1** | Week 2 | API Contract + Backend Scaffold | Epic 7 | 3 | 18 | Amelia | Not Started |
| **2** | Week 3 | Backend Core (Models, DB, Agents) | Epic 7 | 3 | 20 | Amelia | Not Started |
| **3** | Week 4 | Backend Services (Auth, Metrics, Tests) | Epic 7 | 3 | 13 | Amelia, Quinn | Not Started |
| **4** | Week 5 | Frontend Shell (Electron + React) | Epic 7 | 2 | 13 | Barry | Not Started |
| **5** | Week 6 | Frontend Features + Real-time Integration | Epic 2 | 3 | 15 | Barry | Not Started |
| **6** | Week 7 | Voice Pipeline (Epic 1) + Error Recovery (Epic 3) | Epics 1, 3 | 12 | 52 | Amelia, Barry | Not Started |
| **7** | Week 8 | Workflow Execution (Epic 2 & 4) | Epics 2, 4 | 12 | 52 | Barry | Not Started |
| **8** | Week 9 | Security (Epic 5) + Learning (Epic 6) | Epics 5, 6 | 10 | 51 | Amelia, Barry | Not Started |
| **9** | Week 10 | QA, Hardening, Release | All | 20 | 88 | All | Not Started |
| **Phase 1** | Weeks 11–16 | SHOULD/COULD features | Epics 1–7 | 36 | 172 | All | Backlog |

---

## TIMELINE & MILESTONES

```
Week 1:    Sprint 0 – Phase 0 (Blockers, API Contract, Sign-offs)
           ├─ Deliverables: OpenAPI 3.1 spec, error catalog, test plan, signoffs
           └─ Gate: All blockers resolved before Phase 1 coding begins

Week 2:    Sprint 1 – Backend Scaffold
           ├─ Deliverables: FastAPI running, DB schema v1, requirements.txt
           └─ Gate: Backend compiles, tests pass, API docs generated

Week 3:    Sprint 2 – Backend Core
           ├─ Deliverables: Orchestrator, agent registry, core models
           └─ Gate: Orchestrator can route commands, mock agents functional

Week 4:    Sprint 3 – Backend Services
           ├─ Deliverables: Auth, CORS, health checks, logging, CI pipeline
           └─ Gate: All backend unit tests pass (>80% coverage)

Week 5:    Sprint 4 – Frontend Shell
           ├─ Deliverables: Electron window, React Router, IPC bridge, WebSocket client
           └─ Gate: Frontend connects to backend in dev mode, no crashes

Week 6:    Sprint 5 – Frontend Features + Integration
           ├─ Deliverables: Chat UI, progress display, real-time updates, error handling
           └─ Gate: E2E test: User sends command → backend → UI updates in real-time

Week 7:    Sprint 6 – Voice + Error Recovery
           ├─ Deliverables: Hotkey + Whisper STT, recovery levels 1–6
           └─ Gate: Voice works >85% accuracy, recovery chains tested

Week 8:    Sprint 7 – Workflow Execution
           ├─ Deliverables: Real-time progress, screenshot capture, workflow save/load
           └─ Gate: 20-step workflow executes, all screenshots captured, progress visible

Week 9:    Sprint 8 – Security + Learning
           ├─ Deliverables: Passphrase auth, audit logging, workflow pattern learning
           └─ Gate: Passphrase required, audit log immutable, 3 failures → 60s lockout

Week 10:   Sprint 9 – QA, Hardening, Release
           ├─ Deliverables: Installer, QA sign-off, CHANGELOG, release artifacts
           └─ Gate: MVP ready for private beta testing

Week 11+:  Phase 1 (Weeks 11-16) – SHOULD/COULD Features
           ├─ Epics: Continue with lower-priority stories
           └─ Focus: Multilingual, templates, advanced UI, performance optimization
```

---

## TEAM ROSTER & CAPACITY

### Core Team

| Role | Name | Capacity | Primary Focus | Backup Focus |
|------|------|----------|---------------|--------------|
| **Backend Lead** | Amelia | 35 hrs/wk | API, DB, Agents, Security | Voice STT |
| **Quick-Dev / Frontend** | Barry | 35 hrs/wk | Frontend UI, Voice Hotkey, Installation | Testing |
| **QA Lead** | Quinn | 35 hrs/wk | Testing, Documentation, Beta Setup | Backend QA |
| **Dev 4** | (TBD) | 35 hrs/wk | TBD role | Flexible |

### Velocity Assumptions

- **Team Size:** 4 developers (Amelia, Barry, Quinn + 1 TBD)
- **Sprint Duration:** 1 week (5 working days)
- **Dev Capacity:** ~35 hrs/developer/week
- **Ceremonies Overhead:** ~5 hrs/week (standup, planning, retro)
- **Available Dev Time:** ~30 hrs/developer/week
- **Team Velocity:** 20–24 pts/sprint (4-person team at 5–6 pts per developer)
- **Buffer:** 20% contingency (risky stories, unknowns)

### Roles & Responsibilities

| Sprint | Task | Owner | Hours |
|--------|------|-------|-------|
| Sprint 0 | API Contract Review | Amelia | 10 |
| Sprint 0 | Error Codes Catalog | Amelia, Quinn | 8 |
| Sprint 0 | Test Plan Definition | Quinn | 8 |
| Sprint 0 | Sign-offs (Tech Lead approval) | Amelia | 4 |
| Sprint 1–9 | Backend Dev | Amelia | 30/wk |
| Sprint 1–9 | Frontend Dev | Barry | 30/wk |
| Sprint 1–9 | QA / Testing | Quinn | 30/wk |
| Sprint 1–9 | Support / Flexibility | (TBD Dev 4) | 30/wk |

---

## SPRINT DETAILS

### SPRINT 0: PHASE 0 BLOCKERS (GATE)

**Duration:** 1 week (Feb 24–28, 2026)  
**Sprint Goal:** Resolve all Phase 0 critical blockers before Phase 1 coding begins.  
**Velocity:** 0 pts (no user stories; setup/planning only)  

#### Deliverables

| Task | Owner | Acceptance Criteria | Est. Hours | Status |
|------|-------|-------------------|-----------|--------|
| **API Contract (OpenAPI 3.1)** | Amelia | 25+ endpoints defined, request/response schemas, error codes, authentication | 16 | Not Started |
| **Error Codes Catalog** | Amelia, Quinn | 50+ error codes (4XX, 5XX), mapped to UX actions, documented | 8 | Not Started |
| **Test Infrastructure** | Quinn | pytest configured, CI pipeline stub, test template docs | 12 | Not Started |
| **Architecture Sign-off** | Amelia | Backend Lead approves API contract, DB schema v1, agent protocol | 4 | Not Started |
| **Dependency Map** | Amelia | All story dependencies mapped, no circular deps, critical path identified | 8 | Not Started |

**Total Sprint 0 Hours:** ~48 hours (12 hrs/person for 4-person team)

#### Blockers Resolved

From PART 28: PHASE 0 CRITICAL BLOCKERS in JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md:

✅ **Blocker 1: API Contract**
- **Issue:** 25+ endpoints documented informally; no formal OpenAPI spec.
- **Resolution:** Produce formal OpenAPI 3.1 spec (15-20 page document) with:
  - All REST endpoints (method, path, request/response schemas)
  - WebSocket endpoints (connection, events, message format)
  - Error responses (4XX, 5XX codes + payloads)
  - Authentication (passphrase JWT schema)
  - CORS policy
- **Owner:** Amelia  
- **Target Date:** Feb 28, 2026

✅ **Blocker 2: Error Codes**
- **Issue:** Developers don't know error response format; frontend can't map errors to UX.
- **Resolution:** Error codes catalog:
  - 50+ error codes (1XXX agent errors, 2XXX workflow errors, 3XXX security errors, 4XXX system errors)
  - Each code: HTTP status, error message, UX action (retry, notify, fallback)
  - Example: `{ "error_code": "WF_002", "message": "Workflow timeout after 300s", "ux_action": "suggest retry", "retry_allowed": true }`
- **Owner:** Amelia, Quinn  
- **Target Date:** Feb 28, 2026

✅ **Blocker 3: Test Criteria**
- **Issue:** No agreed definition of "done"; tests pass by accident.
- **Resolution:** Test infrastructure:
  - pytest configuration (fixtures, plugins, test templates)
  - Unit test template (agent test, endpoint test, model test)
  - Integration test template (end-to-end workflow, agent composition)
  - Performance test template (latency <500ms, throughput >1000 msg/sec)
  - Coverage threshold: >80% for libs, >70% for apps
- **Owner:** Quinn  
- **Target Date:** Feb 28, 2026

✅ **Blocker 4: Sign-off Process**
- **Issue:** Who approves before coding? No gate.
- **Resolution:** 
  - Amelia (Backend Lead) reviews and approves: API contract, DB schema, agent protocol, test criteria
  - Barry (Frontend Lead) reviews and approves: Frontend contract, IPC protocol, error mapping
  - Quinn (QA Lead) reviews: Test plan, coverage targets
  - All three sign off before Sprint 1 begins
- **Owner:** Amelia  
- **Target Date:** Feb 28, 2026  
- **Sign-off Checklist:**
  - [ ] API contract reviewed by Backend Lead
  - [ ] Error codes approved by Backend + Frontend Leads
  - [ ] DB schema approved by DBA (if external) or Backend Lead
  - [ ] Test criteria approved by QA Lead
  - [ ] All team members understand sprint plan
  - [ ] Risks identified + mitigation plans assigned

#### Success Criteria

✅ OpenAPI 3.1 spec generated (>90% endpoint coverage)  
✅ Error codes catalog complete (50+ codes, mapped to UX actions)  
✅ Test infrastructure ready (pytest, CI templates)  
✅ All sign-offs collected (no showstoppers, dependencies clear)  
✅ Sprint 1 stories ready to work (no API ambiguity)  

---

### SPRINT 1: API CONTRACT & BACKEND SCAFFOLD

**Duration:** 1 week (Mar 3–7, 2026)  
**Sprint Goal:** Produce working FastAPI server with database connection and basic API endpoints.  
**Velocity Target:** 18 pts  
**Team:** Amelia (Backend Lead)  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 7.1 | API Server Setup (FastAPI) | Epic 7 | 5 | Amelia | Sprint 0 | Not Started |
| 7.2 | Database Setup (SQLite/PostgreSQL) | Epic 7 | 5 | Amelia | Sprint 0 | Not Started |
| 7.3 | WebSocket Real-time | Epic 7 | 5 | Amelia | 7.1 | Not Started |
| 7.4 | Health Check Endpoint | Epic 7 | 3 | Amelia | 7.1 | Not Started |

**Total Sprint 1 Pts:** 18  

#### Sprint 1 Detailed User Story Breakdown

##### 7.1: API Server Setup (FastAPI)

```yaml
Title: Backend API server running on localhost
As a  developer
I want  FastAPI backend serving REST endpoints
So that  frontend can communicate with backend

Story Points: 5
Priority: MUST (MVP)
Owner: Amelia
Complexity: Medium
Depends On: Sprint 0 (sign-offs)

Acceptance Criteria:
  ✓ FastAPI server starts: python -m uvicorn app:app --reload
  ✓ Server listens on localhost:9000
  ✓ Swagger UI accessible: http://localhost:9000/docs
  ✓ CORS enabled for localhost:3000 (React dev server)
  ✓ Basic ping endpoint: GET /api/v1/health → { "status": "ok" }
  ✓ All endpoints documented in OpenAPI spec
  ✓ Error responses follow standard format: { "error_code": "...", "message": "..." }
  ✓ Logging configured (console + file)
  ✓ No startup warnings or errors

Definition of Done:
  - Unit test: Server starts without errors
  - Integration test: ping endpoint responds correctly
  - Manual test: Swagger UI loads, all endpoints listed
  - Documentation: Setup instructions in README
  - All endpoints have proper error handling

Technical Notes:
  - Use FastAPI with async/await support
  - Uvicorn as ASGI server (single worker for dev)
  - pydantic for request/response validation
  - Dependencies: fastapi, uvicorn, pydantic, sqlalchemy, python-dotenv
  - requirements.txt created with version pinning

Dev Checklist:
  - [ ] Create project structure: app/, models/, routes/, schemas/
  - [ ] Set up main.py with FastAPI() instance
  - [ ] Register CORS middleware
  - [ ] Create health check endpoint
  - [ ] Generate requirements.txt
  - [ ] Test locally (Swagger UI loads)
  - [ ] Document setup in README

Estimated Dev Time: 2 days (Amelia)
```

##### 7.2: Database Setup (SQLite/PostgreSQL)

```yaml
Title: Database configured and schema deployed
As a  backend developer
I want  SQLite or PostgreSQL configured with schema initialization
So that  data persists reliably

Story Points: 5
Priority: MUST (MVP)
Owner: Amelia
Complexity: Medium
Depends On: 7.1 (FastAPI must be running)

Acceptance Criteria:
  ✓ SQLite database created at ./data/jarvis.db (dev) or using PostgreSQL (prod config)
  ✓ ORM configured: SQLAlchemy with async support
  ✓ Migration tool ready: alembic for schema versioning
  ✓ Schema v1.0 includes: users, sessions, workflows, steps, audit_log (14 tables)
  ✓ Indexes created: session queries <10ms (cold start)
  ✓ Foreign key constraints enforced
  ✓ Database accessible from FastAPI (connection pool working)
  ✓ Seed data (test workflows) optionally loaded
  ✓ No schema errors on startup

Definition of Done:
  - Unit test: Database connection verified
  - Integration test: CRUD operations work (create user, insert session, etc.)
  - Manual test: Schema introspection (describe table users; output matches spec)
  - Documentation: Schema diagram + table descriptions in wiki
  - Alembic migrations tested (empty DB → v1.0 schema)

Technical Notes:
  - Use SQLAlchemy ORM (async support: sqlalchemy[asyncio])
  - Alembic for migrations (version control for schema)
  - Connection pool: max_overflow=10, pool_pre_ping=True
  - SQLite for dev (simple, no setup), PostgreSQL for prod
  - DB initialization script: python -m app.db.init

Dev Checklist:
  - [ ] Set up SQLAlchemy models (User, Session, Workflow, Step, etc.)
  - [ ] Create Alembic migration environment
  - [ ] Write initial migration (create all tables)
  - [ ] Configure connection string (.env)
  - [ ] Test schema creation (alembic upgrade head)
  - [ ] Verify indexes + constraints
  - [ ] Write db.init() script for seeding test data
  - [ ] Document schema in wiki

DB Schema v1.0 Tables (draft):
  - users: id, username, password_hash, created_at
  - sessions: id, user_id, session_name, created_at, last_accessed
  - workflows: id, user_id, name, description, steps_json, created_at
  - steps: id, workflow_id, step_number, action, status, result, attempt_count
  - results: id, user_id, workflow_id, status, output, created_at
  - audit_log: id, user_id, action, timestamp, details
  - agents: id, name, port, protocol_version, status
  - backgrounds: id, type, data (for learning/patterns)
  - error_log: id, error_code, message, timestamp, user_id
  - settings: id, user_id, key, value
  - screenshots: id, workflow_id, step_id, image_path, timestamp
  - voice_history: id, user_id, transcription, confidence, language, timestamp
  - (2 more for future: notifications, integrations)

Estimated Dev Time: 3 days (Amelia)
```

##### 7.3: WebSocket Real-time

```yaml
Title: WebSocket endpoint for real-time progress updates
As a  frontend developer
I want  WebSocket connection to receive real-time step progress
So that  UI updates without polling

Story Points: 5
Priority: MUST (MVP)
Owner: Amelia
Complexity: Medium
Depends On: 7.1 (FastAPI running)

Acceptance Criteria:
  ✓ WebSocket endpoint: ws://localhost:9000/ws/session/{session_id}
  ✓ Authentication: session_id must be valid (verified from DB)
  ✓ Connection latency: <200ms average, <500ms P99
  ✓ Message format: { "type": "step_progress", "session_id": "...", "step": {...} }
  ✓ Server sends progress every 500ms (or on state change)
  ✓ Client can send keep-alive ping (optional but supported)
  ✓ Graceful disconnect on session end or timeout (>5 min idle)
  ✓ No lost messages (queue if client offline briefly)
  ✓ Error messages sent as: { "type": "error", "error_code": "...", "message": "..." }

Definition of Done:
  - Integration test: WebSocket connects, receives messages
  - Performance test: Message delivery latency <200ms (average)
  - Stress test: 10 concurrent connections, all receive updates
  - Manual test: Chat UI receives progress updates in real-time
  - Documentation: WebSocket API contract in spec

Technical Notes:
  - Use FastAPI WebSockets support (await websocket.accept(), etc.)
  - Message queue (asyncio.Queue) for background tasks sending progress
  - Session validation: look up session_id in DB, confirm active
  - Timeout: close connection if no activity >5 min
  - Use JSON for message encoding

Message Types (defined in API contract):
  - step_progress: { type, session_id, step_id, status, confidence, duration, screenshot_url }
  - workflow_complete: { type, session_id, status, final_screenshot_url, duration_total }
  - error: { type, error_code, message, recoverable }
  - ping: { type } (keep-alive, no response needed)

Dev Checklist:
  - [ ] Create WebSocket endpoint in routes/ws.py
  - [ ] Implement session validation
  - [ ] Set up message queue for progress updates
  - [ ] Add timeout logic (close after 5 min idle)
  - [ ] Test with wscat or similar tool
  - [ ] Integrate with frontend (next sprint)

Estimated Dev Time: 3 days (Amelia)
```

##### 7.4: Health Check Endpoint

```yaml
Title: Health check endpoint for monitoring
As a  ops engineer
I want  GET /api/v1/health to return system status
So that  monitoring systems can detect failures

Story Points: 3
Priority: MUST (MVP)
Owner: Amelia
Complexity: Low
Depends On: 7.1 (FastAPI running)

Acceptance Criteria:
  ✓ Endpoint: GET /api/v1/health → 200 OK
  ✓ Response: { "status": "healthy", "timestamp": "...", "uptime_seconds": 12345, "database": "ok", "version": "1.0.0" }
  ✓ Database connectivity check included (ping DB, measure latency)
  ✓ Version from __version__ constant
  ✓ Response time: <50ms
  ✓ HTTP status 503 if database unreachable

Definition of Done:
  - Unit test: Endpoint responds with correct format
  - Performance test: <50ms response time
  - Integration test: Database check works

Estimated Dev Time: 1 day (Amelia)
```

#### Sprint 1 Milestones

- **Monday (Mar 3):** Kickoff, project structure setup, requirements.txt
- **Tuesday (Mar 4):** FastAPI skeleton + health endpoint done
- **Wednesday (Mar 5):** Database ORM + Alembic migration setup
- **Thursday (Mar 6):** WebSocket endpoint implementation + testing
- **Friday (Mar 7):** Final integration testing, documentation, sprint review

#### Sprint 1 Success Criteria

✅ FastAPI backend runs without errors on localhost:9000  
✅ Swagger docs accessible at /docs  
✅ Database schema v1.0 deployed  
✅ WebSocket connects and sends messages with <200ms latency average  
✅ Health check responsive and includes DB status  
✅ All 4 stories 100% done (AC met, tests pass, docs complete)  

---

### SPRINT 2: BACKEND CORE IMPLEMENTATION

**Duration:** 1 week (Mar 10–14, 2026)  
**Sprint Goal:** Implement orchestrator, agent registry, and core workflow logic.  
**Velocity Target:** 20 pts  
**Team:** Amelia (Backend Lead)  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 7.5 | Agent Registry & Discovery | Epic 7 | 5 | Amelia | 7.1 | Not Started |
| 7.6 | Agent Protocol (REST/WebSocket) | Epic 7 | 8 | Amelia | 7.1 | Not Started |
| 3.1 | Timeout Recovery (L1) | Epic 3 | 5 | Amelia | 7.6 | Not Started |
| 3.2 | Alternative Method (L2) | Epic 3 | 8 | Amelia | 3.1 | Not Started |

**Total Sprint 2 Pts:** 26 (overallocated slightly for momentum; reduce if needed)

---

### SPRINT 3: BACKEND SERVICES & INTEGRATIONS

**Duration:** 1 week (Mar 17–21, 2026)  
**Sprint Goal:** Add authentication, CORS, logging, CI pipeline, test infrastructure.  
**Velocity Target:** 13 pts  
**Team:** Amelia + Quinn  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 5.1 | Passphrase Authentication | Epic 5 | 8 | Amelia | 7.1 | Not Started |
| 7.7 | Monitoring & Logging | Epic 7 | 3 | Quinn | 7.1 | Not Started |
| 7.8 | CI Pipeline & Auto-Deploy | Epic 7 | 2 | Quinn | 7.1 | Not Started |

**Total Sprint 3 Pts:** 13

---

### SPRINT 4: FRONTEND SHELL & IPC

**Duration:** 1 week (Mar 24–28, 2026)  
**Sprint Goal:** Scaffold Electron + React, set up IPC bridge to backend, WebSocket client.  
**Velocity Target:** 13 pts  
**Team:** Barry (Frontend Lead)  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 7.11 | Electron UI Shell | Epic 7 | 5 | Barry | Sprint 1 (API ready) | Not Started |
| 2.1 | Real-Time Step Progress | Epic 2 | 5 | Barry | 7.3 (WebSocket) | Not Started |
| 2.2 | Screenshot Capture & Storage | Epic 2 | 3 | Barry | 2.1 | Not Started |

**Total Sprint 4 Pts:** 13

---

### SPRINT 5: FRONTEND FEATURES & INTEGRATION

**Duration:** 1 week (Mar 31–Apr 4, 2026)  
**Sprint Goal:** Build chat UI, component library, error mapping, E2E integration test.  
**Velocity Target:** 15 pts  
**Team:** Barry (Frontend Lead)  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 2.3 | Step Execution Logging | Epic 2 | 3 | Quinn | 2.1 | Not Started |
| 2.4 | Execution Timeline View | Epic 2 | 5 | Barry | 2.1 | Not Started |
| 2.5 | Per-Step Confidence Score | Epic 2 | 3 | Barry | 2.1 | Not Started |
| 1.8 | Fallback to Text Input | Epic 1 | 2 | Amelia | 7.1 | Not Started |
| TBD | E2E Integration Test | -- | 2 | Quinn | All above | Not Started |

**Total Sprint 5 Pts:** 15

---

### SPRINT 6: VOICE & ERROR RECOVERY (Epic 1 & 3)

**Duration:** 1 week (Apr 7–11, 2026)  
**Sprint Goal:** Hotkey activation, Whisper STT, all 6 recovery levels, voice QA.  
**Velocity Target:** 52 pts (heavy sprint; may span into Sprint 7)  
**Team:** Amelia, Barry, Quinn  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 1.1 | Voice Activation via Hotkey | Epic 1 | 5 | Barry | 7.11 (Electron) | Not Started |
| 1.2 | Whisper STT Transcription | Epic 1 | 8 | Amelia | 1.1 | Not Started |
| 1.3 | Voice Pause & Resume | Epic 1 | 3 | Barry | 1.1 | Not Started |
| 1.4 | Silence Detection | Epic 1 | 5 | Barry | 1.2 | Not Started |
| 1.5 | Voice Confidence Threshold | Epic 1 | 3 | Barry | 1.2 | Not Started |
| 3.3 | Recovery Level 3 (Advanced) | Epic 3 | 8 | Amelia | 3.2 | Not Started |
| 3.4 | Recovery Level 4 (State Rollback) | Epic 3 | 8 | Amelia | 3.3 | Not Started |
| 3.5 | Recovery Level 5 (Alt Workflow) | Epic 3 | 8 | Amelia | 3.4 | Not Started |
| 3.6 | Recovery Level 6 (Escalation) | Epic 3 | 5 | Amelia | 3.5 | Not Started |

**Total Sprint 6 Pts:** 53

---

### SPRINT 7: WORKFLOW EXECUTION (Epic 2 & 4)

**Duration:** 1 week (Apr 14–18, 2026)  
**Sprint Goal:** Workflow save/load, execute with real-time feedback, manage workflows.  
**Velocity Target:** 52 pts  
**Team:** Barry, Amelia  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 4.1 | Save Workflow | Epic 4 | 5 | Barry | 7.2 (DB) | Not Started |
| 4.2 | Load & Execute Workflow | Epic 4 | 8 | Barry | 4.1 | Not Started |
| 4.3 | Workflow Parameters | Epic 4 | 5 | Barry | 4.2 | Not Started |
| 4.4 | Tags & Search | Epic 4 | 5 | Barry | 4.2 | Not Started |
| 4.5 | Pre-built Templates | Epic 4 | 8 | Barry | 4.2 | Not Started |
| 2.6 | Workflow Pause During Execution | Epic 2 | 5 | Amelia | 2.1 | Not Started |
| 3.7 | Advanced Recovery Strategies | Epic 3 | 3 | Amelia | 3.6 | Not Started |
| 3.8 | Recovery Analytics & Reporting | Epic 3 | 3 | Quinn | 3.7 | Not Started |
| 4.6 | Workflow Versioning | Epic 4 | 3 | Amelia | 4.1 | Not Started |
| 4.7 | Export Workflows | Epic 4 | 3 | Barry | 4.1 | Not Started |

**Total Sprint 7 Pts:** 48

---

### SPRINT 8: SECURITY & LEARNING (Epic 5 & 6)

**Duration:** 1 week (Apr 21–25, 2026)  
**Sprint Goal:** Authentication workflow, audit logging, learning system, pattern suggestions.  
**Velocity Target:** 51 pts  
**Team:** Amelia, Barry, Quinn  

#### Stories Assigned

| Story ID | Title | Epic | Pts | Owner | Depends On | Status |
|----------|-------|------|-----|-------|-----------|--------|
| 5.1 | Passphrase Authentication | Epic 5 | 8 | Amelia | 7.1 (already done in Sprint 3, moved here for completeness) | Not Started |
| 5.2 | Locked Mode Activation | Epic 5 | 3 | Amelia | 5.1 | Not Started |
| 5.3 | Brute-Force Protection | Epic 5 | 5 | Amelia | 5.1 | Not Started |
| 5.4 | Request Queue While Locked | Epic 5 | 3 | Amelia | 5.2 | Not Started |
| 5.5 | Audit Logging | Epic 5 | 5 | Quinn | 7.1 | Not Started |
| 5.6 | Session Management | Epic 5 | 3 | Amelia | 5.1 | Not Started |
| 5.7 | Data Encryption (at-rest) | Epic 5 | 5 | Amelia | 7.2 | Not Started |
| 6.1 | Workflow Pattern Learning | Epic 6 | 8 | Barry | 4.2 | Not Started |
| 6.2 | Suggest Workflows | Epic 6 | 5 | Barry | 6.1 | Not Started |
| 6.3 | Confidence Learning | Epic 6 | 5 | Amelia | 1.2 (Whisper confidence) | Not Started |

**Total Sprint 8 Pts:** 50

---

### SPRINT 9: QA, HARDENING & RELEASE

**Duration:** 1 week (Apr 28–May 2, 2026)  
**Sprint Goal:** Final QA, performance optimization, security hardening, installer, CHANGELOG, MVP release.  
**Velocity Target:** 88 pts (QA, testing, polish)  
**Team:** All (Amelia, Barry, Quinn + 1)  

#### Stories Assigned (Modified: QA Tasks, Not User Stories)

| Task | Sub-Task | Pts | Owner | Depends On | Status |
|------|----------|-----|-------|-----------|--------|
| **Automated Testing** | Unit test coverage >80% all libs | 5 | Quinn | All sprints | Not Started |
| | Integration test suite (20+ tests) | 5 | Quinn | All sprints | Not Started |
| | E2E test suite (10+ scenarios) | 5 | Quinn | All sprints | Not Started |
| | Performance test (latency, throughput) | 3 | Quinn | All sprints | Not Started |
| **Manual QA** | Functional QA (all 68 stories) | 12 | Quinn | All sprints | Not Started |
| | Regression test (past sprints) | 5 | Quinn | All sprints | Not Started |
| | Security audit (OWASP Top 10) | 5 | Amelia | All sprints | Not Started |
| **Documentation** | API docs finalization | 3 | Amelia | Sprint 1 | Not Started |
| | User README + installation guide | 5 | Barry | All sprints | Not Started |
| | Developer wiki (setup, architecture) | 3 | All | All sprints | Not Started |
| | CHANGELOG v1.0.0 | 3 | Quinn | All sprints | Not Started |
| **Performance & Hardening** | Latency optimization (<200ms WebSocket) | 5 | Amelia | Sprint 1–8 | Not Started |
| | Memory optimization (no leaks, <500MB at rest) | 3 | Amelia | All sprints | Not Started |
| | Error handling edge cases | 5 | Amelia | All sprints | Not Started |
| | Security hardening (secrets mgmt, logging) | 5 | Amelia | Sprint 3 | Not Started |
| **Installer & Release** | Build installer (Electron + Python backend) | 8 | Barry | Sprint 4 | Not Started |
| | Installer testing (Windows 10, 11) | 5 | Quinn | Installer | Not Started |
| | Release artifacts (ZIP, EXE, SHA256 hashes) | 2 | Barry | Installer | Not Started |
| **Beta Setup** | Private beta invitation list | 2 | Barry | All | Not Started |
| | Beta feedback collection (form, Discord) | 2 | Barry | All | Not Started |
| **Sign-off** | Performance sign-off (latency <200ms) | 2 | Amelia | Perf tests | Not Started |
| | Security sign-off (OWASP audit complete) | 2 | Amelia | Security audit | Not Started |
| | QA sign-off (0 critical bugs, >95% AC pass) | 2 | Quinn | All QA | Not Started |
| **Contingency / Flex** | Bug fixes, unknown unknowns | 8 | All | As needed | Not Started |

**Total Sprint 9 Pts:** ~120 (QA-heavy; points loosely defined, often tracked separately)

---

## DEPENDENCIES & CRITICAL PATH

### Dependency Chain (High-Level)

```
SPRINT 0 (Blockers)
  ↓
SPRINT 1–3 (Backend Foundation)
  - 7.1: FastAPI (must come first)
  - 7.2: Database (parallel with 7.1)
  - 7.3: WebSocket (depends on 7.1)
  - 5.1: Auth (depends on 7.1)
  ↓
  Need: API contract + backend running
  ↓
SPRINT 4 (Frontend Shell)
  - 7.11: Electron (depends on 7.1 to call)
  - 2.1: Progress display (depends on 7.3 WebSocket)
  ↓
  Need: Frontend can connect to backend
  ↓
SPRINT 5 (Frontend Features + Integration)
  - 2.3, 2.4, 2.5: Enhanced UI (depends on 2.1)
  - 1.8: Text input fallback (independent)
  ↓
  Need: E2E test passing (send command, see progress)
  ↓
SPRINT 6 (Voice)
  - 1.1: Hotkey (depends on 7.11 Electron)
  - 1.2: Whisper STT (depends on 1.1)
  - 1.3–1.5: Voice refinements (depend on 1.2)
  ↓
SPRINT 6 (Error Recovery)
  - 3.1–3.2: Core recovery (depend on 7.6 agent protocol)
  - 3.3–3.6: Advanced recovery (linear dependency chain)
  ↓
  Need: Both voice and recovery L1–L6 tested
  ↓
SPRINT 7 (Workflow Management)
  - 4.1–4.5: Save, load, search, templates (depend on 7.2 database)
  ↓
SPRINT 8 (Security & Learning)
  - 5.2–5.7: Security features (depend on 5.1 passphrase)
  - 6.1–6.3: Learning (depend on 4.2 workflow load + 1.2 confidence)
  ↓
SPRINT 9 (Release)
  - All dependent work complete
  - QA, polish, installer
```

### Critical Path

**Longest chain (determines minimum timeline):**

```
Sprint 0: Blockers (1 week)
  ↓
Sprint 1: FastAPI (7.1) + WebSocket (7.3) (1 week)
  ↓
Sprint 4: Electron (7.11) + Progress UI (2.1) (1 week)
  ↓
Sprint 6: Voice Hotkey (1.1) + Whisper (1.2) (1 week)
  ↓
Sprint 9: QA + Release (1 week)

**Minimum Timeline: 5 sprints = ~5 weeks** (Feb 24 – Mar 28, 2026)

**Actual Timeline: 10 sprints = ~10 weeks** (Feb 24 – May 2, 2026)
- Extra sprints needed for backend services, frontend features, recovery levels, security, learning, and comprehensive QA.
```

### Story Dependencies (Detailed)

| Story | Depends On | Reason |
|-------|-----------|--------|
| 7.2 (DB) | 7.1 (API) | Need server running to test DB connection |
| 7.3 (WebSocket) | 7.1 (API) | WebSocket is part of FastAPI server |
| 7.6 (Agent Protocol) | 7.1 (API) | Agents call API endpoints |
| 3.1 (Recovery L1) | 7.6 (Agent Protocol) | Recovery needs agents working |
| 3.2 (Recovery L2) | 3.1 (L1) | Linear dependency: L1 → L2 → L3 … |
| 7.11 (Electron) | 7.1 (API) | UI needs backend API to call |
| 2.1 (Progress) | 7.3 (WebSocket) | Real-time progress delivered via WebSocket |
| 1.1 (Hotkey) | 7.11 (Electron) | Hotkey captured by Electron app |
| 1.2 (Whisper STT) | 1.1 (Hotkey) | Hotkey triggers voice input, then Whisper |
| 4.1 (Save Workflow) | 7.2 (DB) | Workflows persisted in database |
| 4.2 (Load Workflow) | 4.1 (Save) | Must save before can load |
| 5.2 (Locked Mode) | 5.1 (Passphrase) | Passphrase required to unlock |
| 6.1 (Learning) | 4.2 (Load Workflow) | Learning requires saved workflows to analyze |

---

## RISK REGISTER

### High-Risk Items

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|-----------|-------|
| **Whisper STT accuracy <85%** | Medium | High | PoC Whisper on target hardware in Sprint 2; fallback to OpenAI API if needed | Amelia |
| **WebSocket latency >500ms** | Medium | High | Load test in Sprint 1; optimize connection pooling + serialization | Amelia |
| **Agent communication unreliable** | Medium | High | Mock agents in Sprint 2; test error paths exhaustively | Amelia |
| **Recovery chain has infinite loops** | High | Critical | Exhaustive testing (50+ failure scenarios); timeout every recovery attempt | Amelia |
| **Installer fails on Windows 11** | Low | High | Test installer on both Windows 10 & 11 in Sprint 9 | Barry, Quinn |
| **Scope creep (SHOULD features treated as MUST)** | High | High | Strict backlog discipline; SHOULD → Phase 1.1 without negotiation | Amelia |
| **Team member (Amelia) unavailable** | Low | Critical | Cross-train Barry on FastAPI basics; pair programming sessions | Amelia |

### Mitigation Strategies

1. **Whisper PoC:** Run proof-of-concept in Sprint 2 (early validation).
2. **Load Testing:** Every sprint includes latency + throughput benchmarks.
3. **Failure Injection:** Simulate agent crashes, network timeouts, DB errors; verify recovery.
4. **Code Review + Pair Programming:** Pre-commit review for recovery logic (no solo changes).
5. **Installer Testing:** Dual-boot Windows 10/11 VM; test on 3 different hardware configs.
6. **Backlog Discipline:** No story added to current sprint without removing equal-sized story.
7. **Cross-training:** Barry + Idiot's guide to FastAPI basics (knowledge transfer).

---

## SUCCESS CRITERIA

### Phase 0 (Sprint 0) Success

✅ API contract finalized and signed off (no changes after Feb 28)  
✅ Error codes catalog documented (50+ codes mapped to UX)  
✅ Test infrastructure ready (pytest, CI, templates)  
✅ All team members understand sprint plan and dependencies  
✅ No showstoppers or blocking questions remaining  

### MVP Success (Sprints 1–8)

✅ All 32 MUST stories 100% complete (AC met, tests pass, docs done)  
✅ 68 story points completed on schedule (avg 20 pts/sprint × 5 sprints = 100 pts)  
✅ Zero critical bugs (P0) in final QA  
✅ Performance targets met: WebSocket <200ms avg, <500ms P99; backend <500ms per request  
✅ Voice accuracy >85% on standard English (PoC confirmed)  
✅ Recovery chains L1–L6 all tested and working (no infinite loops)  
✅ Installer works on Windows 10 21H2 and Windows 11  
✅ Installer fails gracefully (clear error messages, no silent crashes)  

### Release Readiness (Sprint 9)

✅ Unit test coverage >80% (all libs)  
✅ Integration test coverage 20+ scenarios (0 failures)  
✅ E2E test coverage 10+ user journeys (0 failures)  
✅ Security audit complete (OWASP Top 10, auth/encryption validated)  
✅ CHANGELOG v1.0.0 complete (all features, known issues, credits)  
✅ README with installation + troubleshooting guide  
✅ Installer EXE + SHA256 hash ready  
✅ Private beta list ready (50+ testers)  
✅ All sign-offs collected (Amelia, Barry, Quinn) = "Go" for release  

### Extended Success (Phase 1, Weeks 11–16)

✅ All 36 SHOULD/COULD stories prioritized and groomed  
✅ Next 6-sprint plan produced (teams assigned, dependencies mapped)  
✅ Learning system deployed and learning from user patterns  
✅ Multilingual support (Spanish, German, Japanese)  
✅ Pre-built workflow templates shipped  
✅ Performance targets exceeded (latency <100ms WebSocket, >5k msg/sec throughput)  

---

## APPENDIX: SPRINT VELOCITY TRACKING

### Projected vs. Actual Velocity

| Sprint | Planned Pts | Actual Pts | Variance | Notes |
|--------|------------|-----------|----------|-------|
| Sprint 0 | 0 | TBD | — | Setup / No stories |
| Sprint 1 | 18 | TBD | TBD | API + Backend scaffold |
| Sprint 2 | 26 | TBD | TBD | Orchestrator + recovery L1–L2 |
| Sprint 3 | 13 | TBD | TBD | Auth + logging + CI |
| Sprint 4 | 13 | TBD | TBD | Frontend shell |
| Sprint 5 | 15 | TBD | TBD | Frontend features + E2E |
| Sprint 6 | 52 | TBD | TBD | Voice + recovery L3–L6 (high velocity) |
| Sprint 7 | 48 | TBD | TBD | Workflows + versioning |
| Sprint 8 | 50 | TBD | TBD | Security + learning |
| Sprint 9 | 120 | TBD | TBD | QA, polish, release (no user stories; QA points) |
| **Total** | **355** | **TBD** | **TBD** | **User stories: 320 pts + QA overhead: 35 pts** |

**Note:** Sprint velocity typically improves after Sprint 2–3 (team ramp-up). Sprints 6–8 may be overallocated; consider splitting high-velocity sprints across two weeks or adding a 5th developer.

---

**End of SPRINT_PLANNING_MASTER.md**
