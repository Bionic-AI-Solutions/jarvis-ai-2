# JARVIS AI - AI Agent Developer Instructions

## Project Context

**JARVIS AI** is a local desktop automation system with:
- **13-agent bidirectional mesh** orchestrator (planning + execution)
- **FastAPI backend** (async, SQLAlchemy ORM, WebSocket real-time)
- **React frontend** (Electron + Vite)
- **Local LLM inference** (Ollama qwen2.5:3b, moondream vision, Whisper STT)

**Current Status:** Architecture complete, **agent implementations 0% complete** (critical gap)

**Reference:** See `Jarvis_Final_Documents/JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` for complete gap analysis and production roadmap.

---

## Critical Knowledge for AI Agents

### 1. The Big Picture: 13-Agent Orchestration Model

```
USER INPUT (voice/text)
    ↓
PLANNING PIPELINE (5 agents generate execution steps)
├─ RAG Agent: understands intent → structured plan
├─ Clarification: asks clarifying questions if ambiguous
├─ Web Search: finds how-to information
├─ SPA (Semantic Plan Annotator): adds business context
└─ SAA (System-Action-Agent): selects specific actions

    ↓
EXECUTION PIPELINE (real-time feedback loop)
├─ EA (Execution Agent): clicks, types, launches programs
├─ Screenshot: captures current desktop state
├─ moondream (vision): analyzes screenshot
└─ OA (Observer): validates step success

    ↓
SUPPORT AGENTS (safety, recovery, learning)
├─ Safety Agent: blocks dangerous commands
├─ Recovery Engine: 6-level failure backtracking
├─ CMA: manages context persistence across failures
├─ Workflow Learner: remembers & reuses workflows
├─ App Registry: lists installed applications
└─ User Agent: handles input/output
```

**Critical Gap:** Only `Orchestrator` (framework) exists. **All 13 agents need implementation** (~6,200 lines, 3 weeks)

---

### 2. File Structure & Key Components

#### Backend (`backend/app/`)
```
agents/
├── orchestrator.py (401 lines) - Dispatch loop, recovery routing ⚠️ No agents to dispatch to
├── registry.py (209 lines) - Agent registration system (empty)
└── protocol.py - Agent communication interface

services/
├── ollama_service.py ✅ WORKING - LLM calling (tested, 655ms latency)
├── voice_service.py ⚠️ FRAMEWORK - Whisper available check (no transcription code)
├── recovery_engine.py - Recovery levels L1-L6 (structured, callbacks undefined)
└── screenshot_service.py ❌ MISSING - No implementation

routes/
├── agents.py - Agent lifecycle endpoints
├── execution.py - Workflow execution endpoints
├── workflows.py - CRUD for workflows
├── voice.py - Speech endpoints
└── ... (18 route modules total)

core/
├── database.py - SQLAlchemy async setup (18 tables defined)
├── errors.py - ErrorCode enums (screenshot capture errors never triggered)
└── config.py - Has screenshot config, nothing writes to it
```

#### Frontend (`frontend/`)
```
React 18.3.1 + Vite + TypeScript
├── Chat interface (sends text/voice to backend)
├── Execution display (would show real-time steps)
├── Voice UI (listening state)
└── 167 tests passing ✅
```

#### Documentation (`Jarvis_Final_Documents/`)
- `JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md` (5,613 lines) - All specs
- `JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` (NEW) - Implementation roadmap

---

### 3. Implementation Priorities (What's Actually Missing)

| Priority | Component | Status | Why It Matters |
|----------|-----------|--------|----------------|
| 🔴 CRITICAL | All 13 agent classes | 0% | System can't execute anything without them |
| 🔴 CRITICAL | EA (Execution Agent) | 0% | No mouse/keyboard/PowerShell control |
| 🟠 HIGH | Screenshot service | 0% | Vision feedback loop blocked |
| 🟠 HIGH | moondream integration | 0% | Can't analyze screenshots |
| 🟠 HIGH | Recovery engine callbacks | 0% | Failure recovery doesn't work |
| 🟡 MEDIUM | Whisper transcription | 0% | Voice input not processed |
| 🟡 MEDIUM | Workflow learning | 0% | No workflow reuse |
| 🟢 LOW | UI polish | 50% | Can enhance later |

**Before writing code:** Check `JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` Part 2 for what specifically needs implementation.

---

### 4. Critical Patterns & Conventions

#### Agent Pattern (What Every Agent Must Implement)

```python
from app.agents.protocol import BaseAgent

class MyAgent(BaseAgent):
    """All agents inherit from BaseAgent"""
    
    async def process(self, input_data: dict) -> dict:
        """
        REQUIRED: Every agent implements this.
        Takes input from orchestrator, returns result.
        Must handle its own error cases.
        """
        # Your logic here
        return {
            "status": "success",  # or "failure"
            "result": {...},
            "context_updates": {...}
        }
```

**Registration:** Agents auto-register via `registry.register()` on startup (see `backend/app/agents/registry.py`)

#### Async/Await Pattern (Everything is Async)

```python
# ✅ DO: Use async routes, async DB calls
@router.post("/execute")
async def execute_workflow(workflow: WorkflowSchema):
    async with db.session() as session:
        result = await session.execute(...)
    return result

# ❌ DON'T: Block with synchronous calls
# This will freeze the server
workflow = sync_function()  # BAD
```

#### Context Flow (How Data Persists)

```
User Command 
  → RAG Agent writes to context["plan"]
  → EA Agent reads context["plan"], writes context["execution_log"]
  → OA Agent reads context["execution_log"], writes context["observations"]
  → Recovery reads entire context["..."] to decide recovery level

Context stored in: context_snapshots table (schema in core/database.py)
```

**Never lose context on failure** - it's used for recovery/learning.

#### WebSocket Real-Time Updates

```python
# Backend streams execution to frontend
await websocket.send_json({
    "type": "step_executing",
    "step": 3,
    "action": "Click Gmail button",
    "timestamp": datetime.now()
})
```

Frontend listens and updates UI in real-time. See `backend/app/routes/execution.py` for WebSocket implementation.

---

### 5. Development Workflow (Using SKAD Method)

**For implementing ANY agent or feature:**

```bash
# Step 1: Create story with clear acceptance criteria
# (John - Product Manager - does this)
/create-epics-and-stories

# Step 2: Get story assigned to sprint
# (Bob - Scrum Master - does this)
/sprint-planning

# Step 3: Implement story (Amelia - Developer)
/dev-story

# Step 4: Write tests for story (Quinn - QA)
/qa-automate

# Step 5: Review with architect (Winston)
# Approves before merging
```

**NEVER code without a story.** Stories should define:
- What the feature does
- Acceptance criteria (testable)
- Success metrics (tests should pass)

See `Jarvis_Final_Documents/JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` Part 4 for 25-story sprint plan.

---

### 6. Testing Requirements

**Before any PR merge:**

- [ ] All existing tests still pass: `pytest backend/`
- [ ] New tests written for your changes
- [ ] Test acceptance criteria from story (not just "code works")
- [ ] For agents: Unit tests + integration tests with orchestrator

**Test Coverage Target:** >80% (currently 12% - OllamaService only)

```bash
# Run tests locally
cd backend
pytest tests/ -v --cov=app

# Run with specific agent test
pytest tests/test_agents/test_rag_agent.py -v
```

---

### 7. External Dependencies & Configuration

**Models (Downloaded on First Run):**
- `qwen2.5:3b` - LLM reasoning (3.2 GB, local Ollama)
- `whisper-medium` - Speech-to-text (769 MB)
- `moondream` - Vision analysis (2.1 GB, 3-bit quantized)
- `piper` - Text-to-speech (optional, post-launch)

All via Ollama (`http://localhost:11434`)

**Database:** SQLite async (`backend/data/jarvis.db`)

**Frontend Build:** `cd frontend && npm run build` → `dist/`

**Desktop Packaging:** NSIS installer (Windows only for now)

---

### 8. Common Gotchas & Solutions

| Problem | Solution |
|---------|----------|
| "Agents don't exist in registry" | Agents must call `registry.register(self)` on init |
| "Screenshot callback is None" | Recovery engine Level 3 not implemented - this is expected |
| "Whisper transcription fails" | Whisper code doesn't exist - add it to `VoiceService` |
| "moondream analysis missing" | Import not in codebase - create `VisionService` |
| "Tests fail on agent calls" | Mock agents in tests (real agents don't exist yet) |
| "Async function not awaited" | All orchestrator calls must be `await agent.process(...)` |
| "Context lost on failure" | Store to `context_snapshots` table before attempting recovery |

---

### 9. Quick Reference: Key Files to Read

**Understanding Architecture:**
- `Jarvis_Final_Documents/JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md` (complete spec)
- `backend/app/agents/protocol.py` (agent interface)
- `backend/app/agents/orchestrator.py` (how agents are called)

**Understanding Data Flow:**
- `backend/app/core/database.py` (18 tables, context snapshots)
- `backend/app/routes/execution.py` (workflow execution loop)
- `backend/app/services/ollama_service.py` (LLM calling example)

**Understanding What's Missing:**
- `Jarvis_Final_Documents/JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` (gaps + fixes)
- Look at TODO comments: `grep -r "TODO.*agent" backend/`
- Look at mocked functions: `grep -r "pass  # TODO" backend/`

---

### 10. Before Starting Implementation

**Read this first:**
1. `Jarvis_Final_Documents/JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` - Understand what's missing and why
2. This file - Understand architecture and patterns
3. The specific story file - Understand what YOU need to build

**Do NOT:**
- Modify architecture without Winston review
- Write code without story acceptance criteria
- Skip tests (they validate your work)
- Assume agents exist (they don't - Mock them in tests)
- Block with sync operations (use async/await always)

**SKAD Process is Non-Negotiable:**
- Stories first (John defines)
- Sprint plan (Bob organizes)
- Code systematically (Amelia implements)
- Test as you go (Quinn validates)
- Reviews happen (Winston approves)

---

## Summary: How to Be Productive Now

**As an AI Agent, to implement JARVIS features:**

1. **Check Gap Analysis first:** Read `JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` (Part 2) to see what component you're building
2. **Get story from John:** Use `/create-epics-and-stories` to get acceptance criteria
3. **Implement systematically:** Follow agent pattern (inherits BaseAgent, implements process())
4. **Write tests parallel:** Don't code-then-test; test-driven development
5. **Use async patterns:** Everything in this codebase is async
6. **Persist context:** Store execution data to database for recovery
7. **Mock missing pieces:** Other agents don't exist yet; mock them in your tests
8. **Review with Winston:** Architecture decisions need approval before merge

**Reference this document** when implementing any feature. It's your map.

---

*Last Updated: February 24, 2026*  
*Status: Production Readiness Gap Analysis Complete - Ready for Sprint Execution*
