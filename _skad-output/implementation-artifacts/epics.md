# Jarvis AI 3 - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Jarvis AI 3, derived from JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 24 (User Stories) and Part 4 (13-Agent Mesh). It maps what exists vs. what needs building.

## Requirements Inventory

### Functional Requirements

- FR-01: User types/speaks a command in chat → JARVIS plans and executes it autonomously
- FR-02: 13-agent mesh processes commands (RAG → SPA → SAA → EA → OA)
- FR-03: Voice input via Whisper STT with confidence scoring
- FR-04: Desktop automation (PowerShell, pyautogui, file operations)
- FR-05: 6-level backtracking recovery on failures
- FR-06: Safety agent blocks dangerous operations
- FR-07: Workflow save/load/reuse with learning
- FR-08: Real-time execution progress via WebSocket
- FR-09: Security with passphrase authentication
- FR-10: Screenshot + moondream vision verification

### NonFunctional Requirements

- NFR-01: Local-only execution (no cloud dependency)
- NFR-02: qwen2.5:3b via Ollama for all LLM tasks
- NFR-03: <5s voice-to-transcription latency
- NFR-04: >90% STT confidence threshold
- NFR-05: SQLite persistence
- NFR-06: Async everything (FastAPI + asyncio)

### FR Coverage Map

| FR | Epics Covering It |
|----|-------------------|
| FR-01 | Epic 1 (Chat→Agent Pipeline) |
| FR-02 | Epic 2 (Missing Agents) |
| FR-03 | Epic 3 (Voice Input) |
| FR-04 | Epic 1 + Existing EA |
| FR-05 | Epic 4 (Recovery Wiring) |
| FR-06 | Existing Safety Agent |
| FR-07 | Epic 5 (Workflow Learning) |
| FR-08 | Existing WebSocket |
| FR-09 | Existing Auth |
| FR-10 | Epic 2 (Screenshot Agent) |

## What Already Exists (Verified by Code Audit)

| Component | Status | Lines | Quality |
|-----------|--------|-------|---------|
| FastAPI Server + 45 endpoints | ✅ REAL | ~2000 | Production-ready |
| 19 Database Tables (ORM) | ✅ REAL | ~600 | Production-ready |
| RAG Agent (regex + LLM planning) | ✅ REAL | 307 | Good - 13+ regex patterns + qwen2.5 |
| Execution Agent (desktop dispatch) | ✅ REAL | 152 | Good - 18 action mappings |
| Observer Agent (9 verifiers) | ✅ REAL | 303 | Good - file/process verification |
| Safety Agent (blocklists) | ✅ REAL | 334 | Good - hard rules + patterns |
| Orchestrator (step execution) | ✅ REAL | 280 | HTTP dispatch (needs local wiring) |
| Recovery Engine (6 levels) | ✅ REAL | 353 | L1/L2/L5/L6 work; L3/L4 broken |
| Desktop Automation Service | ✅ REAL | 736 | Most substantial - pyautogui/subprocess |
| Ollama Service (LLM interface) | ✅ REAL | 176 | Tested, working |
| Voice Service (Whisper) | ⚠️ PARTIAL | 255 | Ollama path real; local fallback stub |
| Chat Service (CRUD only) | ⚠️ GAP | 100 | Stores messages, NO AI processing |
| WebSocket Infrastructure | ✅ REAL | ~150 | Broadcast + subscribe working |
| Auth/Security System | ✅ REAL | ~300 | Passphrase + lock/unlock + brute-force |
| Frontend (React + Electron) | ✅ REAL | ~3000 | Chat UI, Workflow UI, Voice UI |
| Agent Protocol (message types) | ⚠️ INCOMPLETE | 62 | Message schemas only, no BaseAgent |
| Agent Registry (HTTP health) | ✅ REAL | 175 | Works but agents don't run as services |

## What Does NOT Exist (Critical Gaps)

| Gap | Architecture Section | Impact |
|-----|---------------------|--------|
| **Chat → Agent Pipeline** | Part 4 (full agent mesh) | User messages go nowhere - CRITICAL |
| **Clarification Agent** | §4 Agent 2 | No disambiguation for ambiguous input |
| **Web Search Agent** | §4 Agent 3 | No external info fetching |
| **SPA Agent** | §4 Agent 4 | No semantic annotation of plans |
| **SAA Agent** | §4 Agent 5 | No execution method selection |
| **User Agent** | §4 Agent 9 | No voice/text I/O synchronization |
| **CMA Agent** | §4 Agent 10 | No context management/persistence |
| **App Registry Agent** | §4 Agent 12 | No application discovery |
| **Workflow Learning Agent** | §4 Agent 13 | No workflow reuse |
| **BaseAgent class** | Part 4 preamble | Agents use inconsistent interfaces |
| **Recovery L3/L4 callbacks** | Part 4 Agent 11 | Screenshot/replan recovery broken |
| **Assistant reply generation** | Part 4 full pipeline | Chat stores msg but no AI responds |

## Epic List

- Epic 1: Chat-to-Execution Pipeline (CRITICAL - makes JARVIS actually work)
- Epic 2: Missing Agent Implementations
- Epic 3: Voice Input & Recognition
- Epic 4: Error Recovery & Backtracking Wiring
- Epic 5: Workflow Learning & Reuse
- Epic 6: Security Hardening

---

## Epic 1: Chat-to-Execution Pipeline

**Goal:** When user types a command in JARVIS chat, the full agent mesh processes it and executes desktop automation, returning results to the chat.

### Story 1.1: BaseAgent Protocol & Agent Wiring

As a developer,
I want a consistent BaseAgent interface that all agents implement,
So that the orchestrator can dispatch to any agent uniformly.

**Acceptance Criteria:**

**Given** the protocol.py file exists with message types
**When** I add a BaseAgent abstract class with async process() method
**Then** all existing agents (RAG, EA, Observer, Safety) are refactored to inherit from it
**And** the orchestrator can call any agent via agent.process(input) locally (not HTTP)

### Story 1.2: Chat Message Processing Pipeline

As a user,
I want to type a command in JARVIS chat and get an AI response with execution plan,
So that JARVIS actually processes my requests instead of just storing messages.

**Acceptance Criteria:**

**Given** user sends message "Open Chrome" via chat
**When** the backend receives the message
**Then** RAG Agent processes it → generates execution plan
**And** Safety Agent evaluates the plan
**And** an assistant message is created with the plan summary
**And** the plan is sent to execution pipeline
**And** execution results appear in chat as assistant messages
**And** WebSocket broadcasts real-time step progress

### Story 1.3: Local Orchestrator Dispatch (Replace HTTP with Direct Calls)

As a developer,
I want the orchestrator to call agents directly instead of via HTTP,
So that we don't need agents running as separate microservices.

**Acceptance Criteria:**

**Given** the orchestrator currently dispatches via HTTP POST to localhost:91XX
**When** I refactor dispatch to use direct agent.process() calls
**Then** all agents are called locally within the same FastAPI process
**And** agent results flow through the existing recovery engine
**And** WebSocket broadcasts execution events to frontend

---

## Epic 2: Missing Agent Implementations

**Goal:** Implement the 9 agents that don't exist yet per architecture V3 Part 4.

### Story 2.1: Clarification Agent

As a user,
I want JARVIS to ask clarifying questions when my request is ambiguous,
So that I get better execution results.

**Acceptance Criteria:**

**Given** RAG Agent confidence is <80%
**When** the orchestrator detects low confidence
**Then** Clarification Agent generates 1-2 targeted questions
**And** questions appear in chat as assistant messages
**And** user's answers update the context
**And** RAG Agent re-plans with higher confidence

### Story 2.2: Web Search Agent

As a user,
I want JARVIS to search for current information when needed,
So that plans use up-to-date techniques.

**Acceptance Criteria:**

**Given** RAG Agent needs external info (APIs, frameworks, packages)
**When** Web Search Agent is called
**Then** it returns top 5 results with title, URL, snippet
**And** results are cached for 24 hours
**And** no LLM interpretation is applied to results
**And** 10-second timeout is enforced

### Story 2.3: SPA Agent (Semantic Plan Adapter)

As a developer,
I want plans annotated with preconditions, timeouts, and verification logic,
So that the execution pipeline knows how to verify each step.

**Acceptance Criteria:**

**Given** RAG produces a high-confidence plan
**When** SPA Agent processes it
**Then** each step gets: preconditions, timeout_ms, rollback_hint, expected_ui_change, verification_query
**And** error handling instructions are added per step
**And** the plan structure is not modified

### Story 2.4: SAA Agent (Step-Action Adapter)

As a developer,
I want each step mapped to an execution method with recovery alternatives,
So that EA knows exactly how to execute each step.

**Acceptance Criteria:**

**Given** SPA produces an annotated plan
**When** SAA Agent processes it
**Then** each step gets: primary_method, primary_command, recovery_methods[], timeout_seconds, tools_required[]
**And** CLI/PowerShell is preferred over GUI clicks when more reliable
**And** tool availability is checked before committing

### Story 2.5: User Agent (Interface Bridge)

As a user,
I want seamless voice and text interaction with JARVIS,
So that I can use either input mode.

**Acceptance Criteria:**

**Given** user provides voice or text input
**When** User Agent processes it
**Then** voice is transcribed via Whisper (>90% confidence)
**And** input is routed to appropriate agent
**And** text appears in chat immediately
**And** speech response follows <500ms later

### Story 2.6: CMA Agent (Context Management)

As a developer,
I want persistent context across agent calls and sessions,
So that agents can access shared state and learn from history.

**Acceptance Criteria:**

**Given** any agent produces a result
**When** CMA records the event
**Then** context is stored in SQLite (context_snapshots table)
**And** any agent can query context on demand (<10ms lookup)
**And** context survives restarts
**And** last 10 messages, user preferences, and recent failures are tracked

### Story 2.7: App Registry Agent

As a developer,
I want to know what applications are installed on the system,
So that EA can verify apps exist before trying to launch them.

**Acceptance Criteria:**

**Given** system startup or on-demand request
**When** App Registry Agent scans the system
**Then** it discovers apps from: Program Files, AppData, PATH, Registry
**And** stores results in application_registry table
**And** on-demand lookup: cache hit = instant, cache miss = re-scan
**And** refreshes hourly

### Story 2.8: Workflow Learning Agent

As a user,
I want JARVIS to remember and suggest reusable workflows,
So that I don't repeat the same instructions.

**Acceptance Criteria:**

**Given** a workflow executes successfully
**When** Workflow Learning Agent processes the result
**Then** the execution pattern is auto-saved (Layer 1: silent)
**And** user is prompted to save as named workflow (Layer 2: conscious)
**And** future similar requests trigger suggestions with >95% confidence

---

## Epic 3: Voice Input & Recognition

**Goal:** Implement voice pipeline per architecture V3 Stories 1.1–1.4.

### Story 3.1: Voice Activation via Hotkey

**As a user, I want to press Ctrl+Shift+Alt+S to start voice input.**

### Story 3.2: Whisper STT Transcription

**As a user, I want my voice accurately transcribed to text via Whisper.**

### Story 3.3: Voice Pause & Resume

**As a user, I want to pause and resume voice input.**

### Story 3.4: Silence Detection

**As a user, I want JARVIS to auto-detect when I stop speaking.**

---

## Epic 4: Error Recovery & Backtracking Wiring

**Goal:** Wire up the L3/L4 recovery callbacks that are currently broken.

### Story 4.1: Recovery L3 (Screenshot Verification)

**Given** EA step fails,
**When** L1/L2 fail,
**Then** L3 takes a screenshot, analyzes with moondream, and decides next action.

### Story 4.2: Recovery L4 (Replan)

**Given** L3 fails to recover,
**When** L4 is triggered,
**Then** RAG Agent is called to generate a new plan from current context.

---

## Epic 5: Workflow Learning & Reuse

**Goal:** Implement workflow pattern matching and reuse per architecture V3 Agent 13.

### Story 5.1: Auto-Save Execution Patterns
### Story 5.2: Workflow Suggestion Engine
### Story 5.3: Hybrid Plan Generation

---

## Epic 6: Security Hardening

**Goal:** Per architecture V3 Stories 5.1–5.3.

### Story 6.1: Passphrase Authentication (exists, needs testing)
### Story 6.2: Locked Mode (exists, needs testing)
### Story 6.3: Brute-Force Protection (exists, needs testing)

---

## Sprint Planning

### Sprint 1 (CRITICAL - Make JARVIS Work)
- **Story 1.1**: BaseAgent Protocol & Agent Wiring (3 pts)
- **Story 1.2**: Chat Message Processing Pipeline (8 pts)
- **Story 1.3**: Local Orchestrator Dispatch (5 pts)
- **Story 2.6**: CMA Agent (5 pts)
- **Total**: 21 pts

### Sprint 2 (Complete Agent Mesh)
- **Story 2.1**: Clarification Agent (5 pts)
- **Story 2.2**: Web Search Agent (5 pts)
- **Story 2.3**: SPA Agent (8 pts)
- **Story 2.4**: SAA Agent (8 pts)
- **Total**: 26 pts

### Sprint 3 (Voice + Recovery + Learning)
- **Story 2.5**: User Agent (5 pts)
- **Story 2.7**: App Registry Agent (3 pts)
- **Story 2.8**: Workflow Learning Agent (8 pts)
- **Story 4.1**: Recovery L3 (5 pts)
- **Story 4.2**: Recovery L4 (5 pts)
- **Total**: 26 pts
