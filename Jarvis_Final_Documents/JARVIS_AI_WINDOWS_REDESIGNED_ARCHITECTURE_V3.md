# JARVIS AI – WINDOWS REDESIGNED ARCHITECTURE V3
## Separated UI Modes | Chat Management | Explicit Workflows | Cascading System Changes

**Date:** February 24, 2026  
**Platform:** Windows 10/11  
**Status:** Architecture Refinement (responding to user feedback)

---

## DESIGN PRINCIPLES (UPDATED)

1. **Separate UI Concerns:** Voice mode and chat mode are **completely separate interfaces** – no mixing.
2. **LLM-style Chat UX:** Users can manage multiple chat sessions, see history, start new conversations.
3. **Workflows as First-Class Citizens:** Workflows are explicitly visible, saveable, loadable, and executable from the UI.
4. **Session Isolation:** Each chat session maintains its own execution context, history, and state.
5. **Cascading Architecture:** UI changes drive backend changes in database schema, API routes, and orchestrator logic.

---

# PART 1: REDESIGNED USER INTERFACE (3 MODES)

## UI Mode #1: VOICE MODE (Listening State)

When the user activates voice mode, the floating panel switches to **pure voice interaction** with no chat or text.

### Voice Mode Layout (480 × 400px, minimalist)

```
┌──────────────────────────────────────────────────────┐
│  ◀  JARVIS  ⚙️                                       │  <- Title bar (40px)
├──────────────────────────────────────────────────────┤
│                                                      │
│                                                      │
│          [Breathing bars animation]                 │
│                    ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▇ ▆ ▅ ▄ ▃ ▂ ▁   │  <- 120px tall
│          Status: LISTENING...                       │
│                                                      │
│          [Large microphone icon]                     │
│          (pulsing green if audio detected)          │
│                                                      │
│                                                      │
├──────────────────────────────────────────────────────┤
│  "Open Chrome and go to GitHub"                     │  <- Live transcript (60px)
│                                                      │
├──────────────────────────────────────────────────────┤
│       [🎤 STOP LISTENING] [⏸️ PAUSE]              │  <- 2 action buttons (40px)
│                                                      │
├──────────────────────────────────────────────────────┤
│  ⚙️ Switch to chat mode   [← Toggle mode]            │  <- Mode switch (30px)
└──────────────────────────────────────────────────────┘
```

**Key characteristics:**
- **No text input box** (user speaks, not types)
- **No chat history** visible
- **No execution panel** by default (can be toggled via settings)
- **Live transcript** shows real-time speech-to-text as user speaks
- **Color scheme:** Breathing bars in blue (#0078d4), microphone in green when active
- **Animations:**
  - Breathing bars cycle: 1.5s
  - Microphone: pulse when audio detected
  - Transition from idle → listening → recognized: 200ms fade

**Voice Mode States:**
| State | Visual | Audio | Action |
|-------|--------|-------|--------|
| Idle | Static logo, gray | None | Waiting for hotkey press |
| Listening | Breathing bars, blue | Subtle startup tone | User speaking; live transcript updating |
| Audio Detected | Microphone green + pulse | None | System capturing audio |
| Recognized | Checkmark (✓), green | Confirm beep | Speech recognized; processing plan |
| Thinking | Pulsing orb, blue | None | Agents working; LLM inference |
| Speaking (TTS) | Frequency waveform, purple | Piper voice output | System speaking response |
| Complete | Spinning checkmark + confetti | Success tone | Workflow finished; returning to Idle |
| Error | Red (!) pulse | Error beep | Failed; retry prompt |

---

## UI Mode #2: CHAT MODE (Text & Message History)

When the user switches to chat mode, the floating panel displays a full **conversational interface** with message history, like ChatGPT or Discord.

### Chat Mode Layout (480 × 640px, expandable)

```
┌──────────────────────────────────────────────────────┐
│  ◀  JARVIS  ☰ [Chat Menu]  ⚙️                       │  <- Title bar (40px)
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Jarvis: Hi! What would you like me to do?      │ │
│  │ 12:34 PM                                        │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │ You: Open Chrome and search for GitHub         │ │
│  │ 12:35 PM                                        │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────────┐ │  <- Chat area (scrollable, 300px)
│  │ Jarvis: I'll do that now. Planning...          │ │
│  │ [Step 1/4: Launch Chrome]                      │ │
│  │ [Step 2/4: Navigate to GitHub]                 │ │
│  │ [Step 3/4: Search for query]                   │ │
│  │ Executing now...                                │ │
│  │ ✓ Step 1 complete                              │ │
│  │ ⏳ Step 2 in progress...                         │ │
│  │ 12:36 PM                                        │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
├──────────────────────────────────────────────────────┤
│  [Type message...] [🎤 Voice] [📎 Attach]          │  <- Input bar (40px)
├──────────────────────────────────────────────────────┤
│  [💾 Save Chat] [🔄 New Chat] [📋 Workflows]       │  <- Control buttons (40px)
├──────────────────────────────────────────────────────┤
│ ⚙️ Chat settings  [← Switch to voice mode]          │  <- Mode switch (30px)
└──────────────────────────────────────────────────────┘
```

**Key characteristics:**
- **Full chat history** visible and scrollable
- **Text input box** for typing messages
- **Microphone toggle** (click to switch to voice within this mode)
- **Save/New Chat buttons** for session management
- **Workflows button** to access saved workflows panel
- **Timestamps** on each message
- **Color scheme:** User messages blue (#0078d4), assistant messages gray (#2d2d2d)

---

## UI Mode #3: WORKFLOWS PANEL (Modal or Sidebar)

When the user clicks the **📋 Workflows** button, a workflows management panel appears.

### Workflows Panel Layout (480 × 800px modal)

```
┌──────────────────────────────────────────────────────┐
│  ◀ Back  |  SAVED WORKFLOWS  |  ⚙️ Settings         │  <- Header (40px)
├──────────────────────────────────────────────────────┤
│                                                      │
│  📂 All Workflows (5)                               │  <- Category tabs
│  📂 Favorites (2)                                   │
│  📂 Recent (3)                                      │
│                                                      │
├──────────────────────────────────────────────────────┤
│  Search: [🔍 Type to filter...]                     │  <- Search bar (30px)
├──────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Open Chrome & GitHub Search                 │ │
│  │    Last run: 2 hours ago | ⭐ | 🗑️ | ▶️ Load   │ │  <- Workflow item (50px)
│  │    Steps: 4 | Confidence: 88% | Tags: web, dev │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 2. Check Email & Reply                          │ │
│  │    Last run: 1 day ago | ⭐ | 🗑️ | ▶️ Load     │ │
│  │    Steps: 6 | Confidence: 92% | Tags: email    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────────┐ │  <- Scrollable list (400px)
│  │ 3. Daily Report Generator                       │ │
│  │    Last run: 1 week ago | ⭐ | 🗑️ | ▶️ Load   │ │
│  │    Steps: 8 | Confidence: 85% | Tags: report   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 4. Open Slack & Send Message                    │ │
│  │    Last run: 3 days ago | ☆ | 🗑️ | ▶️ Load    │ │
│  │    Steps: 5 | Confidence: 91% | Tags: comms    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
├──────────────────────────────────────────────────────┤
│  [+ Create New] [Import] [Export All]              │  <- Action buttons (40px)
└──────────────────────────────────────────────────────┘
```

**Workflow Item Details (on hover/click):**
- **Name:** User-provided name (editable)
- **Last run:** Day + time
- **Star icon:** Toggle favorite / pin to top
- **Delete icon:** Remove workflow
- **Load button:** Select and load workflow into current chat session
- **Steps count:** Number of automation steps
- **Confidence:** Average success rate from historical runs
- **Tags:** User-defined labels for organization

**Workflow Item Click Actions:**
- **Load:** Load workflow into current chat and prepare for execution (show plan preview)
- **Delete:** Confirm and remove from database
- **Star:** Toggle favorite flag (affects sort order)
- **Rename:** Double-click name to edit inline

**Workflows created via:**
1. User speaks/types a command and workflow executes successfully
2. At the end, UI shows "Save this workflow?" → user clicks "Yes"
3. Modal appears: "Name this workflow" + optional tags/description
4. Saved to database; added to workflows list

---

# PART 2: CHAT SESSION MANAGEMENT

## Chat History (Sidebar or Dropdown)

Users can manage multiple independent chat sessions (like ChatGPT conversations).

### Chat Navigation Feature

In the title bar, add a hamburger menu (☰) that expands to show:

```
☰ Chat menu (expandable)
├─ ➕ New Chat (clears current session)
├─ 📌 Pinned Chats (if any)
├─────────────────────────────
├─ Today
│  ├─ Chrome & GitHub (just now)
│  ├─ Email Check (2h ago)
└─ Yesterday
   ├─ Check Slack (yesterday @ 3:15 PM)
   ├─ Daily Report (yesterday @ 10:30 AM)
```

**Clicking a chat:**
- Loads that chat session's history, messages, and state
- Switchback to Orchestrator with that session ID
- User can continue conversation or re-run workflows from that context

**New Chat button:**
- Clears current session
- Creates a new session record in database
- Resets orchestrator state
- Shows greeting message: "Hi! What would you like me to do?"

---

# PART 3: CASCADING BACKEND ARCHITECTURE CHANGES

## 3.1 Database Schema (Updated for Chat Sessions + Workflows)

### Current state (11 tables) → New state (14 tables + session isolation)

**New/Modified Tables:**

```sql
-- Chat sessions (container for conversations)
CREATE TABLE chat_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,               -- "Chrome & GitHub Search"
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_pinned BOOLEAN DEFAULT 0,
  is_archived BOOLEAN DEFAULT 0,
  mode TEXT DEFAULT 'chat',          -- 'chat' or 'voice'
  theme TEXT DEFAULT 'dark',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Chat messages (per-session)
CREATE TABLE chat_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT,                         -- 'user' | 'assistant' | 'system'
  content TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  message_type TEXT DEFAULT 'text',  -- 'text' | 'plan' | 'step_update' | 'error'
  metadata JSON,                     -- { "step_count": 4, "confidence": 0.88, ... }
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Workflows (saved automation sequences tied to sessions)
CREATE TABLE workflows (
  id TEXT PRIMARY KEY,
  session_id TEXT,                   -- nullable; workflows can exist independently
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,                -- "Open Chrome & GitHub Search"
  description TEXT,
  plan_json TEXT NOT NULL,           -- serialized plan steps
  tags TEXT,                         -- "web,dev,automation"
  is_favorite BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_executed_at DATETIME,
  execution_count INT DEFAULT 0,
  avg_confidence REAL DEFAULT 0.0,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Workflow executions (track runs for analytics)
CREATE TABLE workflow_executions (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  status TEXT,                       -- 'started' | 'completed' | 'failed' | 'cancelled'
  confidence REAL,
  error_message TEXT,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id),
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Execution logs (per-step details, tied to session)
CREATE TABLE execution_logs (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  workflow_execution_id TEXT,        -- reference to execution
  step_number INT,
  action TEXT,
  status TEXT,                       -- 'started' | 'completed' | 'failed'
  duration_ms INT,
  confidence REAL,
  screenshot_path TEXT,
  error_message TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
  FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id)
);

-- Request queue (for locked mode; tied to session)
CREATE TABLE request_queue (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  request_json TEXT NOT NULL,        -- { "input": "...", "mode": "active", ... }
  status TEXT DEFAULT 'pending',     -- 'pending' | 'approved' | 'rejected' | 'executed'
  created_at DATETIME,
  reviewed_at DATETIME,
  reviewed_by TEXT,                  -- user approval identity
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Users (for multi-user support)
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  passphrase_hash TEXT,              -- bcrypt hash
  lock_mode TEXT DEFAULT 'none',     -- 'none' | 'passphrase' | 'spoken_phrase' | 'pin'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME,
  is_active BOOLEAN DEFAULT 1
);

-- (Keep existing tables: config, device_registry, error_tracking, auth_log, model_cache, etc.)

```

### Key Changes:
- **Session isolation:** Every chat, message, and execution is tied to a `chat_sessions` record
- **Workflows now reference sessions:** But can also exist independently (for reuse)
- **Request queue per-session:** Locked mode requests queued per session
- **Execution logs tied to sessions:** Easier filtering, history, and redaction per session
- **Users table:** Support for multi-user if needed

---

## 3.2 API Endpoint Changes (FastAPI Routes)

### NEW Routes (Chat & Workflows):

```python
# Chat Session Management
POST   /api/chats                      # Create new chat session
GET    /api/chats                      # List all user's chats
GET    /api/chats/<session_id>         # Get chat details + full message history  
PUT    /api/chats/<session_id>         # Update chat title, pin status, etc.
DELETE /api/chats/<session_id>         # Archive/delete chat session
PUT    /api/chats/<session_id>/archive # Archive (soft delete)

# Chat Messages
GET    /api/chats/<session_id>/messages         # Get all messages in session
POST   /api/chats/<session_id>/messages         # Add message to session (internal)
DELETE /api/chats/<session_id>/messages/<msg_id> # Delete single message

# Workflow Management
GET    /api/workflows                  # List all saved workflows
GET    /api/workflows/<workflow_id>    # Get workflow details
POST   /api/workflows                  # Save workflow (from execution or manual)
PUT    /api/workflows/<workflow_id>    # Update workflow name/tags/description
DELETE /api/workflows/<workflow_id>    # Delete workflow
PATCH  /api/workflows/<workflow_id>/favorite  # Toggle favorite flag
GET    /api/workflows/<workflow_id>/executions # Get historical executions

# Workflow Execution (in context of a session)
POST   /api/workflows/<workflow_id>/execute    # Load & execute in current session
GET    /api/workflows/<workflow_id>/preview    # Get plan preview (show steps before executing)

# (Keep existing: /api/execute, /api/cancel, /api/mode/set, /api/settings, /ws)

```

### Modified Routes:

```python
# Execute (now session-aware)
POST /api/execute
  Body: {
    "input": "Open Chrome...",
    "mode": "active",
    "source": "voice" | "text",
    "session_id": "chat_12345",      # NEW: specify session context
    "auto_save_workflow": true       # NEW: auto-save successful workflows
  }
  Response: {
    "status": "ok",
    "session_id": "chat_12345",
    "execution_id": "exec_67890",
    "plan": [ ... ],
    "message": "Planning 4 steps..."
  }

# Cancel (now session-aware)
POST /api/cancel
  Body: {
    "session_id": "chat_12345"       # NEW: cancel in this session's context
  }

# WebSocket (now broadcasts session-specific events)
WS /ws                               # Connected clients listen for:
  {
    "type": "step_update",
    "session_id": "chat_12345",
    "step": 2,
    "status": "completed",
    "message": "Navigated to GitHub"
  }

```

---

## 3.3 Orchestrator Logic Changes

### Session Context Propagation

**Current:** Orchestrator has one global state (mode, current workflow, step counter).  
**New:** Orchestrator maintains a per-session state dictionary.

```python
class Orchestrator:
  def __init__(self):
    self.sessions = {}  # { session_id: SessionState(...) }
    self.current_session_id = None
  
  def execute(self, input_text, session_id, mode='active'):
    """
    1. Load or create session state
    2. Run agents in that session context
    3. Collect messages/steps tied to session_id
    4. Return execution context with session_id
    """
    if session_id not in self.sessions:
      self.sessions[session_id] = SessionState(
        session_id=session_id,
        mode=mode,
        messages=[],
        plan=None,
        current_step=0
      )
    
    session = self.sessions[session_id]
    
    # RAG, SPA, SAA, EA all operate on session context
    plan = self.rag_agent.generate_plan(input_text, session_context=session)
    session.plan = plan
    
    # Run steps, logging to execution_logs with session_id
    for step in plan:
      self.ea_agent.execute_step(step, session_id=session_id)
      # step logged to DB with session_id
    
    return ExecutionResult(session_id=session_id, plan=plan, ...)
  
  def cancel(self, session_id):
    """Cancel workflow in specific session"""
    if session_id in self.sessions:
      self.sessions[session_id].cancel_flag = True
    # Engine polls this flag between steps
  
  def get_session_history(self, session_id):
    """Retrieve all messages, executions, logs for a session"""
    session = self.sessions.get(session_id)
    if not session:
      return None
    return {
      "session_id": session_id,
      "messages": db.query(ChatMessage).filter_by(session_id=session_id),
      "executions": db.query(WorkflowExecution).filter_by(session_id=session_id),
      "logs": db.query(ExecutionLog).filter_by(session_id=session_id)
    }
```

---

## 3.4 UI-to-Backend Message Flow (Updated)

### Creating and Switching Chats:

```
User clicks "New Chat"
  ↓
React calls: POST /api/chats
  ↓
FastAPI: Generates new session_id, creates ChatSession record in DB
  ↓
FastAPI returns: { "session_id": "chat_abc123", "title": "New Chat", ... }
  ↓
React stores current_session_id = "chat_abc123"
  ↓
React clears message list, shows greeting
  ↓
UI ready for user input (voice or text)
```

### Executing in a Session:

```
User speaks: "Open Chrome and go to GitHub"
  ↓
React (voice mode) detects speech end, POSTs to:
  POST /api/execute {
    "input": "Open Chrome and go to GitHub",
    "session_id": "chat_abc123",
    "mode": "active",
    "source": "voice"
  }
  ↓
FastAPI Orchestrator.execute(input_text, session_id):
  - Loads session state for session_id
  - Runs RAG → SPA → SAA → EA agents
  - Each logs to execution_logs(session_id=...)
  - Broadcasts WebSocket events with session_id
  ↓
React receives WebSocket stream:
  { "type": "step_update", "session_id": "chat_abc123", "step": 1, ... }
  ↓
React appends message to chat (tied to session_id)
  ↓
At completion, optionally auto-save workflow tied to session_id
  ↓
Chat updated; workflow added to Workflows panel
```

---

## 3.5 Data Flow: Saving a Workflow

```
Workflow executes successfully in session "chat_xyz"
  ↓
Orchestrator flags: "execution_successful = True"
  ↓
React detects completion, shows: "Save this workflow?"
  ↓
User clicks "Save Workflow"
  ↓
React opens modal: "Name this workflow"
  User enters: "Check Email & Reply"
  User adds tags: "email,productivity"
  ↓
React POSTs: POST /api/workflows {
  "session_id": "chat_xyz",
  "name": "Check Email & Reply",
  "plan_json": <serialized plan>,
  "tags": "email,productivity",
  "description": ""
}
  ↓
FastAPI:
  - Creates Workflow record in DB
  - Sets workflow.last_executed_at = now()
  - Sets workflow.execution_count = 1
  ↓
React:
  - Closes modal
  - Shows: "✓ Workflow saved!"
  - Updates Workflows panel with new entry
  ↓
Next time, user can click Workflows panel → select "Check Email & Reply" → ▶️ Load
  - Loads from workflows table
  - Displays plan preview
  - User confirms → executes with pre-saved steps
```

---

# PART 4: CASCADING UI/BACKEND IMPACT ANALYSIS

## Summary Table: What Changes When We Separate Modes & Add Sessions/Workflows

| Component | Current State | New State | Impact |
|-----------|---------------|-----------|--------|
| **UI modes** | Mixed (chat + voice + execution) | Separated (voice only / chat only / workflows modal) | Simpler UX; cleaner state transitions |
| **Floating panel size** | 480×640 fixed | 480×400 (voice) \| 480×640 (chat) \| 480×800 modal (workflows) | Dynamic sizing; CSS media queries for responsive |
| **Microphone toggle** | In main panel | Voice mode: large visual; Chat mode: small icon | Better affordance in voice mode |
| **Chat history** | None (stateless) | Full per-session history visible | Need scroll optimization; lazy-load old messages |
| **Database** | 11 tables | 14 tables (added: users, chat_sessions, chat_messages, workflows, workflow_executions, request_queue) | +15% DB size; indexing critical on session_id |
| **Session management** | Single global state | Per-session state dict + in-memory cache | Orchestrator refactor (~20% code increase) |
| **Execution logs** | Global table | Partitioned by session_id (query faster) | Add index on (session_id, created_at) |
| **Workflows** | Always saved after run | Explicit save UI + database + API routes | +3 new REST endpoints |
| **Request queue (locked mode)** | Global queue | Per-session queue with isolation | Locked mode now multi-session compatible |
| **WebSocket messages** | { type, step, status } | Add session_id to all events | UI matches messages to session |
| **Settings + Auth** | Single user | Multi-user support baked in (via users table) | Passphrases now per-user; future ready |
| **Installer** | Install once; one login | Future: select user or create new on first launch | Minimal for now; extensible later |

---

# PART 5: VOICE MODE TO CHAT MODE TRANSITION

## How the UI Switches Between Modes

### Voice → Chat (User clicks "Switch to chat mode")

```
React state: { mode: 'voice' } → { mode: 'chat' }
  ↓
React component unmounts: VoiceModePanel
React component mounts: ChatModePanel
  ↓
ChatModePanel:
  - Loads current session's chat_messages from API
  - Renders chat history
  - Shows text input box
  ↓
Window resizes: 480×400 → 480×640 (animate transition over 300ms)
  ↓
Microphone state: if was listening, stop it gracefully
  ↓
User ready to type in chat mode
```

### Chat → Voice (User clicks "Switch to voice mode")

```
React state: { mode: 'chat' } → { mode: 'voice' }
  ↓
React component unmounts: ChatModePanel
React component mounts: VoiceModePanel
  ↓
Window resizes: 480×640 → 480×400 (animate transition over 300ms)
  ↓
VoiceModePanel:
  - Shows "Listening..." state
  - Activates microphone
  - Breathing bars animation starts
  ↓
User ready to speak
```

### Both modes preserve session context:
- Current chat session ID unchanged
- Execution history + logs remain accessible
- Can switch modes mid-conversation without losing state

---

# PART 6: WORKFLOWS PANEL INTEGRATION

## Loading and Executing a Workflow

```
User clicks: 📋 Workflows button (when in chat mode)
  ↓
Modal opens: Workflows panel
  ↓
User sees: List of saved workflows with last-run times, confidence scores, tags
  ↓
User filters: searches "Email" → finds "Check Email & Reply"
  ↓
User clicks: ▶️ Load (next to workflow)
  ↓
React calls: POST /api/workflows/<workflow_id>/preview
  ↓
FastAPI returns: {
  "workflow_id": "wf_123",
  "name": "Check Email & Reply",
  "steps": [
    { "n": 1, "action": "launch_app", "app": "Outlook" },
    { "n": 2, "action": "wait", "duration_ms": 3000 },
    ...
  ],
  "avg_confidence": 0.91
}
  ↓
React displays: Plan preview in modal (inline in workflows panel or new preview window)
  ↓
User clicks: "Execute" button
  ↓
React closes workflows modal; returns to chat mode
  ↓
React posts: POST /api/workflows/<workflow_id>/execute
  Body: { "session_id": "chat_xyz" }
  ↓
FastAPI:
  - Loads workflow plan from DB
  - Calls Orchestrator.execute(input_text=None, session_id=..., workflow_id=...)
  - Runs plan steps directly (skips RAG/SPA/SAA; goes straight to EA)
  - Logs execution to workflow_executions table
  ↓
React receives WebSocket stream: step updates as workflow runs
  ↓
Chat updated with step-by-step progress
  ↓
On completion: "✓ Workflow complete! [Run again] [Edit] [Save new version]"
```

---

# PART 7: IMPLEMENTATION ROADMAP (Phases)

## Phase 1: UI Refactor (Weeks 1–2)
- [ ] Separate voice mode component (VoiceModePanel)
- [ ] Separate chat mode component (ChatModePanel)
- [ ] Create WorkflowsPanel modal
- [ ] Implement mode switching logic (state management)
- [ ] Animate panel resizing

## Phase 2: Database & Schema (Week 3)
- [ ] Design & migrate to new 14-table schema
- [ ] Create chat_sessions, chat_messages, workflows tables
- [ ] Create users table (multi-user prep)
- [ ] Add indexes on [session_id, created_at]
- [ ] Write migration script

## Phase 3: Orchestrator Refactor (Weeks 4–5)
- [ ] Refactor Orchestrator for per-session state
- [ ] Update agents to use session context
- [ ] Modify execution logging to include session_id
- [ ] Update WebSocket message format (add session_id)

## Phase 4: API Expansion (Week 5)
- [ ] Add /api/chats/* endpoints
- [ ] Add /api/workflows/* endpoints
- [ ] Add /api/workflows/<id>/execute endpoint
- [ ] Update /api/execute to accept session_id

## Phase 5: Integration (Weeks 6–7)
- [ ] Connect UI to new API endpoints
- [ ] Test chat switching, workflow loading/saving
- [ ] Test multi-session scenarios
- [ ] TestWebSocket message delivery per session

## Phase 6: Testing & Polish (Week 8)
- [ ] End-to-end tests (voice → chat → workflows)
- [ ] Performance tests (large chat histories)
- [ ] Edge cases (rapid mode switching, concurrent chats)
- [ ] UX refinement based on feedback

---

# PART 8: QUESTIONS FOR USER VALIDATION

Before implementation, confirm:

1. **Chat history retention:** How long should chat sessions be kept? Auto-archive after 30 days?
2. **Workflow execution context:** When executing a saved workflow, should we display a simplified execution panel (steps only) or full detail logs?
3. **Multi-chat state:** If user is in "Chat 1" and switches to "Chat 2", should ongoing executions in "Chat 1" be paused/cancelled?
4. **Workflow versioning:** Should old versions of workflows be kept, or just the latest?
5. **Workflows from templates:** Should workflows be categorized (Built-in Templates, Community, Personal)?
6. **Export/Import:** Should users be able to export workflows as JSON or files for sharing?
7. **Workflow parameters:** Should workflows accept input parameters (e.g., "Search for: [USER INPUT]")?

---

**End of Redesigned Architecture V3**
