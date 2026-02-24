# JARVIS ARCHITECTURE ↔ SKAD WORKFLOWS MAPPING
## Component-by-Component Integration Strategy

**Date:** February 23, 2026  
**Purpose:** Show exactly which Jarvis components are implemented via which SKAD workflows and story sequence

---

## JARVIS COMPONENT → STORY → SKAD WORKFLOW

### LAYER 1: FOUNDATION (Sprint 1, Weeks 3-4)

#### Component: FastAPI Backend Scaffold
**Jarvis Need:** Async Python server, port 8000, config layer, startup bootstrap  
**SKAD Story:**
```bash
/create-story → "As a developer, I need FastAPI app scaffold 
                 so I can build backend agents"
/dev-story    → Write: main.py, config.py, requirements.txt
/code-review  → Tests: port binding, config loading, startup
```
**Implementation:**
```
jarvis-backend/
├─ main.py                    (FastAPI app + startup)
├─ config.py                  (env-based config)
├─ requirements.txt           (dependencies)
└─ tests/
   └─ test_startup.py
```
**SKAD Guidance:** SKAD's Developer agent suggests async patterns, error handling, logging setup

---

#### Component: Agent Base Class & Registry
**Jarvis Need:** `BaseAgent` interface, self-registration pattern, `execute()` method  
**SKAD Story:**
```bash
/create-story → "As orchestrator, I need agent base class + registry
                 so any agent can be plugged in"
/dev-story    → Write: base.py, registry.py
/code-review  → Tests: registration, interface contract
```
**Implementation:**
```python
# agents/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel

class AgentOutput(BaseModel):
    result: Dict
    confidence: float
    errors: List[str]

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def execute(self, payload: Dict) -> AgentOutput:
        pass

# agents/registry.py
_agent_registry: Dict[str, BaseAgent] = {}

def register(name: str, agent: BaseAgent):
    _agent_registry[name] = agent

def get_agent(name: str) -> BaseAgent:
    return _agent_registry[name]
```
**SKAD Guidance:** Architect agent reviews design for extensibility, suggests dependency injection

---

#### Component: Context Management Agent (CMA)
**Jarvis Need:** Persistent context (messages, execution state, snapshots)  
**SKAD Story:**
```bash
/create-story → "As any agent, I need shared context persistence
                 so I can access conversation + state history"
/dev-story    → Write: context_manager.py, SQLAlchemy models
/code-review  → Tests: CRUD, serialization, snapshot recovery
```
**Implementation:**
```python
# agents/context_manager.py
class ContextManager(BaseAgent):
    async def execute(self, payload: Dict) -> AgentOutput:
        """
        Manage context: conversations, execution logs, snapshots
        Payload: {
            "action": "save|load|snapshot|recover",
            "session_id": str,
            "data": Dict
        }
        """
        if payload["action"] == "save":
            # Store to SQLite
            session = Session()
            msg = ConversationMessage(**payload["data"])
            session.add(msg)
            session.commit()
        elif payload["action"] == "snapshot":
            # Create execution snapshot for backtracking
            snapshot = ContextSnapshot(
                session_id=payload["session_id"],
                state=payload["data"],
                timestamp=now()
            )
            session.add(snapshot)
            session.commit()
        return AgentOutput(result={"ok": True}, confidence=1.0, errors=[])
```
**SKAD Guidance:** SKAD's Data Architect suggests schema, migration strategy, backup patterns

---

#### Component: Orchestrator Main Loop
**Jarvis Need:** Route user input → agents → backtracking on failure  
**SKAD Story:**
```bash
/create-story → "As Jarvis brain, I need orchestrator loop
                 so I can route inputs and handle failures"
/dev-story    → Write: orchestrator.py (recursive state machine)
/code-review  → Tests: routing, failure detection, state transitions
```
**Implementation (High-Level):**
```python
# agents/orchestrator.py
class Orchestrator(BaseAgent):
    async def execute(self, payload: Dict) -> AgentOutput:
        """
        Main loop: route → execute → verify → backtrack on failure
        """
        user_input = payload["query"]
        context = await self.context_manager.load(payload["session_id"])
        
        # Route to RAG
        rag_output = await self.router("RAG", {
            "query": user_input,
            "context": context
        })
        
        # Route to SPA
        spa_output = await self.router("SPA", {
            "steps": rag_output.steps,
            "context": context
        })
        
        # Route to Executor
        backtrack_level = 0
        for step in spa_output.steps:
            try:
                ea_output = await self.router("EA", step)
                await self.context_manager.log_step(ea_output)
            except ExecutionError as e:
                backtrack_level = await self.backtrack(e, step, backtrack_level)
                if backtrack_level > 6:
                    raise
        
        return AgentOutput(result={"status": "complete"}, confidence=1.0)
```
**SKAD Guidance:** Architect suggests state machine diagram, error classification schema

---

#### Component: WebSocket Real-Time Streaming
**Jarvis Need:** 8 message types (start, progress, complete, error, etc.) with <200ms latency  
**SKAD Story:**
```bash
/create-story → "As frontend, I need WebSocket streaming
                 so UI updates in real-time as steps execute"
/dev-story    → Write: websocket.py, 8 message types
/code-review  → Tests: latency <200ms, message integrity
```
**Implementation:**
```python
# api/websocket.py
from enum import Enum
from pydantic import BaseModel

class MessageType(str, Enum):
    EXECUTION_START = "execution_start"
    STEP_PROGRESS = "step_progress"
    STEP_COMPLETE = "step_complete"
    PLANNING_UPDATE = "planning_update"
    ERROR_ALERT = "error_alert"
    CONTEXT_UPDATE = "context_update"
    VOICE_OUTPUT = "voice_output"
    SESSION_SNAPSHOT = "session_snapshot"

class WebSocketMessage(BaseModel):
    type: MessageType
    timestamp: datetime
    payload: Dict
    session_id: str

@app.websocket("/ws/jarvis/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    # Listen for execution updates, broadcast to UI
    async for data in orchestrator.execution_stream(session_id):
        msg = WebSocketMessage(
            type=data["type"],
            timestamp=now(),
            payload=data,
            session_id=session_id
        )
        await websocket.send_json(msg.dict())
```
**SKAD Guidance:** Performance engineer agent suggests latency profiling, compression

---

### LAYER 2: CORE AGENT MESH (Sprint 2, Weeks 5-6)

#### Component: RAG Agent
**Jarvis Need:** Parse user intent, retrieve templates, generate execution plan with reasoning  
**SKAD Story:**
```bash
/create-story → "As orchestrator, I need RAG agent
                 so I can generate execution plans from voice input"
/dev-story    → Implement: intent parsing, template retrieval, qwen2.5:3b inference
/code-review  → Tests: confidence >0.7, JSON valid, no syntax errors
```

#### Component: Clarification Agent
**Jarvis Need:** Ask disambiguating questions when confidence <0.7  
**SKAD Story:**
```bash
/create-story → "As RAG, when confidence is low, I need clarification
                 so the user can disambiguate intent"
/dev-story    → Implement: Question generation, Piper audio synthesis, Whisper input
/code-review  → Tests: confidence improvement, audio quality
```

#### Component: Web Search Agent
**Jarvis Need:** Retrieve real-time info, cache results (24h), no LLM involved  
**SKAD Story:**
```bash
/create-story → "As planning agent, I need web search
                 so I can gather current info (prices, docs, status)"
/dev-story    → Implement: HTTP client, BeautifulSoup parsing, cache layer
/code-review  → Tests: cache hit/miss, parse accuracy, timeout handling
```

#### Component: SPA Agent (Semantic Parameter Annotation)
**Jarvis Need:** Bind user context variables to step parameters  
**SKAD Story:**
```bash
/create-story → "As parameter binder, I need SPA
                 so steps have concrete values (URLs, emails, files)"
/dev-story    → Implement: Placeholder matching, qwen2.5:3b binding
/code-review  → Tests: binding accuracy, missing parameter detection
```

#### Component: SAA Agent (Semantic Action Analyzer)
**Jarvis Need:** Verify app installation, select execution method (PowerShell/RobotJS/API)  
**SKAD Story:**
```bash
/create-story → "As pre-executor, I need SAA
                 so I verify resources and choose execution method"
/dev-story    → Implement: App verification, method selector, resource check
/code-review  → Tests: method selection accuracy, resource warnings
```

**SKAD Guidance (for all 5 agents):** 
- SKAD's UX agent validates agent I/O flows
- SKAD's Architect ensures agent mesh can reach each other (bidirectional)
- SKAD's Scrum Master tracks inter-agent dependencies

---

### LAYER 3: EXECUTION & OBSERVATION (Sprint 3, Week 7)

#### Component: EA Agent (Execution Agent) - "The Hands"
**Jarvis Need:** Perform automation (12 sub-steps per main step: pre-screenshot, execute, poll, post-screenshot, verify, etc.)  
**SKAD Story:**
```bash
/create-story → "As automation engine, I need EA
                 so I can execute PowerShell/RobotJS/API calls + monitor"
/dev-story    → Implement: 12-step pipeline, moondream screenshot analysis, error detection
/code-review  → Tests: idempotency, state change detection, error classification
```

#### Component: OA Agent (Observer Agent)
**Jarvis Need:** Monitor OS state changes (every 3-5s), detect unexpected windows/popups  
**SKAD Story:**
```bash
/create-story → "As background monitor, I need OA
                 so I detect unexpected OS state (crashes, dialogs, etc.)"
/dev-story    → Implement: Screenshot polling, moondream analysis, alert classification
/code-review  → Tests: detection latency, false positive rate, alert accuracy
```

#### Component: Safety Agent
**Jarvis Need:** Hardcoded guardrails (no delete without confirmation, no financial txns, etc.)  
**SKAD Story:**
```bash
/create-story → "As safety layer, I need guardrails
                 so high-risk operations require user confirmation"
/dev-story    → Implement: Rule engine, confirmation prompts, audit logging
/code-review  → Tests: rule enforcement, override capabilities
```

**SKAD Guidance:**
- SKAD's Safety officer (role-based agent) reviews risk matrix
- Suggests guardrails for financial, destructive, privacy-sensitive operations

---

### LAYER 4: REAL-TIME UI & STREAMING (Sprint 4, Week 8)

#### Component: React Frontend with Voice UI (8 States)
**Jarvis Need:** Chat display, VoiceUI animations (listening, thinking, speaking, error, etc.), ExecutionPanel with real-time step tracking  
**SKAD Story (Multiple Stories):**
```bash
/create-story → "As user, I need Chat component
                 so I can see conversation history"
/dev-story    → Implement: Chat display, message types, syntax highlighting
/code-review  → Tests: message rendering, scroll performance

/create-story → "As listener, I need Voice UI animation
                 so I know when Jarvis is listening/thinking/speaking"
/dev-story    → Implement: 8 animated states (Canvas-based), audio-visual sync
/code-review  → Tests: animation smoothness, state transitions

/create-story → "As progress watcher, I need Execution Panel
                 so I see step-by-step progress in real-time"
/dev-story    → Implement: Step tracker, progress bar, log viewer
/code-review  → Tests: WebSocket message handling, lag <200ms
```

#### Component: WebSocket Client (Socket.IO / Native WS)
**Jarvis Need:** Connect to backend, subscribe to session events, render real-time updates  
**SKAD Story:**
```bash
/create-story → "As React component, I need WebSocket client
                 so I receive real-time updates from backend"
/dev-story    → Implement: Socket.IO client setup, event handlers, reconnection logic
/code-review  → Tests: connection resilience, message ordering, fallback (HTTP polling)
```

**SKAD Guidance:**
- SKAD's UX agent validates user interaction flows
- SKAD's Performance engineer suggests optimization (lazy loading, virtualization)

---

### LAYER 5: APP REGISTRY & WORKFLOWS (Sprint 5, Week 9)

#### Component: App Registry Agent
**Jarvis Need:** Scan Windows registry, cache installed apps, provide app inventory  
**SKAD Story:**
```bash
/create-story → "As system discoverer, I need App Registry
                 so I know what apps are installed for planning"
/dev-story    → Implement: Registry scan (WMI), JSON cache, incremental updates
/code-review  → Tests: scan accuracy, cache staleness logic, performance
```

#### Component: Workflow Learner Agent
**Jarvis Need:** Save workflow execution sequences, match user requests to cached workflows, reuse (66% time savings after 1000 cmds)  
**SKAD Story:**
```bash
/create-story → "As learning system, I need workflow persistence
                 so I can save and reuse execution sequences"
/dev-story    → Implement: Workflow CRUD, semantic matching, auto-save on success
/code-review  → Tests: workflow accuracy, match confidence, reuse efficiency
```

#### Component: 6-Level Backtracking System
**Jarvis Need:** Retry with increasing action, escalate to user when necessary  
**SKAD Story:**
```bash
/create-story → "As failure handler, I need 6-level backtracking
                 so I can recover from failures gracefully"
/dev-story    → Implement: 6 levels (retry, fallback, clarify, delegate, escalate, abort)
/code-review  → Tests: level transitions, detection of unrecoverable errors
```

**SKAD Guidance:**
- SKAD's Risk Management agent helps define backtracking thresholds
- SKAD's QA agent validates recovery scenarios

---

### LAYER 6: SETUP & BUNDLING (Sprint 6, Week 10)

#### Component: NSIS Installer (.exe Bundling)
**Jarvis Need:** Single-file installer (FastAPI + Frontend + models + config)  
**SKAD Story:**
```bash
/create-story → "As distribution engineer, I need NSIS installer
                 so end-users run single setup.exe"
/dev-story    → Implement: electron-builder config, model downloader, registry scanner in installer
/code-review  → Tests: installer validation, model integrity, uninstall cleanup
```

#### Component: E2E Testing (10 Workflows)
**Jarvis Need:** Validate real workflows end-to-end  
**SKAD Story (use Test Architect module if available):**
```bash
/create-story → "As QA, I need E2E tests
                 so I validate 10 real workflows work correctly"
/dev-story    → Implement: Selenium/Playwright tests for: create file, send email, etc.
/code-review  → Tests: coverage >80%, performance <5s per workflow
```

**SKAD Guidance:**
- SKAD's QA agent (Quinn) suggests test coverage strategies
- Test Architect (TEA) module provides 34 test patterns

---

## DEPENDENCY GRAPH (Story Sequence)

```
┌─ Foundation
│  ├─ FastAPI Scaffold (F1.1)
│  ├─ Agent Base + Registry (F1.2)
│  ├─ CMA Agent (F1.3)
│  ├─ Orchestrator Stub (F1.4)
│  └─ WebSocket Endpoint (F1.5)
│
├─ Database Layer
│  └─ SQLAlchemy ORM + 11 Tables (F1.6)
│
├─ Core Agents
│  ├─ RAG Agent (F2.1, depends on F1.1-F1.6)
│  ├─ Clarification Agent (F2.2)
│  ├─ Web Search Agent (F2.3)
│  ├─ SPA Agent (F2.4)
│  └─ SAA Agent (F2.5)
│
├─ Execution Layer
│  ├─ EA Agent (F3.1, depends on F2)
│  ├─ OA Agent (F3.2)
│  └─ Safety Agent (F3.3)
│
├─ Frontend & Streaming
│  ├─ React Chat Component (F4.1, depends on F1.5)
│  ├─ Voice UI (8 states) (F4.2)
│  ├─ Execution Panel (F4.3)
│  └─ WebSocket Client (F4.4)
│
├─ Intelligence Layer
│  ├─ App Registry Agent (F5.1, depends on F1-F3)
│  ├─ Workflow Learner (F5.2)
│  └─ Backtracking System (F5.3)
│
└─ Production
   ├─ Bundling (.exe) (F6.1, depends on F4)
   ├─ Model Downloader (F6.2)
   └─ E2E Testing (F6.3, depends on all above)
```

---

## SKAD WORKFLOW ASSIGNMENTS

| Story # | Component | SKAD Path |
|---------|-----------|-----------|
| F1.1-F1.5 | Foundation | `/create-story` → `/dev-story` (Developer Agent guides) |
| F1.6 | Database | `/create-story` → `/dev-story` (Data Architect guides) |
| F2.1-F2.5 | Core Agents | `/create-story` → `/dev-story` (Architect guides design) |
| F3.1-F3.3 | Execution | `/create-story` → `/dev-story` (Performance engineer guides) |
| F4.1-F4.4 | Frontend | `/create-story` → `/dev-story` (UX agent guides) |
| F5.1-F5.3 | Intelligence | `/create-story` → `/dev-story` (Architect guides complexity) |
| F6.1-F6.3 | Production | `/create-story` → `/dev-story` (Ops/Release engineer guides) |

**Ongoing:** `/sprint-status` (daily), `/sprint-review` (weekly), `/skad-help` (blockers)

---

## VALIDATION CHECKLIST (Per Sprint)

**End of Sprint 1:**
```bash
/code-review
✓ FastAPI listening on 8000
✓ Agent registry functional
✓ Context persistence working
✓ WebSocket endpoint accepting connections
✓ ORM models created
✓ Unit tests >80% coverage
```

**End of Sprint 2:**
```bash
✓ RAG agent generates valid step JSON
✓ Clarification agent prompts + accepts input
✓ Web Search caches + retrieves
✓ SPA agent binds parameters
✓ SAA agent selects methods
✓ Agents communicate bidirectionally
```

**End of Sprint 3:**
```bash
✓ EA agent executes PowerShell + RobotJS
✓ Screenshots captured + analyzed
✓ OA detects unexpected windows
✓ Safety guardrails enforce
✓ Errors trigger backtracking
```

**End of Sprint 4:**
```bash
✓ React frontend renders chat
✓ Voice UI animates (8 states)
✓ Execution Panel updates real-time
✓ WebSocket latency <200ms
```

**End of Sprint 5:**
```bash
✓ App Registry scans + caches
✓ Workflow Learner saves + matches
✓ Backtracking (6 levels) works
```

**End of Sprint 6:**
```bash
✓ .exe installation succeeds
✓ Models download + available
✓ E2E tests pass (10 workflows)
✓ Release checklist cleared
```

---

## SUCCESS: READY FOR DELIVERY

**Output:** `JARVIS_AI_Setup_01.exe`  
**Capability:** 13 agents + 8-state Voice UI + real-time streaming + workflow learning + 6-level recovery  
**Quality:** Tested, documented, production-ready  
**Time:** 10 weeks (on track with SKAD guidance)

