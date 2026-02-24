# JARVIS AI – COMPLETE MASTER ARCHITECTURE
## Comprehensive Platform Specification | Voice + Chat + Workflows | Full Windows Implementation

**Version:** FINAL MASTER 1.0  
**Date:** February 24, 2026  
**Status:** **PRODUCTION-READY SPECIFICATION – SINGLE SOURCE OF TRUTH**  
**Platform:** Windows 10/11 (primary); macOS/Linux compatible  
**Purpose:** **DEFINITIVE** architecture document consolidating all design decisions, UI modes, backend systems, security, installations, and operational procedures. **Use this document exclusively; discard all previous versions (V1, V2, V3, Windows-specific docs).**

---

## DOCUMENT STRUCTURE

This document is organized as follows:

| Section | Purpose | Audience |
|---------|---------|----------|
| **EXECUTIVE SUMMARY** | High-level overview and key innovations | Stakeholders, decision-makers |
| **PART 1: SYSTEM OVERVIEW** | Core capabilities, target users, key metrics | Everyone |
| **PART 2: USER INTERFACE DESIGN** | Separated UI modes (voice/chat/workflows) with layouts | UI/UX engineers, designers |
| **PART 3: CORE ARCHITECTURE** | Layered system, data flows, component map | Backend engineers |
| **PART 4: 13-AGENT MESH** | Complete agent definitions, responsibilities, APIs | Agent developers, orchestrator engineers |
| **PART 5: OPERATIONAL MODES & SECURITY** | 6 modes, authentication, access control, threat mitigations | Security engineer, operations |
| **PART 6: WORKFLOW MANAGEMENT** | Workflow types, schema, versioning, execution modes | Workflow designer, end-users |
| **PART 7: DATABASE SCHEMA** | 14 tables, schema definitions, relationships | Database engineer, backend |
| **PART 8: API SPECIFICATION** | All endpoints (REST + WebSocket); request/response formats | Backend engineers, frontend engineers |
| **PART 9: WINDOWS-SPECIFIC IMPLEMENTATION** | Installer flow, voice pipeline, Windows API integration | Windows developers, DevOps |
| **PART 10: INSTALLATION & DEPLOYMENT** | Bundle contents, post-install, auto-update | DevOps, end-users |
| **PART 11: SECURITY & PRIVACY** | Threats, mitigations, data residency, audit trails | Security team, compliance |
| **PART 12: PERFORMANCE & SCALABILITY** | Latency breakdown, memory footprint, concurrency | Performance engineers |
| **PART 13: TESTING STRATEGY** | Unit, integration, performance, security tests | QA engineers |
| **PART 14: IMPLEMENTATION ROADMAP** | Phases, sprints, dependencies, critical path | Project manager, engineering leads |
| **PART 15: GLOSSARY** | Definitions of terms, abbreviations, acronyms | All (reference) |

---

## EXECUTIVE SUMMARY

**Jarvis AI** is a **locally-run, voice-driven desktop automation assistant** that listens to natural language commands, plans multi-step workflows, executes them with real-time visual feedback, learns from repeated actions, and provides multiple cancellation/security mechanisms.

### Key Innovations

1. **Separated UI Modes:** Voice mode (breathing bars + transcript), Chat mode (LLM-style history + new chat creation), Workflows panel (save/load/execute) — no mixing.

2. **13-Agent Mesh:** Specialized agents for planning (RAG, Clarification, Web Search, SPA, SAA), execution (EA, OA), safety (Safety, Orchestrator), and learning (CMA, Workflow Learner, App Registry, User Agent).

3. **6-Level Backtracking:** On failure, automatically retry with escalating strategies (retry → alt method → re-screenshot → GUI refresh → user confirmation → abort).

4. **Session Isolation:** Each chat session has independent execution context, message history, and logs; users can manage multiple concurrent chat sessions.

5. **Multi-Layer Security:**
   - Optional passphrase/spoken-phrase/PIN unlock
   - Request queue for locked mode
   - PII redaction before model inputs
   - Audit logging of all auth attempts and sensitive operations
   - Cancel via UI button + global hotkey + voice kill-keywords

6. **Workflow Learning:** After successful execution, users can save workflows with names, tags, and parameters; reuse via voice or text invocation; schedule for automation.

7. **Real-Time Streaming UI:** Dual-channel transport (chat + action stream) shows step-by-step progress with screenshots, confidence scores, and error recovery.

8. **Privacy-First:** Local inference only (Whisper, Piper, qwen2.5:3b, moondream); no cloud calls; user owns all data; encrypted database option.

### Target Metrics

| Metric | Target |
|--------|--------|
| Command latency (end-to-end) | 15–25 s (simple); 50–80 s (with clarification) |
| Voice transcription accuracy | ≥90% |
| First-try execution success | 70% (95% with backtracking) |
| Workflow reuse speedup | <15 seconds per saved task |
| WebSocket round-trip latency | <200 ms |
| Memory footprint | 500 MB–1.2 GB (all models + UI) |

---

# PART 1: SYSTEM OVERVIEW

## 1.1 What is Jarvis AI?

A **voice-first desktop automation assistant** that runs on your machine, listens to natural language commands, plans multi-step workflows (e.g., "open Chrome and search GitHub"), executes them step-by-step with automated error recovery, and learns from repeated actions.

**All processing is local.** No microphone audio, screenshots, or inference data leaves your machine. Models are downloaded lazily on first use and cached locally.

## 1.2 Core Capabilities (Complete List)

- ✅ **Multi-input modes:** Voice (Whisper STT) + text chat (synchronized)
- ✅ **Natural language planning:** qwen2.5:3b reasoning model (8–12 s inference)
- ✅ **Desktop automation:** PowerShell, RobotJS, PyAutoGUI, Windows API
- ✅ **Visual verification:** moondream screenshot analysis with fuzzy matching
- ✅ **Real-time feedback:** Streaming UI shows step-by-step progress + confidence scores
- ✅ **Workflow learning & reuse:** Save sequences as templates; replay with one phrase
- ✅ **Persistent memory:** SQLite local database; automatic session recovery
- ✅ **Intelligent backtracking:** 6-level automated fallback on errors
- ✅ **Multi-layer security:** Passphrase/voice unlock; request queue (locked mode); PII redaction
- ✅ **6 operational modes:** Active, Locked, Batch, Demo, Service, Error
- ✅ **3 cancellation paths:** UI button + global hotkey + voice kill-keywords
- ✅ **Session management:** Multiple independent chat conversations (like ChatGPT)
- ✅ **Privacy-first:** Local-only, encrypted database option, no telemetry by default

## 1.3 Target Users

1. **Developers:** Automate terminal workflows, generate projects, run tests
2. **Business Users:** Email/calendar/document management workflows
3. **IT Admins:** System configuration, installation, registry queries
4. **Power Users:** Complex multi-app orchestration and scheduled workflows

## 1.4 Key Principles

1. **Modularity:** Each agent has single well-defined responsibility
2. **Transparency:** Every action logged; user sees screenshots + confidence scores
3. **Recoverability:** 6-level backtracking; checkpoint recovery; rollback hints
4. **Security-first:** Auth, PII redaction, audit logs baked in from day one
5. **Privacy-preserving:** Local inference, no cloud calls, user-owned data
6. **Extensibility:** Plugin architecture for custom agents (future)

---

# PART 2: USER INTERFACE DESIGN

## 2.1 Three-Mode UI Architecture

The floating panel switches between three distinct modes. **No mixing.** Clean separation of concerns.

### MODE 1: VOICE MODE (480×400px)

**When:** User activates voice listening (hotkey, button click, or continuous listening)  
**UI State:** Pure voice interaction; no text, no chat history, no confusion.

```
┌──────────────────────────────────────────────────────┐
│  ◀  JARVIS  ⚙️                                       │  Title bar (40px)
├──────────────────────────────────────────────────────┤
│                                                      │
│                                                      │
│          [Breathing bars animation]                 │
│                    ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▇ ▆ ▅ ▄ ▃ ▂ ▁   │  Voice indicator (120px)
│          Status: LISTENING...                       │
│                                                      │
│          [Large microphone icon]                     │
│          (pulsing green if audio detected)          │
│                                                      │
├──────────────────────────────────────────────────────┤
│  "Open Chrome and go to GitHub"                     │  Live transcript (60px)
│                                                      │
├──────────────────────────────────────────────────────┤
│       [🎤 STOP LISTENING] [⏸️ PAUSE]              │  Action buttons (40px)
│                                                      │
├──────────────────────────────────────────────────────┤
│  ⚙️ Switch to chat mode   [← Toggle]                │  Mode switch (30px)
└──────────────────────────────────────────────────────┘
```

**Voice Indicator States & Animations:**

| State | Visual | Color | Animation | Audio | Duration |
|-------|--------|-------|-----------|-------|----------|
| **Idle** | Static logo | Gray (#606060) | None | None | — |
| **Listening** | 4 breathing bars | Blue (#0078d4) | 0.5–1.5 scale, 1.5s cycle | Soft startup tone | Continuous |
| **Audio detected** | Green waveform (3 bars) | Green (#10b981) | Animated bars | None | While speaking |
| **Recognized** | Green checkmark (✓) | Green (#10b981) | Pop + fade | Soft confirm | 1s |
| **Thinking** | Pulsing orb | Blue (#0078d4) | Opacity 0.3–1.0, 1.0s | None | While inferring |
| **Speaking (TTS)** | Frequency waveform (7 bars) | Purple (#7c3aed) | Real-time wave | Piper voice | While speaking |
| **Error** | Red (!) with pulse | Red (#ef4444) | Pulse, 1.0s | Error beep | 2s |
| **Complete** | Checkmark + confetti | Green (#10b981) | Confetti shower → dissolve | Success tone | 2s |

**Key behaviors:**
- Live transcript updates as user speaks (Whisper streaming via silence detection)
- User can speak again to refine or cancel
- Mode switch button is always visible for easy toggling

### MODE 2: CHAT MODE (480×640px, expandable)

**When:** User switches to text mode or needs message history  
**UI State:** Full conversational interface with message history, like ChatGPT/Discord.

```
┌──────────────────────────────────────────────────────────┐
│  ◀  JARVIS  ☰ [Chat Menu]  ⚙️                          │  Title bar (40px)
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Jarvis: Hi! What would you like me to do?      │   │
│  │ 12:34 PM                                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ You: Open Chrome and search for GitHub         │   │
│  │ 12:35 PM                                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │  Chat area (scrollable, 300px)
│  │ Jarvis: I'll do that now. Planning...          │   │
│  │ [Step 1/4: Launch Chrome]                      │   │
│  │ [Step 2/4: Navigate to GitHub]                 │   │
│  │ [Step 3/4: Search for query]                   │   │
│  │ Executing now...                                │   │
│  │ ✓ Step 1 complete (2.1s, 95% confidence)      │   │
│  │ ⏳ Step 2 in progress... (taking screenshot)   │   │
│  │ 12:36 PM                                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  [Type message...] [🎤 Voice] [📎 Files]              │  Input bar (40px)
├──────────────────────────────────────────────────────────┤
│  [💾 Save Chat] [🔄 New Chat] [📋 Workflows]          │  Action buttons (40px)
├──────────────────────────────────────────────────────────┤
│  ⚙️ Chat settings  [← Switch to voice mode]             │  Mode switch (30px)
└──────────────────────────────────────────────────────────┘
```

**Chat Navigation Menu (Click ☰):**

```
☰ Chat menu
├─ ➕ New Chat (creates new session)
├─ 📌 Pinned Chats (if any)
├─ ─────────────────────
├─ Today
│  ├─ Chrome & GitHub (2 min ago)
│  ├─ Email Check (15 min ago)
├─ Yesterday
│  ├─ Check Slack (yesterday @ 3:15 PM)
│  ├─ Daily Report (yesterday @ 10:30 AM)
└─ Last 7 Days / Older
```

**Clicking a chat:**
- Loads session history + messages + execution logs
- Orchestrator switches to that session context
- User can continue conversation or re-run workflows

**New Chat button:**
- Creates new session in database
- Clears current messages
- Shows greeting: "Hi! What would you like me to do?"

### MODE 3: WORKFLOWS PANEL (480×800px modal, in chat mode)

**When:** User clicks 📋 Workflows button  
**UI State:** Dedicated panel for managing saved and scheduled workflows.

```
┌──────────────────────────────────────────────────────────┐
│  ◀ Back  |  SAVED WORKFLOWS  |  ⚙️ Settings             │  Header (40px)
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📂 All Workflows (5)  📂 Favorites (2)  📂 Recent (3)  │  Tabs (30px)
│                                                          │
├──────────────────────────────────────────────────────────┤
│  Search: [🔍 Type to filter...]                         │  Search (30px)
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │ 1. Open Chrome & GitHub Search                 │   │
│  │    Last run: 2 hours ago | ⭐ | 🗑️ | ▶️ Load  │   │
│  │    Steps: 4 | Confidence: 88% | Tags: web, dev │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │  Scrollable list (600px)
│  │ 2. Check Email & Reply                          │   │
│  │    Last run: 1 day ago | ⭐ | 🗑️ | ▶️ Load   │   │
│  │    Steps: 6 | Confidence: 92% | Tags: email    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 3. Daily Report Generator                       │   │
│  │    Last run: 1 week ago | ☆ | 🗑️ | ▶️ Load  │   │
│  │    Steps: 8 | Confidence: 85% | Tags: report   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  [+ Create New] [Import] [Export All]                  │  Action buttons (40px)
└──────────────────────────────────────────────────────────┘
```

**Workflow Item Interactions:**
- **⭐ Star:** Toggle favorite (pin to top)
- **🗑️ Delete:** Remove workflow
- **▶️ Load:** Load into current chat; show plan preview
- **Click name:** Edit workflow name inline
- **Click tags:** Add/remove tags; filter by tag

**Workflow Preview (on Load):**

```
┌─ Plan Preview ─────────────────────────────────────────┐
│ Workflow: "Open Chrome & GitHub Search"               │
│ Confidence: 88% | Last run: 2 hours ago              │
│                                                       │
│ Steps:                                               │
│ ✓ 1. Launch Chrome                        (2.1s)     │
│ ✓ 2. Navigate to github.com               (1.8s)     │
│ ✓ 3. Click search box                     (0.9s)     │
│ ✓ 4. Type search query                    (1.2s)     │
│                                                       │
│ [Execute] [Modify] [Cancel]                         │
└────────────────────────────────────────────────────────┘
```

## 2.2 Mode Switching & Transitions

**Voice → Chat:** User clicks "Switch to chat mode" or types anything.
- React unmounts VoiceModePanel, mounts ChatModePanel
- Panel resizes 480×400 → 480×640 over 300ms (smooth animation)
- Loads current session's message history
- Microphone stops listening gracefully

**Chat → Voice:** User clicks "Switch to voice mode" or presses spacebar.
- React unmounts ChatModePanel, mounts VoiceModePanel
- Panel resizes 480×640 → 480×400 over 300ms
- Activates microphone; breathing bars animation starts
- Session context preserved

**Session context preserved:** Switching modes does not lose execution history, logs, or workflow state.

---

# PART 3: CORE ARCHITECTURE

## 3.1 Layered System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  TIER 0: USER INTERFACE                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Electron Main + React Renderer (Voice/Chat/Workflows UI) │  │
│  │ - Window management (always-on-top floating panel)       │  │
│  │ - Global hotkey hook (Ctrl+Shift+Alt+S)                 │  │
│  │ - IPC bridge to backend                                 │  │
│  │ - WebSocket client for real-time updates                │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │ IPC / WebSocket                       │
└───────────────────────┼────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: BACKEND ORCHESTRATION (FastAPI/Python)               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ FastAPI Server (localhost:9000)                          │  │
│  │ - /api/execute, /api/cancel, /api/mode/set              │  │
│  │ - /api/chats/*, /api/workflows/*                         │  │
│  │ - /api/settings, /health                                │  │
│  │ - WS /ws (WebSocket streaming)                          │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │ Orchestrator (State Machine)                             │  │
│  │ - Mode: Active | Locked | Batch | Demo | Service | Error│  │
│  │ - Session state (per-session isolation)                 │  │
│  │ - Backtracking logic (6 levels)                         │  │
│  │ - Cancellation handler (hotkey/button/voice)            │  │
│  │ - Agent routing & sequencing                             │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       ↓                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 2: AGENT MESH (13 Specialized Agents)                    │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │   RAG    │ Clarify  │ WebSrch  │   SPA    │   SAA    │      │
│  │ (reason) │ (QA)     │ (data)   │ (annot)  │ (select) │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
│  ┌────────┬────────┬────────────┬──────────┬──────────┐        │
│  │   EA   │   OA   │   Safety   │  Orchest │   CMA    │        │
│  │ (exec) │(monitor)│  (gate)    │ (control)│ (persist)│        │
│  └────────┴────────┴────────────┴──────────┴──────────┘        │
│  ┌─────────────────┬────────────────┬─────────────────┐        │
│  │ Workflow Learner│ App Registry   │ User Agent      │        │
│  │ (save workflows)│ (app discovery)│ (voice/text I/O)│        │
│  └─────────────────┴────────────────┴─────────────────┘        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 3: SERVICE LAYER & AI MODELS (via Ollama)               │
│  ┌──────────┬──────────┬──────────┬──────────────────────────┐ │
│  │ qwen2.5  │ Whisper  │ Piper    │ moondream              │ │
│  │ (reason) │ (STT)    │ (TTS)    │ (vision)               │ │
│  └──────────┴──────────┴──────────┴──────────────────────────┘ │
│  (via localhost:11434 Ollama socket)                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 4: AUTOMATION & OS ACCESS                                │
│  ┌──────────┬──────────┬──────────┬──────────────────────────┐ │
│  │PowerShell│ RobotJS  │PyAutoGUI │ Windows API / Registry  │ │
│  │ (spawn)  │ (input)  │ (cross)  │ (detection, config)    │ │
│  └──────────┴──────────┴──────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TIER 5: DATA PERSISTENCE & SECURITY                           │
│  ┌──────────────────────────────┬──────────────────────────────┐ │
│  │ SQLite (jarvis.db)           │ Windows Registry / Config   │ │
│  │ - 14 tables (sessions,       │ - Panel position           │ │
│  │   messages, workflows, logs) │ - Auth method              │ │
│  │ - Optional SQLCipher AES-256 │ - Model directory          │ │
│  │ - WAL mode + auto-backup     │ - Hotkey binding           │ │
│  └──────────────────────────────┴──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 Request Flow Diagram (Example: Voice Command "Open Chrome and go to GitHub")

```
1. USER SPEAKS: "Open Chrome and go to GitHub"
   ↓
2. AUDIO CAPTURE (User Agent / Windows Audio API)
   - Microphone active; 16-bit PCM, 16 kHz
   - VAD detects speech; silence threshold triggers end
   ↓
3. WHISPER INFERENCE (STT)
   - Audio chunk → Whisper model → Transcript: "open chrome and go to github"
   - Confidence: 0.96
   ↓
4. HTTP POST /api/execute
   Body: {
     "input": "open chrome and go to github",
     "session_id": "chat_12345",
     "mode": "active",
     "source": "voice"
   }
   ↓
5. ORCHESTRATOR RECEIVES REQUEST
   - Auth check: Unlocked ✓
   - Mode check: Active ✓
   - Rate limit check: OK ✓
   ↓
6. SAFETY AGENT PRE-FILTER
   - "open chrome" → not dangerous ✓
   - "go to github" → not dangerous ✓
   ↓
7. RAG AGENT (Reasoning & Generation)
   - Calls qwen2.5:3b with context: "Open browser and navigate to website"
   - Inference: 8–12s
   - Generates Plan:
     Plan: [
       { n: 1, action: 'launch_app', app: 'chrome', method: 'powershell' },
       { n: 2, action: 'wait', duration_ms: 2000 },
       { n: 3, action: 'click', target: 'address_bar', method: 'robotjs' },
       { n: 4, action: 'type', text: 'github.com', method: 'robotjs' },
       { n: 5, action: 'press_key', key: 'enter', method: 'robotjs' }
     ]
   - Confidence: 0.88
   ↓
8. SPA AGENT (Semantic Plan Annotator)
   - Adds preconditions, timeouts, rollback hints:
     { n: 1, ..., precondition: "chrome not running", timeout_ms: 5000, rollback: "kill process chrome" }
   ↓
9. SAA AGENT (System Action Agent)
   - Confirms method selection (already done above by RAG)
   ↓
10. CMA AGENT (Context Management)
   - Saves checkpoint to DB
   ↓
11. WebSocket broadcast to UI:
   {
     "type": "plan_ready",
     "session_id": "chat_12345",
     "steps": 5,
     "confidence": 0.88,
     "message": "Ready to execute. 5 steps planned."
   }
   ↓
12. EXECUTION LOOP (EA Agent)
   For step 1: Launch Chrome
     - Pre-screenshot
     - PowerShell: Start-Process chrome.exe
     - Post-screenshot (wait 2.5s)
     - Moondream analyzes: "Is Chrome window visible?" → Yes (95%)
     - Success ✓ → Log to execution_logs table
     - WebSocket broadcast:
       { "type": "step_complete", "step": 1, "status": "success", "confidence": 0.95 }
   
   For step 2: Wait 2s (EA sleeps)
   
   For step 3: Click address bar
     - Pre-screenshot
     - Moondream finds address bar location
     - RobotJS clicks at [456, 234] ±5px
     - Wait 500ms
     - Post-screenshot
     - Moondream: "Is address bar focused?" → Yes (92%)
     - Success ✓
   
   For step 4: Type "github.com"
     - Type characters via RobotJS keyboard API
     - Success ✓
   
   For step 5: Press Enter
     - Press Enter key
     - Wait 2s (page load)
     - Post-screenshot
     - Moondream: "Is GitHub visible?" → Yes (88%)
     - Success ✓
   
   ↓
13. WORKFLOW COMPLETE
   - All steps succeeded
   - WebSocket broadcast:
     { "type": "workflow_complete", "status": "success", "total_steps": 5 }
   ↓
14. SAVE WORKFLOW OFFER
   - UI shows: "Save this workflow?"
   - User clicks "Save"
   ↓
15. WORKFLOW SAVE
   - User enters name: "Open Chrome & GitHub"
   - User adds tags: "web,dev"
   - POST /api/workflows
   - Saved to workflows table
   ↓
16. ORCHESTRATOR RESETS
   - Ready for next command
```

## 3.3 Component Integration Map

```
Electron (Windows)
├─ Main Process
│  ├─ Window management (480×640 floating panel)
│  ├─ Global hotkey listener (Ctrl+Shift+Alt+S)
│  ├─ System tray icon + menu
│  ├─ IPC bridge to preload script
│  └─ Menu bar (File, Edit, Window, Help)
│
└─ Renderer Process (React)
   ├─ VoiceModePanel component
   ├─ ChatModePanel component
   ├─ WorkflowsPanel component (modal)
   ├─ SettingsModal
   ├─ WebSocket client (listens to backend events)
   ├─ State management (React Context or Redux)
   └─ UI state (current_session_id, mode, messages, etc.)

FastAPI Backend (Python, localhost:9000)
├─ main.py (entry point)
├─ orchestrator.py (state machine, agent router)
├─ agents/
│  ├─ rag_agent.py (qwen2.5 planner)
│  ├─ clarification_agent.py (disambiguation)
│  ├─ web_search_agent.py (HTTP queries)
│  ├─ spa_agent.py (semantic annotation)
│  ├─ saa_agent.py (method selection)
│  ├─ ea_agent.py (execution + screenshot)
│  ├─ oa_agent.py (observation/monitoring)
│  ├─ safety_agent.py (blocklist validation)
│  ├─ cma_agent.py (persistence)
│  ├─ workflow_learner_agent.py (save/load workflows)
│  ├─ app_registry_agent.py (app inventory)
│  └─ user_agent.py (voice/text I/O)
│
├─ models/ (SQLAlchemy ORM)
│  ├─ chat_session.py
│  ├─ chat_message.py
│  ├─ workflow.py
│  ├─ execution_log.py
│  ├─ pending_request.py
│  ├─ auth_log.py
│  └─ ...
│
├─ routes/ (API endpoints)
│  ├─ chats.py (session management)
│  ├─ workflows.py (workflow CRUD)
│  ├─ execute.py (POST /api/execute)
│  ├─ cancel.py (POST /api/cancel)
│  ├─ settings.py (config)
│  └─ ws.py (WebSocket handler)
│
├─ security/ (auth & safety)
│  ├─ auth.py (passphrase validation)
│  ├─ safety.py (blocklist, regex, injection checks)
│  ├─ pii_redactor.py (PII masking)
│  └─ request_queue.py (locked mode queue)
│
├─ utils/
│  ├─ screenshot.py (PIL screenshot capture)
│  ├─ error_classifier.py (error code mapping)
│  ├─ metrics.py (latency tracking)
│  └─ config.py (registry/file-based config)
│
└─ db/
   ├─ connection.py (SQLite pool)
   ├─ migrations/ (schema updates)
   └─ seed_data.sql (initial data)

Ollama (localhost:11434)
├─ qwen2.5:3b (reasoning, ~3 GB VRAM)
├─ Whisper (STT, ~400 MB VRAM)
├─ Piper (TTS, ~200 MB VRAM)
└─ moondream (vision, ~2 GB VRAM)

Windows OS Layer
├─ Audio Capture (WASAPI / PyAudio)
├─ Audio Playback (WASAPI)
├─ Mouse/Keyboard (SendInput API via RobotJS)
├─ Window Management (Win32 / UWP)
├─ Registry Access (winreg module)
├─ PowerShell (subprocess)
└─ Filesystem (standard Python libraries)

Database (SQLite)
└─ C:\Users\<user>\AppData\Local\Jarvis\jarvis.db (AES-256 if encrypted)
   ├─ chat_sessions
   ├─ chat_messages
   ├─ workflows
   ├─ workflow_executions
   ├─ execution_logs
   ├─ pending_requests
   ├─ auth_log
   ├─ failure_history
   ├─ context_snapshots
   ├─ users
   ├─ application_registry
   ├─ user_settings
   ├─ model_cache
   └─ metrics
```

---

# PART 4: 13-AGENT MESH

## 4.1 Planning & Reasoning Agents

### Agent 1: RAG Agent (Reasoning-and-Generation)

**Role:** Convert natural language request into structured, step-by-step plan  
**Trigger:** User issues voice/text command  
**Input:** User text + conversation context + previous errors (if backtracking)  
**Output:** Ordered list of steps, each with action type, parameters, expected outcome, confidence score  
**LLM:** qwen2.5:3b (inference: 8–12s on CPU; 8–12s on GPU; faster on quantized)  
**Error handling:** Returns confidence score; if ≤0.6, escalates to Clarification Agent  

**API:**
```python
def generate_plan(self, user_input: str, context: dict) -> Plan:
    """
    Returns: Plan(steps=[
      Step(n=1, action='launch_app', app='chrome', ...),
      Step(n=2, action='wait', duration_ms=2000, ...),
      ...
    ], confidence=0.88)
    """
    pass
```

**Example:**
```
Input: "Open Chrome and search GitHub"
Output: Plan([
  Step(n=1, action="launch_app", app="chrome", method="powershell", 
       precondition="chrome_not_running", timeout_ms=5000),
  Step(n=2, action="wait", duration_ms=2000),
  Step(n=3, action="click", target="address_bar", method="robotjs"),
  Step(n=4, action="type", text="github.com", method="robotjs"),
  Step(n=5, action="press_key", key="return", method="robotjs")
], confidence=0.88)
```

### Agent 2: Clarification Agent

**Role:** Ask disambiguation questions when RAG confidence is low or parameters are ambiguous  
**Trigger:** RAG confidence ≤0.6 OR ambiguous parameters detected  
**Output:** Natural language question(s) to user; waits for response  
**Timeout:** 30s; if no input, selects safest default or aborts  

**Example:**
```
User: "Send email to John"
RAG: [multiple Johns in contacts → confidence 0.45]
Clarification Agent: "I found 3 Johns. Which one?"
  (A) john@work.com
  (B) john@home.com
  (C) John Smith (phone)
User: "A"
RAG: Re-plans with full context → confidence 0.92
```

### Agent 3: Web Search Agent

**Role:** Fetch real-time information (weather, stock prices, documentation, etc.)  
**Trigger:** RAG detects plan requires external data  
**Output:** JSON with search results; cached for 5 minutes  
**Tools:** HTTP GET; optional fallback to local cache  

**Example:**
```
RAG plans: "Get current weather in NYC"
Web Search Agent: Queries weather API → { temp: 45°F, condition: "Cloudy", ... }
Caches for 5 minutes to avoid duplicate queries
```

### Agent 4: SPA Agent (Semantic Plan Annotator)

**Role:** Enrich plan with semantic metadata (timeouts, preconditions, rollback hints)  
**Input:** Raw plan from RAG  
**Output:** Plan with additional fields for execution safety  

**Example:**
```
Input: { action: 'click', target: 'save_button' }
Output: {
  action: 'click', 
  target: 'save_button',
  precondition: 'button_visible',
  timeout_ms: 3000,
  rollback_hint: 'press_escape',
  expected_ui_change: 'dialog_closes'
}
```

### Agent 5: SAA Agent (System-Action-Agent)

**Role:** Choose optimal execution method (PowerShell, RobotJS, PyAutoGUI, Windows API, etc.)  
**Input:** SPA-annotated plan  
**Output:** Plan with `method` field assigned  

**Decision logic:**
- File/directory operations → PowerShell
- GUI clicks/typing → RobotJS (Windows/Mac) or PyAutoGUI (Linux)
- Web clicks/forms → embedded Chromium RPC (future)
- System registry reads → Windows API (winreg)
- Privileged operations → PowerShell with UAC elevation

---

## 4.2 Execution & Observation Agents

### Agent 6: EA Agent (Execution Agent)

**Role:** Execute each planned step and report success/failure  
**Responsibility:** 12-step pipeline per action

**12-Step Execution Pipeline:**

1.  **Pre-execution screenshot** – Capture UI state before action
2.  **Validate preconditions** – Check if prerequisites are met
3.  **Execute action** – Perform click, type, launch, etc. using selected method
4.  **Dynamic wait** – Sleep duration based on action type
5.  **Post-execution screenshot** – Capture UI state after action
6.  **Vision analysis** – Analyze screenshots via moondream
7.  **Outcome classification** – Success | Partial | Timeout | Error
8.  **Error code generation** – Map error to code (UI_NOT_FOUND, TIMEOUT, etc.)
9.  **Logging** – Write step details to execution_logs table
10. **Emergent UI detection** – Check for unexpected dialogs/popups
11. **Outcome verification** – Validate expected UI state via vision
12. **Return status** – Send result + confidence to Orchestrator

**Error codes returned:**
```
SUCCESS, PARTIAL_SUCCESS, TIMEOUT, UI_NOT_FOUND,
ACCESS_DENIED, PRECONDITION_FAILED, UNEXPECTED_DIALOG,
NETWORK_ERROR, APP_CRASHED, PERMISSION_ERROR, ...
```

### Agent 7: OA Agent (Observer Agent)

**Role:** Monitor system state during execution; detect unexpected changes  
**Input:** Real-time screenshot stream + OS events  
**Output:** Alert on unexpected UI/behavior  

**Triggers:**
- New window/dialog appeared (unexpected)
- Application crashed
- System sleep requested
- Antivirus/firewall prompt
- Out-of-plan keystroke detected

**Action on alert:** Pause orchestrator; notify user; wait for response

---

## 4.3 Safety & Control Agents

### Agent 8: Safety Agent

**Role:** Block or warn on dangerous/suspicious requests  

**Checks:**
1. Regex patterns – Detect dangerous commands (rm -rf, format c:, etc.)
2. Scope validation – Cannot exceed granted permissions
3. Sensitive data – Block attempts to copy credentials unencrypted
4. Rate limiting – Flag if same high-risk action repeated 3+ times in 1 minute
5. Injection detection – Block SQL/shell escapes, malformed syntax

**Output:**
- ✅ `allow` – proceed
- ⚠️ `warn` – show confirmation dialog
- 🚫 `deny` – abort step

**Modes:**
- `strict` (Demo): Larger blocklist, more warnings
- `normal` (Active): Balanced
- `relaxed` (Service): Minimal checks

### Agent 9: Orchestrator (Control Agent)

**Role:** Central traffic control; route messages; manage backtracking and cancellation  

**Responsibilities:**
1. Pre-flight checks: mode validation, auth, rate limiting
2. Workflow sequencing: call agents in order (RAG → SPA → SAA → EA)
3. Backtracking logic: choose recovery level 1–6 on error
4. State persistence: save checkpoint after each step
5. Cancellation handling: listen for hotkey/kill-keyword/button; abort cleanly
6. Metrics collection: track latency, success rates, backtrack frequency

**Backtracking Levels:**

| Level | Strategy | Condition | Example |
|-------|----------|-----------|---------|
| **1** | Retry same action | Simple transient error | Button click timed out; retry click |
| **2** | Alternative method | Method-specific issue | Click failed → use keyboard nav |
| **3** | Re-screenshot + retry | Vision/detection problem | moondream missed button; refresh screenshot & retry |
| **4** | GUI refresh | App state corrupted | Close/reopen app or dialog; restart step |
| **5** | User confirmation | Repeated failures | Ask user: "Continue?" or "Provide guidance?" |
| **6** | Abort gracefully | Unrecoverable | Log failure; roll back if defined; notify user |

---

## 4.4 Data Management & Learning Agents

### Agent 10: CMA Agent (Context Management Agent)

**Role:** Manage persistent state and history  

**Persists:**
- Conversation history (user message + assistant response + timestamp)
- Execution logs (steps, timestamps, screenshots, error codes)
- Context snapshots (checkpoints for undo/recovery)
- User settings (unlock method, hotkey, privacy filters)

**API:**
```python
def save_conversation(self, session_id, user_input, assistant_output):
    """Save message pair to DB"""
    
def load_history(self, session_id, limit=50):
    """Retrieve last N messages from session"""
    
def save_snapshot(self, session_id, workflow_id, step_n, state_dict):
    """Save checkpoint for recovery"""
    
def recover_from_snapshot(self, session_id, workflow_id, step_n):
    """Restore state from checkpoint"""
```

### Agent 11: Workflow Learner Agent

**Role:** Record executed workflows; enable reuse and optimization  

**Trigger:** After successful plan completion, offer "Save as Workflow"  

**Storage Schema:**
```sql
workflows(
  id, name, description, steps (JSON),
  parameters (JSON), tags, created_at,
  last_used_at, execution_count,
  category, is_scheduled, cron_expression,
  version, avg_confidence, success_rate
)
```

**Reuse:** User says "run invoice workflow" → Orchestrator loads steps → executes in Batch mode

### Agent 12: App Registry Agent

**Role:** Maintain inventory of installed applications; provide executable paths and launch methods  

**Scans:**
- Windows Registry (HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Uninstall)
- macOS Applications folder
- Linux .desktop files and PATH binaries

**Caches:** Updated on startup or manually refreshed  

**API:**
```python
def get_app(self, name: str) -> App:
    """Returns: {executable_path, working_dir, args, icon_path, version}"""
    
def list_apps(self) -> List[App]:
    """All installed apps"""
    
def search(self, keyword: str) -> List[App]:
    """Fuzzy search"""
```

### Agent 13: User Agent (Voice/Text I/O)

**Role:** Interface with user; capture voice/text; deliver audio/visual feedback  

**Voice Pipeline:**
- Listen for hotkey or wake word
- Stream audio to Whisper (silence detection enabled)
- Display live waveform in UI
- Continuous listening until silence timeout (1.5s)

**Text Pipeline:**
- Monitor chat input box
- Pass typed text directly to RAG

**Output Pipeline:**
- Stream TTS via Piper (audio updates as workflow progresses)
- Update UI in real-time via WebSocket

**Kill-Keywords:** Listens for `stop`, `cancel`, `abort`, `halt`, `kill process` — triggers immediate cancellation

---

# PART 5: OPERATIONAL MODES & SECURITY

## 5.1 Six Operational Modes

| Mode | Activation | Behaviour | Security Level |
|------|------------|-----------|-----------------|
| **Active** | Default (unlocked) | Full command acceptance, real-time execution, UI fully responsive | Standard auth |
| **Locked** | Auth required | UI shows padlock, all input queued or rejected, steps do not execute | High (passphrase/PIN) |
| **Batch** | Saved workflow triggered | Executes pre-recorded steps; Pause/Cancel/Retry available | Standard (in Active mode) |
| **Demo** | Training/onboarding | Certain destructive actions disabled; extra UI hints | Strict (deny most changes) |
| **Service** | Scheduled task / API call | Minimal or no UI; runs headless; full logs stored | Depends on scheduler |
| **Error/Panic** | Repeated failures | Orchestrator halts; user notified; may lock until reset | Critical (requires manual intervention) |

### Mode Transitions

```
Active ←--unlock/lock--→ Locked
  ↑                         ↑
  └─────────────────────────┘
         ↓ (on auth)
     Batch (from saved workflow) → Active (on complete)
     ↓
Demo (toggle in settings) ↔ Active
     ↓
Service (background scheduler) → logs recorded
     ↓
Active/Batch --repeated errors--> Error/Panic
```

### Orchestrator Implementation

```python
def pre_execute_check(self):
    if orchestrator.mode == 'locked':
        return { status: 'challenge_required', queued_request: input }
    
    if orchestrator.mode == 'demo':
        safety_agent.stricter_blocklist = True
        rag_agent.simplify_plans = True
    
    if orchestrator.mode == 'batch':
        input = { source: 'stored_workflow', steps: [...] }
    
    if orchestrator.mode == 'error':
        return { status: 'system_error', message: 'Please contact support' }
    
    # Proceed with normal execution
```

## 5.2 Authentication & Locking

### Lock Modes (First Launch Setup)

| Mode | Mechanism | Unlock Method | Time Requirement |
|------|-----------|---------------|-----------------|
| **None** | No protection | Always active | Immediate |
| **Passphrase** | Static text secret (bcrypt hashed) | Type text in UI modal | <10 seconds |
| **Spoken phrase** | Voice-biometric challenge | Say pre-recorded phrase | <5 seconds |
| **PIN** | 4–6 digit code | Type digits; timeout lockout | <10 seconds |
| **Multi-factor** | Combination (passphrase + spoken) | Both required | <15 seconds |

### Locked State Behaviour

When locked:
- **UI:** Padlock icon; input boxes grayed; no data displayed
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

After unlock, authorized user can:
- **Review:** See what was attempted
- **Approve:** Execute the queued request
- **Reject:** Discard it
- **Modify:** Edit before executing

## 5.3 Cancellation Mechanisms

### Channel 1: UI Cancel Button

- Located in execution panel
- Action: Sends `{ type: 'cancel' }` over WebSocket

### Channel 2: Global Hotkey

- Default: `Ctrl+Shift+Alt+S`
- Works even if UI is out of focus
- Invokes orchestrator's cancel handler directly

### Channel 3: Spoken Kill-Keywords

- User Agent listens for: `stop`, `cancel`, `abort`, `halt`, `kill process`
- Case-insensitive; triggers within 1–2s
- Same effect as hotkey/button

### Orchestrator Cancel Handler

```python
def on_cancel_request(self):
    # 1. Set flag
    self.cancel_requested = True
    
    # 2. Signal EA to abort in-flight action
    self.ea.abort_current_action()
    
    # 3. Attempt rollback if defined
    if self.current_workflow.rollback_steps:
        self.execute_rollback_sequence()
    
    # 4. Log cancellation
    self.cma.log_event(f"Workflow cancelled by user at step {self.current_step}")
    
    # 5. Notify user
    self.user_agent.speak(f"Workflow cancelled.")
    
    # 6. Reset state
    self.reset()
```

## 5.4 Sensitive Data Redaction

Before any model inference, redact:
- Email addresses (regex: `[\w\.-]+@[\w\.-]+\.\w+`)
- Phone numbers (regex: `(\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4}`)
- Credit card numbers (regex + Luhn validation)
- Social Security Numbers (regex: `\d{3}-\d{2}-\d{4}`)
- Passwords / passcodes (OCR detection)
- Medical/financial account numbers

Redacted text replaced with `[REDACTED]` in logs and model inputs.

## 5.5 Database Security

- **Encryption at rest:** SQLCipher (AES-256) if enabled by user
- **Workflow integrity:** Checksums on saved workflows
- **Audit trail:** All auth attempts + sensitive operations logged with timestamps
- **User audit export:** Users can download encrypted export of all data

---

# PART 6: WORKFLOW MANAGEMENT

## 6.1 Workflow Types & Execution Modes

| Type | Trigger | Execution | Logging | Reusability |
|------|---------|-----------|---------|------------|
| **Ad-hoc** | Voice/text command | Synchronous; real-time UI | Full | Can be saved |
| **Saved** | User invokes by name/keyword | Batch mode; same orchestrator | Full | Reusable N times |
| **Scheduled** | Cron expression or time-of-day | Service mode; headless | Full | Repeating |
| **Triggered** | External API call / file watcher | Service mode; async | Full | Event-driven |

## 6.2 Workflow Schema

```sql
CREATE TABLE workflows (
  id TEXT PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  steps JSON NOT NULL,  -- Array of step objects
  parameters JSON,      -- Input placeholders { name, type, default }
  category TEXT,        -- 'email', 'file', 'dev', 'admin', etc.
  tags TEXT,           -- CSV for search
  is_scheduled BOOLEAN DEFAULT 0,
  cron_expression TEXT, -- e.g. "0 9 * * MON-FRI"
  is_public BOOLEAN DEFAULT 0,
  version INT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  execution_count INT DEFAULT 0,
  last_executed_at DATETIME,
  avg_duration_ms FLOAT DEFAULT 0,
  success_rate FLOAT DEFAULT 0,
  FOREIGN KEY (created_by) REFERENCES users(id)
);
```

## 6.3 Workflow Execution Paths

### Path A: Ad-hoc (Voice/Text)

```
User voice/text
  → RAG plans (full reasoning)
  → SPA/SAA annotate/select methods
  → EA executes steps
  → User sees real-time progress
  → Completion → "Save as Workflow?" option
```

### Path B: Batch (Saved Workflow)

```
User: "Run invoice workflow"
  → Orchest loads workflow from DB
  → Skips RAG/SPA/SAA (steps pre-recorded)
  → EA iterates over steps with same 12-step pipeline
  → User can Pause/Cancel/Retry
  → Logs written; success rate updated
```

### Path C: Service (Scheduled)

```
Scheduler (cron) triggers at scheduled time
  → Orchestrator starts in Service mode
  → Workflow executes headless (no UI)
  → All output logged to file
  → Completion recorded in DB
```

## 6.4 Workflow Versioning & Rollback

- Each modification creates new version
- Users can revert to prior version via API
- Execution history tracks which version was run
- Parameters can be parameterized (e.g., `[USER_EMAIL]` → replaced at runtime)

---

# PART 7: DATABASE SCHEMA

## 7.1 Complete 14-Table Schema

```sql
-- 1. CHAT SESSION MANAGEMENT
CREATE TABLE chat_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT 'New Chat',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_pinned BOOLEAN DEFAULT 0,
  is_archived BOOLEAN DEFAULT 0,
  mode TEXT DEFAULT 'chat',  -- 'chat' or 'voice'
  theme TEXT DEFAULT 'dark',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 2. CHAT MESSAGES
CREATE TABLE chat_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,  -- 'user' | 'assistant' | 'system'
  content TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  message_type TEXT DEFAULT 'text',  -- 'text' | 'plan' | 'step_update' | 'error'
  metadata JSON,  -- { step_count, confidence, action_type, ... }
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  INDEX idx_session_timestamp (session_id, timestamp)
);

-- 3. WORKFLOWS (saved automation sequences)
CREATE TABLE workflows (
  id TEXT PRIMARY KEY,
  session_id TEXT,  -- nullable; workflows can exist independently
  user_id TEXT NOT NULL,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  steps JSON NOT NULL,  -- [ { step, action, params, method, ... }, ... ]
  parameters JSON,  -- placeholder values
  tags TEXT,  -- "web,dev,automation"
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
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user_name (user_id, name)
);

-- 4. WORKFLOW EXECUTIONS (track runs for analytics)
CREATE TABLE workflow_executions (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  status TEXT,  -- 'started' | 'completed' | 'failed' | 'cancelled'
  confidence REAL,
  error_message TEXT,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id),
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  INDEX idx_workflow_session (workflow_id, session_id)
);

-- 5. EXECUTION LOGS (per-step details)
CREATE TABLE execution_logs (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  workflow_execution_id TEXT,
  step_number INT,
  action TEXT,  -- "launch_app", "click", "type", etc.
  status TEXT,  -- 'started' | 'completed' | 'failed'
  duration_ms INT,
  confidence REAL,
  screenshot_path TEXT,
  error_code TEXT,  -- "UI_NOT_FOUND", "TIMEOUT", etc.
  error_message TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id),
  INDEX idx_session_timestamp (session_id, timestamp)
);

-- 6. PENDING REQUESTS (locked mode queue)
CREATE TABLE pending_requests (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  request_json TEXT NOT NULL,
  status TEXT DEFAULT 'pending',  -- 'pending' | 'approved' | 'rejected' | 'executed'
  created_at DATETIME,
  reviewed_at DATETIME,
  reviewed_by TEXT,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 7. FAILURE HISTORY (for analytics)
CREATE TABLE failure_history (
  id TEXT PRIMARY KEY,
  workflow_id TEXT,
  step_number INT,
  error_code TEXT,
  error_message TEXT,
  backtrack_level_used INT,
  resolution TEXT,  -- 'retry', 'alt_method', 'user_intervention', 'abort'
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

-- 8. CONTEXT SNAPSHOTS (for undo/recovery)
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

-- 9. AUTH LOG (security audit)
CREATE TABLE auth_log (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  auth_method TEXT,  -- 'passphrase', 'spoken_phrase', 'pin'
  success BOOLEAN,
  attempt_count INT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 10. WORKFLOW REVISIONS (versioning)
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
  arguments TEXT,
  working_directory TEXT,
  platform TEXT,  -- 'windows' | 'macos' | 'linux'
  last_scanned DATETIME,
  icon_path TEXT,
  version TEXT
);

-- 12. USER SETTINGS
CREATE TABLE user_settings (
  session_id TEXT PRIMARY KEY,
  auth_mode TEXT,  -- 'none' | 'passphrase' | 'spoken_phrase' | 'pin'
  passphrase_hash TEXT,  -- bcrypt
  lock_timeout_minutes INT DEFAULT 30,
  hotkey_binding TEXT DEFAULT 'Ctrl+Shift+Alt+S',
  kill_keywords TEXT,  -- JSON array
  privacy_filters BOOLEAN DEFAULT 1,
  telemetry_enabled BOOLEAN DEFAULT 0,
  theme TEXT DEFAULT 'dark',
  updated_at DATETIME,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- 13. USERS (multi-user support foundation)
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  passphrase_hash TEXT,
  lock_mode TEXT DEFAULT 'none',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME,
  is_active BOOLEAN DEFAULT 1
);

-- 14. METRICS (performance tracking)
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

# PART 8: API SPECIFICATION

## 8.1 REST API Endpoints (FastAPI)

### Chat Session Management

```
POST   /api/chats
       Create new chat session
       Request: { title (optional) }
       Response: { session_id, title, created_at }

GET    /api/chats
       List all user's chat sessions
       Response: [ { session_id, title, updated_at, is_pinned, ... }, ... ]

GET    /api/chats/<session_id>
       Get chat details + message history
       Response: { session_id, title, messages: [ ... ], workflows_used: [...] }

PUT    /api/chats/<session_id>
       Update chat (title, pin status, etc.)
       Request: { title (optional), is_pinned (optional) }

DELETE /api/chats/<session_id>
       Archive/delete chat session
       Response: { status: 'archived' }

GET    /api/chats/<session_id>/messages
       Get all messages in session (paginated)
       Query: ?page=1&limit=50
       Response: { messages: [...], page, total_pages }
```

### Workflow Management

```
GET    /api/workflows
       List all saved workflows
       Query: ?tag=web&sort=last_used&limit=20
       Response: [ { id, name, steps, confidence, last_executed, ... }, ... ]

GET    /api/workflows/<workflow_id>
       Get workflow details
       Response: { workflow_id, name, steps, parameters, history: [...] }

POST   /api/workflows
       Save/create new workflow
       Request: { name, steps, parameters (opt), tags (opt), description (opt) }
       Response: { workflow_id, status: 'saved' }

PUT    /api/workflows/<workflow_id>
       Update workflow (name, tags, description)
       Request: { name (opt), tags (opt), description (opt) }

DELETE /api/workflows/<workflow_id>
       Delete workflow
       Response: { status: 'deleted' }

PATCH  /api/workflows/<workflow_id>/favorite
       Toggle favorite flag
       Response: { is_favorite: true/false }

GET    /api/workflows/<workflow_id>/executions
       Get historical executions
       Response: [ { execution_id, started_at, status, confidence }, ... ]
```

### Execution & Cancellation

```
POST   /api/execute
       Execute command or workflow
       Request: {
         input: "Open Chrome and go to GitHub",
         session_id: "chat_abc123",
         mode: "active" | "batch" | "service",
         source: "voice" | "text",
         auto_save_workflow: true (opt)
       }
       Response: {
         status: "ok",
         session_id: "chat_abc123",
         execution_id: "exec_67890",
         plan: [ ... ],
         message: "Planning 4 steps..."
       }

POST   /api/cancel
       Cancel ongoing workflow
       Request: { session_id: "chat_abc123" }
       Response: { status: 'cancelled', message: 'Workflow stopped.' }

POST   /api/mode/set
       Change operational mode
       Request: { mode: 'active' | 'locked' | 'batch' | 'demo' | 'service' }
       Response: { status: 'ok', mode: 'locked', requires_auth: true }
```

### Settings & Configuration

```
GET    /api/settings
       Retrieve user settings
       Response: { auth_mode, hotkey, theme, privacy_filters, ... }

PUT    /api/settings
       Update settings
       Request: { auth_mode (opt), hotkey (opt), theme (opt), ... }
       Response: { status: 'saved' }

POST   /api/unlock
       Authenticate (passphrase, PIN, or voice)
       Request: { auth_method: 'passphrase' | 'pin', value: '...' }
       Response: { success: true/false, reason: 'incorrect_passphrase' (if fail) }

GET    /health
       Health check / liveness probe
       Response: { status: 'ok', version: '1.0.0' }
```

## 8.2 WebSocket Streaming (/ws)

**Connection:** `WS localhost:9000/ws`

**Client sends:**
```json
{
  "type": "subscribe",
  "session_id": "chat_abc123"
}
```

**Server broadcasts events:**

```json
{
  "type": "plan_ready",
  "session_id": "chat_abc123",
  "steps": 5,
  "confidence": 0.88,
  "plan": [ ... ],
  "timestamp": 1708800000
}
```

```json
{
  "type": "step_started",
  "session_id": "chat_abc123",
  "step": 2,
  "action": "click",
  "timestamp": 1708800010
}
```

```json
{
  "type": "step_complete",
  "session_id": "chat_abc123",
  "step": 2,
  "status": "success",
  "confidence": 0.95,
  "duration_ms": 1200,
  "timestamp": 1708800012
}
```

```json
{
  "type": "workflow_complete",
  "session_id": "chat_abc123",
  "total_steps": 5,
  "success": true,
  "total_duration_ms": 18500,
  "timestamp": 1708800030
}
```

```json
{
  "type": "error",
  "session_id": "chat_abc123",
  "step": 3,
  "error_code": "UI_NOT_FOUND",
  "error_message": "Element not found",
  "backtrack_level": 1,
  "retry": true,
  "timestamp": 1708800020
}
```

---

# PART 9: WINDOWS-SPECIFIC IMPLEMENTATION

## 9.1 Voice Pipeline (Detailed)

### Audio Capture (Windows.Media.Audio / WASAPI)

```
[Microphone] 
  → WASAPI IAudioCaptureClient (16-bit PCM, 16 kHz)
  → Ring buffer (2–4 seconds capacity)
  → VAD (Voice Activity Detection) via Whisper
  → Silence detection (threshold: <5 dB for 1.5s)
  → Full buffer captured when silence triggers
  → Sent to Whisper model for transcription
```

**Implementation:**
```python
import pyaudio
import numpy as np

SAMPLE_RATE = 16000
CHUNK = 512  # 32ms at 16 kHz
FORMAT = pyaudio.paInt16

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=1, rate=SAMPLE_RATE, 
                     input=True, frames_per_buffer=CHUNK)

buffer = collections.deque(maxlen=4*SAMPLE_RATE)
vad_threshold = 5.0  # dB

while True:
    chunk = stream.read(CHUNK)
    audio_data = np.frombuffer(chunk, dtype=np.int16)
    buffer.append(audio_data)
    
    # Check energy
    energy_db = 20 * np.log10(np.sqrt(np.mean(audio_data**2)) + 1e-10)
    
    if energy_db > vad_threshold:
        silence_duration = 0
        # Speaking
    else:
        silence_duration += 32  # ms
    
    if silence_duration > 1500:  # 1.5s
        # End of speech; send full buffer to Whisper
        full_audio = np.concatenate(buffer)
        transcript = whisper_model.transcribe(full_audio, language='en')
        # Process transcript...
        buffer.clear()
        silence_duration = 0
```

### Audio Playback (Piper TTS Streaming)

```
[TTS Request: "Opening Chrome..."]
  → Piper model generates streaming audio chunks
  → Each chunk streamed to WASAPI IAudioRenderClient
  → System plays in parallel with any other audio
  → Volume controlled via Windows mixer API
```

**Implementation:**
```python
from piper import PiperTTS
import pyaudio

tts = PiperTTS(model_path="en_US-glow_tts-1.0_cpu.onnx")
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paFloat32, channels=1, rate=22050, 
                     output=True)

for chunk in tts.synthesize("Opening Chrome..."):
    stream.write(chunk)
    
stream.close()
```

### Screenshot Capture (PIL + WinRT)

```python
from PIL import ImageGrab
import os
import time

def capture_screenshot(region=None):
    """
    Capture full screen or region; save to temp; return path
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    outfile = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Jarvis\\screenshots\\{timestamp}.jpg"
    
    if region:
        # region = (left, top, right, bottom)
        img = ImageGrab.grab(bbox=region)
    else:
        img = ImageGrab.grab()
    
    # Compress to 85% JPEG quality for speed
    img.save(outfile, 'JPEG', quality=85)
    return outfile
```

### Mouse/Keyboard Automation (RobotJS + SendInput)

```python
import pyautogui
import time

# Click at coordinates
pyautogui.click(456, 234)

# Wait
time.sleep(0.5)

# Type text
pyautogui.typewrite("github.com", interval=0.05)

# Press key
pyautogui.press('return')

# Get current mouse position
x, y = pyautogui.position()
```

Or use RobotJS (Node.js FFI):

```javascript
const robot = require('robotjs');

// Click
robot.moveMouse(456, 234);
robot.mouseClick();

// Type
robot.typeString('github.com', 100);  // 100ms per character

// Press key
robot.keyTap('enter');
```

### Window Management (Win32 API via ctypes)

```python
import ctypes
import win32gui

# Find window by class/title
hwnd = win32gui.FindWindowEx(0, 0, "Chrome_WidgetWin_1", None)

# Get window bounds
rect = ctypes.wintypes.RECT()
ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
print(f"Window bounds: {rect.left}, {rect.top}, {rect.right}, {rect.bottom}")

# Focus window
ctypes.windll.user32.SetForegroundWindow(hwnd)

# Get window title
title = win32gui.GetWindowText(hwnd)
```

### PowerShell Integration (subprocess)

```python
import subprocess

# Launch application
result = subprocess.run(
    ['powershell.exe', '-Command', 'Start-Process chrome.exe'],
    capture_output=True,
    text=True
)

# Run command and capture output
result = subprocess.run(
    ['powershell.exe', '-Command', 'Get-Process | Select-Object Name'],
    capture_output=True,
    text=True
)
print(result.stdout)

# With UAC elevation
result = subprocess.run(
    ['powershell.exe', '-Command', 
     'Start-Process powershell -ArgumentList "-Command ipconfig /release" -Verb runas'],
    capture_output=True
)
```

### Registry Access (winreg)

```python
import winreg
import os

# Open registry key
hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                       r'Software\Microsoft\Windows\CurrentVersion\Uninstall')

# Iterate over subkeys (installed apps)
for i in range(winreg.QueryInfoKey(hkey)[0]):
    subkey_name = winreg.EnumKey(hkey, i)
    subkey = winreg.OpenKey(hkey, subkey_name)
    
    try:
        display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
        install_location = winreg.QueryValueEx(subkey, 'InstallLocation')[0]
        print(f"{display_name}: {install_location}")
    except OSError:
        pass  # Key not present
    
    winreg.CloseKey(subkey)

winreg.CloseKey(hkey)
```

---

## 9.2 Installation Flow (NSIS Installer)

### Installer Stages

1. **License & paths** → User agrees + selects install dir
2. **Feature selection** → Desktop shortcut, Start menu, PATH
3. **Model directory** → Where to store AI models (default: AppData\Local\Jarvis)
4. **Ready screen** → Summary of selections
5. **Installation progress** → Extract files, register shortcuts, create registry entries
6. **Model download offer** → Offer to download models now or later
7. **Launch Jarvis** → Start application

### NSIS Script (Minimal Example)

```nsis
; JARVIS AI Windows Installer

!include "MUI2.nsh"

Name "Jarvis AI"
OutFile "JARVIS_AI_Setup_1.0.exe"
InstallDir "$PROGRAMFILES\Jarvis AI"

; Pages
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR\bin"
  File /r "..\build\*.*"
  
  SetOutPath "$INSTDIR"
  File "config.ini"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Jarvis AI"
  CreateShortCut "$SMPROGRAMS\Jarvis AI\Jarvis AI.lnk" "$INSTDIR\bin\jarvis.exe"
  CreateShortCut "$DESKTOP\Jarvis AI.lnk" "$INSTDIR\bin\jarvis.exe"
  
  ; Registry entries
  WriteRegStr HKCU "Software\Jarvis" "InstallPath" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "JarvisAI" "$INSTDIR\bin\jarvis.exe"
  
  ; Model directory
  CreateDirectory "$LOCALAPPDATA\Jarvis\models"
  CreateDirectory "$LOCALAPPDATA\Jarvis\screenshots"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  RMDir /r "$LOCALAPPDATA\Jarvis"
  Delete "$SMPROGRAMS\Jarvis AI\Jarvis AI.lnk"
  Delete "$DESKTOP\Jarvis AI.lnk"
  DeleteRegKey HKCU "Software\Jarvis"
SectionEnd
```

### Post-Install Directory Structure

```
C:\Program Files\Jarvis AI\
├─ bin/
│  ├─ jarvis.exe (Electron app)
│  ├─ backend.exe (Python FastAPI)
│  └─ ollama.exe (LLM runtime; pre-installed)
├─ resources/
│  ├─ app.asar (React bundle)
│  └─ icon.ico
├─ config.ini
└─ README.txt

C:\Users\<user>\AppData\Local\Jarvis\
├─ jarvis.db (SQLite database)
├─ config/
│  └─ user_settings.json
├─ models/
│  ├─ qwen2.5-3b.gguf (~3 GB)
│  ├─ whisper-medium.pt (~1.5 GB)
│  ├─ piper_en_US.onnx (~50 MB)
│  └─ moondream-0.5.gguf (~2 GB)
├─ screenshots/
│  └─ 20260224_123456.jpg
└─ logs/
   └─ jarvis_2026-02-24.log
```

---

# PART 10: INSTALLATION & DEPLOYMENT

## 10.1 Installer Bundle Components

| Component | Size | Purpose |
|-----------|------|---------|
| Electron app | ~200 MB | UI + IPC bridge |
| Python runtime | ~100 MB | Backend + agents |
| FastAPI + deps | ~50 MB | Web server |
| Ollama runtime | ~200 MB | Model inference engine |
| SQLite + driver | <10 MB | Database |
| **Total (app only)** | **~560 MB** | Before models |
| Models (optional) | ~8–15 GB | Downloaded on-demand |

## 10.2 Runtime Requirements

```
Windows:    Win10/11, Python 3.9+, .NET Framework 4.8+
RAM:        8 GB minimum; 16 GB recommended (for GPU)
Disk:       500 MB for app + 8–15 GB for models
GPU:        NVIDIA (CUDA 11.2+) preferred; optional
Network:    Internet for first model download only
```

## 10.3 Auto-Update Mechanism

Built into Electron; checks weekly; downloads + installs in background; prompts user to restart.

```javascript
// In Electron main process
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();
```

---

# PART 11: SECURITY & PRIVACY

## 11.1 Threat Model & Mitigations

| Threat | Attack Vector | Mitigation | Severity |
|--------|---------------|-----------|----------|
| Shoulder surfing / unauthorized use | Physical access to device | Passphrase lock, request queue, request audit | High |
| Voice spoofing | Attacker replays recorded voice | Spoken-phrase biometric (can be spoofed but harder); multiple challenges | Medium |
| Prompt injection in web pages | Malicious JavaScript in webpage | OA monitors for unexpected dialogs; sandboxing (future) | Medium |
| Model hallucination → destructive command | LLM generates unsafe command | Safety agent regex + scope validation; backtracking; user confirmation | High |
| Credential theft | Attacker accesses stored passwords | PII redaction; separate credential vault; no passwords logged | Critical |
| Local privilege escalation | Attacker gains admin rights | EA runs in user context; UAC prompts for system ops; logs UAC attempts | High |
| Data exfiltration | Attacker sends data to cloud | Local-only inference; all data in ~/ directory; no cloud calls | Critical |
| Malicious workflow import | User imports sabotaged workflow | Workflows previewed before save; all steps visible; checksummed | Medium |
| Database tampering | Attacker modifies DB file | SQLCipher (AES-256) encryption; checksums on workflows | High |

## 11.2 Privacy Safeguards

- **Data residency:** All files, logs, models in C:\Users\<user>\AppData\Local\Jarvis
- **Redaction:** PII automatically stripped before model inputs
- **Opt-in telemetry:** No data collection by default; user explicitly enables
- **Screenshot retention:** User can set auto-delete after N days (default: 7 days)
- **Audit export:** Users can download encrypted export of all execution history
- **No cloud calls:** Ollama runs locally; inference happens on-device

---

# PART 12: PERFORMANCE & SCALABILITY

## 12.1 Latency Breakdown (Example: "Click Save Button")

```
Voice capture:                       0–3 s (depending on speech speed)
Whisper inference:                   2–3 s (silence detection active)
RAG planning:                        10–15 s (qwen2.5:3b)
SPA annotation:                      1–2 s
SAA selection:                       <0.5 s
EA execution + screenshot:           2–3 s (click + post-screenshot)
Backtracking (if needed per level):  +2–5 s per retry
───────────────────────────────────────────
Total (simple, no retry):            ~15–25 s
Total (with clarification):          +30 s (user responds to clarification)
Total (with backtracking × 2):       +10 s
```

## 12.2 Memory Footprint

```
Electron UI:                         ~200 MB
Python FastAPI backend:             ~150 MB
Ollama runtime:                     ~100 MB
qwen2.5:3b model (VRAM):            3–4 GB (GPU) or 1 GB (CPU quantized)
Whisper.tiny (VRAM):                200–400 MB
Piper TTS (VRAM):                   100–200 MB
moondream (VRAM):                   2 GB (GPU) or quantized
SQLite + working data:              50–100 MB
───────────────────────────────────────────
Total (all models active):          1.2–2 GB (GPU) or 600–900 MB (CPU)
```

## 12.3 Concurrent Operations

- **Single user:** System is single-threaded orchestrator with async agents  
- **Multi-session:** Each session gets its own orchestrator instance; shared CMA for persistence  
- **Scalability:** Not designed for multiple concurrent workflows per user (queue additional requests)

---

# PART 13: TESTING STRATEGY

## 13.1 Unit Tests

- **Agent correctness:** RAG output structure, SPA tagging, EA rollback logic, Safety patterns, Orchestrator transitions
- **Safety agent patterns:** Ensure dangerous commands are caught (regex tests, injection tests)
- **Database schema:** CRUD operations, foreign key integrity, indexes

## 13.2 Integration Tests

- **End-to-end workflows:** Voice input → plan → execution → output
- **Cancellation:** Hotkey/voice/button stops at each backtrack level
- **Locked mode:** Passphrase unlock, request queue approval, execution
- **Batch workflows:** Saved sequence reuse, parameter substitution

## 13.3 Performance Tests

- **Latency benchmarks:** Each component (Whisper, RAG, EA, etc.)
- **Memory profiling:** Long sessions, multiple workflows
- **Screenshot + vision analysis timing:** moondream inference times
- **Model load times:** Lazy loading performance

## 13.4 Security Tests

- **PII redaction verification:** Regex patterns, OCR detection
- **Passphrase/PIN validation:** Bcrypt hashing, rate limiting
- **Injection attack handling:** SQL escapes, shell escapes, prompt injection
- **Permission scope validation:** Cannot exceed granted file directories
- **Audit trail completeness:** All sensitive operations logged

---

# PART 14: IMPLEMENTATION ROADMAP

## Phase 1: Foundation & Architecture (Weeks 1–2)

- [ ] Set up FastAPI backend + SQLite + ORM
- [ ] Create agent base classes + registry
- [ ] Implement Orchestrator state machine
- [ ] Set up WebSocket infrastructure
- [ ] Create test harnesses for parallel testing

## Phase 2: Core Agents (Weeks 3–5)

- [ ] RAG Agent (qwen2.5 planning) + tests
- [ ] EA Agent (12-step execution pipeline) + tests
- [ ] Safety Agent (blocklist + validation) + tests
- [ ] SPA + SAA + CMA (annotation, method selection, persistence) + tests
- [ ] Clarification + Web Search agents

## Phase 3: UI & Frontend (Weeks 6–8)

- [ ] Electron + React setup
- [ ] Voice Mode component (breathing bars, transcript)
- [ ] Chat Mode component (history, input)
- [ ] Workflows Panel (list, save, load)
- [ ] Settings Modal (auth modes, lock config)
- [ ] WebSocket client integration

## Phase 4: Windows-Specific & Integration (Weeks 9–11)

- [ ] Audio capture + Whisper streaming
- [ ] Audio playback + Piper TTS
- [ ] Global hotkey registration (Windows API)
- [ ] Screenshot + moondream integration
- [ ] Windows automation (PowerShell, RobotJS, PyAutoGUI)

## Phase 5: Security & Advanced Features (Weeks 12–13)

- [ ] Passphrase/PIN/voice unlock
- [ ] Request queue for locked mode
- [ ] PII redaction + sensitive data vault
- [ ] Audit logging + export
- [ ] Backtracking level 1–6 + rollback

## Phase 6: Installer & Deployment (Week 14)

- [ ] NSIS installer script
- [ ] Post-install directory structure
- [ ] Model download wizard
- [ ] Auto-update setup
- [ ] Release build + signing

## Phase 7: Testing & Hardening (Weeks 15–16)

- [ ] End-to-end integration tests
- [ ] Performance benchmarks
- [ ] Security penetration tests
- [ ] User acceptance testing
- [ ] Bug fixes & polish

## Critical Path

```
Foundation (Wks 1–2)
  ↓
Core Agents (Wks 3–5) [PARALLEL: UI dev starts Wk 4]
  ↓
Audio + Automation (Wks 6–9) [PARALLEL: Windows integration Wks 8–10]
  ↓
Security & Advanced (Wks 10–13)
  ↓
Installer (Wk 14)
  ↓
Testing & Release (Wks 15–16)
───────────────────
Total: 16 weeks
```

---

# PART 15: GLOSSARY

| Term | Definition |
|------|-----------|
| **Agent** | Specialized autonomous component with single well-defined role (e.g. RAG, EA, Safety) |
| **Backtracking** | Automated error recovery; 6 levels (retry → alt method → re-screenshot → GUI refresh → user confirm → abort) |
| **CMA** | Context Management Agent; persists history, logs, and snapshots |
| **EA** | Execution Agent; performs 12-step pipeline to execute a single plan step |
| **LLM** | Large Language Model; in Jarvis, qwen2.5:3b for planning |
| **Locked mode** | Security mode where user must authenticate; input queued; no execution |
| **OA** | Observer Agent; monitors system state during execution; detects unexpected changes |
| **Orchestrator** | Central control agent; routes messages between agents; manages backtracking, cancellation, state |
| **RAG** | Reasoning-and-Generation agent; converts user intent to structured plan |
| **SAA** | System-Action-Agent; selects optimal execution method (PowerShell, RobotJS, etc.) for each step |
| **Safety Agent** | Validates requests; blocks dangerous commands via regex, scope, injection detection |
| **SPA** | Semantic Plan Annotator; enriches plan with preconditions, timeouts, rollback hints |
| **Workflow** | Saved sequence of automation steps; can be replayed, scheduled, or shared |
| **WASAPI** | Windows Audio Session API; low-level audio capture/playback |
| **Whisper** | OpenAI STT model; converts audio to text with silence detection |
| **Piper** | Open-source TTS model; converts text to speech; runs locally |
| **moondream** | Vision model; analyzes screenshots for object detection + state verification |
| **Ollama** | Local LLM runtime (localhost:11434); hosts qwen2.5, Whisper, Piper, moondream |
| **SQLCipher** | SQLite with AES-256 encryption; optional database encryption |
| **VAD** | Voice Activity Detection; detects speech boundaries; triggers end-of-input |
| **WS / WebSocket** | Full-duplex communication channel; Jarvis uses for real-time UI streaming |

---

## DOCUMENT CHANGE LOG

| Version | Date | Changes |
|---------|------|---------|
| 1.0 FINAL MASTER | Feb 24, 2026 | Consolidated all 4 previous docs (V1, V2, Windows-specific, V3 redesign) into single authoritative spec. All design decisions, UI modes, agents, security, DB schema, API routes, Windows impl, and roadmap in one document. **USE ONLY THIS DOCUMENT GOING FORWARD.** |

---

**END OF DEFINITIVE MASTER ARCHITECTURE DOCUMENT**

**THIS IS THE SINGLE SOURCE OF TRUTH FOR ALL JARVIS AI DEVELOPMENT.**  
**All previous versions (V1, V2, V3, Windows-specific) are now SUPERSEDED.**  
**Refer to this document exclusively.**

---
