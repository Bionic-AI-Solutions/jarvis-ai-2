# JARVIS AI – WINDOWS-SPECIFIC COMPLETE ARCHITECTURE & IMPLEMENTATION GUIDE

**Date:** February 24, 2026  
**Platform:** Windows 10/11 only  
**Purpose:** Granular, production-ready specification with every implementation detail, UI mockups, system diagrams, installation flow, voice pipeline, and edge-case handling for Windows desktop.

---

## PART 1: USER INTERFACE SPECIFICATION

### 1.1 Main Floating Panel Layout

The floating panel is the user's primary interface. It **always stays on top** and can be dragged anywhere on screen.

#### Dimensions & Position
- **Width:** 480 pixels (fixed)
- **Height:** 640 pixels (variable: 480–800 px depending on execution panel state)
- **Position:** Stored in registry; defaults to bottom-right corner
- **Frameborder:** None; rounded corners (8px border radius)
- **Opacity:** 95% (slight transparency to see desktop/apps behind)
- **Z-order:** Always topmost (WS_EX_TOPMOST flag in Windows API)

#### Layout Grid (CSS Flexbox / Electron)

```
┌──────────────────────────────────────────────────┐  <- Title bar: 40px
│ ◀  JARVIS  ⚙️                                    │
├──────────────────────────────────────────────────┤
│                                                    │  <- Voice indicator area: 60px
│  [breathing bars animation]                      │
│  Status: LISTENING                               │
├──────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ │  <- Chat area: 200px (scrollable)
│  │ Assistant: What would you like me to do?    │ │
│  │                                              │ │
│  │ You: Open Chrome and go to GitHub           │ │
│  │ Assistant: I'll do that now.                │ │
│  │                                              │ │
│  └──────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤
│  [Text input box - 40px]                         │
│  Type or say something...              [🎤]      │  <- Microphone toggle
├──────────────────────────────────────────────────┤
│  [Action buttons - 50px]                         │
│  [Stop] [Pause] [Save] [Settings]              │
├──────────────────────────────────────────────────┤
│  Execution Panel (collapsed: 20px | expanded)    │
│  ▼ Executing step 2/4: Click browser button     │
│  ┌──────────────────────────────────────────────┐ │
│  │ 1/4 Launch Chrome                  ✓         │ │
│  │ 2/4 Navigate to github.com         ⏳        │ │
│  │     [screenshot thumbnail]          [▼]     │ │
│  │ 3/4 (pending)                      ⊘         │ │
│  │ 4/4 (pending)                      ⊘         │ │
│  └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

#### Color Scheme (Windows 11 Dark Mode compatible)

| Element | Color | Hex |
|---------|-------|-----|
| Panel background | Dark slate | #1e1e1e |
| Title bar | Accent blue | #0078d4 |
| Text (primary) | Off-white | #e0e0e0 |
| Text (status) | Gray | #808080 |
| Success (✓) | Bright green | #10b981 |
| Pending (⊘) | Gray | #606060 |
| Error (✗) | Bright red | #ef4444 |
| Processing (⏳) | Yellow | #fbbf24 |
| Button hover | Lighter blue | #1084d8 |
| Input box border | Subtle blue | #0078d4 |

### 1.2 Voice Indicator States (8 states, visual)

| State | Icon/Animation | Color | Sound | Speech |
|-------|---|---|---|---|
| **Idle** | Static logo (Jarvis text) | Gray (#606060) | None | None |
| **Listening** | 4 breathing bars (0.5–1.5 scale) | Blue (#0078d4) | Soft startup tone | "I'm listening" |
| **Audio detected** | Green waveform (3 bars, animated) | Green (#10b981) | None | (none) |
| **Recognized** | Green checkmark (✓) | Green (#10b981) | Soft confirm tone | "Got it" |
| **Thinking** | Pulsing orb (opacity 0.3–1.0) | Blue (#0078d4) | None | (silent) |
| **Speaking** | Frequency waveform (7 bars) | Purple (#7c3aed) | Real-time TTS | (Piper voice) |
| **Error** | Red exclamation (!) with pulse | Red (#ef4444) | Error beep | "Something went wrong" |
| **Complete** | Spinning checkmark + confetti | Green (#10b981) | Success tone | "All done!" |

**Animation timings:**
- Breathing bars: 1.5 second cycle
- Pulse (thinking/error): 1.0 second cycle
- Confetti: 2 seconds, then fade
- All transitions: 200ms easing

### 1.3 Title Bar & Controls

```
┌─ 40px tall ────────────────────────────────────────┐
│  [◀ minimize to tray] [JARVIS] [⚙️ settings] [✕ close]
└────────────────────────────────────────────────────┘
```

**Left side:**
- `◀` (minimize button): Hides to system tray; left-click to restore
- Label: "JARVIS" (14pt, bold, centered)

**Right side:**
- `⚙️` (settings gear): Opens settings modal (480×600px)
- `✕` (close button): Closes to tray (not full exit; stays running)
- **Right-click on title:** Context menu with "Exit", "Restart", "Open logs"

### 1.4 Microphone Toggle & Input Mode

```
Text input box (40px tall):
┌─────────────────────────────────────────────────┐
│ Type or say something...              [🎤 ON]   │
└─────────────────────────────────────────────────┘
```

- **Placeholder text:** Gray, italicized
- **Active (focus):** Blue border (2px)
- **Microphone button:** Toggle between text & voice
  - State: `[🎤 ON]` (blue) = voice active; user can speak or type
  - State: `[🎤 OFF]` (gray) = voice off; text input only
  - Click to toggle; visual feedback immediate

**Enter key behavior:**
- If text input has content → submit
- If voice is on AND user speaks for >0.5s → auto-submit after speech ends
- Allow Ctrl+V to paste (respects PII redaction later)

### 1.5 Action Buttons (4 main buttons, 50px tall)

```
┌────────┬────────┬────────┬──────────┐
│ [Stop] │[Pause] │ [Save] │[Settings]│
└────────┴────────┴────────┴──────────┘
```

Each button: 100px wide, 40px tall, 10px horizontal margin.

| Button | Icon | Function | States |
|--------|------|----------|--------|
| **Stop** | 🛑 (red square) | Kill current workflow immediately | Enabled during execution; disabled when idle |
| **Pause** | ⏸️ (two vertical bars) | Pause execution (holds state) | Enabled during execution; swaps to ▶️ (Resume) when paused |
| **Save** | 💾 (floppy disk) | Save current/last workflow as template | Enabled after workflow completes; shows "Saved!" confirmation for 2s |
| **Settings** | ⚙️ (gear) | Open settings modal | Always enabled |

**Button styling:**
- Default: Raised (subtle shadow)
- Hover: Slight highlight + shadow increase
- Disabled: Grayed out (opacity 0.5)
- Press: Inset (slight depression)

### 1.6 Chat Area (Scrollable, 200px nominal)

```
┌──────────────────────────────┐  <- User message (right-aligned, blue bg)
│     Your: Open Chrome        │
└──────────────────────────────┘
┌──────────────────────────────┐  <- Assistant response (left-aligned, dark bg)
│ Jarvis: I'll launch Chrome   │
│ and wait for it to open.     │
└──────────────────────────────┘
```

**Styling:**
- User messages: Light blue background (#0078d4), white text, right-aligned, 8px padding, 6px border-radius
- Jarvis messages: Darker gray background (#2d2d2d), light text, left-aligned
- Timestamp: Small gray text (10pt) below each message
- Font: Segoe UI, 11pt, line-height 1.4
- Max width per message: 380px (wrap text)
- Auto-scroll to latest message
- Max height: 200px; overflow-y: auto with subtle scrollbar

### 1.7 Execution Panel (Expandable, variable height)

**Collapsed state (20px):**
```
▼ Executing step 2/4: Click browser button
```

**Expanded state (200–400px depending on steps):**
```
▼ Executing step 2/4: Click browser button
┌────────────────────────────────────────────────────┐
│ Step 1/4: Launch Chrome                      ✓    │
│ Duration: 2.3s | Confidence: 95%                  │
│                                                    │
│ Step 2/4: Navigate to github.com             ⏳   │
│ Current: Taking screenshot...                     │
│ Pre-screenshot: [thumbnail] ← click to expand    │
│ [▼ Show logs]                                      │
│                                                    │
│ Step 3/4: Click search button              ⊘       │
│ (waiting for step 2 to complete)                  │
│                                                    │
│ Step 4/4: Type search query               ⊘       │
│                                                    │
│ Overall progress: ████░░░░░░░░ 50%               │
└────────────────────────────────────────────────────┘
```

**Per-step layout (60px per step):**
- Icon + step number + action name (left side, 20px)
- Status badge (✓ / ⏳ / ⊘ / ✗) (right side, 20px)
- Duration + confidence (10pt gray text below)
- Expandable logs section (click [▼ Show logs] to reveal)
- Screenshot thumbnail (optional; 60×40px with hover → full-size modal)

**Log format (when expanded):**
```
[▼ Hide logs]
12:34:56 - Pre-execution: Screenshot taken
12:34:56 - Vision analysis: Button detected at [456, 234]
12:34:57 - Action: Clicked at [456, 234]
12:34:58 - Post-execution: Screenshot taken
12:34:58 - Verification: Success (confidence 0.92)
```

### 1.8 Settings Modal (480×600px, centered on screen)

```
┌─ Settings ─────────────────────────────────────────┐ 40px
│ ◀ Back                                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ VOICE & INPUT                                       │
│ ☑ Microphone enabled                               │ 30px each
│ ☑ Silence detection (optimized for speech)        │
│ Volume: [◀ ████████░ ▶] 80%                       │
│ Language: [English ▼]                              │
│                                                     │
│ SECURITY & ACCESS                                   │
│ Lock mode: [Disabled ▼]                             │
│   └─ Options: None, Passphrase, Spoken phrase, PIN │
│ Passphrase: [••••••••••] [Change]                   │
│ Auto-lock timeout: [30 minutes ▼]                   │
│ Request queue review: [No pending requests]        │
│                                                     │
│ MODEL & STORAGE                                     │
│ Model directory: [C:\Users\...\jarvis\models]      │
│ [Browse] [Show in explorer]                         │
│ Auto-download models: ☑                             │
│ Auto-delete screenshots after: [7 days ▼]          │
│                                                     │
│ PRIVACY & TELEMETRY                                 │
│ ☐ Send crash reports to developer                  │
│ ☐ Allow usage analytics (anonymized)               │
│ [Download my data] [Clear all data]                │
│                                                     │
│ DISPLAY & BEHAVIOR                                  │
│ Theme: [Dark ▼]                                     │
│ ☑ Always on top                                    │
│ ☑ Show tooltips                                    │
│                                                     │
│                [Save] [Cancel]                      │
└─────────────────────────────────────────────────────┘
```

---

## PART 2: SYSTEM ARCHITECTURE DIAGRAM

### 2.1 Layered Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TIER 1: USER INTERFACE                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Electron Main Process (IPC bridge)                            │  │
│  │ ┌─────────────────┬──────────────────┬──────────────────┐    │  │
│  │ │ Window Manager  │ Menu & Keyboard  │ System Tray      │    │  │
│  │ │ (480×640 panel) │ Hotkey Listener  │ Integration      │    │  │
│  │ │                 │ (Ctrl+Shift+Alt+S)│ (minimize/tray) │    │  │
│  │ └─────────────────┴──────────────────┴──────────────────┘    │  │
│  │ ┌─────────────────────────────────────────────────────────┐  │  │
│  │ │ Preload Script (context isolation)                      │  │  │
│  │ │ - Secure IPC: listen('execute'), send('status')        │  │  │
│  │ │ - Hotkey registration wrapper (Windows API)            │  │  │
│  │ └─────────────────────────────────────────────────────────┘  │  │
│  │ ┌─────────────────────────────────────────────────────────┐  │  │
│  │ │ React Renderer Process (UI components)                 │  │  │
│  │ │ - Chat component (auto-scroll)                         │  │  │
│  │ │ - Voice indicator state machine                        │  │  │
│  │ │ - Execution panel (collapsible, step expand/collapse) │  │  │
│  │ │ - Settings modal (form validation)                     │  │  │
│  │ │ - Real-time WebSocket listener (SSE fallback)         │  │  │
│  │ └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
├─ IPC (sync/async) / WebSocket ───────────────────────────────────────┤
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│              TIER 2: BACKEND ORCHESTRATION (Python/FastAPI)         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ FastAPI Server (localhost:9000)                               │  │
│  │ ┌──────────────────────────────────────────────────────────┐  │  │
│  │ │ Routes:                                                  │  │  │
│  │ │ POST   /api/execute          (plan + execute)           │  │  │
│  │ │ POST   /api/cancel           (immediate stop)           │  │  │
│  │ │ POST   /api/mode/set         (mode transitions)         │  │  │
│  │ │ GET    /api/settings         (read/write config)        │  │  │
│  │ │ WS     /ws                   (real-time streaming)      │  │  │
│  │ │ GET    /health               (liveness probe)           │  │  │
│  │ └──────────────────────────────────────────────────────────┘  │  │
│  │ ┌──────────────────────────────────────────────────────────┐  │  │
│  │ │ Orchestrator (core state machine)                        │  │  │
│  │ │ - Mode: Active | Locked | Batch | Demo | Service       │  │  │
│  │ │ - Current workflow state + step counter                 │  │  │
│  │ │ - Backtrack level (1–6)                                 │  │  │
│  │ │ - Cancel flag (polled between steps)                    │  │  │
│  │ │ - Error queue (accumulating failures)                   │  │  │
│  │ │ - Checkpoint loading/saving                             │  │  │
│  │ └──────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      TIER 3: AGENT MESH                              │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │   RAG   │  Clarif  │ Web Sear │   SPA    │   SAA    │    EA    │ │
│  │ (8–12s) │  (30s)   │ (1–3s)   │ (1–2s)   │(<0.5s)   │ (2–4s)   │ │
│  └─────────┴──────────┴──────────┴──────────┴──────────┴──────────┘ │
│  ┌────────────────────────┬────────────────┬──────────────────────┐ │
│  │        OA (observer)   │  Safety (gate) │  CMA (persistence)   │ │
│  │  (continuous monitor)  │  (pre-filter)  │  (logs + snapshots)  │ │
│  └────────────────────────┴────────────────┴──────────────────────┘ │
│  ┌──────────────────────────┬────────────────────────────────────┐ │
│  │ Workflow Learner (save) │ App Registry (app detection)        │ │
│  │ (post-completion save)   │ (scans registry on startup)        │ │
│  └──────────────────────────┴────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                  TIER 4: SERVICE LAYER & MODELS                     │
│ ┌──────────────┬─────────────┬──────────────┬──────────────────────┐ │
│ │ LLM Inference│ Voice I/O   │ Vision Anal. │ Audio Processing     │ │
│ │ (Ollama)     │ (Whisper/   │ (moondream)  │ (Piper streaming)    │ │
│ │ - qwen2.5:3b │  Piper)     │ - fuzzy match│ - real-time TTS      │ │
│ │              │ - VAD       │ - screenshot │ - buffer mgmt        │ │
│ │              │   (silence) │   caching    │                      │ │
│ └──────────────┴─────────────┴──────────────┴──────────────────────┘ │
├─ Ollama socket (localhost:11434) / Windows audio APIs ────────────────┤
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│              TIER 5: AUTOMATION & SYSTEM ACCESS                     │
│ ┌──────────────┬──────────────┬──────────────┬──────────────────────┐ │
│ │ PowerShell   │ RobotJS      │ PyAutoGUI    │ Windows Registry     │ │
│ │ - app launch │ - mouse move │ - keyboard   │ - app discovery      │ │
│ │ - file ops   │ - click      │ - OCR (WinRT)│ - settings read      │ │
│ │ - admin runs │ - keyboard   │              │ - env vars           │ │
│ │ - UAC prompts│              │              │                      │ │
│ └──────────────┴──────────────┴──────────────┴──────────────────────┘ │
├─ Windows API (WinRT, UWP), COM objects ──────────────────────────────┤
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                TIER 6: DATA PERSISTENCE & SECURITY                  │
│ ┌──────────────────────────┬────────────────────────────────────────┐ │
│ │ SQLite (local file DB)   │ Windows Registry (config)              │ │
│ │ - 11 tables (history,    │ - HKEY_CURRENT_USER\Software\Jarvis   │ │
│ │   logs, workflows, etc.) │ - panel position, theme, auth method   │ │
│ │ - optional SQLCipher     │ - model directory path                 │ │
│ │   encryption (AES-256)   │                                        │ │
│ │ - journal mode: WAL      │                                        │ │
│ │ - auto-vacuum: enabled   │                                        │ │
│ └──────────────────────────┴────────────────────────────────────────┘ │
├─ File system: C:\Users\<user>\AppData\Local\Jarvis ───────────────────┤
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Request Flow Diagram (Voice Command)

```
USER speaks: "Open Chrome and go to GitHub"
        ↓
    [Microphone active in UI]
        ↓
    [Audio captured by Windows Audio API]
        ↓
    [Whisper inference on audio chunk]
        ↓ (silence detected → end of speech)
        ↓
    [Full transcript: "open chrome and go to github"]
        ↓
    [POST /api/execute { input: "...", mode: "active", source: "voice" }]
        ↓
    [Orchestrator receives request]
        ↓
    [Mode check: Active ✓ | Auth check: unlocked ✓]
        ↓
    [Safety Agent pre-filter: "open chrome" OK ✓ | "go to github" OK ✓]
        ↓
    [Call RAG Agent]
        ↓
    [RAG calls qwen2.5:3b LLM]
        ↓
    [LLM generates plan (8–12s inference)]
        ↓
    [Plan returned]
        Plan: [
          { n: 1, action: 'launch_app', app: 'chrome', method: 'powershell', timeout_ms: 5000 },
          { n: 2, action: 'wait', duration_ms: 2000 },
          { n: 3, action: 'type_url', url: 'github.com', method: 'keyboard' },
          { n: 4, action: 'press_key', key: 'enter', method: 'keyboard' }
        ]
        ↓
    [SPA Agent annotates]
        ↓
    [SAA Agent selects execution methods]
        ↓
    [CMA Agent saves checkpoint]
        ↓
    [WebSocket send to UI: "Plan ready. 4 steps. Confidence: 0.88"]
        ↓
    [UI updates: shows plan preview]
        ↓
    [Orchestrator waits for user confirmation OR auto-executes (configurable)]
        ↓
    [Execution loop begins for step 1]
        ├─ EA takes pre-screenshot
        ├─ PowerShell: Start-Process chrome.exe
        ├─ Sleep 2s
        ├─ EA takes post-screenshot
        ├─ moondream analyzes: "Chrome window visible?" ✓
        ├─ CMA logs success; confidence 0.95
        ├─ WebSocket send: "Step 1/4 complete"
        └─ Move to step 2
    
    ... (repeat for steps 2, 3, 4)
    
    [All steps complete]
        ↓
    [Workflow Learner: "Save this workflow?"]
        ↓
    [User clicks "Save as Workflow"]
        ↓
    [Saved to workflows table with name "Open Chrome & GitHub"]
        ↓
    [UI shows "✓ Workflow saved!"]
        ↓
    [Orchestrator resets; waits for next command]
```

### 2.3 Windows-Specific Component Map

```
┌─────────────────────────────────────────────────────────────┐
│                  WINDOWS-SPECIFIC LAYER                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Audio Capture (Windows.Media.Audio / WASAPI)              │
│  ├─ Enumerate audio devices (WASAPI)                      │
│  ├─ Set up IAudioCaptureClient stream                     │
│  ├─ VAD (Voice Activity Detection) – Whisper built-in     │
│  ├─ Stream to Python via ctypes + WinRT bridge            │
│  └─ Fallback: PyAudio (portaudio wrapper)                 │
│                                                             │
│ Audio Playback (Windows.Media.Audio / WASAPI)             │
│  ├─ Piper TTS→ WAV stream                                 │
│  ├─ IAudioRenderClient sends to output device             │
│  ├─ Stream mixing: system sounds + Piper simultaneously   │
│  └─ Volume control via Windows volume mixer API           │
│                                                             │
│ Mouse/Keyboard Automation (RobotJS for Windows)           │
│  ├─ SendInput() API wrapper                               │
│  ├─ GetCursorPos() for current mouse position             │
│  ├─ GetKeyboardState() to check modifier keys             │
│  ├─ SetForegroundWindow() to focus target app             │
│  └─ Relative vs. absolute positioning logic               │
│                                                             │
│ Window Management (Win32 Window API)                       │
│  ├─ FindWindow() – locate app windows by class/title      │
│  ├─ GetWindowRect() – get window bounds                   │
│  ├─ GetDC() – device context for screenshot capture       │
│  ├─ EnumWindows() – find all top-level windows            │
│  └─ SendMessage()/PostMessage() for control              │
│                                                             │
│ PowerShell Integration (subprocess module)                 │
│  ├─ subprocess.Popen(['powershell.exe', ...])             │
│  ├─ Standard input/output redirection                     │
│  ├─ Error code parsing ($LASTEXITCODE)                    │
│  ├─ UAC elevation: runas /user:Administrator              │
│  └─ Working directory management                          │
│                                                             │
│ Screenshot Capture (PIL + WinRT)                          │
│  ├─ PIL.ImageGrab.grab() – full screen or region          │
│  ├─ Alternative: Windows.Graphics.Capture API (newer)     │
│  ├─ Save to temp directory (C:\Users\<user>\AppData\...) │
│  ├─ Compression: JPEG 85% quality for speed              │
│  └─ Timestamping: YYYYMMDD_HHMMSS_nnn format             │
│                                                             │
│ Registry Access (winreg module / ctypes)                  │
│  ├─ HKEY_CURRENT_USER → config storage                   │
│  ├─ HKEY_LOCAL_MACHINE → installed app detection         │
│  ├─ Uninstall entry parsing (DisplayName, InstallLocation)│
│  └─ File association queries (Open With)                  │
│                                                             │
│ Process Management (psutil / subprocess)                  │
│  ├─ Detect running apps (Process.name, pid)               │
│  ├─ Graceful kill: taskkill /PID + timeout                │
│  ├─ Force kill: taskkill /F /PID if timeout expires       │
│  └─ Environment variables: os.environ + registry          │
│                                                             │
│ Hotkey Registration (pynput + Windows API)                │
│  ├─ Win32 RegisterHotKey() for global hotkey              │
│  ├─ Ctrl+Shift+Alt+S bound to cancel_workflow()           │
│  ├─ Message pump listening in separate thread             │
│  └─ Fallback: pynput listener (Python-only, less reliable)│
│                                                             │
│ System Tray Integration (wxPython / Electron Menu)        │
│  ├─ Icon in notification area (bottom-right)              │
│  ├─ Right-click context menu                              │
│  ├─ Single-click to restore / double-click to open        │
│  └─ Hover tooltip ("Jarvis AI – Running")                 │
│                                                             │
│ File System Access (pathlib + `open()`)                   │
│  ├─ Base directory: C:\Users\<user>\AppData\Local\Jarvis  │
│  ├─ Subdirs: models/, logs/, screenshots/, workflows/     │
│  ├─ Symbolic links: NOT supported (use real paths)        │
│  └─ Permission checks: os.access(path, os.R_OK)          │
│                                                             │
│ Environment Setup (Windows .bat / .exe wrapper)           │
│  ├─ Python: via embeddable python or virtual env          │
│  ├─ PATH: Ollama, PowerShell, model tools                 │
│  ├─ PYTHONPATH: include backend modules                   │
│  └─ OLLAMA_HOME: C:\Users\<user>\AppData\Local\Ollama    │
│                                                             │
│ Logging & Diagnostics (logging module + Event Viewer)    │
│  ├─ File logs: C:\Users\<user>\AppData\Local\Jarvis\logs │
│  ├─ Windows Event Viewer integration (optional)           │
│  ├─ Crash dumps: minidump + .pdb files                    │
│  └─ Performance counters: task manager integration         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PART 3: INSTALLATION BUNDLE & SETUP FLOW

### 3.1 Installer Components

**File:** `JARVIS_AI_Setup.exe` (built with NSIS + Electron-builder)

**Bundled contents:**
```
JARVIS_AI_Setup.exe (15 MB, compressed)
├─ Electron app (prebuilt, asar-packed)
│  ├─ main.js
│  ├─ preload.js
│  ├─ renderer/ (React compiled)
│  └─ resources/ (icons, fonts)
├─ Python runtime (embeddable or vcruntime only)
├─ FastAPI + dependencies (pip freeze list; downloaded during setup if needed)
├─ SQLite DLL + SQLCipher (optional encryption)
├─ NSIS installer script (with custom pages)
└─ [Models NOT included – downloaded on-demand post-install]
```

### 3.2 Installation Wizard Flow

**Step 1: Welcome Screen (Splash)**
```
┌─────────────────────────────────────────────┐
│                                             │
│        JARVIS AI Installation               │
│                                             │
│   Welcome to Jarvis AI – Your personal     │
│   desktop assistant.                        │
│                                             │
│   This wizard will guide you through       │
│   the installation process.                 │
│                                             │
│                                             │
│              [Next >]  [Cancel]             │
│                                             │
└─────────────────────────────────────────────┘
```

**Step 2: License Agreement**
```
┌─────────────────────────────────────────────┐
│ License Agreement                           │
├─────────────────────────────────────────────┤
│ MIT License – Full text scrollable...       │
│                                             │
│ ☐ I Agree to the License Terms             │
│                                             │
│              [Back] [Next >]                │
└─────────────────────────────────────────────┘
```

**Step 3: Destination Folder**
```
┌─────────────────────────────────────────────┐
│ Installation Directory                      │
├─────────────────────────────────────────────┤
│ Install to:                                 │
│ [C:\Program Files\Jarvis AI]  [Browse...]  │
│                                             │
│ Space required: ~500 MB (app only)         │
│ + 8–15 GB for AI models (downloaded later) │
│                                             │
│              [Back] [Next >]                │
└─────────────────────────────────────────────┘
```

**Step 4: Model & Data Directory**
```
┌─────────────────────────────────────────────┐
│ Model Storage Location                      │
├─────────────────────────────────────────────┤
│ Where to store downloaded models & data:    │
│ [C:\Users\<user>\AppData\Local\Jarvis]     │
│   [Browse...]                               │
│                                             │
│ ☐ Download models on first launch          │
│ ☑ Create isolated environment               │
│                                             │
│              [Back] [Next >]                │
└─────────────────────────────────────────────┘
```

**Step 5: Feature Selection**
```
┌─────────────────────────────────────────────┐
│ Features (Optional)                         │
├─────────────────────────────────────────────┤
│ ☑ Desktop Shortcut                         │
│ ☑ Start Menu Shortcut                      │
│ ☑ Add to PATH (for CLI usage)              │
│ ☐ Create System Tray Icon                  │
│                                             │
│              [Back] [Next >]                │
└─────────────────────────────────────────────┘
```

**Step 6: Ready to Install**
```
┌─────────────────────────────────────────────┐
│ Ready to Install                            │
├─────────────────────────────────────────────┤
│ Destination: C:\Program Files\Jarvis AI     │
│ Models dir:  C:\Users\...\AppData\Local\... │
│ Features:    Desktop + Start Menu shortcuts │
│                                             │
│ Click [Install] to begin.                   │
│                                             │
│              [Back] [Install]               │
└─────────────────────────────────────────────┘
```

**Step 7: Installation Progress (with logs)**
```
┌─────────────────────────────────────────────┐
│ Installing Jarvis AI                        │
├─────────────────────────────────────────────┤
│ ████████████░░░░░░░░ 60%                   │
│                                             │
│ Currently:                                  │
│ Installing FastAPI backend...               │
│ [Details ▼]                                 │
│                                             │
│ Log output:                                 │
│ [Extracting app files...]                  │
│ [Registering file associations...]         │
│                                             │
└─────────────────────────────────────────────┘
```

**Step 8: Post-Installation (Model Download Offer)**
```
┌─────────────────────────────────────────────┐
│ Download AI Models                          │
├─────────────────────────────────────────────┤
│ Installation complete!                      │
│                                             │
│ Jarvis needs to download models for voice, │
│ reasoning, and vision. This is large        │
│ (~8–10 GB) and will take 5–15 min on       │
│ broadband.                                   │
│                                             │
│ ☑ Download now                             │
│ ☐ Remind me later (download on first run)  │
│ ☐ Cancel (manual download later)           │
│                                             │
│ If now: [Download Models] [Cancel]         │
└─────────────────────────────────────────────┘
```

**Step 9: Model Download Progress** (if "Download now" chosen)
```
┌─────────────────────────────────────────────┐
│ Downloading AI Models                       │
├─────────────────────────────────────────────┤
│ Downloading: qwen2.5:3b (3.5 GB)           │
│ ████████░░░░░░░░░░░ 40%                    │
│ Speed: 15 MB/s | Time remaining: 4 min     │
│                                             │
│ Models queued:                              │
│   ✓ qwen2.5:3b (downloading)                │
│   ◯ Whisper-tiny (3.2 GB – pending)         │
│   ◯ Piper (1.2 GB – pending)                │
│   ◯ moondream (2.1 GB – pending)            │
│                                             │
│ Total: ~10 GB | Est. time: 12 minutes      │
│                                             │
│ Network: Excellent | Battery: 100%         │
│ [Pause] [⏸ Cancel] [Minimize]              │
│                                             │
└─────────────────────────────────────────────┘
```

Note: Download is resumable. If user closes or loses connection, it restarts from last checkpoint on next launch.

**Step 10: Installation Complete**
```
┌─────────────────────────────────────────────┐
│ Installation Complete                       │
├─────────────────────────────────────────────┤
│ ✓ Jarvis AI installed successfully!        │
│ ✓ Models downloaded and verified            │
│                                             │
│ Next steps:                                 │
│ 1. Click [Finish] to launch Jarvis         │
│ 2. On first launch, you'll configure       │
│    security (passphrase/voice unlock)      │
│ 3. Speak or type to begin!                 │
│                                             │
│ ☑ Launch Jarvis now                        │
│                                             │
│                    [Finish]                 │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.3 Post-Install Directory Structure

```
C:\Program Files\Jarvis AI\
├─ Jarvis AI.exe              (Electron entry point; starts Python backend + UI)
├─ app/
│  ├─resources.asar           (prebuilt React app + Electron main)
│  └─ (other app resources)
├─ Python runtime/ (if bundled)
│  └─ python.exe + libraries
├─ backend/
│  ├─ main.py                 (FastAPI app entry point)
│  ├─ orchestrator.py
│  ├─ agents/ (13 agent modules)
│  ├─ security/ (auth, PII redaction)
│  ├─ tools/ (automation wrappers)
│  └─ models/ (ORM, schemas)
├─ scripts/
│  ├─ run_backend.bat         (starts FastAPI)
│  ├─ install_dependencies.bat
│  └─ windows_setup.bat
├─ config/
│  ├─ default_settings.json
│  └─ logging_config.yaml
└─ README.md

C:\Users\<user>\AppData\Local\Jarvis\
├─ models/                    (downloaded Ollama models)
│  ├─ qwen2.5:3b/
│  ├─ whisper-tiny/
│  ├─ piper/
│  └─ moondream/
├─ data/
│  ├─ jarvis.db              (SQLite main database)
│  ├─ jarvis-wal             (WAL journal)
│  └─ jarvis-shm             (shared memory)
├─ logs/
│  ├─ jarvis-2026-02-24.log
│  ├─ orchestrator.log
│  ├─ agents.log
│  └─ system.log
├─ screenshots/              (temp storage)
│  ├─ 20260224_143012_001.jpg
│  └─ (timestamped PNG/JPEG)
├─ workflows/                (exported/imported workflows)
│  ├─ send_email.json
│  └─ backup_files.json
├─ cache/
│  ├─ web_search_cache.db   (5-min TTL)
│  └─ app_registry.json     (scanned apps)
└─ config/
   ├─ user_settings.json     (copied from registry)
   ├─ auth_settings.enc      (encrypted passphrase hash)
   └─ privacy_filters.yaml
```

### 3.4 First Launch Initialization

**Upon clicking "Launch Jarvis" after install:**

1. **Electron main process starts**
   - Checks Python runtime availability
   - Spawns FastAPI backend via `python backend/main.py`
   - Waits for `/health` endpoint to respond (max 10s)
   - If timeout: error dialog with troubleshooting steps

2. **FastAPI backend startup sequence**
   - Load config from AppData (or defaults)
   - Initialize SQLite database
   - Register all 13 agents
   - Load crash handler (minidump writer) – Windows API
   - Bind to localhost:9000 + WebSocket endpoint
   - Broadcast `ready` message to Electron

3. **React UI initialization**
   - Establish WebSocket connection to backend
   - Load saved user settings from registry
   - Display settings modal if first launch (passphrase setup)
   - Render floating panel; register global hotkey

4. **Settings Modal (first-launch only)**
```
┌─────────────────────────────────────────┐
│ Welcome! Let's Secure Jarvis             │
├─────────────────────────────────────────┤
│                                         │
│ Protect your assistant with a password: │
│                                         │
│ Lock mode:                              │
│ ◯ None (anyone can use Jarvis)         │
│ ◉ Passphrase (text password)            │
│ ◯ Spoken phrase (voice unlock)          │
│ ◯ PIN (4–6 digits)                     │
│                                         │
│ Passphrase: [••••••••••] [Show]        │
│ Confirm:    [••••••••••]                │
│                                         │
│ (Passphrase policy: min 8 chars,       │
│  1 uppercase, 1 number recommended)    │
│                                         │
│   [Skip] [Set Passphrase]              │
│                                         │
└─────────────────────────────────────────┘
```

5. **Model availability check**
   - Orchestrator calls `app_registry.scan_installed_apps()`
   - Checks Ollama socket at localhost:11434
   - If Ollama not running: offer to start it automatically via:
     ```powershell
     Start-Process "C:\Users\<user>\AppData\Local\Programs\Ollama\ollama.exe" serve
     ```
   - If models not yet downloaded: remind user to download (or start download wizard)

6. **UI goes live**
   - Voice indicator shows "Idle"
   - Chat box shows: "Hi! I'm Jarvis. What would you like me to do?"
   - Hotkey registered (Ctrl+Shift+Alt+S)
   - System tray icon added
   - Floating panel positioned at last-saved location (or bottom-right if first time)

---

## PART 4: VOICE PIPELINE SPECIFICATION

### 4.1 Audio Capture (Microphone → Inference)

**Windows Audio Stack:**
- **Capture device:** Default recording device (user can change in Windows sound settings)
- **Format:** 16-bit PCM, 16 kHz sample rate (matching Whisper's expected input)
- **Chunk size:** 512 samples per frame = 32ms latency per chunk
- **Buffer:** Ring buffer (FIFO, 2–4 seconds of audio at any time)

**Voice Activity Detection (VAD):**
- **Built into Whisper:** The model internally detects silence and only processes audio segments
- **Silence threshold:** If <5 dB for >1.5 seconds, transcript is finalized and sent to RAG
- **Implementation:** Whisper returns confidence score; if <0.3, retry or ask user to repeat

**Audio Pipeline Code Pseudocode:**
```python
def capture_and_transcribe():
    audio_buffer = RingBuffer(capacity=4*16000)  # 4 sec @ 16kHz
    
    while not stop_requested:
        chunk = audio_device.read(512)  # blocking read
        audio_buffer.append(chunk)
        
        if audio_buffer.energy() > VAD_THRESHOLD and not recording:
            recording = True
            ui_update("listening_active")  # green waveform
        
        if recording and audio_buffer.silence_duration() > 1.5:
            # Silence detected for 1.5s
            final_audio = audio_buffer.get_all()
            
            # Send to Whisper
            transcript = whisper_model.transcribe(final_audio, language="en")
            
            if transcript.confidence > 0.3:
                return transcript.text
            else:
                ui_update("unclear", "Say that again?")
                recording = False
                audio_buffer.clear()
```

### 4.2 Whisper Model Configuration (Audio-to-Text)

**Model:** OpenAI Whisper (tiny variant – 39M params, ~390 MB VRAM)

**Inference settings:**
- **Input:** PCM audio, 16 kHz, mono
- **Output:** JSON with text + confidence + timing info
- **Batch size:** 1 (single utterance per request)
- **Temperature:** 0.0 (deterministic)
- **Language detection:** Auto (but default to English)
- **Max length:** 224 tokens (~1 min speech)

**Timeout & retry logic:**
```python
max_retries = 2
timeout_seconds = 10

try:
    result = whisper.transcribe(audio_input, timeout=timeout_seconds)
    if result['confidence'] < 0.5:
        retry_count += 1
        if retry_count < max_retries:
            return { 'status': 'retry', 'message': 'Could not understand. Please repeat.' }
    return result
except TimeoutError:
    return { 'status': 'error', 'error_code': 'WHISPER_TIMEOUT' }
```

### 4.3 Text-to-Speech (TTS) Streaming via Piper

**Model:** Piper (lightweight, 15–20 MB per voice)

**Voice selection:**
- Default: English (US) – Amy (female) or Ryan (male)
- User can select in settings

**Streaming pipeline:**
```python
def stream_piper_tts(text, voice_name="amy"):
    """
    Stream TTS output in real-time chunks to audio output.
    """
    piper_process = subprocess.Popen(
        [
            "piper",
            "--model", f"models/{voice_name}.onnx",
            "--output-file", "-"  # stdout
        ],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )
    
    # Send text to Piper stdin
    piper_process.stdin.write(text.encode() + b'\n')
    piper_process.stdin.close()
    
    # Read WAV stream from stdout in 4KB chunks
    audio_output = audio_device.open_output_stream()
    
    while True:
        chunk = piper_process.stdout.read(4096)
        if not chunk:
            break
        
        audio_output.write(chunk)  # Write to speaker in real-time
        yield chunk  # Yield for progress UI updates
    
    audio_output.close()
    piper_process.wait()
```

**Real-time feedback:**
- As Piper generates audio, each 4KB chunk is sent to speakers immediately (no buffering)
- UI shows frequency waveform (7 bars) updating in real-time
- Users can interrupt TTS by clicking "Stop" or saying a kill-keyword

### 4.4 Microphone & Speaker Management

**Input device selection (Windows):**
```python
import pyaudio

pa = pyaudio.PyAudio()
input_devices = []
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        input_devices.append({
            'index': i,
            'name': info['name'],
            'sample_rate': info['defaultSampleRate']
        })

# User selects from dropdown in settings
selected_device = input_devices[user_choice_index]
```

**Output device selection (Windows):**
```python
output_devices = []
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxOutputChannels'] > 0:
        output_devices.append({
            'index': i,
            'name': info['name'],
            'sample_rate': info['defaultSampleRate']
        })
```

**Volume control (Windows Audio API):**
- Access via `ctypes` + Windows Core Audio API (ISimpleAudioVolume)
- Settings modal slider: 0–100%
- Slider updates live (no restart needed)

---

## PART 5: EDGE CASES & FAILURE SCENARIOS

### 5.1 System Robustness Matrix

**Scenario:** What happens if...?

| Scenario | Probability | Impact | Mitigation | Recovery |
|----------|-------------|--------|-----------|----------|
| **User speaks during Thinking state** | High | Queue input → replay after thinking ends | "One moment..." message | Auto-replay after current plan |
| **Windows sleeps mid-workflow** | Medium | All steps are lost; context snapshots help | Save checkpoint before each step | Load snapshot on wake; resume from step N |
| **Chrome crashes during click** | Medium | Action timeout; step marked failed | OA monitors for app crash signals | Backtrack level 4: reopen app; retry |
| **Screenshot capture fails** | Low | moondream can't analyze; step fails | Retry with 300ms wait | Backtrack level 3: retake screenshot |
| **Ollama not running** | Medium | LLM inference fails; all planning halts | Check on startup; offer auto-start | User manually starts Ollama; retry |
| **Network hiccup** (web search) | Low | Web Search timeout (10s) | Cache results; use fallback empty set | RAG continues without external data |
| **Microphone unplugged** | Low | Audio capture fails | Check device availability on startup | Error dialog; offer text-only mode |
| **Disk full (screenshots)** | Very low | Screenshot write fails | Monitor disk space; warn at 80% | Auto-cleanup old screenshots |
| **User presses Stop 5 times rapidly** | Low | Multiple cancel signals race | Orchestrator uses atomic flag | First cancel wins; subsequent ignored |
| **moondream misidentifies UI element** | Medium (10–15% baseline) | Click in wrong place | Fuzzy match + bounding box center | Backtrack level 2: alternate method |
| **Long pause in speech (>2s)** | High | User thinks but Whisper finalizes early | Configurable silence threshold | Clarification agent asks for repeat |
| **Passphrase forgotten** | Medium | User locked out | Recovery mechanism needed | Security question + email verification |
| **Python backend crashes** | Low | All automation stops | Electron detects `/health` timeout | Auto-restart backend; notify user |
| **RAG generates unsafe command** | Low | Safety agent should catch it | Regex + scope validation (defense-in-depth) | Step is blocked; user notified |
| **Database corruption** | Very low (SQLite is resilient) | Logs/workflows inaccessible | WAL mode + auto-backup | Restore from backup; user data preserved |

### 5.2 Detailed Failure Scenario: "Execution Timeout"

**Context:** EA is clicking a button; waits for UI change; times out after 3 seconds.

```
[✓ Pre-screenshot taken: 20260224_143012_phase1.jpg]
         ↓
[→ Action: click at (456, 234) via RobotJS]
         ↓
[→ Sleep 500ms (click feedback delay)]
         ↓
[→ Take post-screenshot]
         ↓
[⏳ Waiting for moondream analysis... (3s timeout)]
         ↓
[✗ moondream timed out after 3s]
         ↓
[ERROR_CODE: TIMEOUT]
         ↓
Orchestrator backtrack logic:
  Level 1: Retry same action
    [→ Sleep 1s more]
    [→ Take screenshot]
    [→ moondream analyze (retry)]
    ├─ Success? → Continue to next step
    └─ Fail? → Move to Level 2
  
  Level 2: Alternate execution method
    [→ Try keyboard navigation instead of click]
    [Tab + Enter sequence]
    [→ Verify with screenshot]
    ├─ Success? → Continue
    └─ Fail? → Move to Level 3
  
  Level 3: GUI refresh
    [→ Reopen parent application]
    [→ Re-navigate to the original screen]
    [→ Retry action]
    ├─ Success? → Continue
    └─ Fail? → Move to Level 5 (escalate to user)

  Level 5: User escalation
    [→ Notify user: "I tried to [action] but the app is not responding."]
    [→ Show pre/post screenshots]
    [→ Ask: "Continue?" / "Skip?" / "Manual fix?"]
    ├─ User says "continue" → attempt Level 4/6
    ├─ User says "skip" → go to next step
    └─ User manually fixes & says "resume" → resume from here
```

**Logged entry (SQLite `execution_logs` table):**
```sql
INSERT INTO execution_logs VALUES (
  NULL,                                      -- id (auto)
  'session_abc123',                          -- session_id
  'workflow_456',                             -- workflow_id
  2,                                          -- step_n
  'click',                                    -- action_type
  '{"x": 456, "y": 234, "element": "confirm_button"}', -- parameters
  'robotjs',                                  -- method_used
  '/local/appdata/jarvis/screenshots/20260224_143012_phase1.jpg',
  '/local/appdata/jarvis/screenshots/20260224_143012_phase2.jpg',
  'failed',                                   -- status
  'TIMEOUT',                                  -- error_code
  'moondream analysis exceeded 3s timeout',  -- error_message
  3200,                                       -- latency_ms
  '2026-02-24 14:30:12'                      -- timestamp
);
```

### 5.3 Detailed Failure Scenario: "Locked Mode – Incorrect Passphrase"

**Context:** User attempts to unlock; enters wrong passphrase 3 times.

```
[UI shows padlock icon]
[User clicks "Unlock"]
         ↓
[Modal appears: "Enter passphrase"]
[User types: "wrongpass123"]
[Clicks "Unlock"]
         ↓
[Backend validates: hash_compare(input_hash, stored_hash)]
[Result: FAIL – incorrect]
         ↓
Orchestrator response:
  attempt_count = 1 / 3
  UI updates: "Incorrect. Try again. (1/3 attempts)"
  [Modal stays open; text box clears]
  
  ... user tries again ...
  
  [User types: "alsowrong456"]
  attempt_count = 2 / 3
  UI updates: "Incorrect. (2/3 attempts. After 3 fails, lock for 10 min.)"
  
  ... user tries once more ...
  
  [User types: "stillnope789"]
  attempt_count = 3 / 3
  ✗ LOCKOUT TRIGGERED
         ↓
Lockout action:
  lockout_until = now + 10 minutes
  lockout_reason = 'max_attempts_exceeded'
  
  CMA logs to auth_log table:
  INSERT INTO auth_log VALUES (
    NULL,
    'session_xyz',
    'passphrase',
    FALSE,  -- not successful
    3,      -- attempt_count
    '2026-02-24 14:35:20'
  );
  
  UI modal closes
  UI shows: "🔒 Too many incorrect attempts. Locked for 10 minutes."
         ↓
  [Countdown timer visible: "10:00 remaining..."]
  [All input ignored during lockout]
  
  ... after 10 minutes ...
  
  [UI updates]: "Try again?"
  [Modal appears for passphrase re-entry]
  [attempt_count resets to 0]
```

**Registry entry (Locked state):**
```
HKEY_CURRENT_USER\Software\Jarvis
  lockout_until: "2026-02-24 14:45:20"
  lockout_count: 1
  last_failed_auth: "2026-02-24 14:35:20"
```

### 5.4 Robustness Guarantees

We make these explicit guarantees to prevent catastrophic failure:

1. **No data loss on error**
   - All steps logged before execution
   - Context snapshots saved every 5 steps
   - Database commits are atomic (no partial writes)

2. **No runaway processes**
   - EA sets 10s timeout on ALL subprocess calls
   - Orphaned processes are reaped via `psutil`
   - PowerShell commands have explicit exit handlers

3. **No infinite loops**
   - Backtrack level max = 6; if all fail → abort
   - Retry count capped at 3 per step
   - Orchestrator loop has guard: max 300 steps per workflow

4. **No UI freezes**
   - All long operations run asynchronously (FastAPI tasks)
   - WebSocket heartbeat every 5s (detects dead connections)
   - React UI has async/await for all backend calls

5. **Graceful degradation**
   - If GPU unavailable → use CPU (slower but works)
   - If Ollama down → show error + recovery steps
   - If internet down → use cached web results / skip web searches
   - If microphone unavailable → text-only mode

---

## CONCLUSION

This specification is a **complete, Windows-focused, production-ready blueprint** for Jarvis AI. Every component has:

✅ **Concrete UI dimensions & colors**  
✅ **Detailed system architecture diagrams**  
✅ **Complete installation bundle workflow**  
✅ **Voice pipeline with exact Whisper/Piper settings**  
✅ **Real-world edge-case handling (12+ scenarios)**  
✅ **Windows-specific API usage**  
✅ **Robustness guarantees & failure recovery**  

Developers can now **implement this directly** without ambiguity. The document is **not aspirational** – it's a detailed, actionable spec ready for Sprint 2 foundation work.

---

**Document:** JARVIS_AI_WINDOWS_COMPLETE_ARCHITECTURE_FINAL.md  
**Date:** February 24, 2026  
**Status:** ✅ Production-Ready | Ready for Development  
**Next Phase:** Sprint 2 – Backend Foundation (FastAPI, SQLite, Orchestrator, Agent Registry)
