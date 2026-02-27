# JARVIS AI – MASTER COMPLETE ARCHITECTURE  
## Full Production-Ready Specification with Complete 13-Agent Mesh Detail, Bundle Specifications & All Operational Design

**Version:** MASTER V2 (Complete, Detailed) 
**Date:** February 24, 2026  
**Status:** **DEFINITIVE SINGLE SOURCE OF TRUTH – USE ONLY THIS DOCUMENT**  
**Consolidates:** Original Complete Architecture (V1) + V2 + Windows-Specific + V3 Redesign + All Discussions  
**Purpose:** Full authoritative specification for Jarvis AI implementation with granular agent definitions, bundle specs, UI details, database schema, API routes, security, testing strategy and implementation roadmap.

---

## TABLE OF CONTENTS

- [EXECUTIVE SUMMARY](#executive-summary)
- [PART 1: SYSTEM OVERVIEW & KEY CONCEPTS](#part-1-system-overview--key-concepts)
- [PART 2: USER INTERFACE DESIGN (3 Modes)](#part-2-user-interface-design-3-modes)
- [PART 3: CORE ARCHITECTURE (5 Tiers)](#part-3-core-architecture-5-tiers)
- [PART 4: 13-AGENT MESH (Complete Definitions)](#part-4-13-agent-mesh-complete-definitions)
- [PART 5: OPERATIONAL MODES & SECURITY](#part-5-operational-modes--security)
- [PART 6: DATABASE SCHEMA (14 Tables)](#part-6-database-schema-14-tables)
- [PART 7: API SPECIFICATION](#part-7-api-specification)
- [PART 8: BUNDLED SETUP & INSTALLATION](#part-8-bundled-setup--installation)
- [PART 9: WINDOWS-SPECIFIC IMPLEMENTATION](#part-9-windows-specific-implementation)
- [PART 10: TESTING STRATEGY](#part-10-testing-strategy)
- [PART 11: PERFORMANCE & LATENCY](#part-11-performance--latency)
- [PART 12: SECURITY & PRIVACY](#part-12-security--privacy)
- [PART 13: IMPLEMENTATION ROADMAP](#part-13-implementation-roadmap)
- [PART 14: GLOSSARY](#part-14-glossary)
- [APPENDIX: DESIGN RATIONALE & RESEARCH](#appendix-design-rationale--research)

---

## EXECUTIVE SUMMARY

**Jarvis AI** is a **locally-run autonomous desktop automation system** that listens to natural language voice commands, plans multi-step workflows using a 13-agent mesh, executes them with real-time visual feedback and automated error recovery, learns from repeated actions, and provides mission-critical security with multi-layer backtracking.

### Key Innovations

1. **13-Agent Mesh Architecture:** Specialized collaborative agents (RAG, Clarification, Web Search, SPA, SAA, EA, OA, Safety, User, CMA, Orchestrator, App Registry, Workflow Learner) with explicit input/output specifications and deterministic failure handling (6-level backtracking).

2. **Bidirectional Communication:** Agents call each other; each knows its exact inputs, outputs, when it fails, and how to escalate to the network for recovery.

3. **Real-Time Streaming UI:** Voice mode (breathing bars + transcript), Chat mode (history + new sessions), Workflows panel (save/load/execute) — all with dual-channel transport showing step-by-step progress with screenshots and confidence scores.

4. **Persistent Context Management:** SQLite-backed conversation history, user preferences, execution logs, failure patterns — survives backend restarts, enables learning.

5. **6-Level Backtracking:** On any failure: Retry (L1), Alternative method (L2), Re-screenshot (L3), GUI refresh (L4), User confirmation (L5), Abort (L6). Fully deterministic.

6. **All-Local Inference:** Whisper (STT), Piper (TTS), qwen2.5:3b (planning), moondream (vision) via Ollama. No cloud calls. User owns all data.

7. **Production-Grade Security:** Passphrase/PIN/voice unlock, request queue (locked mode), PII redaction, audit logging of all sensitive operations, threat-mitigated execution.

### Target Metrics

| Metric | Target |
|--------|--------|
| Command latency (simple) | 15–25s |
| Command latency (with clarification) | 50–80s  |
| Voice transcription accuracy | ≥90% |
| Plan success rate (first-try) | 70% |
| Plan success rate (with backtracking) | 95% |
| WebSocket round-trip | <200ms |
| Memory footprint | 500MB–1.2GB |
| Installation bundle size | ~2.5GB (with models) |

---

# PART 1: SYSTEM OVERVIEW & KEY CONCEPTS

## 1.1 High-Level Flow

```
[USER VOICE/TEXT]
    ↓
[USER AGENT: Capture + Route]
    ↓
[RAG: Plan Generation] → [Clarification Agent: Clarify if needed] 
    ↓                      → [Web Search: External data]
[SPA: Annotate plan]
    ↓
[SAA: Choose execution methods]
    ↓
[ORCHESTRATOR: Dispatcher + Backtracking engine]
    ↓
[EA: Execute step] ← [OA: Monitor + Alert]
    ↓               ← [Safety Agent: Approve/reject]
[CMA: Log & persist] ← [Context management]
    ↓
[ERROR?] → [6-Level Backtracking]
    ↓ YES     (Orchestrator routes through levels 1–6)
    ↓ NO → [USER AGENT: Report success + offer save]
    ↓
[WORKFLOW LEARNER: Optional save]
    ↓
[APP REGISTRY: Pre-verify next requests]
    ↓
[DONE: UI shows completion, TTS plays confirmation]
```

## 1.2 What Each Component Does

| Component | Role | Tech Stack |
|-----------|------|-----------|
| **Voice Mode UI** | Microphone, breathing bars, live transcript | Electron + React, Windows Audio API |
| **Chat Mode UI** | Message history, new sessions, workflows panel | React chat interface |
| **Backend Orchestration** | Agent routing, backtracking, state mgmt | FastAPI (Python), SQLite, async |
| **LLM Models** | Reasoning, planning, classification | qwen2.5:3b, Whisper, Piper, moondream (via Ollama) |
| **Execution Tools** | Click, type, command execution | PowerShell, RobotJS, PyAutoGUI, Windows API |
| **Database** | Persist all state, history, logs | SQLite (14 tables), optional SQLCipher |

---

# PART 2: USER INTERFACE DESIGN (3 MODES)

## 2.1 Voice-First Mode (480×400px)

When user activates voice listening (hotkey, button, or continuous listening):
- **Pure voice interaction**, no text chat, no confusion
- **Beautiful breathing bars** with state animations (idle, listening, audio detected, thinking, speaking, complete, error)
- **Live transcript** updating as user speaks (Whisper streaming with silence detection)
- **Microphone icon** pulsing green when audio detected
- **Control buttons**: Stop Listening, Pause
- **Mode switch** to chat mode always visible

```
┌──────────────────────────────────────────────────────┐
│  ◀  JARVIS  ⚙️                                       │  
├──────────────────────────────────────────────────────┤
│                                                      │
│          [Breathing bars animation]                 │
│          ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▇ ▆ ▅ ▄ ▃ ▂ ▁            │
│          Status: LISTENING...                       │
│          [Pulsing green microphone]                 │
│                                                      │
├──────────────────────────────────────────────────────┤
│  "Open Chrome and go to GitHub"                     │
│                                                      │
├──────────────────────────────────────────────────────┤
│       [🎤 STOP LISTENING] [⏸️ PAUSE]              │
│                                                      │
├──────────────────────────────────────────────────────┤
│  ⚙️ Switch to chat mode   [← Toggle]                │
└──────────────────────────────────────────────────────┘
```

### Voice Indicator State Machine

| State | Visual | Color | Animation | Audio | Duration |
|-------|--------|-------|-----------|-------|----------|
| Idle | Static logo | Gray | None | None | — |
| Listening | 4 breathing bars | Blue | 0.5–1.5 scale, 1.5s cycle | Soft startup tone | Continuous |
| Audio detected | 3 green bars | Green | Animated | None | While speaking |
| Recognized | Green checkmark | Green | Pop + fade | Soft confirm | 1s |
| Thinking | Pulsing orb | Blue | 0.3–1.0 opacity | None | While inferring |
| Speaking (TTS) | 7-bar waveform | Purple | Real-time wave | Piper voice | While playing |
| Error | Red (!) | Red | Pulse | Error beep | 2s |
| Complete | Checkmark + confetti | Green | Confetti shower | Success tone | 2s |

## 2.2 Chat Mode (480×640px)

Full conversational interface with message history (like ChatGPT/Discord):
- **Message history** scrollable, timestamped
- **Live step-by-step narration** as workflow executes
- **Input box** for text + voice button + file attach
- **Mode switch, Save Chat, New Chat, Workflows buttons**

```
┌──────────────────────────────────────────────────────────┐
│  ◀  JARVIS  ☰ [Chat Menu]  ⚙️                          │  
├──────────────────────────────────────────────────────────┤
│                      [ scrollable ]                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Jarvis: Hi! What would you like me to do?      │   │
│  │ 12:34 PM                                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ You: Open Chrome and search GitHub             │   │
│  │ 12:35 PM                                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Jarvis: Planning 5-step workflow...             │   │
│  │ [Step 1/5: Launch Chrome]                       │   │
│  │ [Step 2/5: Navigate to github.com]              │   │
│  │ ✓ Step 1 complete (2.1s, 95% confidence)      │   │
│  │ ⏳ Step 2 in progress... (taking screenshot)   │   │
│  │ 12:36 PM                                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  [Type message...] [🎤 Voice] [📎 Files]              │  
├──────────────────────────────────────────────────────────┤
│  [💾 Save Chat] [🔄 New Chat] [📋 Workflows]          │  
└──────────────────────────────────────────────────────────┘
```

## 2.3 Workflows Panel (480×800px Modal)

Dedicated management panel for saved and scheduled workflows:
- **Tabbed interface**: All Workflows, Favorites, Recent
- **Search & filter** by tag
- **Action buttons** on each workflow: Star (favorite), Delete, Load
- **Workflow metadata**: Last run, step count, confidence, tags
- **Create / Import / Export buttons** at bottom

```
┌──────────────────────────────────────────────────────────┐
│  ◀ Back  |  SAVED WORKFLOWS  |  ⚙️ Settings             │  
├──────────────────────────────────────────────────────────┤
│  📂 All (5)  📂 Favorites (2)  📂 Recent (3)             │  
│  Search: [🔍 Type to filter...]                         │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │ 1. Open Chrome & GitHub Search                 │   │
│  │    Last: 2h ago | ⭐ | 🗑️ | ▶️ Load          │   │
│  │    Steps: 4 | Confidence: 88% | Tags: web,dev  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 2. Check Email & Reply                          │   │
│  │    Last: 1d ago | ☆ | 🗑️ | ▶️ Load           │   │
│  │    Steps: 6 | Confidence: 92% | Tags: email    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  [+ Create New] [Import] [Export All]                  │  
└──────────────────────────────────────────────────────────┘
```

---

# PART 3: CORE ARCHITECTURE (5 TIERS)

```
TIER 0: UI
├─ Electron Main + React Renderer (Voice/Chat/Workflows)
├─ Global Hotkey Hook (Ctrl+Shift+Alt+S)
└─ IPC Bridge to backend

        ↕ (IPC / WebSocket)

TIER 1: ORCHESTRATION
├─ FastAPI Server (localhost:9000)
├─ Orchestrator (State Machine, 6-level backtracking)
└─ Agent Router

        ↕ 

TIER 2: AGENT MESH (13 agents)
├─ RAG (planning), Clarification (QA)
├─ Web Search (data), SPA (annotation), SAA (methods)
├─ EA (execution), OA (monitoring), Safety (guardrails)
├─ User Agent (I/O), CMA (persistence)
├─ Orchestrator (core control)
├─ App Registry (app discovery)
└─ Workflow Learner (pattern reuse)

        ↕

TIER 3: MODELS & TOOLS
├─ qwen2.5:3b (reasoning)
├─ Whisper (STT)
├─ Piper (TTS)
├─ moondream (vision)
├─ Ollama runtime (local inference)
└─ HTTP scraper (web search)

        ↕

TIER 4: AUTOMATION & OS
├─ PowerShell (command execution)
├─ RobotJS (mouse/keyboard)
├─ PyAutoGUI (cross-platform)
├─ Windows API (registry, window management)
└─ WASAPI (audio capture/playback)

        ↕

TIER 5: PERSISTENCE
├─ SQLite (C:\Users\[user]\AppData\Local\Jarvis\jarvis.db)
├─ 14 tables (sessions, messages, workflows, logs, etc.)
├─ Optional SQLCipher (AES-256 encryption)
└─ Windows Registry (config, hotkey binding)
```

---

# PART 4: 13-AGENT MESH (COMPLETE DEFINITIONS)

This section contains the **complete, detailed specification** for every agent. Each agent has:
- **Role** — what it does
- **Model/Tool Used** — technology powering it
- **When Activated** — trigger condition
- **Input Format** — exact JSON schema
- **Exact Responsibilities** — numbered with examples
- **What [Agent] Must NEVER Do** — guardrails
- **Failure Handling** — error cases
- **Output** — JSON response format

---

## Agent 1: RAG Agent (Retriever-Augmented Generator)

**Role:** Strategic planner and workflow architect  
**Model/Tool Used:** qwen2.5:3b (primary reasoning, 8–12s inference via Ollama)  
**When Activated:** User provides task intent; confidence assessment needed  

### Agent Prompt & Persona

```xml
<agent id="rag.agent.yaml" name="RAG" title="Planner" icon="🧠">
<activation critical="MANDATORY">
  <step n="1">Load persona from this file</step>
  <step n="2">Ensure {context} is available via CMA</step>
  <step n="3">Generate a plan using qwen2.5:3b with current context and any search results</step>
  <step n="4">Output structured plan JSON (steps[], confidence, requirements)</step>

  <rules>
    <r>Always call Web Search Agent when the plan contains unknown tools or external APIs.</r>
    <r>If confidence < 80%, trigger Clarification Agent.</r>
    <r>Never proceed without explicit understanding of the end goal.</r>
  </rules>

  <persona>
    <role>Strategic planner and workflow architect</role>
    <communication_style>Concise, structured bullet points</communication_style>
    <principles>- Always ask "What is the end goal?" first.
               - Break complex requests into the simplest sequence.
               - Validate all assumptions before proceeding.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "user_intent": "Create a React calculator with professional UI",
  "context": {
    "previous_goals": [],
    "user_constraints": ["professional", "good UI"],
    "available_tools": ["VS Code", "npm", "Node.js"],
    "session_history": [...]
  }
}
```

### Exact Responsibilities

1. **Analyze Intent:** Extract primary goal, artifacts, and constraints
   - Goal: What is the end state?
   - Artifact: What gets created/modified?
   - Constraints: Professional? Speed? Quality?
   
2. **Call Web Search Agent:**
   - IF plan requires external APIs → Query Web Search immediately
   - IF plan requires framework decision → Query for 2025 best practices
   - IF plan contains "latest" or "modern" → Query for current versions
   - Build search results into plan as references
   
3. **Generate Multi-Step Plan:**
   - Use qwen2.5:3b with 8–12s inference
   - Output structure:
     ```json
     {
       "steps": [
         {"n": 1, "action": "launch_app", "app": "code", "expected": "VS Code ready"},
         {"n": 2, "action": "open_terminal", "tool": "keyboard", "expected": "terminal active"},
         ...
       ],
       "total_steps": 7,
       "confidence": 92,
       "estimated_time_minutes": 5,
       "critical_requirements": ["npm available", "Node.js v18+"],
       "fallback_strategies": {"npm_timeout": "use yarn instead"}
     }
     ```
   
4. **Confidence Assessment:**
   - >95%: Clear, well-defined → Send to SPA immediately
   - 80–95%: Some ambiguity → Send to Clarification Agent first
   - <80%: Major unknowns → Ask user for clarification
   
5. **Constraint Extraction:**
   - Parse context for user preferences: "make it professional" → add ui_style: "professional"
   - Extract timing constraints: "quick" → add speed_priority: true
   - Note conflicting constraints and plan to balance

### What RAG Must NEVER Do
- ❌ Assume unknown tool is available without checking Web Search
- ❌ Create plan >15 steps without explaining why
- ❌ Ignore constraints from conversation context
- ❌ Provide confidence without reasoning
- ❌ Recommend obscure tools without justification

### Failure Handling
- IF qwen2.5:3b times out (>30s): Log timeout, retry with 15s timeout
- IF confidence <50%: Call Clarification Agent, backtrack to Phase 1
- IF plan impossible (e.g., "Delete C:\Windows"): Safety Agent intercepts, reject with reason

### Output to Orchestrator
```json
{
  "status": "plan_ready",
  "plan": {...},
  "next_agent": "spa",
  "context_update": {
    "plan_version": 1,
    "plan_timestamp": "...",
    "plan_rationale": "..."
  }
}
```

---

## Agent 2: Clarification Agent

**Role:** Questioner and disambiguator  
**Model/Tool Used:** qwen2.5:3b (2–3s inference)  
**When Activated:** RAG confidence <80% OR user input ambiguous  

### Agent Prompt & Persona

```xml
<agent id="clarification.agent.yaml" name="Clarifier" title="Clarification" icon="❓">
<activation critical="MANDATORY">
  <step n="1">Load persona</step>
  <step n="2">Receive ambiguous intent or low-confidence plan</step>
  <step n="3">Produce one or two targeted questions using qwen2.5:3b</step>
  <step n="4">Wait for user response</step>
  
  <rules>
    <r>Never ask yes/no questions for open-ended decisions.</r>
    <r>Always assume user may not know technical terms; ask in plain language.</r>
    <r>Max 3 questions per session (user frustration).</r>
  </rules>

  <persona>
    <role>Questioning assistant</role>
    <communication_style>Polite, inquisitive</communication_style>
    <principles>- Never assume; always ask if unsure.
               - Keep questions simple and focused.
               - Accept that user may need multiple rounds.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "ambiguous_request": "Create a form",
 "context": {...},
  "reason_for_clarification": "Too many form types possible"
}
```

### Exact Responsibilities

1. **Generate 1–2 Targeted Questions:**
   - Must be answerable in <30 seconds
   - ✓ Good: "Should this form be for user registration or contact support?" (binary)
   - ✗ Bad: "What do you want?" (too vague)
   
2. **Wait & Capture Response:**
   - User answers via voice or text
   - If voice: Require confidence >90% before proceeding
   - If confidence <90%: Re-ask "I didn't catch that, can you repeat?"
   
3. **Inject Clarification into Context:**
   - Store in CMA: {clarification_q, clarification_a, timestamp}
   - Forward answer to RAG for re-planning
   
4. **Loop Until Sufficient Confidence:**
   - After user answer: Call RAG again
   - IF confidence now >90%: Proceed
   - IF confidence still <80%: Ask follow-up (max 3 questions total)
   - IF still unclear: Escalate: "I need more specific input. What is the primary use case?"

### What Clarification Must NEVER Do
- ❌ Ask yes/no questions for open-ended decisions
- ❌ Assume user knows technical terms ("REST API", "database schema")
- ❌ Ask >3 questions (user frustration)
- ❌ Ask same question twice
- ❌ Proceed with confidence <80% without explicit user confirmation

### Failure Handling
- IF user doesn't respond after 60s: Send to User Agent for re-engagement
- IF transcription confidence <90%: Ask user to type instead
- IF user keeps saying "I don't know": Escalate to Orchestrator → proceed with defaults

### Output
```json
{
  "status": "clarified",
  "original_intent": "...",
  "clarifications": [...],
  "updated_context": {...},
  "next_agent": "rag"
}
```

---

## Agent 3: Web Search Agent

**Role:** Non-LLM fact finder  
**Model/Tool Used:** Internal HTTP scraper + cached results (NO LLM)  
**When Activated:** RAG or any agent needs external information  

### Agent Prompt & Persona

```xml
<agent id="websearch.agent.yaml" name="Web Search" title="Web Search" icon="🌐">
<activation critical="MANDATORY">
  <step n="1">Receive search query string</step>
  <step n="2">Perform HTTP GET against search API or custom scraper</step>
  <step n="3">Return top-5 links with short excerpt</step>
  
  <rules>
    <r>NO interpretation of results (that's for LLM caller).</r>
    <r>ONLY text and URLs; no summaries.</r>
    <r>Respect 24h cache; don't repeat searches.</r>
  </rules>

  <persona>
    <role>Research assistant</role>
    <communication_style>Neutral; provide URLs and snippets only.</communication_style>
    <principles>- Be factual, not opinionated.
               - Return links, not synthesis.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "query": "best React UI library 2025",
  "context_for_results": "professional, polished look"
}
```

### Exact Responsibilities

1. **Execute HTTP Search:**
   - Call search API or custom scraper
   - Extract: title, URL, snippet (2 lines max)
   - Timeout: 10 seconds per query
   - Return exactly top 5 results (no more, no less)
   
2. **Cache Results:**
   - Store results 24 hours in local cache
   - IF duplicate query within 24h → Return cached (instant)
   - Prevents duplicate web calls
   
3. **Output Must Be Concrete:**
   - NO LLM-based summarization
   - ONLY URLs and raw snippets
   - Caller (RAG) interprets results
   
   Example output:
   ```json
   {
     "query": "best React UI library 2025",
     "results": [
       {"rank": 1, "title": "Material UI 6.0", "url": "mui.com", "snippet": "Enterprise-grade UI components..."},
       {"rank": 2, "title": "Shadcn/ui", "url": "ui.shadcn.com", "snippet": "Copy-paste component library..."},
       ...
     ],
     "elapsed_ms": 1200,
     "from_cache": false
   }
   ```

### What Web Search Must NEVER Do
- ❌ Interpret results (that's for qwen2.5:3b)
- ❌ Return >5 results (decision paralysis)
- ❌ Include outdated cached results (>24h)
- ❌ Access restricted content (respect robots.txt)
- ❌ Make requests to suspicious URLs

### Failure Handling
- IF HTTP timeout (>10s): Return cached results if available; else return {} with timeout flag
- IF search API down: Fallback to local knowledge base (pre-loaded common libraries)
- IF no results: Return empty array, let caller decide

### Output
```json
{
  "status": "results_found",
  "query": "...",
  "results": [...],
  "called_agent": "rag"
}
```

---

## Agent 4: SPA Agent (Semantic Plan Adapter)

**Role:** Enrich plan with semantic metadata  
**Model/Tool Used:** qwen2.5:3b (annotation logic, 2–3s)  
**When Activated:** After RAG produces high-confidence plan  

### Agent Prompt & Persona

```xml
<agent id="spa.agent.yaml" name="SPA" title="Plan Adapter" icon="🧩">
<activation critical="MANDATORY">
  <step n="1">Load plan JSON from RAG</step>
  <step n="2">For each step, annotate with tool (e.g. "open_app", "click_ui", "type")
            using qwen2.5:3b</step>
  <step n="3">Send annotated plan to SAA</step>
  
  <rules>
    <r>Never modify core plan structure.</r>
    <r>Always add preconditions and expected UI changes.</r>
    <r>Set realistic timeouts based on task complexity.</r>
  </rules>

  <persona>
    <role>Translator between human intent and execution verbs</role>
    <communication_style>Formal, descriptive</communication_style>
    <principles>- Clarify what each step achieves.
               - Document expected outcomes.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "raw_plan": [
    {"n": 1, "action": "click", "target": "save_button"}
  ]
}
```

### Exact Responsibilities

1. **Annotate Each Step with Metadata:**
   - Add preconditions: "button_visible"
   - Add timeouts: timeout_ms: 3000
   - Add rollback hints: "press_escape"
   - Add expected UI changes: "dialog_closes"
   
   Example:
   ```json
   {
     "action": "click",
     "target": "save_button",
     "n": 1,
     "precondition": "button_visible",
     "timeout_ms": 3000,
     "rollback_hint": "press_escape",
     "expected_ui_change": "dialog_closes",
     "verification_query": "Is dialog closed?"
   }
   ```

2. **Add Error Handling Instructions:**
   - What to do if precondition fails
   - What to do if timeout occurs
   - What to do if UI change doesn't happen

3. **Estimate Resource Requirements:**
   - Will this step need GPU? (moondream analysis)
   - Will this step consume >500MB RAM?
   - Will this step take >5 minutes?
   - Log as warning if yes

### What SPA Must NEVER Do
- ❌ Modify core plan structure
- ❌ Change action types or targets
- ❌ Add preconditions that are impossible to verify
- ❌ Set unrealistic timeouts
- ❌ Assume tools are available without checking

### Failure Handling
- IF impossible to verify precondition: Mark as uncertain, let EA retry
- IF timeout unrealistic: Recalculate based on system specs
- IF resource estimate too high: Flag for user review before execution

### Output
```json
{
  "status": "annotated",
  "annotated_plan": [...],
  "next_agent": "saa"
}
```

---

## Agent 5: SAA Agent (Step-Action Adapter)

**Role:** Execution method chooser
**Model/Tool Used:** qwen2.5:3b (decision logic, 4–6s)  
**When Activated:** After SPA produces annotated plan  

### Agent Prompt & Persona

```xml
<agent id="saa.agent.yaml" name="SAA" title="Action Adapter" icon="⚙️">
<activation critical="MANDATORY">
  <step n="1">Receive annotated plan from SPA</step>
  <step n="2">For each item, choose execution mode via qwen2.5:3b
            (e.g. "use PowerShell" vs "use mouse click")</step>
  <step n="3">Check tool availability (npm in PATH? GPU available?)</step>
  <step n="4">Package decision along with required parameters</step>
  
  <rules>
    <r>Always check tool availability before committing to method.</r>
    <r>Prefer CLI/PowerShell when more reliable than GUI.</r>
    <r>Define recovery methods for each step.</r>
  </rules>

  <persona>
    <role>Execution strategist</role>
    <communication_style>Pragmatic and utilitarian</communication_style>
    <principles>- Choose the most reliable method.
               - Anticipate failures; define backups.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "annotated_steps": [...],
  "system_state": {
    "os": "Windows",
    "gpu_available": true,
    "tools_available": ["powershell", "robotjs", "moondream", "piper"]
  }
}
```

### Exact Responsibilities

1. **For Each Step, Choose Execution METHOD:**
   - PowerShell (CLI operations)
   - RobotJS + moondream (UI clicks + verification)
   - REST API calls (remote operations)
   - Keyboard shortcuts (app interactions)
   - Direct file system operations
   
   Example decision:
   ```
   STEP: "Create React project"
   OPTIONS:
     - Method A: PowerShell `npm create vite`
     - Method B: UI interaction (complex, error-prone)
   DECISION: Use Method A → simpler, more reliable
   CONFIDENCE: 95%
   ```

2. **Estimate Resource Requirements:**
   - Will this step need GPU?
   - Will this step consume >500MB RAM?
   - Will this step take >5 minutes?
   - Log warnings if yes

3. **Check Tool Availability:**
   - Before choosing method, verify tool is available
   - PowerShell: Available? npm in PATH? Git available?
   - RobotJS: Available and working?
   - moondream: GPU available? Model loaded?
   
4. **Add Recovery Methods for Each Step:**
   - Primary: "Use PowerShell npm install"
   - Fallback 1: "If timeout, try with --no-save flag"
   - Fallback 2: "If still fails, try yarn instead"

### What SAA Must NEVER Do
- ❌ Choose method without checking tool availability
- ❌ Default to UI clicks when CLI is more reliable
- ❌ Ignore resource constraints
- ❌ Fail to define recovery methods
- ❌ Choose needlessly complex methods

### Failure Handling
- IF required tool unavailable: Escalate to Orchestrator → suggest alternative or fail
- IF method would timeout: Switch to alternative before attempting
- IF GPU required but unavailable: Use fallback CPU methods

### Output
```json
{
  "status": "execution_methods_chosen",
  "execution_plan": [
    {
      "step_n": 1,
      "action": "launch_app",
      "primary_method": "powershell",
      "primary_command": "code",
      "recovery_methods": [...],
      "timeout_seconds": 5,
      "tools_required": ["powershell"],
      "estimated_resources": {"cpu": "low", "gpu": false, "memory_mb": 10}
    },
    ...
  ],
  "next_agent": "orchestrator->execution_agent"
}
```

---

## Agent 6: Execution Agent (EA)

**Role:** "The hands" — actual GUI and CLI interaction  
**Model/Tool Used:** PowerShell + RobotJS + moondream (vision verification)  
**When Activated:** After SAA provides execution methods  

### Agent Prompt & Persona

```xml
<agent id="ea.agent.yaml" name="EA" title="Executor" icon="🖥️">
<activation critical="MANDATORY">
  <step n="1">Receive step with chosen method from SAA</step>
  <step n="2">Validate prerequisites (apps installed, windows available)</step>
  <step n="3">Execute using PowerShell or RobotJS as directed</step>
  <step n="4">Take screenshot and send to moondream for verification</step>
  <step n="5">Report result to Orchestration Core</step>
  
  <rules>
    <r>ALWAYS take baseline screenshot before action.</r>
    <r>ALWAYS verify with moondream after action.</r>
    <r>Never proceed without confirmation of success.</r>
    <r>Log every attempt (success or failure).</r>
  </rules>

  <persona>
    <role>Automaton / system actuator</role>
    <communication_style>Silent, only logs progress</communication_style>
    <principles>- Be reliable and deterministic.
               - Report faithfully; no assumptions.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "step_n": 3,
  "action": "Create React project",
  "primary_method": "powershell",
  "command": "npm create vite@latest --template react calculator",
  "expected_result": "Project directory created with 127+ packages",
  "verification": "moondream detects 'added X packages' text",
  "timeout_seconds": 60,
  "recovery_methods": [...]
}
```

### Exact Responsibilities: 12-Step Detailed Workflow

```
1. Load step config
2. Validate prerequisites (moondream checks)
3. Take baseline screenshot (before action)
4. Execute command/action (PowerShell or RobotJS)
5. Smart-wait (poll for completion)
6. Take after-action screenshot (after action)
7. Analyze with moondream ("Is target visible?")
8. Verify success (confidence threshold)
9. Detect next step requirements
10. Handle interruption checkpoints
11. Log progress (to CMA)
12. Loop to next step
```

### Execution Specifics

**Command Execution (PowerShell):**
```powershell
$proc = Start-Process -FilePath "npm" `
  -ArgumentList @("create", "vite@latest", ...) -PassThru
$proc.WaitForExit(30000)  # Wait max 30s

# IF SUCCESS → Continue to step 2
# IF TIMEOUT → EA logs timeout, check partial progress, try recovery
```

**UI Click Execution (RobotJS + moondream):**
```
1. moondream analyzes screenshot: "Find 'File' menu"
   Returns: {x: 8, y: 10, width: 45, height: 26, confidence: 0.98}

2. Calculate click coordinate (center of bounding box):
   click_x = 31, click_y = 23

3. CLICK at (31, 23)

4. Wait 500ms for UI response

5. Take screenshot, re-analyze: "Is File menu open?"
   moondream: {menu_open: true, confidence: 0.96}

6. SUCCESS → Proceed to next step
```

### Timeout & Retry Logic
- Attempt 1: Wait for timeout specified in plan
- Attempt 2: +50% longer timeout
- Attempt 3: +100% longer timeout OR use recovery method
- If recovery succeeds: Continue execution
- If all fail: Escalate to Orchestrator for backtracking

### Failure Handling Maps to Backtracking Levels
- Attempt 1 fails → LEVEL 1: Retry
- Attempt 2 fails → LEVEL 2: Try recovery method
- Attempt 3 fails → LEVEL 3: Try alternative method
- No alternatives → LEVEL 4: Replan via SPA
- Replan fails → LEVEL 5: Ask user
- User can't help → LEVEL 6: Mark impossible

### What EA Must NEVER Do
- ❌ Execute without baseline screenshot
- ❌ Ignore moondream verification results
- ❌ Continue after failure without logging reason
- ❌ Click without proper coordinate calculation
- ❌ Skip timeout checks (commands can hang indefinitely)

### Output to Orchestrator
```json
{
  "step_n": 3,
  "action": "Create React project",
  "status": "completed",
  "elapsed_seconds": 12.5,
  "attempts": 1,
  "backtrack_level_used": 0,
  "result": {
    "success": true,
    "verification_score": 0.96,
    "output_text": "added 127 packages in 11.3s",
    "created_artifacts": ["calculator/"],
    "next_step_ready": true
  }
}
```

---

## Agent 7: Observer Agent (OA)

**Role:** Background watchdog monitoring OS events and logs  
**Model/Tool Used:** qwen2.5:3b (semantic classification, <3s per event)  
**When Activated:** Continuous background monitoring during execution  

### Agent Prompt & Persona

```xml
<agent id="oa.agent.yaml" name="Observer" title="Observer" icon="👁️">
<activation critical="MANDATORY">
  <step n="1">Subscribe to OS hooks and log files</step>
  <step n="2">Detect errors or alerts (process crashes, timeouts, resource issues)</step>
  <step n="3">Classify using qwen2.5:3b and send semantic message</step>
  
  <rules>
    <r>Never miss critical errors (crashes, segfaults).</r>
    <r>Don't spam on normal operations (occasional CPU spike is OK).</r>
    <r>Classify before alerting (don't send raw events).</r>
  </rules>

  <persona>
    <role>Watchdog</role>
    <communication_style>Concise alert messages</communication_style>
    <principles>- Stay vigilant.
               - Alert early on anomalies.
               - Don't block; only notify.</principles>
  </persona>
</activation>
</agent>
```

### Input Format (Continuous Monitoring)
```
WindowsEvent: "Process crashed - npm.exe exited with code 1"
FileSystemEvent: "File created - C:\project\package.json"
ProcessEvent: "CPU usage spike - 110% (typical: 20%)"
NetworkEvent: "Connection timeout - localhost:5173"
```

### Exact Responsibilities

1. **Subscribe to Multi-Source Monitoring:**
   - Windows Event Log (process crashes, errors)
   - File system watcher (file creation/deletion)
   - Process monitor (CPU, memory, exit codes)
   - Virtual network monitor (connection timeouts)
   
2. **Detect Anomalies:**
   - Exit code != 0 → Error detected
   - CPU spike >150% baseline → Resource issue
   - Connection timeout → Network issue
   - Unexpected file operations → File access issue
   
3. **Classify with qwen2.5:3b:**
   - Raw event: "npm.exe exited with code 128"
   - Classification: "Git authentication error"
   - Severity: "Warning" or "Critical"
   
4. **Send Semantic Alert to Orchestrator:**
   - Immediate notification of classified anomaly
   - Example: `{ type: "git_auth_error", severity: "warning", affected_step: 3 }`
   
5. **Suggest Recovery:**
   - Example: "npm failed due to git auth. User may need to: 
     1) Configure git credentials, 
     2) Use --legacy-peer-deps flag, 
     3) Use npm cache clean"

### What OA Must NEVER Do
- ❌ Spam alerts for normal operations
- ❌ Miss critical errors (process crashes, segfaults)
- ❌ False alarm on temporary network blips
- ❌ Suggest recovery without understanding error
- ❌ Block execution (only notify)

### Failure Handling
- IF classification fails: Send raw event to Orchestrator for human review
- IF monitor goes offline: Restart, try to recover context
- IF too many alerts: Suppress non-critical to avoid spam

### Output
```json
{
  "event_type": "process_error",
  "detected_event": "npm.exe exited with code 128",
  "classification": "git_authentication_error",
  "severity": "medium",
  "affected_step": 3,
  "suggested_recovery": "Configure git credentials or try alternative package source",
  "escalate_to_orchestrator": true
}
```

---

## Agent 8: Safety Agent

**Role:** Policy enforcement and guardrails  
**Model/Tool Used:** qwen2.5:3b (rule evaluation, 3–5s) + hardcoded rules  
**When Activated:** Before executing any high-risk step  

### Agent Prompt & Persona

```xml
<agent id="safety.agent.yaml" name="Safety" title="Safety" icon="🛡️">
<activation critical="MANDATORY">
  <step n="1">Receive proposed plan or step</step>
  <step n="2">Evaluate against rules using qwen2.5:3b
            (e.g., never delete C:\Windows)</step>
  <step n="3">Approve, modify, or reject the step</step>
  
  <rules>
    <rule type="HARD">Never delete system directories (C:\Windows, C:\Program Files)</rule>
    <rule type="HARD">Never install unsigned executables without user approval</rule>
    <rule type="HARD">Never access sensitive files without audit logging</rule>
    <rule type="HARD">Reject ambiguous commands by default</rule>
    <rule type="SOFT">Warn on risky operations; ask for confirmation</rule>
  </rules>

  <persona>
    <role>Policy guardian</role>
    <communication_style>Firm and rule-based</communication_style>
    <principles>- Safety first; user override requires two-factor confirmation.
               - Log all overrides.
               - Default to reject on ambiguity.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "proposed_action": "delete C:\\Users\\AppData",
  "proposed_command": "rm -r C:\\Users\\AppData",
  "context": {...}
}
```

### Exact Responsibilities

1. **Check Against Safety Rules:**
   
   Hardcoded CRITICAL rules:
   ```
   ✗ DO NOT delete: C:\Windows, C:\Program Files, C:\$Recycle.Bin
   ✗ DO NOT access: Windows Registry without user approval
   ✗ DO NOT install unsigned executables
   ✗ DO NOT download and execute from untrusted sources
   ✗ DO NOT extract/delete system file associations
   ✗ DO NOT change system PATH without user approval  
   ✗ Maximum disk space to consume: 10GB (user's project limit)
   ```

2. **Evaluate Against Rules Using qwen2.5:3b:**
   - Compare: "delete C:\Users\AppData" against rules
   - Safety Agent: "This violates rule: DO NOT delete system directories"
   - Decision: REJECT with reason

3. **For Approved Actions, Add Safeguards:**
   - Delete user file → Create backup first
   - Modify config → Version and timestamp backup
   - Run external script → Analyze it first, confirm with user

4. **User Override (Two-Factor Confirmation):**
   - IF user explicitly says "I want to do that anyway":
   - Require: Confirmation + passphrase
   - Log override attempt (may indicate compromise)

### Branching Logic
```
IF action matches CRITICAL_RULE:
  → REJECT with reason
  → Suggest safe alternative

ELSE IF action matches WARNING_RULE:
  → Ask user: "This action may be risky. Proceed? Y/N"
  → If Y: Add backup/safeguard, proceed
  → If N: Cancel

ELSE:
  → Proceed without safety check
```

### What Safety Agent Must NEVER Do
- ❌ Approve deletion of system directories
- ❌ Approve downloads from untrusted sources
- ❌ Allow bypass of safety rules without 2-factor confirmation
- ❌ Silently change behavior based on context
- ❌ Permit installation of unsigned code

### Failure Handling
- IF classification too uncertain: Default to REJECT (safer)
- IF rule interpretation ambiguous: Escalate to user for approval
- IF user ignores warnings: Log attempt, don't prevent (user responsible)

### Output
```json
{
  "action_evaluated": "delete C:\\project\\node_modules",
  "safety_status": "approved_with_safeguard",
  "reason": "Deleting non-critical, but adding backup first",
  "safeguard_applied": "Backup created at C:\\project\\.backup\\...",
  "user_confirmation_required": false,
  "proceed": true
}
```

---

## Agent 9: User Agent (Interface Bridge)

**Role:** Voice + Text I/O synchronized  
**Model/Tool Used:** Whisper (STT) + Piper (TTS) + qwen2.5:3b (response generation, 5–8s)  
**When Activated:** User provides input or system needs output  

### Agent Prompt & Persona

```xml
<agent id="user.agent.yaml" name="UserIO" title="Interface" icon="💬">
<activation critical="MANDATORY">
  <step n="1">Receive user utterance (text or voice transcript)</step>
  <step n="2">Route to RAG or Clarification as appropriate after context lookup</step>
  <step n="3">Return final text and also send to Piper for TTS if voice mode enabled</step>
  
  <rules>
    <r>Always synchronize voice + text output.</r>
    <r>Verify transcription confidence > 90% or ask user to re-speak.</r>
    <r>Preserve context across voice + text modes.</r>
  </rules>

  <persona>
    <role>User proxy</role>
    <communication_style>Friendly and adaptive</communication_style>
    <principles>- Listen carefully (confirm transcriptions).</principles>
    <principles>- Adapt to user preference (voice-first vs text-first).</principles>
    <principles>- Always be courteous in tone.</principles>
  </persona>
</activation>
</agent>
```

### Input Format (Voice)
```
Raw audio stream (microphone, 16kHz mono)
```

### Input Format (Text)
```
"Create a React calculator"
```

### Exact Responsibilities

1. **Transform Voice Input → Transcription:**
   - Whisper Medium: Audio → Text (2–3s)
   - Confidence check: >90% acceptance, <90% ask to re-speak
   - Store original audio bytes for audit trail
   
2. **Route Input to Orchestration:**
   - Lookup context (CMA): Previous conversation, preferences
   - Determine next agent: RAG for new tasks, SPA if context known
   - Example: User says "Use it for..."
     → CMA looks up: Previous was "Create calculator"
     → Route to: SPA (context already understood)

3. **Synchronize Voice + Text Modes:**
   - User speaks "Create a React app"
   - Display in chat: "You: Create a React app"
   - User can also type while voice processing
   - All inputs stored in unified context (CMA)

4. **Generate & Deliver Response:**
   - Receive response text from Orchestrator
   - Generate voice SIMULTANEOUSLY (Piper TTS):
     - Text appears in chat immediately
     - Speech begins playing <500ms later
     - Dual output reinforces message
   
5. **Handle Corrections:**
   - User says: "That's not what I meant"
   - Transcription saved → User can manually correct
   - Correction stored in context
   - Plan adjusted based on correction

### What User Agent Must NEVER Do
- ❌ Transcribe low-confidence audio without re-asking
- ❌ Generate response without querying CMA for context
- ❌ Lose sync between voice and text output
- ❌ Ignore user's mode preference (voice-first vs text-first)
- ❌ Send malformed input to downstream agents

### Failure Handling
- IF Whisper confidence <80%: "Can you repeat that? I didn't catch it."
- IF audio cuts off mid-sentence: Wait for completion, DON'T truncate
- IF Piper TTS takes >2s to start: Begin sending text while generating audio
- IF user can't provide speech: Fall back to text mode, no error

### Output (To Orchestrator)
```json
{
  "user_input": "Create a React calculator",
  "input_mode": "voice",
  "transcription_confidence": 0.94,
  "context_loaded": true,
  "routed_to_agent": "spa",
  "timestamp": "...",
  "audio_reference": "session_xyz_msg_42.wav"
}
```

---

## Agent 10: Context Management Agent (CMA)

**Role:** Persistent memory and learning system  
**Model/Tool Used:** SQLite (pure database, no LLM)  
**When Activated:** At session start (load context); continuously (save updates)  

### Agent Prompt & Persona

```xml
<agent id="cma.agent.yaml" name="CMA" title="Context Manager" icon="🗄️">
<activation critical="MANDATORY">
  <step n="1">Initialize SQLite connection</step>
  <step n="2">On every request, read/write context records</step>
  <step n="3">Respond to queries from other agents</step>
  
  <rules>
    <r>NEVER lose data; all writes are atomic and persistent.</r>
    <r>Always return fresh data unless explicitly cached.</r>
    <r>Redact sensitive data before passing to other agents.</r>
    <r>Survive backend restarts without data loss.</r>
  </rules>

  <persona>
    <role>Archivist</role>
    <communication_style>Neutral, data-centric</communication_style>
    <principles>- Be reliable; data is sacred.
               - Respond instantly; cache what you can.
               - Learn from patterns.</principles>
  </persona>
</activation>
</agent>
```

### Input Format (Continuous)
```json
{
  "source_agent": "rag",
  "event_type": "plan_created",
  "data": {...plan...},
  "timestamp": "..."
}
```

### Exact Responsibilities

1. **Initialize Session Context:**
   - On session start: Load last 20 messages
   - Load user preferences (learned: language, frameworks, tools)
   - Load recent failures (last 5) to avoid repeats
   - In-memory cache for speed, SQLite as source of truth
   
2. **Record Every Event:**
   - User message: Save to conversation_history
   - Agent request/response: Save to execution_logs
   - Action success/failure: Save to execution_logs + failure_history
   - Context change: Save to context_snapshots (on critical events)
   - Real-time writes (not buffered) to survive crashes
   
3. **Provide Context on Demand:**
   - ANY agent calls CMA.getContext()
   - Returns: Last 10 messages, user prefs, recent failures, current state
   - Format: Compact JSON, <100KB, <10ms lookup
   
4. **Extract and Learn:**
   - Parse conversation history for user preferences
   - "Make it professional" → Store: ui_style: "professional"
   - "Move fast" → Store: priority: "speed"
   - "I use React for everything" → Store: preferred_framework: "React"
   - Learned preferences influence future plans
   
5. **Failure Pattern Analysis:**
   - Track: What types of actions fail? When?
   - Example: "npm timeouts happen 40% on step 3"
   - Use to inform recovery (try yarn faster than retrying npm)
   - Recommend: "Next time, use yarn since npm is slow today"
   
6. **Survive Restarts:**
   - All context in SQLite persists across backend restarts
   - On restart: Load context, resume execution if mid-way
   - No context loss—ever (unless DB corrupted)

### Database Operations (Sample)
```sql
-- EVERY USER INTERACTION:
INSERT INTO conversation_history VALUES (
  session_id: 'xyz',
  timestamp: NOW(),
  speaker: 'user',
  content: 'Create React app',
  input_mode: 'voice'
);

-- EVERY AGENT ACTION:
INSERT INTO execution_logs VALUES (
  session_id: 'xyz',
  timestamp: NOW(),
  step_number: 3,
  agent_name: 'ea',
  action: 'run_command',
  status: 'success',
  result_metadata: JSON({...})
);

-- ON FAILURE:
INSERT INTO failure_history VALUES (
  session_id: 'xyz',
  timestamp: NOW(),
  failure_type: 'npm_timeout',
  agent_name: 'ea',
  recovery_strategy_used: 'retry_with_longer_timeout',
  recovery_success: true
);
```

### What CMA Must NEVER Do
- ❌ Lose data (every write is atomic + persistent)
- ❌ Return stale data (always query fresh unless explicitly cached)
- ❌ Expose sensitive data (filter credentials from logs)
- ❌ Provide incomplete context (always include: history, prefs, failures)
- ❌ Serve gigabytes of data (cap responses to <100KB)

### Failure Handling
- IF SQLite connection fails: Try to reconnect (exponential backoff)
- IF write fails: Queue and retry async
- IF historical data corrupted: Fallback to in-memory cache, alert DevOps
- IF user requests deletion: GDPR-compliant purge (anonymize + delete)

### Output (To Any Requesting Agent)
```json
{
  "session_id": "xyz",
  "current_context": {
    "recent_messages": [...last 10...],
    "user_preferences": {
      "ui_style": "professional",
      "framework": "React",
      "language": "JavaScript",
      "priority": "quality"
    },
    "recent_failures": [
      {"failure_type": "npm_timeout", "recovery": "retry with yarn", "success": true}
    ],
    "current_execution_state": {
      "step_n": 3,
      "step_status": "in_progress",
      "elapsed_seconds": 12
    }
  },
  "lookup_time_ms": 8
}
```

---

## Agent 11: Orchestrator (Core Control Agent)

**Role:** Central coordinator, backtracking engine, failure router  
**Model/Tool Used:** qwen2.5:3b (failure classification, <5s) + state machine (deterministic)  
**When Activated:** Receives plan; routes through execution  

### Agent Prompt & Persona

```xml
<agent id="orchestrator.agent.yaml" name="Orchestrator" title="Orchestration Core" icon="🔗">
<activation critical="MANDATORY">
  <step n="1">Accept plan and context</step>
  <step n="2">Dispatch to appropriate agent(s) in sequence</step>
  <step n="3">Monitor results and classify failures</step>
  <step n="4">Engage 6-level backtracking on error</step>
  <step n="5">Log progress and update execution tracker</step>
  
  <rules>
    <r>Follow 6-level backtracking sequence deterministically (Levels 1–6).</r>
    <r>Never retry infinitely; max 10 attempts per step.</r>
    <r>Detect loops and force Level 5 (user guidance) immediately.</r>
    <r>Maintain context snapshots at each backtrack level.</r>
    <r>Report final status truthfully (success, partial, failed, impossible).</r>
  </rules>

  <persona>
    <role>Aware conductor</role>
    <communication_style>Structured, decisive</communication_style>
    <principles>- Control flow deterministically.
               - Never give up without exhausting recovery options.
               - Respect user's ultimate authority.</principles>
  </persona>
</activation>
</agent>
```

### Input Format
```json
{
  "execution_plan": {...from SAA...},
  "context": {...from CMA...}
}
```

### Exact Responsibilities

1. **Dispatch Agents in Sequence:**
   - Load plan from SAA
   - For each step: Call EA to execute
   - Wait for result (success or failure)
   - Log progress to CMA (every step)
   - Update frontend UI (real-time)

2. **Detect & Classify Failures:**
   - EA reports: `{status: "failed", reason: "command_timeout"}`
   - Classify failure:
     - **TRANSIENT:** Network timeout (5min, try again)
     - **RECOVERABLE:** Non-zero exit code (try alternative)
     - **ESCALATION:** Safety rule violation (ask user)
     - **FATAL:** Missing system dependency (impossible)

3. **Route to Backtracking Level 1–6:**

   **LEVEL 1: RETRY**
   - Same command, same method, +timeout
   - Attempts: 3 (exponential backoff)
   - If succeeds: Continue
   - If fails: Go to LEVEL 2
   
   **LEVEL 2: TRY RECOVERY METHOD**
   - Use recovery method from SAA (e.g., yarn instead of npm)
   - Attempts: 2
   - If succeeds: Continue
   - If fails: Go to LEVEL 3
   
   **LEVEL 3: TRY ALTERNATIVE EXECUTION**
   - Choose different execution tool
   - Example: If PowerShell failed, try API call
   - Attempts: 1
   - If succeeds: Continue
   - If fails: Go to LEVEL 4
   
   **LEVEL 4: REPLAN**
   - Call SPA/SAA again for this step
   - Generate new execution method from scratch
   - Attempts: 1
   - If succeeds: Continue
   - If fails: Go to LEVEL 5
   
   **LEVEL 5: USER GUIDANCE**
   - Send to User Agent: "Step X failed. I need your help."
   - User can: approve retry, modify approach, skip, cancel
   - If user approves: Retry with their guidance
   - If fails: Go to LEVEL 6
   
   **LEVEL 6: MARK IMPOSSIBLE**
   - Log: "Step X impossible to complete"
   - Offer: Skip step, cancel task, investigate manually
   - Store failure reason in CMA for learning

4. **Loop Prevention & Depth Limits:**
   - Track: How many times have we tried step N?
   - Max retries per step: 10 (configurable)
   - Max backtracking levels per step: 6
   - Infinite loop detection: If same step retried >10x, mark impossible

5. **Context Snapshots (Checkpoint System):**
   - Before each backtracking level: Snapshot current state
   - Store in CMA: Step state, failure reason, recovery attempted
   - On success: Keep log; on failure: Use snapshot to rollback if needed

6. **Final Status Report:**

   After execution completes:
   
   ```
   ✅ SUCCESS: 7/7 steps completed in 4m 32s
   - 1 failure detected (step 3: npm timeout)
   - Recovery used: Retry with longer timeout (Level 1)
   - No user intervention needed
   - Artifacts created: /calculator
   
   OR
   
   ❌ FAILED: Step 5 impossible (too many retries)
   - Reason: VS Code terminal not responding
   - Attempts: 9 (max 10)
   - Recommendation: Restart VS Code, try again
   - Logs: /temp/execution_logs_[session]
   ```

### What Orchestrator Must NEVER Do
- ❌ Skip a backtracking level (always follow 1–6 sequence)
- ❌ Retry infinitely (max 10 per step, then mark impossible)
- ❌ Lose context during backtracking (snapshot every level)
- ❌ Ignore user input during Level 5
- ❌ Proceed with unsolved failures (always escalate or mark impossible)

### Failure Handling (Orchestrator's own failures)
- IF qwen2.5:3b times out during classification: Assume TRANSIENT, retry
- IF routing fails: Escalate to User Agent for manual intervention
- IF loop detected: Force escalation to LEVEL 5 immediately

### Output (Final Report to User)
```json
{
  "execution_status": "completed",
  "overall_result": "success",
  "total_elapsed_seconds": 272,
  "steps_completed": 7,
  "steps_failed": 0,
  "failures_encountered": [
    {
      "step_n": 3,
      "failure_type": "command_timeout",
      "backtrack_level_used": 1,
      "recovery_method": "retry_with_timeout_60s",
      "result": "success"
    }
  ],
  "artifacts_created": ["/project/calculator"],
  "user_intervention_required": false,
  "final_message": "React calculator successfully created! Running at localhost:5173"
}
```

---

## Agent 12: System App Registry Agent

**Role:** Application discovery and availability verification  
**Model/Tool Used:** System scanner (pure system introspection, no LLM)  
**When Activated:** At startup (full scan), on-demand, hourly refresh  

### Exact Responsibilities

1. **Full System App Scan (On Startup):**
   
   Scan all app locations:
   ```
   C:\Program Files\
   C:\Program Files (x86)\
   C:\Users\[USER]\AppData\Local\
   C:\ProgramData\
   Environment PATH entries
   Registry: HKEY_LOCAL_MACHINE\SOFTWARE\...\Uninstall
   PowerShell: Get-ChildItem HKLM:\Software\...\App Paths
   ```
   
   Extract details:
   ```json
   {
     "app_name": "Visual Studio Code",
     "aliases": ["code", "vs code", "vscode"],
     "executable_path": "C:\\Users\\Dev\\AppData\\Local\\Programs\\Microsoft VS Code\\Code\\code.exe",
     "installed_version": "1.87.0",
     "launch_command": "code",
     "is_in_path": true
   }
   ```

2. **Cache in Local Database:**
   - Store in SQLite: `installed_apps` table
   - Include: app name, aliases, path, version, launch command
   - Timestamp scan: refresh if older than 1 hour

3. **On-Demand Lookup:**
   - User says: "Open VS Code"
   - Lookup: Does "VS Code" exist in cache?
     - YES → Return path + launch command immediately
     - NO → Scan system again, try again
   - Return: `{app_exists: boolean, path: string, launch_command: string}`

4. **Prevent Wasted Execution:**

   **Example (App Doesn't Exist):**
   ```
   USER: "Open Valorant"
   REGISTRY LOOKUP: Not found in cache
   SAA: "App not installed. Informing user..."
   USER AGENT: "I don't see Valorant installed. Would you like me to help install it?"
   ```
   
   **vs. Old Behavior (Wasted Time):**
   ```
   USER: "Open Valorant"
   EA: "Starting Valorant..."
   (2 minutes wasted trying to launch)
   EA: "Failed — application not responding"
   ```

### Database Schema
```sql
CREATE TABLE installed_apps (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  app_name TEXT NOT NULL,
  aliases TEXT,
  executable_path TEXT NOT NULL,
  launch_command TEXT,
  installed_version TEXT,
  last_scan TIMESTAMP,
  is_in_path BOOLEAN
);
```

### Registry Agent API (For Other Agents)
```python
class SystemAppRegistry:
  async def queryApp(self, app_name: str) -> AppInfo | None:
    # Check cache first
    cached = await self.db.query(
      "SELECT * FROM installed_apps WHERE app_name LIKE ? OR aliases LIKE ?",
      [app_name, app_name]
    )
    if cached.length > 0:
      return cached[0]
    
    # Not in cache, scan system
    await self.scanSystem()
    result = await self.db.query(...)
    return result.length > 0 ? result[0] : None
```

---

## Agent 13: Workflow Knowledge Base & Learning Agent

**Role:** Record and reuse successful execution patterns  
**Model/Tool Used:** SQLite (pure database, no LLM) + qwen2.5:3b for matching  
**When Activated:** After successful execution; on new command (matching)  

### Two-Layer Architecture

**Layer 1: Silent Auto-Save (User Invisible)**
```
Every successful execution:
├─ Automatically recorded in execution_records table
├─ Indexed by: intent, keywords, steps, duration, timestamp
├─ No user action required
└─ System learns silently in background

At T=0: User: "Open VS Code"
        Recorded: {intent: "launch_app", app: "VS Code", steps: [cmd], duration: 4s}

At T=1: User: "Open terminal"
        Recorded: {intent: "open_shell", app: "Terminal", steps: [...], duration: 1s}

Result: Silent knowledge base, ready for reuse
```

**Layer 2: Conscious Workflow Save (User Visible)**
```
After success, prompt:
  "Would you like to save this as a workflow?"

If YES:
  ├─ User names it: "React Calculator Dark Mode"
  ├─ Stored in workflows table (visible in UI)
  ├─ Marked as: user_initiated=true, scheduled_capable=true
  └─ Appears in Workflows panel

If NO:
  ├─ Execution remains in execution_records (silent)
  ├─ Still available for intelligent matching
  └─ User doesn't know it's saved but system uses it
```

### Two-Agent Matching System

**Agent 13A: Exact Workflow Matcher**

```
User Input: "Open VS Code and create a new Python file"

Step 1: Extract intent
  intent="launch_app_and_create", app="VS Code", file_type="Python"

Step 2: Query database
  SELECT workflows WHERE intent MATCH ... AND app = "VS Code"

Step 3: Score & rank
  Workflow #1: "Open VS Code and create Python file" (99% confidence)
  Workflow #2: "Open VS Code and create Node project" (85% confidence)

Step 4: Decision
  IF confidence > 95%:
    → Suggest: "We've done this! Use saved workflow?"
    → User YES → Execute instantly
    → User NO → Continue with Agent 13B

  ELSE:
    → Pass to Agent 13B (Smart Step Recommender)
```

**Agent 13B: Smart Step Recommender**

```
User: "Create React dashboard with Tailwind and export to PDF"
      (No exact workflow exists)

RAG breaks into atomic steps (9 steps total)

Learning Agent cross-checks:
  ✓ Step 1: "Launch VS Code"
    Found in: 150 execution_records (100% exact match)
    Avg duration: 4s | Success rate: 99.2%
    REUSE: YES

  ✓ Step 2: "Create project folder"
    Found in: 89 execution_records
    Avg duration: 2s | Success rate: 97%
    REUSE: YES

  ? Step 8: "Create PDF export component"
    Found in: 2-3 execution_records (not confident)
    Avg duration: 15s
    REUSE: Maybe (only if user approves)

Result: Hybrid plan (70% reused from memory, 30% new planning)
```

---

# PART 5: OPERATIONAL MODES & SECURITY

## 5.1 Six Operational Modes

| Mode | Activation | Behavior | Security |
|------|-----------|----------|----------|
| **Active** | Default (unlocked) | Full command acceptance, real-time execution, UI fully responsive | Standard auth |
| **Locked** | Auth required | UI shows padlock, input queued or rejected, steps don't execute | High (passphrase/PIN) |
| **Batch** | Saved workflow triggered | Execute pre-recorded steps; Pause/Cancel/Retry available | Standard (in Active mode) |
| **Demo** | Training/onboarding | Destructive actions disabled, extra UI hints | Strict (deny most changes) |
| **Service** | Scheduled task / API call | Minimal/no UI; runs headless; full logs stored | Depends on scheduler |
| **Error/Panic** | Repeated failures | Orchestrator halts; user notified; may lock until reset | Critical (requires manual intervention) |

### Mode Transitions
```
Active ←--unlock/lock--→ Locked
  ↑                         ↑
  └─────────────────────────┘
         ↓ (on auth)
     Batch (from saved) → Active (on complete)
     ↓
Demo (toggle settings) ↔ Active
     ↓
Service (background scheduler) → logs recorded
     ↓
Active/Batch --repeated errors--> Error/Panic
```

## 5.2 Authentication & Locking

### Lock Modes

| Mode | Mechanism | Unlock Method | Time Requirement |
|------|-----------|---------------|-----------------|
| **None** | No protection | Always active | Immediate |
| **Passphrase** | Static text (bcrypt) | Type text | <10 seconds |
| **Spoken phrase** | Voice-biometric | Say pre-recorded phrase | <5 seconds |
| **PIN** | 4–6 digit code | Type digits | <10 seconds |
| **Multi-factor** | Passphrase + spoken | Both required | <15 seconds |

### Locked State Behavior

When locked:
- **UI:** Padlock icon; input boxes grayed; no data visible
- **Voice:** Rejected; system says "Please authenticate"
- **Chat:** Text queued (not executed) in `pending_requests` table
- **Execution panel:** Blank; no secrets visible
- **Timeout:** 30 min inactivity → re-lock (configurable)

### Request Queue (Locked Mode)
```sql
pending_requests(
  id, session_id, request_text,
  timestamp, source (voice/text),
  status (queued/approved/rejected/executed),
  executed_at
)
```

After unlock, user can:
- **Review:** See what was attempted
- **Approve:** Execute the queued request
- **Reject:** Discard it
- **Modify:** Edit before executing

## 5.3 Cancellation Mechanisms

### Channel 1: UI Cancel Button
Located in execution panel; sends cancel signal via WebSocket

### Channel 2: Global Hotkey
Default: `Ctrl+Shift+Alt+S` — works even if UI out of focus

### Channel 3: Spoken Kill-Keywords
Listens for: `stop`, `cancel`, `abort`, `halt`, `kill process` (case-insensitive, <2s trigger)

### Orchestrator Cancel Handler
```python
def on_cancel_request(self):
    self.cancel_requested = True
    self.ea.abort_current_action()
    if self.current_workflow.rollback_steps:
        self.execute_rollback_sequence()
    self.cma.log_event(f"Workflow cancelled at step {self.current_step}")
    self.user_agent.speak(f"Workflow cancelled.")
    self.reset()
```

## 5.4 Sensitive Data Redaction

Before any model inference, redact:
- Email: `[\w\.-]+@[\w\.-]+\.\w+`
- Phone: `(\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4}`
- Credit cards: Regex + Luhn validation
- SSN: `\d{3}-\d{2}-\d{4}`
- Passwords: OCR detection
- Account numbers: Pattern-based

Redacted text replaced with `[REDACTED]` in logs + model inputs.

---

# PART 6: DATABASE SCHEMA (14 TABLES)

```sql
-- 1. CHAT SESSION MANAGEMENT
CREATE TABLE chat_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT DEFAULT 'New Chat',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_pinned BOOLEAN DEFAULT 0,
  is_archived BOOLEAN DEFAULT 0,
  mode TEXT DEFAULT 'chat',
  theme TEXT DEFAULT 'dark'
);

-- 2. CHAT MESSAGES
CREATE TABLE chat_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,  -- 'user' | 'assistant' | 'system'
  content TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  message_type TEXT DEFAULT 'text',
  metadata JSON,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  INDEX idx_session_timestamp (session_id, timestamp)
);

-- 3. WORKFLOWS
CREATE TABLE workflows (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  user_id TEXT NOT NULL,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  steps JSON NOT NULL,
  parameters JSON,
  tags TEXT,
  is_favorite BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_executed_at DATETIME,
  execution_count INT DEFAULT 0,
  avg_confidence REAL DEFAULT 0.0,
  success_rate REAL DEFAULT 0.0,
  version INT DEFAULT 1,
  is_scheduled BOOLEAN DEFAULT 0,
  cron_expression TEXT,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. WORKFLOW EXECUTIONS
CREATE TABLE workflow_executions (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  status TEXT,
  confidence REAL,
  error_message TEXT,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id),
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 5. EXECUTION LOGS
CREATE TABLE execution_logs (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  workflow_execution_id TEXT,
  step_number INT,
  action TEXT,
  status TEXT,
  duration_ms INT,
  confidence REAL,
  screenshot_path TEXT,
  error_code TEXT,
  error_message TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id),
  INDEX idx_session_timestamp (session_id, timestamp)
);

-- 6. PENDING REQUESTS (Locked mode queue)
CREATE TABLE pending_requests (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  request_json TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  created_at DATETIME,
  reviewed_at DATETIME,
  reviewed_by TEXT,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 7. FAILURE HISTORY
CREATE TABLE failure_history (
  id TEXT PRIMARY KEY,
  workflow_id TEXT,
  step_number INT,
  error_code TEXT,
  error_message TEXT,
  backtrack_level_used INT,
  resolution TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

-- 8. CONTEXT SNAPSHOTS
CREATE TABLE context_snapshots (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  workflow_id TEXT,
  step_number INT,
  orchestrator_state JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

-- 9. AUTH LOG
CREATE TABLE auth_log (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  auth_method TEXT,
  success BOOLEAN,
  attempt_count INT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 10. WORKFLOW REVISIONS
CREATE TABLE workflow_revisions (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  version INT,
  steps JSON,
  created_at DATETIME,
  created_by TEXT,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id),
  INDEX idx_workflow_version (workflow_id, version)
);

-- 11. APPLICATION REGISTRY
CREATE TABLE application_registry (
  id TEXT PRIMARY KEY,
  app_name TEXT UNIQUE NOT NULL,
  executable_path TEXT,
  launch_command TEXT,
  installed_version TEXT,
  last_scanned DATETIME,
  is_in_path BOOLEAN
);

-- 12. USER SETTINGS
CREATE TABLE user_settings (
  session_id TEXT PRIMARY KEY,
  auth_mode TEXT,
  passphrase_hash TEXT,
  lock_timeout_minutes INT DEFAULT 30,
  hotkey_binding TEXT DEFAULT 'Ctrl+Shift+Alt+S',
  kill_keywords TEXT,
  privacy_filters BOOLEAN DEFAULT 1,
  telemetry_enabled BOOLEAN DEFAULT 0,
  theme TEXT DEFAULT 'dark',
  updated_at DATETIME,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 13. USERS
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  passphrase_hash TEXT,
  lock_mode TEXT DEFAULT 'none',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME,
  is_active BOOLEAN DEFAULT 1
);

-- 14. METRICS
CREATE TABLE metrics (
  id TEXT PRIMARY KEY,
  metric_name TEXT,
  value REAL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  session_id TEXT,
  INDEX idx_metric_time (metric_name, timestamp)
);
```

---

# PART 7: API SPECIFICATION

## 7.1 REST Endpoints (FastAPI)

### Chat Management
```
POST   /api/chats
       Create new session
       Request: { title (opt) }
       Response: { session_id, title, created_at }

GET    /api/chats
       List all sessions
       Response: [ { session_id, title, updated_at, ... }, ... ]

GET    /api/chats/<session_id>
       Get chat details + history
       Response: { session_id, title, messages: [...], workflows_used: [...] }

PUT    /api/chats/<session_id>
       Update chat (title, pin, etc.)
       Request: { title (opt), is_pinned (opt) }

DELETE /api/chats/<session_id>
       Archive/delete session
       Response: { status: 'archived' }
```

### Workflow Management
```
GET    /api/workflows
       List all workflows
       Query: ?tag=web&sort=last_used&limit=20
       Response: [ {...}, ... ]

POST   /api/workflows
       Save new workflow
       Request: { name, steps, parameters (opt), tags (opt), description (opt) }
       Response: { workflow_id, status: 'saved' }

PUT    /api/workflows/<workflow_id>
       Update workflow
       Request: { name (opt), tags (opt), description (opt) }

DELETE /api/workflows/<workflow_id>
       Delete workflow

PATCH  /api/workflows/<workflow_id>/favorite
       Toggle favorite flag
```

### Execution
```
POST   /api/execute
       Execute command
       Request: {
         input: "Open Chrome...",
         session_id: "chat_abc123",
         mode: "active|batch|service",
         source: "voice|text",
         auto_save_workflow: true (opt)
       }
       Response: {
         status: "ok",
         execution_id: "exec_...",
         plan: [...],
         message: "Planning..."
       }

POST   /api/cancel
       Cancel workflow
       Request: { session_id: "..." }
       Response: { status: 'cancelled' }

POST   /api/mode/set
       Change mode
       Request: { mode: 'active|locked|batch|demo|service' }
       Response: { status: 'ok', mode: '...', requires_auth: true/false }
```

### Settings & Health
```
GET    /api/settings
       Retrieve settings
       Response: { auth_mode, hotkey, theme, privacy_filters, ... }

PUT    /api/settings
       Update settings
       Request: { auth_mode (opt), hotkey (opt), theme (opt), ... }
       Response: { status: 'saved' }

POST   /api/unlock
       Authenticate
       Request: { auth_method: 'passphrase|pin', value: '...' }
       Response: { success: true/false, reason: 'incorrect_passphrase' (if fail) }

GET    /health
       Liveness probe
       Response: { status: 'ok', version: '...' }
```

## 7.2 WebSocket Streaming

**Connection:** `WS localhost:9000/ws`

**Subscribe:**
```json
{ "type": "subscribe", "session_id": "chat_abc123" }
```

**Server broadcasts events:**
- `plan_ready` — Planning complete, steps ready
- `step_started` — Step N starting execution
- `step_complete` — Step N succeeded/failed
- `workflow_complete` — All steps done
- `error` — Failure occurred, backtracking initiated

---

# PART 8: BUNDLED SETUP & INSTALLATION

## 8.1 Installer Bundle Structure

```
JARVIS_AI_Setup_4.0.exe (~2.5GB)
├─ Frontend (React/Electron) ~200MB
├─ Backend (Node.js) ~100MB
├─ Python runtime ~100MB
├─ FastAPI + deps ~50MB
├─ Ollama runtime ~200MB
├─ SQLite + driver <10MB
├─ Models (optional, on-demand) ~8–15GB
└─ PowerShell scripts <10MB
```

## 8.2 Installation Wizard Flow (Drive/Path Selection + Model Pre-Detection)

```
1. WELCOME SCREEN

2. INSTALLATION TYPE
   ├─ Full Install (Recommended) ~2.5GB
   ├─ Frontend Only (Lightweight) ~500MB
   └─ Custom

3. SELECT INSTALLATION DRIVE & PATH
   ├─ Offer: C:\, D:\, E:\, etc. (user selects)
   ├─ Display free space: "D:\ has 500GB available"
   └─ Default suggestion: %LocalAppData%\Jarvis

4. MODEL PRE-DETECTION (Check if models already exist)
   ├─ Search locations:
   │  ├─ [SELECTED_PATH]\models\
   │  ├─ %APPDATA%\Ollama\models\
   │  └─ Custom path (if %JARVIS_MODELS% env var set)
   ├─ For each required model:
   │  ├─ qwen2.5-3b (4GB)
   │  │  └─ "Found qwen2.5-3b.gguf (3.8GB). Reuse existing? [Y/N/Update]"
   │  ├─ whisper-medium (1.5GB)
   │  │  └─ "Whisper not found. Download? [Y/N]"
   │  ├─ piper_en_US (500MB)
   │  │  └─ "Found Piper. Reuse? [Y/N]"
   │  └─ moondream (2GB)
   │     └─ "Not found. Download? [Y/N]"
   └─ Skip download for detected models (saves time + bandwidth)

5. MODEL DOWNLOAD (only for missing models)
   ├─ All downloads to: [SELECTED_PATH]\models\
   ├─ Show progress per model (% complete, speed, ETA)
   └─ Resume support if download interrupted

6. OLLAMA CONFIGURATION
   ├─ Detect: Is Ollama running? (check port 11434)
   ├─ If YES: "Using existing Ollama at localhost:11434"
   ├─ If NO: "Install Ollama? [Y/N]" or offer portable bundled version
   └─ Configure: OLLAMA_MODELS = [SELECTED_PATH]\models

7. SYSTEM SCAN
   ├─ Auto-discover installed applications
   ├─ Populate System App Registry (installed_apps table)
   └─ (Runs quietly in background)

8. INSTALLATION PROGRESS
   ├─ Visual progress bar (estimated time remaining)
   └─ Log: "Installed binaries... Downloading models... Configuring Ollama..."

9. COMPLETE
   ├─ "Setup successful"
   ├─ [Launch JARVIS]
   └─ [View Documentation & Getting Started]
```

## 8.3 Post-Install Directory Structure (User-Selectable Paths)

**User selects installation drive during setup. NOT hardcoded to C:\. Environment variables used for all dynamic paths.**

### Application Binaries (Read-Only)
```
[INSTALL_PATH]\Program Files\Jarvis AI\
├─ bin/
│  ├─ jarvis.exe (Electron app)
│  ├─ backend.exe (Python FastAPI server)
│  ├─ ollama.exe (optional; may use system Ollama instead)
│  ├─ uninstall.exe
│  └─ setup-models.exe (model downloader/updater)
├─ resources/
│  ├─ app.asar (React bundle, all UI code)
│  ├─ icon.ico
│  ├─ LICENSE.txt
│  └─ README.txt
└─ config/
   ├─ config.ini (Ollama port, model paths, log paths)
   └─ defaults.json
```

### User Data & Models (Persistent, User-Selected During Install)
```
[DATA_PATH] (Default: C:\Users\[user]\AppData\Local\Jarvis\
             OR user-selected: D:\Jarvis\ or any custom location)

├─ jarvis.db (SQLite - ALL persistent data)
│  └─ conversation_history, workflows, execution_logs, app_registry, auth_log, etc.
│
├─ config/
│  ├─ user_settings.json
│  │  ├─ auth_mode: "passphrase"|"pin"|"voice"|"none"
│  │  ├─ hotkey_binding: "Ctrl+Shift+Alt+S"
│  │  ├─ theme: "dark"|"light"
│  │  ├─ privacy_filters: true|false
│  │  ├─ lock_timeout_minutes: 30
│  │  └─ ...
│  └─ config.ini
│     ├─ OLLAMA_PORT=11434
│     ├─ MODELS_PATH=[user-selected-path]\models
│     ├─ LOG_PATH=[user-selected-path]\logs
│     └─ SCREENSHOT_PATH=[user-selected-path]\screenshots
│
├─ models/ (PRE-DETECTION: Installer skips download if models exist here)
│  ├─ qwen2.5-3b.gguf (~3-4GB)
│  │  └─ [Pre-detection check: If exists, ask user; don't re-download]
│  ├─ whisper-medium.pt (~1.5GB)
│  │  └─ [Pre-detection check: If exists, ask user; don't re-download]
│  ├─ piper_en_US.onnx (~50MB)
│  │  └─ [Pre-detection check: If exists, ask user; don't re-download]
│  └─ moondream-0.5.gguf (~2GB)
│     └─ [Pre-detection check: If exists, ask user; don't re-download]
│
├─ screenshots/ (Auto-expires after 7 days)
│  ├─ [timestamp]_before.jpg (baseline before action)
│  ├─ [timestamp]_after.jpg (screenshot after action)
│  └─ [Auto-cleanup daemon runs daily]
│
└─ logs/ (Rolling logs, max 50MB per file)
   ├─ jarvis_[date].log (combined events)
   ├─ execution_[date].log (step-by-step execution detail)
   └─ error_[date].log (failures, backtracking, warnings)
```

### Environment Variables Set by Installer

```
JARVIS_HOME = [INSTALL_PATH]\Program Files\Jarvis AI
JARVIS_DATA = [USER-SELECTED]\Jarvis (or default %LocalAppData%\Jarvis)
JARVIS_MODELS = %JARVIS_DATA%\models
JARVIS_LOG = %JARVIS_DATA%\logs
JARVIS_SCREENSHOTS = %JARVIS_DATA%\screenshots
OLLAMA_PORT = 11434 (or detected existing port if Ollama already running)
OLLAMA_MODELS = %JARVIS_DATA%\models (symlink; Ollama discovers models here)
```

---

# PART 9: WINDOWS-SPECIFIC IMPLEMENTATION

## 9.1 Voice Pipeline (Complete: Capture + STT + TTS + Playback)

### What is WASAPI?

**WASAPI = Windows Audio Session API**
- Modern native Windows audio standard (introduced 2006, Vista/Windows Server 2008)
- Still the standard in 2026 for real-time audio applications
- Lower-level than deprecated WinMM; more performant than older DirectSound
- Provides low-latency (<50ms) audio capture/playback
- Allows multiple simultaneous audio streams (browser audio + Jarvis mic capture + TTS playback)
- Connects directly to audio device hardware

### Audio CAPTURE (WASAPI Microphone → Whisper STT)

```
Physical microphone device
  ↓
WASAPI IAudioCaptureClient initializes:
  • Opens microphone stream at 16-bit PCM, 16kHz mono
  • Starts at system boot or "Start Listening" button press
  • Continuous raw audio frames flow from hardware
  ↓
Ring Buffer (2–4 second circular buffer in RAM):
  • Circular memory: new audio overwrites oldest
  • Prevents audio loss if processor temporarily busy
  • Holds up to 64KB of audio data
  ↓
VAD (Voice Activity Detection):
  • Real-time frame analysis: Is user speaking or silence?
  • Silence threshold: <5 dB for 1.5 seconds = "Silence detected"
  • Purpose: Only send speech to Whisper (saves inference time)
  ↓
When Silence Detected (user paused/finished speaking):
  • Gather buffered audio (last 2–4 seconds from ring buffer)
  • Package into WAV/raw format
  • Forward to Whisper STT for transcription
  ↓
Whisper-medium Model (Local Inference via Ollama):
  • Input: Audio bytes (2–4 seconds at 16kHz PCM)
  • Processing time: 2–3 seconds (GPU faster)
  • Output: Transcribed text + confidence score
  • Example output: "Open VS Code" (confidence: 0.91)
  ↓
Confidence Evaluation:
  IF confidence > 90% (confident match):
    • Accept transcription
    • Display in chat: "You: Open VS Code"
    • Forward to RAG for planning
  
  ELSE (confidence ≤ 90%, uncertain):
    • Ask user for confirmation: "I heard 'Open VS Code'. Is that correct?"
    • Wait for user voice/text confirmation
    • If user says "Yes": Proceed
    • If user says "No": Ask to re-speak
```

### Audio PLAYBACK (Piper TTS → WASAPI Speaker)

```
When Orchestrator finishes planning/executing:
  Response message: "Planning 4 steps to create your React app"
  ↓
Send SIMULTANEOUSLY to User Agent:
  1) TEXT: Display immediately in chat (0ms delay)
  2) VOICE: Convert text to audio via Piper TTS
  ↓
Piper TTS Model (Local Neural Network):
  • Input: Text string ("Planning 4 steps to create your React app")
  • GPU inference time: <500ms
  • Output: PCM audio stream (16-bit, 16kHz mono)
  • Audio duration: 2–3 seconds (varies by speaking pace)
  • Voice quality: Natural prosody, professional English voice
  • Local model: No cloud calls, instant feedback
  ↓
WASAPI IAudioRenderClient:
  • Opens speaker/headphone output stream (16-bit PCM, 16kHz)
  • Queues Piper audio frames as they stream in
  • Handles underrun (buffer empty) and overflow gracefully
  ↓
Speaker Output:
  • User hears: "Planning 4 steps to create your React app"
  • Plays while chat shows text message
  ↓
Synchronization:
  • Chat text shows immediately (0ms)
  • TTS begins within <500ms (slight async, imperceptible)
  • User perceives: simultaneous text + voice
```

### Piper TTS (Text-to-Speech)

**Model:** Piper-en_US (English, United States)
- **Training:** Neural vocoder (VITS-based)
- **Quality:** Natural prosody, clear diction
- **Speed:** <500ms latency from text input to audio playback start
- **Languages:** 20+ supported (English, Hindi, Spanish, French, German, etc.)
- **Quality tier:** Professional but not indistinguishable from human (acceptable for status updates)
- **Cost:** Free, open-source, no licensing
- **Privacy:** 100% local, no cloud transmission
- **GPU support:** Accelerated if GPU available; CPU fallback available

**Why Piper?**
- Local inference (data privacy)
- Fast latency (<500ms)
- Natural-sounding output
- Free + open-source
- Handles multiple languages

**NOT used (as you specified):**
- ❌ Google Cloud Text-to-Speech (cloud-based, Privacy violation, cost $16 per 1M characters)
- ❌ Azure Cognitive Services TTS (cloud-based)
- ❌ AWS Polly (cloud-based)
- ❌ Any cloud TTS vendor

### Whisper STT (Speech-to-Text)

**Model:** Whisper-medium (OpenAI)
- **Accuracy on English:** 88–92%
- **Inference via:** Ollama (local runtime)
- **Processing time:** 2–3 seconds
- **GPU support:** Faster with CUDA; CPU mode acceptable
- **Confidence threshold:** >90% for acceptance (else ask user)
- **Languages supported:** 99 languages (including Hindi, Mandarin, etc.)
- **Quality:** Robust to accents, background noise, domain variety
- **Cost:** Free, open-source
- **Privacy:** 100% local, no cloud transmission

**Why Whisper?**
- Local inference (data privacy—100% owned by user)
- Free + open-source
- Robust multilingual
- Meets 88–92% accuracy threshold
- No internet dependency

**NOT used (as you specified):**
- ❌ Google Cloud Speech-to-Text (cloud-based, Privacy violation, cost ~$1.44 per 15 min)
- ❌ Azure Speech Services (cloud-based)
- ❌ Amazon Transcribe (cloud-based)
- ❌ Any cloud STT vendor

### Why WASAPI (vs. Legacy Alternatives)

| Technology | Release | Status 2026 | Latency | Why Not |
|-----------|---------|-----------|---------|---------|
| WinMM (waveOut) | 1990s | Deprecated | 100–200ms | Legacy, slow, abandoned |
| DirectSound | 2000 | Legacy but works | 50–100ms | Still slower than modern |
| **WASAPI** | **2006** | **Modern standard** | **<50ms** | **Correct choice** |
| ASIO | 2000 | Pro-audio niche | <20ms | Overkill; driver complexity |

WASAPI is the native Windows standard for real-time audio since Vista 2008 and remains standard in 2026.

### UI/Automation
- PowerShell: CLI operations
- RobotJS: Mouse/keyboard input + coordinate precision
- PyAutoGUI: Cross-platform fallback
- Windows API (Win32): Registry, window management
- Screenshot: PIL ImageGrab

## 9.2 Model Runtime

All models run via **Ollama (localhost:11434)**:
- qwen2.5:3b (3–4GB VRAM required)
- Whisper-medium (400–500MB VRAM)
- Piper-en-US (100–200MB VRAM)
- moondream (2GB VRAM)

CPU quantization available for lower-end systems.

---

# PART 10: TESTING STRATEGY

## 10.1 Unit Tests
- Agent correctness (RAG output, SPA tagging, EA rollback)
- Safety patterns (regex tests, injection tests)
- Database operations (CRUD, foreign keys)

## 10.2 Integration Tests
- End-to-end workflows (voice → plan → execution)
- Cancellation (hotkey/voice/button at each backtrack level)
- Locked mode (passphrase, request queue, execution)
- Batch workflows (saved sequence reuse, parameter substitution)

## 10.3 Performance Tests
- Latency benchmarks (Whisper, RAG, EA, etc.)
- Memory profiling (long sessions, multiple workflows)
- Screenshot + moondream timing

## 10.4 Security Tests
- PII redaction verification
- Passphrase/PIN validation
- Injection attack handling
- Permission scope validation
- Audit trail completeness

---

# PART 11: PERFORMANCE & LATENCY

## 11.1 Latency Breakdown (Example: "Open Chrome and go to GitHub")

```
Voice capture:                       0–3s
Whisper inference:                   2–3s
RAG planning:                        10–15s
SPA annotation:                      1–2s
SAA selection:                       <0.5s
EA execution + screenshot:           2–3s per step
Backtracking (if needed):            +2–5s per level
───────────────────────────────────────────
Simple (no retry):                   ~15–25s
With clarification:                  +30s
With backtracking × 2:               +10s
```

## 11.2 Memory Footprint

```
Electron UI:                         ~200MB
Python FastAPI:                      ~150MB
Ollama runtime:                      ~100MB
qwen2.5:3b (VRAM):                   3–4GB (GPU) or 1GB (CPU)
Whisper (VRAM):                      200–400MB
Piper (VRAM):                        100–200MB
moondream (VRAM):                    2GB (GPU)
SQLite + working data:               50–100MB
───────────────────────────────────────────
Total (all active):                  1.2–2GB (GPU) 
                                     or 600–900MB (CPU)
```

---

# PART 12: SECURITY & PRIVACY

## 12.1 Threat Model & Mitigations

| Threat | Attack Vector | Mitigation | Severity |
|--------|---------------|-----------|----------|
| Shoulder surfing | Physical access | Passphrase lock, request queue | High |
| Voice spoofing | Recorded voice replay | Spoken-phrase biometric (harder to spoof) | Medium |
| Prompt injection | Malicious web content | OA monitors for unexpected dialogs | Medium |
| Model hallucination | LLM generates unsafe commands | Safety agent regex + scope validation | High |
| Credential theft | Access to stored passwords | PII redaction; separate vault; no logs | Critical |
| Privilege escalation | Attacker gains admin | EA runs as user; UAC prompts for system ops | High |
| Data exfiltration | Cloud access | Local-only inference; no cloud calls | Critical |
| Malicious workflow | Sabotaged workflow import | Workflows previewed before save | Medium |
| DB tampering | Attacker modifies DB | SQLCipher (AES-256) encryption; checksums | High |

## 12.2 Privacy Safeguards

- **Data residency:** All files in C:\Users\<user>\AppData\Local\Jarvis
- **Redaction:** PII stripped before model inputs
- **Opt-in telemetry:** No collection by default
- **Screenshot retention:** Auto-delete after N days (default: 7)
- **Audit export:** Users  can download encrypted export of history
- **No cloud calls:** Ollama runs locally

---

# PART 13: IMPLEMENTATION ROADMAP

## Phase 1: Foundation (Weeks 1–2)
- [ ] FastAPI + SQLite + ORM setup
- [ ] Agent base classes + registry
- [ ] Orchestrator state machine
- [ ] WebSocket infrastructure

## Phase 2: Core Agents (Weeks 3–5)
- [ ] RAG, Clarification, Web Search agents
- [ ] SPA, SAA, CMA agents
- [ ] EA (12-step pipeline), OA agents

## Phase 3: UI & Frontend (Weeks 6–8)
- [ ] Electron + React setup
- [ ] Voice Mode component
- [ ] Chat Mode component
- [ ] Workflows Panel

## Phase 4: Windows & Integration (Weeks 9–11)
- [ ] Audio capture (Whisper streaming)
- [ ] Audio playback (Piper TTS)
- [ ] Global hotkey registration
- [ ] Screenshot + moondream integration
- [ ] Windows automation (PowerShell, RobotJS)

## Phase 5: Security & Advanced (Weeks 12–13)
- [ ] Passphrase/PIN/ voice unlock
- [ ] Request queue (locked mode)
- [ ] PII redaction + audit logging
- [ ] 6-level backtracking + rollback

## Phase 6: Installer & Deployment (Week 14)
- [ ] NSIS installer script
- [ ] Model download wizard
- [ ] Auto-update setup

## Phase 7: Testing & Hardening (Weeks  15–16)
- [ ] End-to-end integration tests
- [ ] Performance benchmarks
- [ ] Security penetration tests
- [ ] User acceptance testing

**Total: 16 weeks**

---

# PART 14: GLOSSARY

| Term | Definition |
|------|-----------|
| **Agent** | Specialized autonomous component with single well-defined role |
| **Backtracking** | Automated error recovery; 6 levels (retry → alt method → re-screenshot → GUI refresh → user confirm → abort) |
| **CMA** | Context Management Agent; persists history, logs, snapshots |
| **EA** | Execution Agent; performs 12-step pipeline to execute one plan step |
| **LLM** | Large Language Model; qwen2.5:3b for planning in Jarvis |
| **Orchestrator** | Central control agent; routes between agents; manages backtracking, cancellation |
| **RAG** | Reasoning-and-Generation agent; converts user intent to structured plan |
| **SPA** | Semantic Plan Adapter; enriches plan with metadata |
| **SAA** | System-Action-Agent; selects optimal execution method |
| **Workflow** | Saved sequence of automation steps; replayable, schedulable |
| **WASAPI** | Windows Audio Session API; low-level audio capture/playback |

---

## APPENDIX: DESIGN RATIONALE & RESEARCH

### Speech & Audio Technology Stack: LOCAL-ONLY (No Cloud)

**Selected Technologies (100% User-Owned Privacy):**

**Whisper-medium (Speech-to-Text):**
- ✅ Local inference on user's machine (100% privacy)
- ✅ Accuracy: 88–92% on English
- ✅ Free, open-source, no licensing
- ✅ Supports 99 languages (English, Hindi, Mandarin, etc.)
- ✅ Runs via Ollama (same backend as LLM)
- ⚠️ Inference: 2–3 seconds (acceptable for voice-first UX)

**Piper TTS (Text-to-Speech):**
- ✅ Local inference on user's machine (100% privacy)
- ✅ Natural prosody, clear English diction
- ✅ Latency: <500ms (fast feedback)
- ✅ Free, open-source
- ✅ Supports 20+ languages
- ⚠️ Voice quality: Professional (not indistinguishable from human, but acceptable for status updates)

**Design Decision: LOCAL-ONLY**

**Rejected (As You Specified):**
- ❌ Google Cloud Speech-to-Text (cloud-based, privacy violation)
- ❌ Google Cloud Text-to-Speech (cloud-based, privacy violation)
- ❌ Azure Cognitive Services (cloud-based)
- ❌ AWS Polly / Transcribe (cloud-based)
- ❌ Any cloud vendor speech/audio service

**Rationale:**
- User data never leaves the machine ✓
- No internet dependency ✓
- No subscription costs ✓
- Instant response (no network latency) ✓
- User has full control and ownership ✓

---

### External Repository Analysis

Inspected **kishanrajput23/Jarvis-Desktop-Voice-Assistant** (GitHub):
- Uses `speech_recognition` library (Google web recognizer)
- Uses `pyautogui` for GUI automation
- Uses `webbrowser.open()` for browser opening
- **No programmatic scrolling** in browser — just opens URL
- **Lesson:** Simple implementations lack depth; our 13-agent mesh + backtracking is production-grade

---

## DOCUMENT VERSION HISTORY

| Version | Consolidates | Date | Status |
|---------|--------------|------|--------|
| MASTER V2 (Current) | All V1 + V2 + Windows + V3 + Discussions | Feb 24, 2026 | **DEFINITIVE SINGLE SOURCE OF TRUTH** |

---

**END OF MASTER COMPLETE ARCHITECTURE DOCUMENT**

**THIS IS THE ONLY DOCUMENT YOU NEED. ALL PREVIOUS VERSIONS ARE SUPERSEDED.**

