# JARVIS AI – COMPLETE SYSTEM SPECIFICATION

**Date:** February 23, 2026  
**Purpose:** single, definitive reference describing every aspect of the Jarvis AI desktop assistant: what it is, how it looks, what it does, why we made each choice, and how all the pieces fit together. This document synthesizes every other file in `Jarvis_Final_Documents` and can be read by technical and non‑technical audiences alike.

---

## 1. OVERVIEW

Jarvis AI is a **voice‑driven desktop assistant** that understands natural language, executes tasks on your laptop on your behalf, and keeps you informed of its progress in real time. It behaves like a coworker with hands and eyes: you tell it to "open Chrome and send an email to John," and it will launch the browser, click the right buttons, type the text, and notify you when the job is done. All processing happens locally; user data never leaves the machine unless explicitly permitted.

### 1.1 Core Capabilities
- **Voice and text input**: speak or type commands; the system transcribes and interprets them.  
- **Task automation**: any action that a human can perform on the laptop (launch programs, manipulate files, navigate menus) can be automated.  
- **Real‑time feedback**: a visual panel shows each step as Jarvis performs it, and Piper TTS speaks status updates.  
- **Workflow learning**: Jarvis remembers what you’ve asked it to do and can reuse previous plans for faster execution.  
- **Persistent memory**: context and conversation history are stored in SQLite so sessions can resume after reboot.  
- **Privacy first**: no cloud dependencies for core features; models are downloaded locally and run on‑device.  

### 1.2 Example Use Case
You say: "Jarvis, organize my downloads folder and send the most recent invoice to accounting."  
Jarvis does the following behind the scenes: transcribes your voice, plans a sequence of steps (open file explorer, sort by date, attach file in email client), executes them one by one while streaming progress to the UI, and speaks "done" when complete. If Chrome crashed halfway, Jarvis automatically retries and asks you for guidance only if necessary. The entire plan and its outcome are saved so you can simply say "do the invoice task" next week and it will repeat in seconds.

### 1.3 Why This Architecture?
Traditional RPA tools are brittle and require manual scripting; Jarvis instead uses large language models to **generate plans dynamically from natural language** and a robust backtracking mechanism to recover from failures. The architecture balances flexibility (AI planning) with reliability (step‑by‑step verification) and maintains user control at all times. A comprehensive risk analysis shows the design is safe when the five critical changes from research are implemented (fuzzy vision, lazy models, silence detection, error codes, precomputed embeddings).

---

## 2. USER EXPERIENCE

### 2.1 Interface
- **Main window**: a floating panel containing a chat area, a voice indicator, and an execution panel.  
- **Voice indicator states**: Idle, Listening, Audio Detected, Recognized, Thinking, Speaking, Error, Complete.  
- **Execution panel**: shows a numbered list of steps (e.g. 1/4 launch Chrome); each step expands with logs and screenshots.  
- **Settings**: model directory, voice volume, privacy options, workflow library.  

### 2.2 Interaction Flow
1. Wake word or click microphone.  
2. Speak request or type into chat box.  
3. Whisper transcribes; RAG agent generates a plan.  
4. Execution agent carries out each step, verifying success via moondream vision.  
5. Real-time updates stream to the UI.  
6. Piper reads final summary; Jarvis asks follow‑up questions if clarification is needed.  
7. Optionally save the sequence as a reusable workflow.  

### 2.3 Installation & Setup
- Run single small installer (15 MB) that installs Electron frontend and Python backend.  
- On first launch, Jarvis checks for required models and offers to download them to a user‑chosen location.  
- User grants access to folders/apps; Jarvis warns about destructive actions and uses an explicit permissions dialog.  

### 2.4 Privacy & Controls
- All data (audio, screenshots, transcripts, workflows) reside in `~/.jarvis/` by default.  
- Users can exclude directories or use an opt‑out switch.  
- Sensitive data (passwords, cards) are automatically redacted before being processed by models.  

---

## 3. ARCHITECTURE

### 3.1 High‑Level Components
```
User Interface (Electron/React)
   ↕ WebSocket/SSE ↕
Backend Orchestrator (FastAPI, Python)
   ↕
Context DB (SQLite)
   ↕
AI Models (qwen2.5:3b, Whisper, Piper, moondream via Ollama)
   ↕
System Automation (PowerShell, RobotJS, PyAutoGUI)
```

### 3.2 Agent Mesh
Thirteen specialised agents communicate via message passing (see `JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md` for full personas):  
- **RAG**: turns user intent into a step plan.  
- **Clarification**: asks follow‑up questions when confidence is low.  
- **Web Search**: provides real‑time facts (not an LLM).  
- **SPA**: semantically annotates the plan.  
- **SAA**: chooses execution methods.  
- **EA**: executes each step with verification.  
- **OA**: observes external state for unexpected changes.  
- **Safety**: enforces hardcoded guardrails.  
- **User Agent**: manages voice i/o.  
- **CMA**: manages persistent context.  
- **App Registry**: scans installed apps.  
- **Workflow Learner**: records and reuses sequences.  
- **Orchestrator**: routes between agents and handles backtracking.

### 3.3 Backtracking
Six levels of automated recovery from step failures, from simple retry to requesting elevation or manual intervention.  Errors are classified using an `ErrorCode` enum so the orchestrator chooses the correct level.  

### 3.4 Data Flow Example
User says "Send email to John" → Whisper → RAG produces 4‑step plan → SPA/SAA annotate → EA takes screenshot→ moondream detects Outlook icon → EA clicks & types → OA monitors for popups → CMA logs each step → if EA times out with `UI_NOT_FOUND` error, orchestrator triggers backtrack level 2 and tries alternative click method.

### 3.5 Model Handling
- Models are downloaded lazily on first run.  
- qwen2.5 handles all reasoning, with dynamic filtering to parallelise web search.  
- Whisper with silence detection transcribes voice.  
- Piper streams TTS.  
- moondream analyzes screenshots; fuzzy matching mitigates its 86‑89 % baseline accuracy.

### 3.6 Database Schema
Eleven tables (conversation_history, execution_logs, workflows, failure_history, etc.) supporting context, learning, and backtracking.  See `IMPLEMENTATION_PLAN_SCRATCH.md` for schema details.  

### 3.7 Performance & Metrics
Research found median command latency ~25‑30 s and first‑try success ~50‑60 %. Metrics are tracked in‑system; thresholds exist for quality (see section 1.4 of PRD).  

---

## 4. USE CASES

### 4.1 Everyday Tasks
- Open/start applications.  
- Navigate menus and dialogs.  
- Copy/move/delete files.  
- Fill and submit web forms.  
- Send emails, schedule meetings.  
- Take screenshots and record notes.  

### 4.2 Developer Workflows
- "Create new React project"  
- "Run unit tests and report failures"  
- "Search codebase for TODOs"  

### 4.3 Administrative Work
- "Install update for Chrome"  
- "List installed printers"  
- "Set up firewall rule"  

### 4.4 Repetitive Automation
- Monthly invoice emails.  
- Daily standup reports.  
- Periodic system cleanup.

### 4.5 Advanced Scenarios
- Browser automation inside embedded WebView using a privileged renderer agent (Comet‑inspired pattern).  
- Scheduled workflows via cron.  
- Multi‑agent coordination (future research; Moltbook idea).  

---

## 5. INSTALLATION & DEPLOYMENT

### 5.1 Installer
- Electron‑builder + NSIS to produce `JARVIS_AI_Setup.exe`.  
- User selects install location and model directory.  
- Post‑install script initializes SQLite and optionally downloads Ollama models; can resume interrupted downloads.

### 5.2 System Requirements
- Windows 10/11, macOS Ventura, or Linux.  
- 8 GB RAM (models range 1–4 GB each).  
- GPU recommended for qwen2.5 inference; CPU only works but slower (35‑50 s vs 8‑12 s).  

### 5.3 Updates & Telemetry
- Auto‑updater built into Electron.  
- Telemetry optional, opt‑in only.  

---

## 6. SECURITY & PRIVACY

- Data stored locally and encrypted.  
- PII redaction before model inference.  
- Permission dialogs for file/folder access and destructive actions.  
- Error Code & backtracking ensure no unexpected commands.  
- Safety agent blocks known dangerous requests (format disk, kill system process).  

---

## 7. SPRINT PLAN & NEXT STEPS

Follow the roadmap in `RESEARCH_SPRINT_ROADMAP.md`: six multi‑week sprints from backend foundation through testing.  Key milestones:
1. Foundation agents and database.  
2. Planning agents wired.  
3. Execution & vision pipeline.  
4. Frontend voice UI & streaming.  
5. Intelligence layer (workflow learning).  
6. Installer & release preparation.

Metrics to monitor: latency, success rate, backtrack frequency, resource usage.  

---

## 8. RATIONALE SUMMARY

Every component exists for a reason:
- **Agents** modularise functionality and allow bidirectional reasoning.  
- **Backtracking** compensates for imperfect vision and flaky UIs.  
- **Lazy model downloads** reduce installation pain.  
- **Silence detection** tightens speech recognition.  
- **Error codes** make recovery deterministic.  
- **Workflow learning** turns repeated effort into seconds saved.  
- **Dual‑channel transports** keep chat fluid while actions occur.  

When a reader finishes this document they should know both *what* Jarvis will do and *why* each architectural decision was made.

---

This specification supersedes all earlier planning documents; it is the single source of truth for the project moving forward.  Any further changes must be logged and cross‑referenced here.



