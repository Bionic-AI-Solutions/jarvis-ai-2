# JARVIS AI – COMPLETE ARCHITECTURE V2 (FINAL)

**Date:** February 24, 2026  
**Purpose:** Comprehensive, production-ready architecture incorporating all agreed features, security controls, operational modes, and workflow management.  
**Supersedes:** JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md (original) – this document merges all subsequent improvements.

---

## 1. SYSTEM OVERVIEW

**Jarvis AI** is a **voice-driven desktop automation assistant** that runs entirely on-device, listens to natural language commands, plans multi-step workflows, executes them with real-time feedback, and learns from repeated actions. All processing is locally hosted; user data never leaves the machine unless explicitly exported.

### 1.1 Core Capabilities (Complete List)

- **Voice & text input** with Whisper transcription and silence detection
- **Natural language planning** using qwen2.5:3b reasoning
- **Desktop automation** via PowerShell, RobotJS, and PyAutoGUI
- **Visual understanding** through moondream screenshot analysis with fuzzy matching
- **Real-time streaming UI** showing step-by-step progress with dual-channel transport (chat + actions)
- **Workflow learning & reuse** – save sequences and replay with a single phrase
- **Persistent memory** – all sessions stored in SQLite with automatic recovery
- **Backtracking & error recovery** – six-level automated fallback logic
- **Security & access control** – optional passphrase/spoken-phrase unlock; request queue for unauthenticated access
- **Multi-mode operation** – Active, Locked, Batch, Demo, Service, and Error modes
- **Cancellation mechanisms** – global hotkey, voice kill-keywords, UI stop button
- **Local-only inference** – models downloaded lazily, no network dependency for core features
- **Privacy-first design** – PII redaction, sensitive-data vault, no telemetry without consent

### 1.2 Target Users

1. **Developer** – automate terminal workflows, generate projects, run tests
2. **Business User** – email/calendar/document management workflows
3. **IT Admin** – system configuration, installation, registry queries
4. **Power User** – complex multi-app orchestration and workflow scheduling

### 1.3 Key Metrics

| Metric | Target |
|--------|--------|
| Command latency (end-to-end) | 25–30 s (simple); 50–80 s (with clarification) |
| Voice transcription accuracy | ≥90% |
| First-try execution success | 70% (95% with backtracking) |
| Workflow reuse speedup | <15 seconds per saved task |
| WebSocket round-trip latency | <200 ms |
| Model startup time (lazy load) | 3–5 s per model |
| Memory footprint | 500 MB–1.2 GB (interpreter + active models) |

---

## 2. OPERATIONAL MODES

The system transitions between modes to regulate behaviour and security. Each mode alters how the orchestrator processes input and what agents are active.

### 2.1 Mode Definitions

| Mode | Activation | Behaviour |
|------|------------|-----------|
| **Active** | Default when unlocked | Full command acceptance, real-time execution, UI fully responsive |
| **Locked** | Password/phrase required | UI shows padlock, all input queued or rejected, no steps execute |
| **Batch** | Saved workflow triggered | Executes pre-recorded steps; Pause/Cancel/Retry available |
| **Demo** | Training/onboarding | Certain destructive actions disabled; extra UI hints; can replay recorded sessions |
| **Service** | Scheduled task or external API call | Minimal or no UI; runs headless; full logs stored |
| **Error/Panic** | Repeated failures or Safety block | Orchestrator halts; user notified; may enter Locked or Demo until reset |

### 2.2 Mode Transitions

```
Active ←--unlock--→ Locked
  ↓                   ↑
Batch (from saved)   (failed auth)
  ↓
Active (on complete)

Demo ←--enable--→ Active (toggle in settings)
  
Service (background) ←--schedule--→ (cron trigger)
  ↓
logs recorded

Active/Batch ←--repeated errors--→ Error/Panic
  ↓
halts & notifies user
```

### 2.3 Mode Implementation

The **orchestrator** maintains a `current_mode` field in its state machine. Before each workflow execution, it branches:

```javascript
if (orchestrator.mode === 'locked') {
  return { status: 'challenge_required', queued_request: input };
}
if (orchestrator.mode === 'demo') {
  safetyAgent.stricter_blocklist = true;
  ragAgent.simplify_plans = true;
}
if (orchestrator.mode === 'batch') {
  input = { source: 'stored_workflow', steps: [...] };
}
// ... proceed with planning
```

Users change mode via the UI settings panel or API endpoint `/api/mode/set`.

---

## 3. AGENT MESH – 13 SPECIALIZED AGENTS

The system decomposes the problem into 13 focused agents that communicate through the orchestrator. Each agent has a single well-defined role; together they provide planning, execution, observation, safety, and learning.

### 3.1 Planning & Reasoning Agents

#### 3.1.1 RAG Agent (Reasoning-and-Generation)
- **Role:** Convert user intent into a concrete, step-by-step plan
- **Input:** Natural language request (text or ASR output) + conversation context
- **Output:** Structured plan with ordered steps, each tagged with action type, parameters, and expected outcome
- **Tools:** qwen2.5:3b LLM; inference time ~8–12 seconds
- **Error handling:** Returns confidence score; if ≤0.6, escalates to Clarification agent
- **Integration:** Calls Web Search agent for real-time information if needed

#### 3.1.2 Clarification Agent
- **Role:** Ask disambiguation questions when RAG confidence is low
- **Trigger:** RAG returns confidence <0.6 or detects ambiguous parameters
- **Output:** Follow-up questions to the user; waits for response and re-invokes RAG
- **Timeout:** 30 seconds; if no user response, selects safest default or aborts
- **Example:** User says "send email to John" → multiple Johns in contacts → "Which John? (john@work.com / john@home.com)"

#### 3.1.3 Web Search Agent
- **Role:** Fetch real-time information (weather, stock prices, news, etc.)
- **Trigger:** RAG detects plan requires external data
- **Output:** JSON with results; cached for 5 minutes to avoid duplicate queries
- **Tools:** HTTP GET; optional fallback to local cache
- **Constraint:** Runs synchronously but asynchronously called by RAG to avoid blocking

#### 3.1.4 SPA Agent (Semantic-Plan-Annotator)
- **Role:** Enrich the plan with semantic metadata (step type, parameters, category)
- **Input:** Raw plan from RAG
- **Output:** Plan with additional fields: `step_type` (click, type, launch, wait, etc.), `parameter_bindings`, `estimated_duration_ms`, `rollback_hint`
- **Example:** `{ action: 'click', element: 'save_button', timeout_ms: 3000 }`

#### 3.1.5 SAA Agent (System-Action-Agent)
- **Role:** Choose the optimal execution method (PowerShell, RobotJS, PyAutoGUI, etc.) for each step
- **Input:** SPA-annotated plan
- **Output:** Plan with execution method field: `method: 'powershell' | 'robotjs' | 'pyautogui' | 'applescript' | 'rpc'`
- **Decision logic:** 
  - File operations → PowerShell
  - GUI clicks/typing → RobotJS (Windows/Mac) or PyAutoGUI (Linux)
  - Web automation → embedded Chromium RPC
  - Privileged operations → PowerShell with UAC prompt

---

### 3.2 Execution & Observation Agents

#### 3.2.1 EA Agent (Execution Agent)
- **Role:** Execute each planned step and report success/failure
- **12-step sub-pipeline per action:**
  1. Pre-execution screenshot
  2. Validate preconditions (app running, UI state)
  3. Execute action (click, type, launch, etc.)
  4. Wait for UI response (dynamic based on action type)
  5. Post-execution screenshot
  6. Analyze before/after via moondream
  7. Classify result (success, partial, timeout, error)
  8. Generate error code if failed
  9. Log step & outputs
  10. Check for emergent UI (dialogs, alerts)
  11. Verify expected outcome via vision
  12. Return status + confidence to orchestrator

- **Error codes returned:** `UI_NOT_FOUND`, `TIMEOUT`, `ACCESS_DENIED`, `PRECONDITION_FAILED`, `PARTIAL_SUCCESS`, `UNEXPECTED_DIALOG`, `NETWORK_ERROR`, etc.
- **Screenshot delays:** 300ms after GUI click, 1–2s after command, 500ms after form submit
- **Retry logic:** Delegated to orchestrator (not EA's responsibility)

#### 3.2.2 OA Agent (Observer Agent)
- **Role:** Monitor system state during execution; detect unexpected changes
- **Input:** Real-time screenshot stream, application events, OS notifications
- **Output:** Alert if unexpected dialog, system popup, or out-of-plan event occurs
- **Triggers:** 
  - New window/dialog appeared
  - Application crashed
  - System sleep/lock initiated
  - Antivirus/firewall prompt
  - Out-of-plan keystroke detected
- **Action on alert:** Pause orchestrator, notify user, wait for response
- **Trusted zones:** Cached known dynamic regions (stock tickers, live feeds) to avoid false positives

---

### 3.3 Safety & Control Agents

#### 3.3.1 Safety Agent
- **Role:** Block or warn on dangerous/suspicious requests
- **Checks performed:**
  1. Regex patterns: `rm -rf /`, `format c:`, `shutdown -s`, delete system files, etc.
  2. Scope validation: Cannot exceed granted permissions (file directory whitelist)
  3. Sensitive data: Block attempts to copy credentials or send them unencrypted
  4. Rate limiting: Flag if same high-risk action repeated 3+ times in 1 minute
  5. Injection detection: Block requests with SQL, shell escapes, or malformed syntax
  
- **Modes:** 
  - `strict` (Demo mode): Larger blocklist, more warnings
  - `normal` (Active mode): Balanced
  - `relaxed` (Service mode): Minimal checks
  
- **Output:** 
  - ✅ `allow` – proceed
  - ⚠️ `warn` – show user confirmation dialog
  - 🚫 `deny` – abort step

#### 3.3.2 Orchestrator (Conductor / Control Agent)
- **Role:** Central traffic control; route messages between agents; manage backtracking and error recovery
- **Responsibilities:**
  1. Pre-flight checks: mode validation, authentication, rate limiting
  2. Workflow sequencing: call agents in sequence (RAG → SPA → SAA → EA)
  3. Backtracking logic: on error, choose recovery level 1–6
  4. State persistence: save checkpoint after each step
  5. Cancellation handling: listen for hotkey/kill-keyword; abort cleanly
  6. Metrics collection: track latency, success rates, backtrack frequency
  
- **Backtracking levels:**
  - **Level 1 (Retry):** Same action, default method
  - **Level 2 (Alt method):** Switch execution method (click → keyboard nav, etc.)
  - **Level 3 (Re-screenshot):** Retake screenshot, re-analyze, retry
  - **Level 4 (GUI refresh):** Refresh UI or reopen app
  - **Level 5 (Escalation):** Ask user for confirmation/guidance
  - **Level 6 (Abort):** Gracefully halt workflow, roll back if possible

---

### 3.4 Data Management & Learning Agents

#### 3.4.1 CMA Agent (Context Management Agent)
- **Role:** Manage persistent state (conversation history, execution logs, user preferences)
- **Persists:**
  - Conversation history (user message + agent response)
  - Execution logs (steps, timestamps, screenshots, error codes)
  - Context snapshots (for undo/recovery)
  - User settings (unlock method, default actions, privacy filters)
  
- **API:**
  ```python
  cma.save_conversation(session_id, user_input, assistant_output)
  cma.load_history(session_id, limit=50)
  cma.save_snapshot(session_id, workflow_id, step_n, state_dict)
  cma.recover_from_snapshot(session_id, workflow_id, step_n)
  ```

#### 3.4.2 Workflow Learner Agent
- **Role:** Record executed workflows; enable reuse and optimization
- **Trigger:** After successful plan completion, offer "Save as Workflow"
- **Storage:** SQLite `workflows` table with schema:
  ```sql
  workflows(
    id, name, description, steps (JSON), 
    parameters (JSON), tags, created_at,
    last_used_at, execution_count,
    category, is_scheduled, cron_expression
  )
  ```
- **Reuse:** User says "run invoice workflow" → orchestrator loads steps → executes in Batch mode
- **Optimization:** Tracks execution time and success rate; suggests parameter refinements over time

#### 3.4.3 App Registry Agent
- **Role:** Maintain inventory of installed applications and how to launch them
- **Scans:** 
  - Windows Registry (HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Uninstall)
  - macOS Applications folder & Launch Services
  - Linux `.desktop` files and PATH binaries
  
- **Caches:** Updated on startup or manually refreshed
- **API:**
  ```python
  app_registry.get_app(name)  # Returns executable path, args, working directory
  app_registry.list_apps()    # All installed apps
  app_registry.search(keyword) # Fuzzy search
  ```

#### 3.4.4 User Agent (Voice/Text I/O)
- **Role:** Interface with the user; capture voice/text input; deliver audio/visual output
- **Voice pipeline:**
  - Listen for wake word or explicit hotkey
  - Stream audio to Whisper for transcription (silence detection enabled)
  - Display waveform in UI
  
- **Text pipeline:**
  - Monitor chat input box
  - Pass typed text directly to RAG
  
- **Output pipeline:**
  - Stream TTS via Piper (voice updates as workflow progresses)
  - Update UI in real-time via WebSocket
  
- **Kill keywords:** Listens for `stop`, `cancel`, `abort`, `kill process` – any of these triggers immediate cancellation

---

## 4. CANCELLATION MECHANISMS

Users can interrupt and stop an ongoing workflow via **three complementary channels**:

### 4.1 UI Cancel Button
- Located in the execution panel of the floating window
- Text: "Cancel" or "Stop"
- Action: Sends `{ type: 'cancel', timestamp }` over WebSocket to orchestrator

### 4.2 Global Hotkey
- Default: `Ctrl+Shift+Alt+S` (platform-specific alternatives on macOS/Linux)
- Registered at startup via a low-level keyboard hook (Windows API or native equivalent)
- Advantage: Works even if the UI window is out of focus or obscured
- Action: Invokes orchestrator's cancel handler directly

### 4.3 Spoken Kill-Keywords
- User Agent continuously listens for: `stop`, `cancel this`, `abort workflow`, `abort`, `halt`, `kill process`
- Works during voice input or execution phase
- Case-insensitive; interpreted by the User Agent within 1–2 seconds
- Action: Same as button/hotkey – routes to orchestrator cancel handler

### 4.4 Orchestrator Cancel Handler

```python
def on_cancel_request(self):
    # 1. Set cancellation flag
    self.cancel_requested = True
    
    # 2. Signal EA to abort in-flight action
    self.ea.abort_current_action()
    
    # 3. Attempt rollback if defined in workflow
    if self.current_workflow.rollback_steps:
        self.execute_rollback_sequence()
    
    # 4. Log cancellation
    self.cma.log_event(f"Workflow cancelled by user at step {self.current_step}")
    
    # 5. Notify user
    self.user_agent.speak(f"Workflow cancelled.")
    
    # 6. Clear orchestrator state & return to Active mode
    self.reset()
```

**Cancellation semantics:**
- If EA was waiting (e.g., for a window to open), it stops waiting and returns immediately.
- If EA was executing a command (PowerShell, click), the OS call is allowed to finish (no SIGKILL); EA will not retry.
- Partial effects are logged; user can manually undo if needed (e.g., half-typed email in draft folder).

---

## 5. ACCESS CONTROL & SECURITY LAYER

### 5.1 Authentication Modes

On first launch, the user selects one of:

| Mode | Mechanism | Unlock Method |
|------|-----------|---------------|
| **None** | No protection | Always active; anyone at keyboard can issue commands |
| **Passphrase** | Static text secret | Enter text or type passphrase in chat UI |
| **Spoken phrase** | Voice-biometric "challenge" | Say a pre-recorded spoken phrase (e.g. "Jarvis, are you there?") |
| **PIN + timeout** | Simple 4–6 digit code; locks after 30 min inactivity | Type digits into UI modal |
| **Multi-factor** | Combination of above | E.g. passphrase + spoken phrase |

### 5.2 Locked State Behaviour

When locked:

- **UI State:** Floating panel shows a padlock icon; all input boxes are grayed out; a "Unlock" button leads to a challenge dialog.
- **Voice:** User Agent rejects voice input; does not transcribe; may speak "please authenticate".
- **Chat:** Text input is queued (not executed) in a `pending_requests` table.
- **Visual:** Execution panel is blank; no secrets displayed; metrics hidden.
- **Timeouts:** If no correct unlock attempt within configurable window (e.g. 5 attempts = 10 sec lockout), lock persists until manual reset.

### 5.3 Request Queue

When in Locked mode, unauthenticated commands are stored in the `pending_requests` table:

```sql
pending_requests(
  id, session_id, request_text, 
  timestamp, source (voice/text),
  status (queued/approved/rejected/executed),
  executed_at
)
```

After unlock, the authorized user can:
- **Review** pending requests (see who tried to do what)
- **Approve** – execute the queued request
- **Reject** – discard it
- **Modify** – edit the request before executing

This prevents "shoulder surfing" attacks and gives the owner a chance to audit suspicious requests.

### 5.4 Sensitive Data Redaction

Before any model inference (vision analysis, planning, etc.), the system redacts:
- Email addresses & phone numbers (regex patterns)
- Credit card numbers (Luhn validation)
- Social Security Numbers / passcodes
- Password fields (via OCR detection)
- Medical/financial account numbers

Redacted text is replaced with `[REDACTED]` in logs and model inputs.

### 5.5 Database Security

- **Encryption at rest:** SQLite database is encrypted using SQLCipher (AES-256) if user enables it in settings.
- **Workflow integrity:** Saved workflow steps are versioned and checksummed to prevent tampering.
- **Audit trail:** All authentications (success/fail), mode changes, and sensitive operations are logged with timestamps.

---

## 6. WORKFLOW MANAGEMENT SYSTEM

### 6.1 Workflow Types

| Type | Trigger | Execution | Logging |
|------|---------|-----------|---------|
| **Ad-hoc** | Voice/text command | Synchronous; real-time UI | Full; user-facing |
| **Saved** | User invokes by name or keyword | Batch mode; same orchestrator | Full; stored in workflows table |
| **Scheduled** | Cron expression or time-of-day | Service mode; headless | Full; written to logs directory |
| **Triggered** | External API call or file watcher | Service mode; asynchronous | Full; accessible via API |

### 6.2 Workflow Schema

```sql
workflows(
  id PRIMARY KEY,
  name TEXT UNIQUE,
  description TEXT,
  steps JSON,  -- array of { action, params, method, error_code }
  parameters JSON,  -- input placeholders { name, type, default }
  category TEXT,  -- 'email', 'file', 'dev', 'admin', etc.
  tags TEXT,  -- CSV for search
  is_scheduled BOOLEAN,
  cron_expression TEXT,  -- if scheduled
  is_public BOOLEAN,  -- shareable; others can import
  version INT,  -- for migration/rollback
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  created_by TEXT,  -- user/session ID
  execution_count INT,
  last_executed_at TIMESTAMP,
  avg_duration_ms FLOAT,
  success_rate FLOAT
)
```

### 6.3 Workflow Execution Modes

#### 6.3.1 Active (Ad-hoc) Execution
```
User voice/text → RAG plans → SPA/SAA annotate/select → 
  EA executes each step → User sees real-time UI → 
    Workflow completes → User can save as template
```

#### 6.3.2 Batch (Saved Workflow) Execution
```
User says "run invoice workflow" → 
  Orchestrator loads workflow from DB → 
    Execution skips RAG/planning (steps are pre-recorded) → 
    EA iterates over stored steps → 
      User can Pause/Cancel/Retry mid-workflow → 
        Logs written; success rate updated
```

#### 6.3.3 Service (Scheduled) Execution
```
Scheduler/cron triggers at scheduled time → 
  Orchestrator switches to Service mode → 
    Workflow executes headless (no UI) → 
      All output logged to file → 
        Completion recorded in DB
```

### 6.4 Workflow Versioning & Rollback

- Each time a workflow is modified, a new version is created.
- Users can revert to a prior version via API or UI.
- Execution history tracks which version was run.

---

## 7. DATA FLOW & INTEGRATION POINTS

### 7.1 High-Level Data Flow (Example: "Send email to John")

```
1. User speaks "send email to John"
   ↓
2. User Agent captures audio → Whisper transcribes
   ↓
3. Orchestrator routes to RAG
   ↓
4. RAG: "Ambiguous (multiple Johns)" → confidence 0.45
   ↓
5. Clarification Agent: "Which John? (A) john@work.com (B) john@home.com"
   ↓
6. User responds: "A"
   ↓
7. RAG re-plans with full context:
   Plan: [
     { step: 1, action: 'launch_app', app: 'outlook', method: 'powershell' },
     { step: 2, action: 'wait', duration_ms: 2000 },
     { step: 3, action: 'click', element: 'new_email_button', method: 'robotjs' },
     { step: 4, action: 'type', text: 'john@work.com', method: 'robotjs' },
     { step: 5, action: 'type', text: 'subject', location: 'subject_field', method: 'robotjs' },
     { step: 6, action: 'type', text: 'body text...', location: 'body_field', method: 'robotjs' },
     { step: 7, action: 'click', element: 'send_button', method: 'robotjs' }
   ]
   ↓
8. SPA annotates each step with preconditions, timeouts, rollback hints
   ↓
9. SAA assigns execution methods (already done above)
   ↓
10. Orchestrator begins execution loop:
    For step 1: EA launches Outlook via PowerShell
    Pre-screenshot → execute → wait 2s → post-screenshot → 
    moondream verifies "Outlook is open" → confidence 0.92 ✓ → log & continue
    
    For step 3: EA clicks new email button
    Pre-screenshot → moondream finds button → click at center ± 2px → 
    wait 500ms → post-screenshot → moondream checks "new email dialog opened" 
    → confidence 0.85 ✓ → continue
    
    ... (steps 4–6: similar)
    
    For step 7: EA clicks send button
    ... same pipeline ...
   ↓
11. All steps succeeded → Workflow complete
   ↓
12. CMA logs full conversation + execution trace
   ↓
13. Workflow Learner: "Save this?" → User clicks "Save as 'Send to John's work email'"
   ↓
14. Saved to `workflows` table; next time user says "send to John" it uses this cached workflow
```

### 7.2 Component Integration Map

```
┌─────────────────────────────────────────────┐
│  User Interface (Electron/React)            │
│  - Floating panel, chat, execution view     │
│  - Voice indicator, kill button, hotkey reg │
└──────────────┬──────────────────────────────┘
               │ WebSocket / SSE
               ↓
┌──────────────────────────────────────────────┐
│  FastAPI Backend (Python)                    │
│  - /api/execute, /api/cancel, /api/mode/set │
│  - /ws (WebSocket for real-time streaming)  │
└──┬──────────────────────────────────────────┘
   │
   ├──→ Orchestrator (orchestration.py)
   │    ├─ Routes RAG, SPA, SAA, EA, OA
   │    ├─ Manages backtracking
   │    ├─ Cancellation handler
   │    └─ Mode state machine
   │
   ├──→ Agent Registry (agents/)
   │    ├─ rag_agent.py
   │    ├─ clarification_agent.py
   │    ├─ web_search_agent.py
   │    ├─ spa_agent.py
   │    ├─ saa_agent.py
   │    ├─ ea_agent.py
   │    ├─ oa_agent.py
   │    ├─ safety_agent.py
   │    ├─ cma_agent.py
   │    ├─ workflow_learner_agent.py
   │    ├─ app_registry_agent.py
   │    └─ user_agent.py
   │
   ├──→ Data Layer (models/)
   │    ├─ SQLite ORM (SQLAlchemy)
   │    ├─ conversation_history table
   │    ├─ execution_logs table
   │    ├─ workflows table
   │    ├─ pending_requests table (Locked mode)
   │    ├─ failure_history table
   │    └─ context_snapshots table
   │
   ├──→ LLM Models (via Ollama)
   │    ├─ qwen2.5:3b (planning & reasoning)
   │    ├─ Whisper (voice transcription with silence detection)
   │    ├─ Piper (TTS streaming)
   │    └─ moondream (screenshot analysis with fuzzy matching)
   │
   ├──→ Automation Layer (tools/)
   │    ├─ RobotJS (mouse/keyboard)
   │    ├─ PowerShell wrapper
   │    ├─ PyAutoGUI (cross-platform)
   │    ├─ AppKit/NSRunningApplication (macOS)
   │    └─ X11/Wayland (Linux)
   │
   ├──→ Security Layer (security/)
   │    ├─ passphrase_handler.py
   │    ├─ voice_biometric.py
   │    ├─ pii_redactor.py
   │    └─ request_queue_manager.py
   │
   └──→ Utilities (utils/)
        ├─ screenshot_capture.py
        ├─ error_classifier.py
        ├─ metrics_tracker.py
        └─ config_manager.py
```

---

## 8. DATABASE SCHEMA

### 8.1 Core Tables

```sql
-- Conversation history (context for RAG)
conversation_history(
  id, session_id, message_text, 
  speaker (user/assistant), 
  timestamp, voice_transcript_raw,
  confidence_score, tokens_used
);

-- Execution logs (audit trail + debugging)
execution_logs(
  id, session_id, workflow_id,
  step_n, action_type, parameters,
  method_used, pre_screenshot_path,
  post_screenshot_path, status,
  error_code, error_message,
  latency_ms, timestamp
);

-- Saved workflows (reusable sequences)
workflows(
  id, name, description, steps (JSON),
  parameters (JSON), category, tags,
  is_scheduled, cron_expression,
  is_public, version, created_at,
  updated_at, created_by, execution_count,
  last_executed_at, avg_duration_ms, success_rate
);

-- Pending requests (Locked mode queue)
pending_requests(
  id, session_id, request_text,
  timestamp, source (voice/text),
  status, executed_at
);

-- Failure history (backtracking & analytics)
failure_history(
  id, workflow_id, step_n,
  error_code, error_message,
  backtrack_level_used, resolution,
  timestamp
);

-- Context snapshots (for undo/recovery)
context_snapshots(
  id, session_id, workflow_id,
  step_n, orchestrator_state (JSON),
  created_at
);

-- Authentication log (security audit)
auth_log(
  id, session_id, auth_method,
  success, attempt_count,
  timestamp
);

-- Workflow revisions (versioning)
workflow_revisions(
  id, workflow_id, version,
  steps (JSON), created_at, created_by
);

-- Application inventory (registry)
application_registry(
  id, app_name, executable_path,
  arguments, working_directory,
  platform (windows/mac/linux),
  last_scanned
);

-- User settings (preferences)
user_settings(
  session_id, auth_mode,
  unlock_passphrase_hash,
  lock_timeout_minutes,
  hotkey_binding, kill_keywords,
  privacy_filters, telemetry_enabled,
  updated_at
);

-- Metrics (performance tracking)
metrics(
  id, metric_name, value,
  timestamp, session_id
);
```

---

## 9. SECURITY CONSIDERATIONS

### 9.1 Threats & Mitigations

| Threat | Mitigation |
|--------|-----------|
| Shoulder surfing / unauthorized use | Passphrase lock, request queue, request audit |
| Voice spoofing | Spoken-phrase biometric option; multiple challenges |
| Prompt injection in web pages | OA monitors for unexpected dialogs; blocks unknown scripts |
| Model hallucination → destructive command | Safety agent regex + scope validation; backtracking |
| Credential theft | PII redaction; no passwords logged; separate credential vault |
| Local privilege escalation | EA runs in user context; UAC prompts for system ops |
| Data exfiltration | Local-only inference; no cloud calls; user can audit logs |
| Malicious workflow import | Imported workflows are previewed; user must approve before save |

### 9.2 Privacy Safeguards

- **Data residency:** All files, logs, and models stay in `~/.jarvis/` (or user-chosen directory).
- **Redaction:** PII automatically stripped before model inputs.
- **Opt-in telemetry:** No data collection by default; user must explicitly enable.
- **Screenshot retention:** User can set auto-delete after N days (default: 7 days).
- **Audit trail:** Users can download full execution history as encrypted export.

---

## 10. PERFORMANCE & SCALABILITY

### 10.1 Latency Breakdown (Example: Simple Click)

```
Voice capture:                       0–5 s (depends on user's speech length)
Whisper inference:                   2–3 s (silence detection active)
RAG planning:                        8–12 s (qwen2.5:3b on CPU: 12–25 s; GPU: 8–12 s)
SPA annotation:                      1–2 s
SAA selection:                       <0.5 s
EA execution + screenshot:           2–4 s (click + wait + capture)
Backtracking (if needed):            +2–5 s per retry
Total (simple command, no retry):    ~15–25 s
Total (with clarification):          +30 s (user responds)
Total (with backtracking × 2):       +10 s
```

### 10.2 Memory Footprint

```
Electron UI:                         ~200 MB
Python backend:                      ~150 MB
Ollama runtime:                      ~100 MB
qwen2.5:3b model (VRAM):            3–4 GB (GPU) or 1 GB (quantized CPU)
Whisper.tiny (VRAM):                 200–400 MB
Piper TTS (VRAM):                    100–200 MB
SQLite + working data:               50–100 MB
Total (all models loaded):           1.2–2 GB (GPU) or 600–900 MB (CPU+quantized)
```

### 10.3 Concurrent Operations

- **Single user:** System is single-threaded orchestrator with async agents.
- **Multi-session:** Each session gets its own orchestrator instance; they share CMA for persistence.
- **Scalability:** Not designed for >1 concurrent workflow per user (queues additional requests).

---

## 11. DEPLOYMENT & RUNTIME

### 11.1 Installer

- **Format:** NSIS installer (`JARVIS_AI_Setup.exe` on Windows; `.dmg` on macOS; `.AppImage` on Linux)
- **Size:** ~15 MB (UI + skeleton backend; models downloaded on-demand)
- **Post-install:** User selects model download directory; installer begins lazy-downloading via resume-capable HTTP

### 11.2 Runtime Environment

```
Windows:    Windows 10/11, Python 3.9+, Ollama, SQLite, Electron 24+
macOS:      macOS Ventura+, Python 3.9+, Ollama, SQLite, Electron 24+
Linux:      Ubuntu 20.04+, Python 3.9+, Ollama, SQLite, Electron 24+
GPU:        NVIDIA (CUDA 11.2+) or AMD (ROCm); optional but recommended
RAM:        8 GB minimum; 16 GB recommended for GPU inference
Disk:       500 MB for app + 8–15 GB for models
```

### 11.3 Auto-Update

Built into Electron; checks for app updates weekly; downloads + installs in background; prompts user to restart.

---

## 12. EXTENSIBILITY & FUTURE

### 12.1 Agent Plugins

Future versions may allow custom agents via a plugin registry:

```yaml
plugin.yaml
name: "custom_api_agent"
entrypoint: "custom_api_agent.py::CustomAPIAgent"
dependencies:
  - "requests>=2.25"
  - "pydantic>=1.8"
```

### 12.2 Multi-Agent Collaboration

Moltbook-inspired: multiple agents can brainstorm or debate a solution before executing. Orchestrator can invoke this in Demo mode or as an opt-in feature.

### 12.3 Scheduled Triggers & Webhooks

Service mode can be triggered externally via:
- IFTTT / Zapier integrations
- File watcher (new file in folder → run workflow)
- Time-based cron
- HTTP webhook

---

## 13. TESTING & VALIDATION STRATEGY

### 13.1 Unit Tests

- Per-agent correctness: RAG output structure, SPA tagging, EA rollback logic
- Safety agent patterns: ensure dangerous commands are caught
- Orchestrator state transitions: mode changes, backtracking levels

### 13.2 Integration Tests

- End-to-end workflows: voice input → plan → execution → output
- Cancellation: hotkey/voice/button stops at each backtrack level
- Locked mode: passphrase unlock, request queue approval
- Batch workflows: saved sequence reuse

### 13.3 Performance Tests

- Latency benchmarks for each component
- Memory profiling during long sessions
- Screenshot + moondream analysis timing
- Model inference times (CPU vs GPU)

### 13.4 Security Tests

- PII redaction verification
- Passphrase/phrase validation
- Injection attack handling
- Permission scope validation

---

## 14. SUMMARY & KEY TAKEAWAYS

**Jarvis AI** is a production-ready architecture that combines:

✅ **Modular agent design** – 13 focused agents, each with single responsibility  
✅ **Robust recovery** – 6-level backtracking, comprehensive error codes, rollback support  
✅ **Security first** – passphrase lock, request queue, PII redaction, audit trails  
✅ **Multiple cancellation paths** – UI button, hotkey, voice kill-keywords  
✅ **Flexible modes** – Active, Locked, Batch, Demo, Service, Error  
✅ **Workflow learning** – save and reuse sequences; schedule for automation  
✅ **Privacy-preserving** – local inference, no cloud calls, user-controlled telemetry  
✅ **Real-time feedback** – streaming UI, dual-channel transport, step-by-step logs  

The architecture is **ready for implementation beginning in Sprint 2 (Foundation)**. All 13 agents have clear APIs and dependencies; the orchestrator is the central hub; data layer is fully specified; and security policies are baked in from day one.

---

**Document Version:** 2.0 (Final)  
**Status:** Production-ready specification  
**Next Phase:** Sprint 2 foundation implementation (FastAPI, SQLite ORM, orchestrator core, agent registry)
