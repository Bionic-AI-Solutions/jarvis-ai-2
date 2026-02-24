# JARVIS AI Development Using SKAD Framework
## Integration Strategy & Execution Plan

**Date:** February 23, 2026  
**Purpose:** Leverage SKAD's AI-driven agile workflows to develop Jarvis AI from scratch  
**Status:** Ready to execute

---

## EXECUTIVE SUMMARY

**The Challenge:**
Jarvis AI is a complex, 13-agent Python/FastAPI system with real-time streaming, orchestration, persistence, and workflow learning. The architecture is defined but not implemented.

**The Solution:**
Use **SKAD Method (SKM)** as the **agile orchestrator** to guide development. SKAD's 21+ specialized agents and 50+ workflows provide:
- Structured planning (requirements → architecture → epics → stories)
- Domain-expert guidance (Architect, Developer, UX, Scrum Master agents)
- Intelligent backtracking when obstacles arise
- Real-time sprint tracking and story management
- Testing strategy (Quinn QA + optional Test Architect module)
- Continuous validation and code review workflows

**Key Insight:** SKAD is not a code generator for Jarvis—it's a **process orchestrator** that guides YOUR decisions and implementations. You make the code; SKAD ensures you follow a sound, iterative path.

---

## SECTION 1: HOW SKAD WORKFLOWS MAP TO JARVIS DEVELOPMENT

### Full Planning Path (SKAD Lifecycle for Jarvis)

#### **Phase 1: Requirements & Vision (Week 1)**

**SKAD Workflows to Execute:**

```bash
/product-brief
```

**Goal:** Align on Jarvis's problem, users, and MVP scope

**SKAD will ask:**
- What problem does Jarvis solve? ("Automate desktop tasks via voice")
- Who are the users? ("Professionals, developers, business users")
- What is the MVP? ("Voice command → execution with real-time feedback")
- Success metrics? ("50 distinct workflows, <5s latency, 95% accuracy")

**Output:** Product brief document (SKAD-generated, you iterate)

**Your Action:** Review Jarvis docs, confirm:
- ✅ Problem: Desktop automation via voice + AI agents
- ✅ Users: Desktop users, power users, developers
- ✅ MVP: Voice input + orchestrator + 6 core agents + real-time streaming
- ✅ Success: 10-week delivery, all 13 agents, bundled .exe

**Next:** Run:
```bash
/create-prd
```

---

#### **Phase 2: Requirements Document (Week 1-2)**

**SKAD Workflow:**
```bash
/create-prd
```

**Goal:** Full product requirements with personas, metrics, risks

**SKAD will:**
- Generate user personas (e.g., "Desktop Power User", "Developer Automation", "Business Analyst")
- List acceptance criteria (voice quality, step execution, error handling)
- Identify risks (LLM latency, OS state tracking, context persistence)
- Define non-functional requirements (performance budgets, scalability)

**Your Input (from Jarvis docs):**
- **Personas:** 
  - Developer (uses for automation, testing, CI/CD)
  - Business user (uses for email, scheduling, reporting)
  - IT admin (uses for system management)
- **Acceptance Criteria:**
  - Voice input understood with >90% accuracy
  - Steps executed with real-time feedback (<200ms WebSocket latency)
  - Context persisted across sessions
  - Can recover from step failure via backtracking
- **Risks:**
  - Ollama model timeout (→ fallback to clarification)
  - OS state changes mid-execution (→ OA agent + screenshots)
  - Network failure during web search (→ cache + retry)

**Output:** PRD document (SKAD-generated, your review)

**Next:** Run:
```bash
/create-architecture
```

---

#### **Phase 3: Architecture & Technical Design (Week 2-3)**

**SKAD Workflow:**
```bash
/create-architecture
```

**Goal:** Technical decisions, system design, tech stack validation

**SKAD will ask:**
- Backend language? ("Python + FastAPI, why?")
- Frontend? ("Electron + React")
- Database? ("SQLite + SQLAlchemy")
- Deployment? (".exe bundled with models")
- AI/ML models? ("Ollama local, qwen2.5:3b, Whisper, Piper, moondream")
- Real-time transport? ("WebSocket, SSE fallback, long-polling fallback")

**Your Input (reference Jarvis docs):**
- Backend: **FastAPI** (async, type-safe, WebSocket native)
- Frontend: **Electron + React 18** (Vite build, TS)
- Database: **SQLite + SQLAlchemy** (100% portable)
- Voice: **Whisper (STT) + Piper (TTS)**
- Execution: **PyAutoGUI + RobotJS + PowerShell**
- Vision: **moondream (local 3-bit quantized)**
- LLM: **qwen2.5:3b via Ollama**
- Real-time: **WebSocket (primary), SSE (fallback), long-polling (fallback)**

**Architecture Decisions to Ratify:**
- ✅ 13-agent bidirectional mesh (not linear pipeline)
- ✅ 6-level backtracking (not fail-fast)
- ✅ Persistent context snapshots (recovery on restart)
- ✅ Orchestrator as recursive state machine (not simple event bus)
- ✅ Real-time WebSocket for <200ms latency UI updates

**Output:** Architecture document (SKAD-generated + your refinements)

**Next:** Run:
```bash
/create-epics-and-stories
```

---

#### **Phase 4: Breakdown into Epics & Stories (Week 3)**

**SKAD Workflow:**
```bash
/create-epics-and-stories
```

**Goal:** Slice architecture into prioritized, implementable stories

**SKAD will:**
- Group related work into **epics** (e.g., "Core Agent Mesh", "Real-Time Streaming", "Workflow Learning")
- Break each epic into **user stories** (e.g., "As an orchestrator, I want to route user input to RAG agent so that plans are generated")
- Estimate effort (S/M/L/XL)
- Identify dependencies
- Suggest priority order

**Your Epic Definitions (from Jarvis):**

| Epic | Stories | Estimate | Dependencies |
|------|---------|----------|--------------|
| **F1: Foundation** | FastAPI scaffold, agent base class, agent registry, orchestrator stub | 2 weeks | None |
| **F2: Core Agent Mesh** | RAG, Clarification, Web Search, SPA, SAA agents (not EA yet) | 2 weeks | F1 |
| **F3: Execution Agent** | EA (hands), OA (observer), pre/post screenshots, moondream, step logging | 1.5 weeks | F2 |
| **F4: Context & Persistence** | 11 database tables, context snapshots, session management | 1 week | F1 |
| **F5: Real-Time Streaming** | WebSocket with 8 message types, SSE/polling fallback | 1 week | F1 |
| **F6: Safety & Recovery** | Safety agent, 6-level backtracking, failure detection heuristics | 1 week | F2 + F3 |
| **F7: App Registry & Workflows** | System app scan, app_inventory.json, workflow CRUD, matching | 1 week | F4 |
| **F8: Voice UI & Frontend** | Electron + React, Chat, VoiceUI (8 states), ExecutionPanel, WebSocket client | 2 weeks | F1 + F5 |
| **F9: Setup & Bundling** | NSIS installer, model downloader, registry scanner, .exe packaging | 1 week | All above |
| **F10: Testing & Polish** | E2E tests (10 workflows), stress tests, docs | 1 week | All above |

**Total Estimate:** 10-11 weeks (matches Jarvis plan)

**SKAD Output:** Story list with acceptance criteria, assigned owners, sprint assignments

**Next:** Run:
```bash
/sprint-planning
```

---

#### **Phase 5: Sprint Planning (Week 3-4)**

**SKAD Workflow:**
```bash
/sprint-planning
```

**Goal:** Initialize sprint tracking, assign stories, set velocity

**SKAD will:**
- Ask: team size, sprint length, available capacity
- Auto-create sprint board (ideally integrated with your tool: GitHub, Jira, etc.)
- Assign stories to sprints
- Calculate team velocity

**Your Input:**
- **Team:** 1-2 engineers (you + optional collaborator)
- **Sprint length:** 2 weeks
- **Capacity:** ~80 hours/person/sprint (with breaks)
- **Tool:** GitHub Issues + Projects (or Jira if preferred)

**Sprint 1 Breakdown (Weeks 1-2):**
1. FastAPI scaffold (6h)
2. Agent base class + registry (4h)
3. Orchestrator stub (6h)
4. WebSocket endpoint (4h)
5. SQLAlchemy ORM + 11 tables (8h)
6. RAG agent skeleton (4h)
7. Local dev setup + testing (4h)
8. Buffer/review (4h)

**Output:** Sprint board with cards, assignments, estimated velocity

**Next per story:** Run:
```bash
/create-story → /dev-story → /code-review
```

---

### Phase 6: Development Loop (Weeks 4-10)

**For Each Story:**

#### Step 1: Create Story with Full Context
```bash
/create-story
```

**Example (Story: "Implement RAG Agent"):**

SKAD will ask:
- Story title? ("As orchestrator, I need to route user intent to RAG agent so plan steps are generated")
- Acceptance criteria? ("1. Parse user input into intent + constraints. 2. Invoke qwen2.5:3b with context. 3. Return steps JSON with confidence. 4. Validation: JSON parseable, confidence ≥0.6, no syntax errors.")
- Dependencies? ("Orchestrator, LLM service")
- Edge cases? ("Model timeout, confidence <0.6, missing app, network error")
- Test strategy? ("Unit test: mock input → verify JSON. Integration: real Ollama + context")

**Output:** Story card with full context, linked epics, acceptance criteria

#### Step 2: Implement the Story
```bash
/dev-story
```

**SKAD will:**
- Ask: any blockers? Questions? Do you need the Architect to review?
- Provide implementation tips based on your tech stack
- Offer links to relevant docs
- Suggest code patterns

**You do:**
- Write the Python code (using the Jarvis architecture as spec)
- Write tests
- Validate against acceptance criteria
- Commit to git

**Example RAG Agent Implementation (from Jarvis spec):**
```python
# agents/rag.py
from pydantic import BaseModel
from typing import List, Dict
import ollama

class Step(BaseModel):
    id: int
    action: str
    params: Dict
    rationale: str

class RAGOutput(BaseModel):
    steps: List[Step]
    total_steps: int
    estimated_duration_seconds: float
    confidence: float
    warnings: List[str]

async def execute(input_payload: Dict) -> RAGOutput:
    """
    Transform user intent into structured execution plan.
    
    Input: {
        "query": "Create React calculator app",
        "context": [Message, Message, ...],
        "device_state": {...},
        "installed_apps": [...]
    }
    """
    query = input_payload["query"]
    context = input_payload["context"]
    
    # Embed + retrieve similar templates
    templates = retrieve_workflow_templates(query, top_k=3)
    
    # Generate plan with qwen2.5:3b
    prompt = build_rag_prompt(query, context, templates)
    response = await ollama.generate(
        model="qwen2.5:3b",
        prompt=prompt,
        timeout=15
    )
    
    # Parse steps, validate
    steps = parse_steps_json(response)
    confidence = calculate_confidence(steps, templates)
    
    return RAGOutput(
        steps=steps,
        total_steps=len(steps),
        estimated_duration_seconds=sum(s.estimated_duration for s in steps),
        confidence=confidence,
        warnings=detect_warnings(steps)
    )
```

#### Step 3: Code Review & Validation
```bash
/code-review
```

**SKAD will:**
- Ask: automated tests passing? Code following team standards? Ready for merge?
- Offer quality checklist (type hints, docstrings, error handling, etc.)
- Suggest optimizations

**You do:**
- Verify tests pass
- Check type hints, docstrings
- Ensure error handling matches Jarvis backtracking levels
- Get peer review (if team)
- Merge to main

**Next story:** Repeat `/create-story → /dev-story → /code-review`

---

## SECTION 2: STEP-BY-STEP EXECUTION ROADMAP

### **Week 1: Foundation & Vision**

```bash
# Install SKAD into Jarvis project
cd "E:\Bionic AI\Jarvis AI 3"
npx skad-method install --directory . --modules skm --tools claude-code --yes

# Run initial workflows
/product-brief          # Align on problem, users, MVP
/create-prd            # Full requirements + personas + risks
/create-architecture   # Tech stack + system design validation
```

**Deliverables:**
- Product brief (Jarvis as 13-agent voice automation system)
- PRD with personas (Developer, Business User, IT Admin)
- Architecture document (FastAPI + Electron + SQLite + Ollama confirmed)

---

### **Week 2: Planning & Breakdown**

```bash
/create-epics-and-stories      # Break into 10 epics + 50+ stories
/sprint-planning               # Create Sprint 1-6, assign stories
```

**Deliverables:**
- Epic/story breakdown (F1-F10 as listed above)
- Sprint board with assignments
- Velocity estimate (~16 points/week)

---

### **Weeks 3-10: Development Sprints (6 * 2-week sprints)**

**Pattern per story:**
```bash
/create-story          # Full context + acceptance criteria
/dev-story            # Implement, test, validate
/code-review          # QA + merge
```

**Sprint 1 Examples:**
- Story 1: FastAPI scaffold + config
- Story 2: Agent base class + registry pattern
- Story 3: Orchestrator main loop (stub)
- Story 4: WebSocket endpoint + 8 message types
- Story 5: SQLAlchemy ORM (11 tables)
- Story 6: RAG agent (qwen2.5:3b integration)
- Story 7: Context Management Agent (persistence layer)

**Sprint 2 Examples:**
- Story 8: Clarification Agent (Piper + Whisper)
- Story 9: Web Search Agent (HTTP + caching)
- Story 10: SPA Agent (parameter binding)
- Story 11: SAA Agent (method selection)
- On-demand QA/testing via Quinn (SKAD built-in)

**Subsequent Sprints:**
- Execution Agent (EA) + Observer Agent (OA)
- Real-time streaming + React frontend
- Workflow learning + app registry
- Voice UI animations (8 states)
- NSIS bundling + model downloader
- E2E testing + polish

---

## SECTION 3: OPTIONAL SKAD MODULES FOR JARVIS

### **Module 1: Test Architect (TEA)**

**When to use:** End of sprints 4-5 (coverage + quality gates)

```bash
/tea-strategy          # Risk-based test planning
/tea-automation        # Auto-generate test patterns
/tea-gates             # Release quality gates
```

**Why:** Jarvis has complex failure modes (backtracking, observations, context recovery). TEA's 34 patterns + release gates ensure confidence before bundling .exe.

### **Module 2: SKAD Builder (BMB)**

**When to use:** End of Sprint 6 (custom agent patterns)

```bash
/builder-create-agent          # Template for custom Jarvis agents
/builder-create-workflow       # Template for domain workflows
```

**Why:** Users may want to extend Jarvis with domain-specific agents (code review agents, data analysis agents, etc.) post-launch. BMB shows the pattern.

---

## SECTION 4: CONCRETE NEXT STEPS (THIS WEEK)

### **Step 1: Install SKAD into Jarvis workspace**

```bash
cd "E:\Bionic AI\Jarvis AI 3"
npx skad-method install --directory . --modules skm --tools claude-code --yes
```

**Expected output:** SKAD module files, `/skad-help` command available, `.skad/` folder created.

---

### **Step 2: Run `/skad-help` to confirm**

```bash
/skad-help I'm building Jarvis AI, a desktop automation assistant with 13 AI agents. What's the best way to start?
```

**SKAD will respond** with a tailored roadmap based on Jarvis complexity, suggesting the Full Planning Path.

---

### **Step 3: Start Phase 1 (Requirements)**

```bash
/product-brief
```

**When prompted:**
- **Problem:** "Desktop task automation via natural language voice commands"
- **Users:** "Developers, power users, business professionals"
- **MVP:** "Voice input → AI agents orchestrate actions → real-time visual feedback"
- **Success metric:** "50 distinct workflows, <5s end-to-end latency, 95% voice accuracy"

**Output:** SKAD-generated product brief (in `.skad/docs/` or project root)

---

### **Step 4: Review & iterate PRD**

```bash
/create-prd
```

**Key personas to confirm:**
1. **Developer Automation:** Uses Jarvis to automate testing, build tasks, deployments
2. **Business User:** Uses for email, calendar, data entry, reporting
3. **IT Admin:** Uses for system management, software deployment, monitoring

**Risks SKAD will identify:**
- Model latency (>15s qwen timeout)
- OS state changes (apps crashing mid-execution)
- Context loss (session restart edge case)
- Network failure (web search / Ollama access)

---

### **Step 5: Lock technical architecture**

```bash
/create-architecture
```

**Confirm with SKAD:**
- Backend: FastAPI (Python 3.10+)
- Frontend: Electron + React 18 + TypeScript
- Database: SQLite + SQLAlchemy ORM
- Models: Ollama (local), qwen2.5:3b, Whisper, Piper, moondream
- Real-time: WebSocket (primary), SSE (fallback), long-polling (fallback)
- Deployment: .exe via electron-builder + NSIS

**SKAD output:** Architecture decision document (ratified by framework)

---

### **Step 6: Break into sprints**

```bash
/create-epics-and-stories
/sprint-planning
```

**SKAD will create:**
- 10 epics (F1-F10 from this document)
- 50+ stories (each with acceptance criteria)
- 6 * 2-week sprints
- Sprint board assignments

---

## SECTION 5: TEAM WORKFLOW WITH SKAD

### **Daily Standup:**
```bash
/sprint-status
```
SKAD reports: stories in progress, blockers, velocity, ETA.

### **Weekly Review:**
```bash
/sprint-review
```
SKAD asks: what was completed? What's next? Any course corrections?

### **Sprint Planning (Every 2 Weeks):**
```bash
/sprint-planning
```
SKAD confirms next sprint's stories and assignments.

### **When Stuck:**
```bash
/skad-help I'm blocked on WebSocket real-time latency. How should we debug?
```
SKAD queries the Architect agent, offers guidance (logging strategy, profiling tools, etc.).

---

## SECTION 6: EXPECTED OUTCOMES BY WEEK 10

| Week | Deliverable | Status |
|------|-------------|--------|
| 1 | Product brief, PRD, Architecture locked | ✅ Planned docs |
| 2 | Epics, stories, sprints, velocity | ✅ Sprint board ready |
| 3-4 (Sprint 1) | FastAPI scaffold, agent base, orchestrator stub, RAG agent | ✅ Core runtime |
| 5-6 (Sprint 2) | Clarification, Web Search, SPA, SAA agents | ✅ Mesh foundation |
| 7 (Sprint 3) | EA (execution), OA (observation), moondream integration | ✅ Automation layer |
| 8 (Sprint 4) | Real-time WebSocket streaming, React frontend, Voice UI | ✅ User experience |
| 9 (Sprint 5) | App registry, workflow learning, Safety agent, backtracking (6 levels) | ✅ Intelligence layer |
| 10 (Sprint 6) | NSIS .exe bundling, model downloader, E2E testing, polish | ✅ Production ready |

**Final Output:** `JARVIS_AI_Setup.exe` (single distributable, no setup complexity for end-users)

---

## SECTION 7: KEY SUCCESS METRICS

### **Process Metrics (SKAD tracks):**
- ✅ Velocity per sprint (target: 16-20 points/week)
- ✅ Burndown chart (stories completed vs. planned)
- ✅ Cycle time (story start → code review → merge)
- ✅ Code review turnaround (target: <24h)

### **Product Metrics:**
- ✅ Voice accuracy: >90% (Whisper + context)
- ✅ Latency: <5s end-to-end (transcribe + plan + execute)
- ✅ WebSocket latency: <200ms (step updates)
- ✅ Error recovery: 6-level backtracking reduces user intervention by 70%
- ✅ Workflow reuse: After 1000 commands, 66% time savings (cache hit)

---

## SECTION 8: WHY THIS WORKS

| Aspect | SKAD Contribution | Jarvis Benefit |
|--------|-------------------|----------------|
| **Planning** | Structured PRD, architecture reviews, epic breakdown | No ad-hoc decisions; every feature traced to requirements |
| **Guidance** | 21 agents (Architect, Developer, UX, Scrum Master, etc.) | Expert perspectives without hiring 10 consultants |
| **Risk Management** | Identifies blockers early, suggests backtracking | Avoids rework; saves weeks |
| **Sprint Tracking** | Real-time velocity, burndown, story status | Team always aligned on progress |
| **Code Quality** | Integrated code review workflows, testing checklists | Higher quality, fewer bugs, easier maintenance |
| **Documentation** | Auto-generates requirements, architecture, decisions | Future developers inherit context, decisions, rationale |
| **Adaptability** | `/skad-help` for domain-specific guidance | Custom advice based on Jarvis's complexity (13 agents, ML, voice, etc.) |

---

## FINAL ACTION: START TODAY

**Right now:**

```bash
cd "E:\Bionic AI\Jarvis AI 3"
npx skad-method install --directory . --modules skm --tools claude-code --yes
```

Then:

```bash
/skad-help
```

**SKAD will guide you through the First Planning Path. You'll have a product brief, PRD, architecture decision document, and sprint board by end of week 1.**

**Then:** Open the project in Claude Code (or Cursor/Windsurf) and follow SKAD's `/dev-story` workflow for each story.

**Result:** 10-week delivery of production-ready Jarvis AI.

---

**Status:** Ready to execute. Proceed with SKAD installation and run `/product-brief`.

