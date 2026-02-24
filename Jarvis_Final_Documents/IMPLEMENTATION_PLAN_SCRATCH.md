# JARVIS AI - Comprehensive Implementation Plan (Scratch Build)

**Date:** February 22, 2026  
**Status:** Complete Specification - Greenfield Development  
**Reference:** `JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md`  
**Target Release:** 10 weeks from sprint start

---

## Table of Contents

1. [Overview & Greenfield Approach](#overview--greenfield-approach)
2. [Complete Architecture Implementation](#complete-architecture-implementation)
3. [13-Agent System Specification](#13-agent-system-specification)
4. [Real-Time Streaming Architecture](#real-time-streaming-architecture)
5. [Voice UI Implementation (8 States)](#voice-ui-implementation-8-states)
6. [Workflow Learning System](#workflow-learning-system)
7. [Database Design & Migrations](#database-design--migrations)
8. [12-Step Execution Pipeline](#12-step-execution-pipeline)
9. [6-Level Backtracking System](#6-level-backtracking-system)
10. [Backend Architecture (FastAPI)](#backend-architecture-fastapi)
11. [Frontend Architecture (React + Electron)](#frontend-architecture-react--electron)
12. [Setup & .EXE Bundling](#setup--exe-bundling)
13. [All Use Cases & Scenarios](#all-use-cases--scenarios)
14. [10-Week Phased Breakdown](#10-week-phased-breakdown)
15. [Testing Strategy](#testing-strategy)
16. [Performance Budgets & Profiling](#performance-budgets--profiling)
17. [Deployment & Release Checklist](#deployment--release-checklist)

---

## Overview & Greenfield Approach

This document specifies **complete scratch implementation** of JARVIS AI desktop agent. Nothing currently exists except empty Express + Electron shell. We build **everything** from zero, guided by the complete architecture specification.

### Implementation Philosophy

1. **Architecture-First**: Every component derives from `JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md` Section 1.7-1.15
2. **Scenario-Complete**: All 10 workflow scenarios implemented, not ignored
3. **Production-Ready**: Assume ship-day requirements from day 1
4. **User-Centric**: Voice UI professional, setup UX frictionless, error recovery elegant
5. **Extensible Foundation**: New agents added via registry pattern, not code surgery

### Team & Stack

- **Backend**: FastAPI + Python 3.10+ (async, type-checked)
- **Frontend**: Electron + React 18 + TypeScript (Vite)
- **Database**: SQLite + SQLAlchemy ORM
- **Voice**: Whisper (STT) + Piper (TTS)
- **Execution**: RobotJS + PowerShell + PyAutoGUI
- **Vision**: moondream (local 3-bit quantized)
- **LLM**: qwen2.5:3b via Ollama
- **Installer**: NSIS (electron-builder)

**Total LOC Estimate**: 12,000-15,000 (backend 6000, frontend 4000, tests 2500, setup 1500)

---

## Complete Architecture Implementation

### System Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  ELECTRON WINDOW (Browser)               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Chat UI | Voice UI | Execution Panel | Workflows   │ │
│  │  (Real-time updates via WebSocket 8 msg types)      │ │
│  └─────────────────────────────────────────────────────┘ │
│  WebSocket ↔ Socket.IO Namespace: /jarvis               │
└─────────────────────────────────────────────────────────┘
                          ↓ (Port 8000)
┌─────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Python)                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  ORCHESTRATOR (Main Loop)                          │  │
│  │  ├─ Input: Transcription from User Agent           │  │
│  │  ├─ Routes: RAG → SPA → SAA → EA → ...            │  │
│  │  ├─ Backtracking: 6 levels with escalation logic   │  │
│  │  └─ Output: WebSocket events to frontend           │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  AGENT REGISTRY (Self-registration pattern)        │  │
│  │  ├─ RAG Agent (Planning, qwen2.5:3b, 8-12s)       │  │
│  │  ├─ Clarification Agent (UX questions)             │  │
│  │  ├─ Web Search Agent (HTTP scraper, 24h cache)     │  │
│  │  ├─ SPA Agent (Semantic annotation, 5-8s)         │  │
│  │  ├─ SAA Agent (Execution method, 4-6s)             │  │
│  │  ├─ EA Agent (PowerShell/RobotJS, 12-30s vary)     │  │
│  │  ├─ OA Agent (OS monitoring, 3-5s per screenshot)  │  │
│  │  ├─ Safety Agent (Hardcoded rules)                 │  │
│  │  ├─ User Agent (Whisper input, Piper output)       │  │
│  │  ├─ CMA Agent (SQLite persistence)                 │  │
│  │  ├─ App Registry Agent (Windows registry scan)     │  │
│  │  ├─ Workflow Learner (Silent auto-save)            │  │
│  │  └─ Metadata Agent (Analytics, timing)             │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  REAL-TIME STREAMING ENGINE                        │  │
│  │  ├─ WebSocket (primary, <200ms latency)            │  │
│  │  ├─ SSE fallback (if WS unavailable)               │  │
│  │  ├─ Long-polling fallback (3s interval)            │  │
│  │  └─ 8 Message Types (start, progress, complete...) │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  PERSISTENCE LAYER (SQLite 11 Tables)              │  │
│  │  ├─ conversation_history (messages + confidence)    │  │
│  │  ├─ execution_logs (step traces + verification)     │  │
│  │  ├─ context_snapshots (backtracking recovery)      │  │
│  │  ├─ sessions (new/continue/resume management)      │  │
│  │  ├─ workflows (user-named sequences)                │  │
│  │  ├─ execution_records (silent auto-saves)          │  │
│  │  ├─ step_templates (reliability + timing stats)    │  │
│  │  ├─ workflow_executions (history + failures)       │  │
│  │  ├─ installed_apps (Windows registry cache)        │  │
│  │  ├─ app_scan_history (scan metadata)               │  │
│  │  └─ failure_history (patterns + recovery methods)  │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ↓           ↓              ↓               ↓
    [Models]  [Audio Streams]  [Screenshots]  [Logs/Telemetry]
```

---

## 13-Agent System Specification

All agents implement `BaseAgent` interface with `execute(input_payload)` → `AgentOutput(result, confidence, errors)`.

### Agent 1: RAG (Retrieval-Augmented Generation)

**Purpose**: Transform user intent into structured execution plan (step sequence)

**Input**:
- `query`: Cleaned user transcription (string)
- `context`: Last 5 conversation turns (list of Message records)
- `device_state`: Current device info (CPU, RAM, apps running)
- `installed_apps`: Cached app inventory (JSON from App Registry Agent)

**Process**:
1. Embed query using qwen2.5:3b context window
2. Retrieve 3 most similar historical workflow templates (semantic search)
3. Generate 4-12 atomic steps with parameters: `[{"action": "open_chrome", "params": {"url": "google.com"}}, ...]`
4. Add reasoning labels per step (why this step, error scenarios)

**Output**:
```json
{
  "steps": [
    {"id": 1, "action": "open_chrome", "params": {...}, "rationale": "..."},
    {"id": 2, "action": "type_text", "params": {...}, "rationale": "..."}
  ],
  "total_steps": 2,
  "estimated_duration_seconds": 25,
  "confidence": 0.87,
  "warnings": ["Chrome might not be installed"]
}
```

**Timing**: 8-12 seconds (qwen model inference)

**Failure Modes**:
- Model timeout (>15s) → Backtrack to Level 3 (user clarification)
- Confidence <0.6 → Trigger Clarification Agent
- Parameter binding failed → Ask user for input values

**Success Criteria**: Confidence ≥0.7, steps parseable as JSON, no syntax errors

---

### Agent 2: Clarification Agent

**Purpose**: Ask user targeted questions when confidence is low

**Input**:
- `user_query`: Original intent
- `confidence_gap_reason`: Why confidence is <0.7
- `ambiguity_score`: 0-1 measure of ambiguity

**Process**:
1. Generate 2-3 multiple-choice questions to disambiguate
2. Synthesize question audio using Piper
3. Wait for voice input via microphone (5s timeout)
4. Transcribe response with Whisper
5. Return clarified context

**Output**:
```json
{
  "clarified_query": "Open Outlook and send email to john@example.com",
  "modifications": ["Added recipient email"],
  "confidence_improvement": 0.23,
  "new_confidence": 0.90
}
```

**Timing**: 8-15 seconds (depends on user response time)

**Fallback**: If user silent after 5s, assume original intent with warning

---

### Agent 3: Web Search Agent

**Purpose**: Gather real-time info (prices, news, status pages) without LLM

**Input**:
- `search_query`: What to search (extracted from user intent)
- `source_filter`: reddit|twitter|news|all (optional)
- `cache_max_age_hours`: How old cache can be (default 24h)

**Process**:
1. Check SQLite cache (execution_logs.web_search_results) for age
2. If cache fresh (<age): return cached result
3. Else: HTTP GET to duckduckgo/searx/custom endpoint
4. Parse HTML (BeautifulSoup), extract top 5 results
5. Store cache with `cached_at` timestamp
6. Return structured [{"title": "...", "url": "...", "snippet": "..."}]

**Output**:
```json
{
  "results": [
    {"title": "...", "url": "...", "snippet": "...", "source": "reddit"},
    ...
  ],
  "search_duration_ms": 1200,
  "cached": false,
  "next_refresh": "2026-02-23T14:00:00Z"
}
```

**Timing**: 1-3 seconds (cache hit) or 3-8 seconds (HTTP request)

**Note**: No LLM involved. Pure HTTP + parsing.

---

### Agent 4: SPA (Semantic Parameter Annotation)

**Purpose**: Bind variables from user context to action parameters

**Input**:
- `steps_from_rag`: RAG output (unparsed parameters)
- `user_context`: Available variables (emails, phone numbers, app windows)
- `device_state`: Current device info

**Process**:
1. For each step's `params` dict with placeholders (`{email}`, `{file_path}`)
2. Use qwen2.5:3b to match placeholder to context variable
3. Perform fuzzy matching (user said "send to John" → find john@company.com in contacts)
4. Return filled parameters + confidence per binding

**Output**:
```json
{
  "steps_annotated": [
    {
      "id": 1,
      "action": "send_email",
      "params": {
        "recipient": "john.doe@company.com",
        "subject": "Q1 Report",
        "body": "..."
      },
      "bindings_confidence": {"recipient": 0.95, "subject": 0.88}
    }
  ],
  "missing_parameters": [],
  "overall_confidence": 0.91
}
```

**Timing**: 5-8 seconds

**Failure Mode**: Missing parameter → Ask user directly via User Agent (Piper question + Whisper input)

---

### Agent 5: SAA (Semantic Action Analyzer)

**Purpose**: Verify resource availability + select execution method

**Input**:
- `annotated_steps`: SPA output (all params bound)
- `device_state`: CPU, RAM, disk, network status

**Process**:
1. For each step, verify required app is installed (check App Registry cache)
2. Type-check parameters (URL vs file path vs email)
3. Estimate resource needs (disk write ~10MB? network required?)
4. Choose execution method: KeyboardEmulation | PowerShell | API | RobotJS
5. Return method assignments + resource warnings

**Output**:
```json
{
  "steps_verified": [
    {
      "id": 1,
      "action": "open_file",
      "method": "PowerShell",
      "resource_check": {
        "app_installed": true,
        "disk_available_mb": 5120,
        "sufficient": true
      }
    }
  ],
  "blockers": [],
  "estimated_execution_time_seconds": 32
}
```

**Timing**: 4-6 seconds

**Failure Mode**: Missing app → Trigger App Registry scan, cache result, ask user if should auto-install

---

### Agent 6: EA (Execution Agent) - "The Hands"

**Purpose**: Actually perform the automation (PowerShell commands, mouse/keyboard, web automation)

**Input**:
- `verified_steps`: SAA output (method assigned)
- `session_id`: For recovery

**Process** (Per Step):
1. **Pre-execution**: Take baseline screenshot (moondream scan for UI state)
2. **Execute**: Run PowerShell / RobotJS / direct API call
3. **Monitor**: Run moondream on captured screenshot every 2 seconds
4. **Verify**: Check step-result matches expected (e.g., file created, window opened)
5. **Record**: Log execution_log entry with timing, screenshot refs, confidence
6. On failure: Capture error state, alert Orchestrator for backtracking

**Sub-steps (12 total within EA)**:
1. Check if already done (idempotency)
2. Take pre-screenshot
3. Execute primary action
4. Poll for state change (max 10 polls, 2s each)
5. Take post-screenshot
6. Compare pre/post via moondream
7. Extract result data (window handle, filename, response JSON)
8. Record to execution_log
9. Persist to SQLite
10. Emit WebSocket step_complete event
11. Check for side effects (new windows, popups)
12. Return step result + confidence

**Output**:
```json
{
  "step_id": 3,
  "action": "open_file",
  "status": "completed",
  "duration_seconds": 2.1,
  "screenshots_captured": 3,
  "moondream_analysis": "File explorer opened showing /Documents folder",
  "confidence": 0.94,
  "extracted_data": {"window_handle": 12345}
}
```

**Timing**: Varies 1-30s per step (depends on action)

**Failure Points**:
- Action timeout (>15s with no state change) → Level 1 backtrack (retry with longer timeout)
- Moondream analysis shows error (red popup) → Level 2 backtrack (alternative method)
- Prerequisites failed (app not running) → Level 3 backtrack (ask clarification)
- Network timeout → Level 4 backtrack (retry with exponential backoff)
- Permission denied → Level 5 backtrack (ask user for elevation)
- Unrecoverable → Level 6 backtrack (abort, show error, ask user)

---

### Agent 7: OA (Observer Agent)

**Purpose**: Continuous background monitoring for unexpected OS state changes

**Running Parallel To**: EA steps (every 3-5 seconds)

**Input**:
- `current_device_state`: Baseline (apps, windows, files)
- `execution_id`: Which execution to monitor

**Process**:
1. Take screenshot every 3-5s (moondream analyze)
2. Scan for unexpected windows (error popups, UAC dialogs)
3. Monitor process list (new processes spawned?)
4. Check disk errors, CPU spikes (via psutil)
5. Classify changes: expected (file created) vs unexpected (crash dialog)
6. Emit alert if unexpected

**Output** (Alert sent to Orchestrator):
```json
{
  "alert_type": "unexpected_window",
  "description": "Windows SmartScreen popup appeared",
  "screenshot_ref": "screenshots/exec_123/frame_04.png",
  "recommended_action": "Level 2 Backtrack - click through SmartScreen",
  "confidence": 0.89
}
```

**Timing**: Every 3-5 seconds (async)

---

### Agent 8: Safety Agent

**Purpose**: Prevent destructive actions (hardcoded policy + user override)

**Input**:
- `steps`: Full execution plan
- `device_state`: What might be affected

**Hardcoded Rules**:
1. Reject: `rm -rf /`, DELETE all files, format disk
2. Reject: Disable Windows Defender, uninstall antivirus
3. Reject: Modify SYSTEM registry keys
4. Reject: Kill critical processes (svchost, csrss, lsass)
5. Reject: Run unverified .exe downloads
6. Warn: Send email/message (require user confirmation)
7. Warn: Modify code files (require user review)
8. Warn: Network requests to non-trusted domains (check whitelist)

**Process**:
1. Scan each step against ruleset
2. Categorize: safe | warn | reject
3. If warn: show user confirmation (Piper ask, Whisper confirm)
4. If reject: block step, suggest alternative

**Output**:
```json
{
  "safety_checks": [
    {"step_id": 1, "action": "send_email", "level": "warn", "reason": "User action, requires confirmation"},
    {"step_id": 2, "action": "open_chrome", "level": "safe"}
  ],
  "blocked_steps": [],
  "user_confirmations_needed": 1
}
```

**Timing**: <1 second

---

### Agent 9: User Agent

**Purpose**: Handle voice I/O (Whisper STT, Piper TTS) + context synchronization

**Input**:
- `message_type`: "ask_question" | "confirm_action" | "report_status"
- `content`: Text to speak or wait for input
- `timeout_seconds`: How long to listen (default 5s)

**Process for Output (TTS)**:
1. Queue Piper request (streaming audio generation)
2. Stream audio to Electron frontend via WebSocket
3. Frontend plays via Web Audio API
4. Store transcript as alternative in execution_log

**Process for Input (STT)**:
1. Activate microphone (PyAudio stream)
2. Capture audio for N seconds
3. Send to Whisper (local inference or Ollama)
4. Return transcription + confidence

**Output**:
```json
{
  "action": "spoke_and_listened",
  "spoken_text": "Which email recipient?",
  "spoken_duration_seconds": 1.2,
  "user_response": "john at company dot com",
  "transcription_confidence": 0.92
}
```

**Timing**: 2-3s (Piper) + user latency (Whisper)

---

### Agent 10: CMA (Conversation Memory Agent)

**Purpose**: Persist all execution state to SQLite for recovery and learning

**Input**:
- `execution_id`: Which execution summary to store
- `all_step_results`: Array of step outputs from EA
- `conversation_context`: Chat messages + user profile

**Process**:
1. Insert rows into: conversation_history, execution_logs, execution_records, step_templates
2. Update: context_snapshots (for backtracking recovery)
3. Store screenshots references
4. Calculate timing stats per step for future burden estimation
5. Commit transaction

**Output**:
```json
{
  "conversation_id": "msg_456",
  "execution_id": "exec_789",
  "records_persisted": {
    "conversation_history": 1,
    "execution_logs": 12,
    "step_templates": 2,
    "context_snapshots": 1
  },
  "database_size_mb": 154.2
}
```

**Timing**: <1 second (batch insert)

---

### Agent 11: App Registry Agent

**Purpose**: Scan Windows registry for installed apps, cache in SQLite

**Input**:
- `force_refresh`: Boolean (skip cache, always scan)
- `app_filter`: Optional (e.g., only "Microsoft.Office*")

**Process**:
1. Run PowerShell script to read HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall
2. Parse: DisplayName, InstallLocation, UninstallString, Version
3. Cache in SQLite with `scanned_at` timestamp (5-day TTL)
4. Return JSON list: `[{"name": "Chrome", "version": "123.0.1", "path": "C:\\..."}]`

**Output**:
```json
{
  "apps_found": 127,
  "scan_duration_seconds": 2.3,
  "cached": false,
  "apps": [
    {"name": "Google Chrome", "version": "123.0.1", "path": "C:\\Program Files\\Google\\Chrome\\Application"},
    ...
  ],
  "next_refresh": "2026-02-27T14:00:00Z"
}
```

**Timing**: 2-4 seconds (first scan), <100ms (cache hit)

---

### Agent 12: Workflow Learner (Dual-Agent)

**Agent 12A: Silent Auto-Saver**

Every execution automatically saved to `execution_records` with:
- `execution_id`, `step_sequence` (steps taken), `user_intent`, `timestamp`
- No UI, silent background operation

**Agent 12B: Intelligent Matcher**

When user says something similar to past workflows:
1. Semantic search past 50 executions (embedding similarity)
2. Rank by match confidence (0-1.0):
   - >0.95: Exact match → Suggest with "Run this workflow?"
   - 0.85-0.95: Near match → Suggest hybrid (skip already-done steps)
   - 0.70-0.84: Partial match → Suggest as template (fill gaps)
   - <0.70: No match → Generate new plan via RAG

**Output**:
```json
{
  "workflow_suggestions": [
    {
      "workflow_id": "w_123",
      "similarity": 0.93,
      "reason": "User said 'send email to John' again (did this 3 times before)",
      "suggested_action": "Reuse previous workflow",
      "time_saved_seconds": 35
    }
  ],
  "total_commands_learned": 47,
  "workflows_available": 12
}
```

**10 Scenarios Covered**:
1. **Exact Repetition** (same query verbatim) → 0-3s execution
2. **Intent Drift** (similar but slightly different params) → Use template, fill gaps
3. **Composite Tasks** (chain multiple known workflows) → Merge step sequences
4. **Partial Matches** (some steps already done) → Skip done steps, execute remainder
5. **Step Deduplication** (user does "open Chrome, open Gmail, open Gmail again") → Detect dupe, skip
6. **Failure Pattern Learning** (step 3 always times out) → Add 10s buffer before retry
7. **Device-Specific Paths** (paths differ Windows vs Linux) → Learn both, pick based on OS
8. **Workflow Evolution** (workflow improved after 20 executions) → Replace template with latest version
9. **Scheduled + Learned** (user wants task daily at 9am) → Create cron, use workflow template
10. **Cross-User Patterns** (team members run same workflows) → Shared workflow library basis

**Time Savings**: After 1000 commands, ~66% faster average execution (45s → 15s median due to workflow reuse)

---

### Agent 13: Orchestrator (Main Loop)

**Purpose**: Route input → agents → backtracking on failures

**State Machine**:
```
[Input] → [RAG] → [Clarification?] → [Web Search?] → [Safety Check]
         ↓                                              ↓
    [RAG Output]                                  [Safe to Execute]
                        ↓
              [SPA] → [SAA] → [EA (per step)]
              ↓                  ↓
          Annotation        Execution
          Complete          Complete
              ↓                  ↓
         [OA Monitoring] ← ← ← ← 
              ↓
          [Success?] YES → [CMA Persist] → [Complete]
              ↓ NO
          [Backtrack Router]
              ↓
     Level 1-6 Escalation
```

**6-Level Backtracking**:
1. **Level 1 - Retry with Longer Timeout** (action timing edge case)
   - Rerun last step with 2x timeout
   - Max 2 attempts before escalate

2. **Level 2 - Alternative Method** (method failed, try another)
   - If PowerShell failed, try RobotJS
   - If API failed, try web UI automation
   - Rerun last 1-2 steps

3. **Level 3 - Ask for Clarification** (confidence drops, need user input)
   - Piper: "Did you mean X or Y?"
   - Whisper: Get user response
   - Regenerate plan with clarification

4. **Level 4 - Retry with Exponential Backoff** (network/resource contention)
   - Wait 1s, retry (all steps from current)
   - Wait 3s, retry
   - Wait 10s, retry
   - Max 3 attempts

5. **Level 5 - Request Elevation** (permission denied)
   - Piper: "I need admin rights. Allow UAC dialog?"
   - Require user confirmation
   - Rerun with elevation flag

6. **Level 6 - Manual Recovery** (unrecoverable error)
   - Show error state (screenshot, error message)
   - Ask user: continue anyway | start over | abort
   - Store in failure_history for future learning

**Decision Logic**:
```python
def route_to_backtrack_level(error_code, attempt_count):
    if error_code == "TIMEOUT" and attempt_count < 2:
        return Level1  # Retry with longer timeout
    elif error_code == "METHOD_FAILED":
        return Level2  # Alternative method
    elif error_code == "LOW_CONFIDENCE":
        return Level3  # Ask clarification
    elif error_code in ["NETWORK_ERROR", "RESOURCE_EXHAUSTED"]:
        return Level4  # Exponential backoff
    elif error_code == "PERMISSION_DENIED":
        return Level5  # Request elevation
    else:
        return Level6  # Manual recovery
```

**Orchestrator Output** (WebSocket events throughout):
- `execution_started` (timestamp, total_steps)
- `agent_started` (which agent, step)
- `agent_completed` (result, duration, confidence)
- `step_completed` (step N/M, took Xs, confidence)
- `backtrack_triggered` (level, reason)
- `execution_completed` (success, total_duration, commands_learned)
- `execution_failed` (error, recovery_suggestions)

**Timing**: Zero overhead (state machine routes between agents)

**Context Persistence**: Before any backtrack, snapshot `context_snapshots` table with full execution state, allowing recovery from any level

---

## Real-Time Streaming Architecture

### WebSocket Message Types (8 Total)

All messages sent via Socket.IO namespace `/jarvis` with JSON payload:

#### 1. `execution_started`
```json
{
  "type": "execution_started",
  "execution_id": "exec_abc123",
  "timestamp": "2026-02-22T14:00:00Z",
  "total_steps": 5,
  "estimated_duration_seconds": 35
}
```

#### 2. `step_started`
```json
{
  "type": "step_started",
  "execution_id": "exec_abc123",
  "step_number": 2,
  "step_total": 5,
  "action": "send_email",
  "timestamp": "2026-02-22T14:00:15Z"
}
```

#### 3. `step_progress` (Per-step sub-steps)
```json
{
  "type": "step_progress",
  "execution_id": "exec_abc123",
  "step_number": 2,
  "sub_step": "take_post_screenshot",
  "elapsed_ms": 2350,
  "message": "Verifying email opened in Outlook"
}
```

#### 4. `step_completed`
```json
{
  "type": "step_completed",
  "execution_id": "exec_abc123",
  "step_number": 2,
  "step_total": 5,
  "action": "send_email",
  "duration_seconds": 4.2,
  "status": "success",
  "confidence": 0.92,
  "timestamp": "2026-02-22T14:00:19Z"
}
```

#### 5. `backtrack_initiated`
```json
{
  "type": "backtrack_initiated",
  "execution_id": "exec_abc123",
  "step_number": 3,
  "backtrack_level": 2,
  "reason": "METHOD_FAILED",
  "recovery_message": "Trying alternative method (RobotJS instead of PowerShell)",
  "timestamp": "2026-02-22T14:00:25Z"
}
```

#### 6. `user_input_needed`
```json
{
  "type": "user_input_needed",
  "execution_id": "exec_abc123",
  "input_type": "clarification",
  "tts_text": "Which email recipient: john@company.com or john.doe@gmail.com?",
  "timeout_seconds": 10,
  "timestamp": "2026-02-22T14:00:30Z"
}
```

#### 7. `execution_completed`
```json
{
  "type": "execution_completed",
  "execution_id": "exec_abc123",
  "status": "success",
  "total_duration_seconds": 32.5,
  "steps_executed": 5,
  "workflow_saved_as": "email_john_quarterly_report",
  "similar_workflows_found": 2,
  "timestamp": "2026-02-22T14:00:33Z"
}
```

#### 8. `execution_failed`
```json
{
  "type": "execution_failed",
  "execution_id": "exec_abc123",
  "step_number": 4,
  "error_code": "UNRECOVERABLE_ERROR",
  "error_message": "Chrome crashed and cannot be recovered",
  "recovery_suggestions": [
    "Try again after restart",
    "Use Firefox instead",
    "Check system logs for details"
  ],
  "failure_screenshot": "screenshots/exec_abc123/error_frame.png",
  "timestamp": "2026-02-22T14:00:40Z"
}
```

### Connection Management

```python
# FastAPI + python-socketio

from fastapi import FastAPI
from fastapi_socketio import SocketManager

app = FastAPI()
sio = SocketManager(app, cors_allowed_origins="*")

@sio.on('connect', namespace='/jarvis')
async def connect(sid, environ):
    session_id = environ.get('HTTP_COOKIE')  # Extract session ID
    print(f"Client {sid} connected, session {session_id}")

@sio.on('disconnect', namespace='/jarvis')
async def disconnect(sid):
    print(f"Client {sid} disconnected")

# Server → Client (broadcast execution updates)
async def emit_execution_event(execution_id, message_type, payload):
    await sio.emit(message_type, payload, namespace='/jarvis')

# Client → Server (user confirms action, provides input)
@sio.on('user_confirmed_action', namespace='/jarvis')
async def handle_user_confirmation(sid, data):
    execution_id = data['execution_id']
    confirmation = data['confirmed']
    # Resume execution with user confirmation
```

### Fallback Chain

1. **Primary**: WebSocket (persistent, <200ms latency)
2. **Fallback 1**: Server-Sent Events (if WS unavailable, use XHR polling with chunked encoding)
3. **Fallback 2**: Long-Polling (3s interval HTTP GET, client processes event batch)
4. **Last Resort**: Frontend polls `/api/execution/{execution_id}` every 1s for status (janky but works)

---

## Voice UI Implementation (8 States)

All states run on separate RAF (requestAnimationFrame) loop for smooth 60fps animation. Canvas-based rendering for performance.

### State 1: Default (Idle)
- Visual: Static JARVIS logo (blue gradient, no animation)
- Color: `#0078D4` (Microsoft blue)
- Duration: Forever (until user speaks)
- CSS: `opacity: 1, scale: 1`

### State 2: Listening (Active Microphone)
- Visual: Breathing waveform (5-8 bars, growing/shrinking)
- Animation: `exp(sin(t * π)) * max_height` (smooth breathing)
- Color: `#0078D4` (blue)
- Frequency**: 2-3 breaths per second
- Duration: Until audio detected
- Audio Sync: Bar heights DO NOT follow microphone amplitudes (just breathing, decorative)

### State 3: Audio Detected (Microphone Picking Up Sound)
- Visual: Waveform bars sync to actual microphone amplitude
- Animation: Bar height = current audio level (real-time frequency analysis)
- Color: `#0078D4` (transitions slightly brighter)
- Frequency: Update every 100ms (10x per second)
- Duration: Until silence detected (>1s no sound)

### State 4: Recognized (STT Success)
- Visual: Green checkmark overlaid on waveform + flash
- Animation: Checkmark scales from 0→1 (200ms ease-out), flash background (500ms fade)
- Color: `#34C759` (iOS green)
- Duration: 500ms (auto-advance to thinking)

### State 5: Thinking (LLM Planning)
- Visual: Pulsing central orb + orbiting particles
- Animation: 
  - Orb: scale 0.8→1.2→0.8 (2s loop)
  - Particles: 3 dots orbit around orb (360° rotation every 3s)
  - Color shifts: Orange pulse (#FF9500), particle glow
- Duration: 8-15 seconds (RAG + SPA + SAA)

### State 6: Speaking (Audio Playback)
- Visual: Frequency waveform synced to TTS audio playback
- Animation: 8-10 bars, height = frequency amplitude from Web Audio API analyzer
- Color: `#FFD700` (golden)
- Audio Sync: **Precise sync** - frequency bins from analyser.getByteFrequencyData()
- Duration: Until audio finishes (1-5s typically)

### State 7: Error (Failure Detected)
- Visual: Red pulsing ring around logo + alert icon (!)
- Animation:
  - Ring scale: 1→1.3→1 (1s pulse, 3x repeats then hold)
  - Alert icon rotation: Slight wiggle (±5°)
  - Background: Subtle red tint (#FF3B30)
- Duration: 3 seconds (auto-dismiss) or until user interacts

### State 8: Complete (Execution Success)
- Visual: Celebratory checkmark (large, centered) + confetti animation
- Animation:
  - Checkmark: Draw animation (SVG pathLength transition)
  - Confetti: 20-30 small circular particles falling from top with rotation
- Color: `#34C759` (green)
- Duration: 1-2 seconds then fade back to default

### State Transitions (With Timings)

```
Default (idle)
    ↓ [user wakes mic]
Listening (breathing, 2-3s)
    ↓ [detects sound >-30dB]
Audio Detected (real-time waveform)
    ↓ [Whisper completes, confidence >0.7]
Recognized (checkmark flash, 0.5s)
    ↓ [auto-advance]
Thinking (pulsing orb, 8-15s)
    ├─ [if need clarification]
    │  └→ User Input Needed (Piper speaks, user responds)
    │     └→ Back to Thinking
    ├─ [if error in backtracking]
    │  └→ Error (3s)
    │     └→ Thinking (retry) OR Default (abort)
    ├─ [if execution needed]
    │  └→ Speaking (TTS, 1-5s)  [runs DURING EA steps too]
    └─ [success]
       └→ Complete (1-2s checkmark + confetti)
          └→ Default
```

### Code Structure

```typescript
// React component managing voice UI state machine
import { useVoiceState } from '@/store/useVoiceState'
import { WaveformAnimation } from './WaveformAnimation'
import { ParticleEffect } from './ParticleEffect'
import { useState, useEffect } from 'react'

export function VoiceIndicator() {
  const [voiceState, setVoiceState] = useVoiceState()
  const [animationFrame, setAnimationFrame] = useState(0)

  // Main animation loop (60fps)
  useEffect(() => {
    const raf = requestAnimationFrame((timestamp) => {
      updateAnimation(timestamp, voiceState)
      setAnimationFrame(prev => prev + 1)
    })
    return () => cancelAnimationFrame(raf)
  }, [voiceState])

  // Render appropriate visual per state
  const renderState = () => {
    switch (voiceState.current_state) {
      case 'listening':
        return <WaveformAnimation mode="breathing" />
      case 'audio_detected':
        return <WaveformAnimation mode="realtime" audioLevel={voiceState.audio_level} />
      case 'recognized':
        return <CheckmarkFlash />
      case 'thinking':
        return <ParticleEffect type="thinking" />
      case 'speaking':
        return <WaveformAnimation mode="frequency" frequencies={voiceState.frequencies} />
      case 'error':
        return <ErrorPulse message={voiceState.error_message} />
      case 'complete':
        return <SuccessConfetti />
      default:
        return <StaticLogo />
    }
  }

  return (
    <div className="voice-indicator-container">
      {renderState()}
      <div className="state-label">{voiceState.current_state}</div>
    </div>
  )
}
```

### CSS Animations

```css
@keyframes breathing {
  0% { height: 20px; }
  50% { height: 60px; }
  100% { height: 20px; }
}

@keyframes pulse-think {
  0% { transform: scale(0.8); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0.7; }
}

@keyframes orbit {
  0% { transform: rotate(0deg) translateX(40px) rotate(0deg); }
  100% { transform: rotate(360deg) translateX(40px) rotate(-360deg); }
}

@keyframes error-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes confetti-fall {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(200px) rotate(360deg); opacity: 0; }
}

.waveform-bar {
  animation: breathing 2s ease-in-out infinite;
  height: 30px;
  width: 4px;
  background: linear-gradient(to top, #0078D4, #00B4D8);
  border-radius: 2px;
}

.pulsing-orb {
  animation: pulse-think 2s ease-in-out infinite;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, #FF9500 0%, #FFB500 100%);
  border-radius: 50%;
}

.orbit-particle {
  animation: orbit 3s linear infinite;
  width: 8px;
  height: 8px;
  background: #FFD700;
  border-radius: 50%;
  position: absolute;
}
```

### Audio Sync for Speaking State

```typescript
// Electron main process (audio playback)
import Speaker from 'speaker'
import { Transform } from 'stream'

// Get frequency data during playback
const audioContext = new AudioContext()
const analyser = audioContext.createAnalyser()
analyser.fftSize = 256

// Wire speaker output to analyser
speaker.pipe(analyser)

// Send frequencies to frontend every 100ms
setInterval(() => {
  const frequencies = new Uint8Array(analyser.frequencyBinCount)
  analyser.getByteFrequencyData(frequencies)
  
  // Send to frontend via WebSocket
  socket.emit('audio_frequencies', {
    frequencies: Array.from(frequencies),
    timestamp: Date.now()
  })
}, 100)
```

---

## Workflow Learning System

### Architecture (2-Layer)

**Layer 1: Silent Auto-Save (Execution Records)**
- Every execution automatically recorded to `execution_records` table
- No UI, no user interaction required
- Records: `[execution_id, step_sequence_json, user_intent, timestamp, success_flag]`
- Grows continuously (50-100 records/day assumed)

**Layer 2: Conscious Save (User-Named Workflows)**
- User can explicitly "name" a successful execution
- Saved to `workflows` table with user-provided name
- Appears in UI sidebar for quick reuse
- Example: "Send Quarterly Report to John"

### Intelligent Matching (Agent 12B)

When user speaks new command:

1. **Semantic Search**: 
   - Embed user query with qwen2.5:3b
   - Find 5 most similar past executions (cosine similarity in vector space)
   - Rank by time-decay (recent executions weighted higher)

2. **Confidence Calculation**:
   - Exact parameter match (same email address): +0.15
   - Same action steps: +0.10 per match
   - Same sequence order: +0.10
   - Time since execution (recent): +0.05
   - User success rate on template: +varies
   - Result: confidence score 0-1.0

3. **Decision Thresholds**:
   - **0.95-1.0**: Exact match → "Run this workflow again?" (1-click approval)
   - **0.85-0.94**: Near match → "Should I reuse steps 1-3 from last time?" (confirm with diffs)
   - **0.70-0.84**: Partial match → Show as template, user fills gaps
   - **<0.70**: No suggestion, generate new plan via RAG

### 10 Concrete Scenarios with Implementation

#### Scenario 1: Exact Repetition (Confidence: 0.98)
- **User**: "Send email to john about Q4 report"
- **History**: Did exact same thing Tuesday
- **Workflow**: Store full execution (steps identical, parameters identical)
- **Action**: Show "Rerun workflow 'Q4 Report Email'? [1 Click]"
- **Time Saved**: 45s → 3s (execution skips RAG/SPA/SAA, goes straight to EA with cached params)
- **Storage**: 1 record in execution_records table + 1 namedworkflow

#### Scenario 2: Intent Drift (Confidence: 0.82)
- **User**: "Email john about Q1 report" (last time was Q4)
- **History**: Previous workflow has same template (email + attachment)
- **Workflow**: Suggest "Reuse template, change report to Q1?"
- **Action**: Show diff (old param: Q4, new param: Q1)
- **Time Saved**: 45s → 20s (skip RAG planning, use SPA from history)
- **Implementation**: Match first 3 steps, regenerate param binding for step 2

#### Scenario 3: Composite Tasks (Confidence: 0.88)
- **User**: "Send email about Q4 report and then forward to team"
- **History**: Have two workflows: "Email John" (4 steps) + "Forward to Team" (3 steps)
- **Action**: Suggest merging workflows
- **Time Saved**: 45s×2 = 90s → 35s (reuse both templates, merge steps)
- **Implementation**: combine_workflows(template_1, template_2) → detect step overlap, remove duplicates

#### Scenario 4: Partial Matches (Confidence: 0.75)
- **User**: "Do the spreadsheet analysis like last week"
- **History**: Last week: open Excel, load file, create pivot table, send results (5 steps)
- **Today**: Excel already open, just load file and pivot
- **Action**: "Steps 1-2: Open Excel - already done. Continue from step 3?" (skip already-done steps)
- **Time Saved**: 45s → 20s (EA skips 2 steps, starts step 3)
- **Implementation**: Compare device state (is Excel open?) against workflow preconditions

#### Scenario 5: Step Deduplication (Confidence: 0.91)
- **User**: "Open Chrome, open Gmail" (does this every day)
- **History**: Pattern: user says "open Chrome" then "open Gmail" then "open Gmail" again
- **Detection**: Workflow learning detects redundant steps in history
- **Action**: Auto-deduplicate workflow (store only: open Chrome, open Gmail once)
- **Time Saved**: 15s → 8s (skip second Gmail open)
- **Implementation**: step_dedup(execution_records) → if step[n] == step[n-1], remove step[n]

#### Scenario 6: Failure Pattern Learning (Confidence: 0.70)
- **User**: "Run the Python script" (tried 5 times, step 3 times out)
- **History**: In failure_history table: "python_script.py times out 30% of attempts"
- **Detection**: Machine learning: "timeout at step 3, add buffer before next retry"
- **Action**: Pre-emptively increase timeout from 10s → 20s for step 3
- **Time Saved**: 45s + 8s backtrack → 35s (no backtrack needed)
- **Implementation**: analyze_failure_history(step_id, action) → if timeout_rate > 20%, increase timeout_buffer = timeout_base * 1.5

#### Scenario 7: Device-Specific Paths (Confidence: 0.85)
- **User**: "Compile the C++ project"
- **History**: Learned Windows path: `C:\build\project\CMakeLists.txt`
- **Today Context**: Running on laptop (same Windows machine)
- **Action**: Reuse Windows path from history
- **Time Saved**: 45s → 15s (skip SAA resource check for known path)
- **Implementation**: workflow_template.params = interpolate_for_device(device_id, past_params)

#### Scenario 8: Workflow Evolution (Confidence: 0.88)
- **User**: "Do the morning standup"
- **History**: Workflow "morning_standup" tried 20 times, success rate improved after 15th attempt
- **Evolution**: Repository of past executions shows continuous refinement
- **Action**: Use LATEST version of workflow (after 15th attempt improvements)
- **Time Saved**: 45s → 12s (optimized workflow, unnecessary steps removed)
- **Implementation**: workflow_version = max(execution_records[workflow_id], key=timestamp) if success_flag

#### Scenario 9: Scheduled + Learned (Confidence: 0.92)
- **User**: "Run standup at 9am every weekday"
- **History**: Workflow "morning_standup" exists, reliable
- **Action**: Create cron job + save workflow reference (recurring_workflows table)
- **Time Saved**: Manual execution 5s × 5 days = 25s/week → Fully automated
- **Implementation**: scheduler.add_cron(cron="0 9 * * 1-5", workflow_id="morning_standup")

#### Scenario 10: Cross-User Patterns (Confidence: 0.81)
- **User A**: "Send weekly report to manager"
- **User B**: "Send report to manager" (same person, different team)
- **Detection**: Team members can opt-in to shared workflow library
- **Action**: Suggest "Similar workflow exists in team library, use it?"
- **Time Saved**: 45s → 8s (use team template)
- **Implementation**: query workflows WHERE team_shared=true, calculate_similarity()

### Database Tables for Learning

**execution_records** (Silent auto-save):
```sql
CREATE TABLE execution_records (
  id INTEGER PRIMARY KEY,
  execution_id TEXT UNIQUE,
  step_sequence JSON,              -- Array of steps taken
  user_intent TEXT,                -- Original user spoken text
  success_flag BOOLEAN,
  total_duration_seconds FLOAT,
  timestamp DATETIME,
  device_id TEXT                   -- Tied to device (laptop vs desktop)
);
CREATE INDEX idx_execution_records_similarity ON execution_records(user_intent);
```

**workflows** (Conscious save):
```sql
CREATE TABLE workflows (
  id INTEGER PRIMARY KEY,
  workflow_id TEXT UNIQUE,
  user_name TEXT,                  -- What user called it
  step_sequence JSON,
  created_at DATETIME,
  last_used DATETIME,
  success_rate FLOAT,              -- Percent of times it succeeded
  execution_count INTEGER,
  team_shared BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_workflows_success_rate ON workflows(success_rate);
```

**step_templates** (Reliability stats):
```sql
CREATE TABLE step_templates (
  id INTEGER PRIMARY KEY,
  action_name TEXT,
  execution_count INTEGER,
  success_count INTEGER,
  avg_duration_seconds FLOAT,
  median_duration_seconds FLOAT,
  p95_duration_seconds FLOAT,
  failure_rate FLOAT
);
```

**failure_history** (Learn from mistakes):
```sql
CREATE TABLE failure_history (
  id INTEGER PRIMARY KEY,
  step_id INTEGER,
  action_name TEXT,
  error_code TEXT,
  occurrence_count INTEGER,
  last_occurrence DATETIME,
  successful_recovery_method TEXT,  -- Which backtrack level worked?
  recovery_success_rate FLOAT
);
```

### ROI Calculation

Assumptions:
- User executes ~10 commands/day with average 45s per command
- After 1000 commands (~100 days), 50 core workflows learned
- Workflow reuse speeds up: 45s → 15s (repeats), 45s → 25s (partial matches), 45s → 35s (intent drift)

```
Day 1-50: All new workflows (45s × 10 cmd/day = 450s/day)
Day 50-100: 30% workflow reuse (45s × 7cmd + 15s × 3cmd = 360s/day) - 20% savings
Day 100+: 60% workflow reuse (45s × 4cmd + 20s × 6cmd = 300s/day) - 33% savings

Total time after 1000 commands:
Without learning: 1000 cmd × 45s = 45,000s (12.5 hours)
With learning: (500 × 45s) + (300 × 20s) + (200 × 15s) = 22,500 + 6,000 + 3,000 = 31,500s (8.75 hours)

Time Saved: 13,500s = 3.75 hours over 100 days = 2.25 min/day average
ROI: (13,500s saved / 31,500s final time) = 43% faster average execution
```

---

## Database Design & Migrations

### 11 Core Tables (All)

#### 1. **conversation_history**
```sql
CREATE TABLE conversation_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  user_message TEXT,
  user_confidence FLOAT,
  assistant_response TEXT,
  assistant_confidence FLOAT,
  turn_number INTEGER,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);
CREATE INDEX idx_conv_session ON conversation_history(session_id);
CREATE INDEX idx_conv_timestamp ON conversation_history(timestamp);
```

#### 2. **execution_logs**
```sql
CREATE TABLE execution_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  execution_id TEXT UNIQUE,
  session_id TEXT,
  step_number INTEGER,
  action_name TEXT,
  status TEXT,              -- 'pending', 'in_progress', 'success', 'failed'
  start_time DATETIME,
  end_time DATETIME,
  duration_seconds FLOAT,
  input_params JSON,
  output_result JSON,
  confidence FLOAT,
  error_message TEXT,
  screenshot_ref TEXT,      -- Path like "screenshots/exec_abc/frame_04.png"
  moondream_analysis TEXT,  -- Semantic description of screenshot
  FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);
CREATE INDEX idx_exec_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_exec_logs_action ON execution_logs(action_name);
```

#### 3. **context_snapshots** (Backtracking recovery)
```sql
CREATE TABLE context_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  execution_id TEXT,
  backtrack_level INTEGER,  -- Which level was triggered
  snapshot_timestamp DATETIME,
  device_state JSON,        -- Full device state at failure point
  failed_step_number INTEGER,
  recovery_action TEXT,     -- What was tried
  recovery_success BOOLEAN,
  FOREIGN KEY(execution_id) REFERENCES execution_logs(execution_id)
);
CREATE INDEX idx_snapshots_execution ON context_snapshots(execution_id);
```

#### 4. **sessions**
```sql
CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT UNIQUE,
  session_type TEXT,        -- 'new', 'continue', 'resume'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_activity DATETIME,
  execution_count INTEGER DEFAULT 0,
  total_commands TEXT,      -- Comma-separated command IDs in order
  recovery_step_number INTEGER,  -- For 'resume' sessions
  user_profile_id TEXT
);
CREATE INDEX idx_sessions_user ON sessions(user_profile_id);
```

#### 5. **workflows** (Conscious saves)
```sql
CREATE TABLE workflows (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workflow_id TEXT UNIQUE,
  workflow_name TEXT,       -- "Send Q4 Report to John"
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_used DATETIME,
  execution_count INTEGER DEFAULT 0,
  success_count INTEGER DEFAULT 0,
  step_sequence JSON,       -- Full step array as JSON
  user_intent_template TEXT,  -- Pattern like "Send {report_type} to {recipient}"
  estimated_duration_seconds FLOAT,
  team_shared BOOLEAN DEFAULT FALSE,
  is_latest_version BOOLEAN DEFAULT TRUE
);
CREATE INDEX idx_workflows_shared ON workflows(team_shared);
```

#### 6. **execution_records** (Silent auto-saves)
```sql
CREATE TABLE execution_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  execution_id TEXT UNIQUE,
  user_intent TEXT,
  step_sequence JSON,
  success_flag BOOLEAN,
  total_duration_seconds FLOAT,
  device_id TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  embedding_vector BLOB     -- SQLite VSS for semantic search
);
CREATE INDEX idx_exec_records_timestamp ON execution_records(timestamp);
```

#### 7. **step_templates** (Reliability database)
```sql
CREATE TABLE step_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action_name TEXT UNIQUE,  -- "open_chrome", "send_email", etc.
  execution_count INTEGER DEFAULT 0,
  success_count INTEGER DEFAULT 0,
  total_duration_seconds FLOAT DEFAULT 0,
  avg_duration_seconds FLOAT,
  median_duration_seconds FLOAT,
  p95_duration_seconds FLOAT,
  p99_duration_seconds FLOAT,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_templates_action ON step_templates(action_name);
```

#### 8. **workflow_executions** (History per workflow)
```sql
CREATE TABLE workflow_executions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workflow_id TEXT,
  execution_id TEXT,
  session_id TEXT,
  ran_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT,              -- 'success', 'failed', 'partial'
  duration_seconds FLOAT,
  steps_completed INTEGER,
  total_steps INTEGER,
  failure_reason TEXT,
  user_rating INTEGER,      -- 1-5 stars
  FOREIGN KEY(workflow_id) REFERENCES workflows(workflow_id),
  FOREIGN KEY(execution_id) REFERENCES execution_logs(execution_id)
);
CREATE INDEX idx_workflow_execs_workflow ON workflow_executions(workflow_id);
```

#### 9. **installed_apps** (Registry cache)
```sql
CREATE TABLE installed_apps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  app_name TEXT,
  display_name TEXT,
  version TEXT,
  install_location TEXT,
  uninstall_string TEXT,
  publisher TEXT,
  install_date DATETIME,
  cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_apps_name ON installed_apps(app_name);
```

#### 10. **app_scan_history**
```sql
CREATE TABLE app_scan_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scan_id TEXT UNIQUE,
  scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  total_apps_found INTEGER,
  scan_duration_seconds FLOAT,
  scan_type TEXT             -- 'full', 'incremental'
);
```

#### 11. **failure_history** (Learn from failures)
```sql
CREATE TABLE failure_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action_name TEXT,
  error_code TEXT,
  occurrence_count INTEGER DEFAULT 1,
  successful_recovery_method TEXT,  -- Which backtrack level worked
  recovery_success_rate FLOAT,
  last_occurrence DATETIME DEFAULT CURRENT_TIMESTAMP,
  severity_level INTEGER             -- 1-5, where 5 is critical
);
CREATE INDEX idx_failures_action ON failure_history(action_name, error_code);
```

### Migrations & Schema Versioning

```python
# database/migrations.py

class MigrationV1:
    """Initial schema creation (all 11 tables)"""
    version = 1
    
    def up(db):
        # Run all 11 CREATE TABLE statements
        pass
    
    def down(db):
        # Drop all 11 tables (rollback)
        pass

class MigrationV2:
    """Add embedding vector column for semantic search"""
    version = 2
    
    def up(db):
        # ALTER TABLE execution_records ADD COLUMN embedding_vector BLOB
        pass

# Auto-apply migrations on startup
def ensure_schema(db):
    schema_version = db.execute("PRAGMA user_version").fetchone()[0]
    if schema_version < CURRENT_VERSION:
        for migration in all_migrations:
            if migration.version > schema_version:
                migration.up(db)
        db.execute(f"PRAGMA user_version = {CURRENT_VERSION}")
```

### Indices for Performance

Critical indices created:
- `conversation_history(session_id, timestamp)` - Fast chat history retrieval
- `execution_logs(execution_id, action_name)` - Query by execution or action type
- `workflows(team_shared, success_rate)` - Quick workflow suggestions
- `step_templates(action_name, median_duration_seconds)` - Timing lookups
- `failure_history(action_name, error_code)` - Failure pattern analysis
- Full-text search on `user_intent` for semantic matching

---

## 12-Step Execution Pipeline

Complete timing breakdown from user input to output:

```
T=0s      [User speaks "Send email to John"]
          └─ Microphone active (PyAudio stream begins)

T=0-2.5s  [STEP 1-2: Audio Capture + Whisper STT]
          ├─ PyAudio continuously captures audio (16kHz, 16-bit)
          ├─ Once user stops talking, send audio to Whisper
          ├─ Whisper inference: 2-3 seconds
          ├─ Output: "Send email to John" (confidence: 0.94)
          └─ WebSocket emit: `recognition_completed` event

T=2.5s    [User Agent output: transcription confidence 0.94]

T=2.5-12s [STEP 3-5: RAG Planning]
          ├─ Input: "Send email to John" + conversation context
          ├─ Embed query with qwen2.5:3b (8-12s)
          ├─ Generate step sequence: [open_outlook, compose_email, type_to_john@..., send]
          ├─ Output: 4 steps, confidence 0.87
          └─ WebSocket emit: `planning_completed` event

T=12s     [RAG Agent output: step_sequence]

T=12-18s  [STEP 6-7: SPA Annotation + Parameter Binding]
          ├─ SPA takes RAG output + user context
          ├─ Match "john" → calendar shows john@company.com
          ├─ Fill all placeholders
          ├─ Output: steps fully annotated
          └─ Duration: 5-8 seconds

T=18s     [SPA Agent output: all params bound]

T=18-23s  [STEP 8-9: SAA Method Selection + Resource Check]
          ├─ SAA analyzes each step
          ├─ Check: Is Outlook installed? (app registry cache hit, <100ms)
          ├─ Assign execution method per step: PowerShell vs RobotJS vs direct API
          ├─ Final resource check: disk ok, network ok
          ├─ Duration: 4-6 seconds
          └─ WebSocket emit: `resource_check_completed` event

T=23s     [SAA Agent output: steps ready for execution]

T=23s-45s [STEP 10-12: EA Execution (Step-by-step)]
          │
          ├─ Step 1: Open Outlook
          │ ├─ Pre-screenshot (moondream: desktop idle)
          │ ├─ Execute: RobotJS click on desktop, Win+R, type outlook.exe, enter
          │ ├─ Monitor: Poll every 2s for window (max 10 polls)
          │ ├─ Post-screenshot (moondream: Outlook window detected)
          │ ├─ Duration: ~2-3 seconds
          │ └─ Confidence: 0.95
          │
          ├─ Step 2: Compose Email
          │ ├─ Execute: RobotJS click "New Email" button
          │ ├─ Monitor: Check email compose window opened
          │ ├─ Duration: ~1-2 seconds
          │ └─ Confidence: 0.92
          │
          ├─ Step 3: Type Recipient
          │ ├─ Execute: Click To field, type "john@company.com"
          │ ├─ Monitor: Screenshot shows text entered
          │ ├─ Duration: ~1 second
          │ └─ Confidence: 0.96
          │
          ├─ Step 4: Type Subject
          │ ├─ Execute: Click Subject field, type (from context)
          │ ├─ Duration: ~0.5 seconds
          │ └─ Confidence: 0.95
          │
          ├─ Step 5: Type Body
          │ ├─ Execute: Click body, type message
          │ ├─ Duration: ~1 second (assume QA already knows message)
          │ └─ Confidence: 0.94
          │
          └─ Step 6: Send
            ├─ Execute: RobotJS click "Send" button
            ├─ Post-screenshot (moondream: email sent confirmation)
            ├─ Duration: ~1 second
            └─ Confidence: 0.97

T=45s     [All steps completed successfully]

T=45-46s  [STEP 12: Narration (Piper TTS)]
          ├─ Piper generates: "Email sent to john at company dot com"
          ├─ Stream audio to frontend
          ├─ Frontend plays via Web Audio API
          ├─ Duration: 1-2 seconds
          └─ Voice UI state: Speaking (frequency waveform synced)

T=46-48s  [STEP 13: Persistence (CMA Agent)]
          ├─ Insert execution_log entry (all 6 steps)
          ├─ Insert step_templates stats (timing, success)
          ├─ Update workflows if matched template
          ├─ Commit SQLite transaction
          └─ Duration: <1 second

T=48s     [Complete - User gets success confirmation]

Total: ~48 seconds (realistic for simple email task)

Real-time updates sent to frontend at each step via WebSocket:
- T=2.5s: "Recognized: Send email to John"
- T=12s: "Planning: 4 steps ready"
- T=18s: "Parameters bound: Recipient = john@company.com"
- T=23s: "Resource check passed, starting execution"
- T=25s: "Step 1/6: Opened Outlook"
- T=26s: "Step 2/6: New email composed"
- T=27s: "Step 3/6: Recipient entered"
- T=28s: "Step 4/6: Subject entered"
- T=29s: "Step 5/6: Message typed"
- T=30s: "Step 6/6: Email sent"
- T=45s: "Narrating result..."
- T=48s: "Complete! Execution time: 48 seconds"

Performance Budget:
- Whisper: <3s (goal), fail >5s → Level 4 backtrack
- RAG: 8-12s (goal), fail >15s → Level 3 clarification
- SPA+SAA: <12s (goal), fail >15s → Level 3 clarification
- EA total: Varies, target 25-35s for simple tasks
- Piper: <2s (goal), fail >3s → Skip narration, show text
- CMA: <1s (goal), fire-and-forget if >2s

```

---

(Document continues with remaining sections...)

### Section Structure Continues:

- Section 9: 6-Level Backtracking System (specific routing rules + code examples)
- Section 10: Backend Architecture (FastAPI routes, schemas, async patterns)
- Section 11: Frontend Architecture (React hooks, WebSocket client, state management)
- Section 12: Setup & .EXE Bundling (NSIS config, model downloader parallel downloads)
- Section 13: All Use Cases & Scenarios (1000+ commands, device-specific, scheduling, team)
- Section 14: 10-Week Phased Breakdown (specific deliverables per week)
- Section 15: Testing Strategy (unit tests, E2E, performance benchmarks)
- Section 16: Performance Budgets & Profiling
- Section 17: Deployment & Release Checklist

---

**END OF SECTION 1-8 (Complete Implementation Specification - Scratch Build)**

*Remaining sections (9-17) follow in documentation system, totaling 3000+ lines of complete, greenfield implementation specification referencing JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md as source of truth.*

**Next Steps When Ready:**
1. Initialize FastAPI backend folder structure
2. Define Pydantic models (Agent inputs/outputs)
3. Implement base Agent class + registry pattern
4. Build agents in dependency order (1. RAG → 2. Clarification → ... → 13. Orchestrator)
5. Frontend: Electron setup + React component scaffold
6. Integration: WebSocket connection + E2E test scenarios

---

*Document Status: Ready for development hand-off*