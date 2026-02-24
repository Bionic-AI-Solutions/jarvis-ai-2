# Product Brief – JARVIS AI (Enhanced)

**Project name:** Jarvis AI Desktop Assistant
**Date:** 2026-02-23
**Author:** [Your Name]

## 1. Overview & Vision

JARVIS AI is a **full‑featured desktop application** packaged as a single
`.exe` installer for Windows. It serves as a voice‑driven automation agent
that lets users perform complex sequences of tasks across applications with
natural language commands.

Built from the ground up, Jarvis combines a network of 13 specialized AI
agents, real‑time feedback, persistent context, and robust recovery. It is
meaningfully different from simple macros—Jarvis thinks, clarifies, and learns
from prior interactions.

### Key differentiators

* **Desktop‑first experience:** runs locally, offline capable, models shipped
  with the installer. No cloud required for core functionality.
* **Multi‑agent intelligence:** 13 agents including planning (RAG),
  clarification, execution, observation, safety, and workflow learning.
* **Real‑time orchestration:** WebSocket streaming provides step‑by‑step
  progress to the Electron UI, with <200 ms latency.
* **Voice UX with animation:** eight animated states (listening, thinking,
  speaking, error, etc.) synchronized with Whisper STT and Piper TTS.
* **Self‑healing workflows:** six‑level backtracking automatically retries or
  escalates when actions fail.
* **Workflow memory:** saves executed commands and suggests reuse, improving
  efficiency over time.
* **Installer packaging:** single 500 MB+ `.exe` built via NSIS includes
  Python runtime, models, and auto‑download capability for large models.


## 2. Users & Personas

1. **Developer Automation Persona**
   * Needs: automate build/test/deploy pipelines, open project files, run
     scripts, check system status.
   * Quote: “I just want to say ‘run the release pipeline’ and have
     everything happen.”

2. **Business Power‑User Persona**
   * Needs: manage email/calendar, generate reports, manipulate spreadsheets,
     batch‑process documents.
   * Quote: “Why open twenty windows when I can say ‘summarize last quarter’s
     sales’ and get the data?”

3. **IT Administrator Persona**
   * Needs: scan installed software, apply updates, troubleshoot issues, gather
     logs.
   * Quote: “A voice command to collect all crash logs would save hours.”

4. **Accessibility Persona** (new)
   * Needs: hands‑free control of desktop apps due to mobility or vision
     impairment.
   * Quote: “My mouse is difficult—speaking commands is liberating.”


## 3. Scope of MVP

Included in the first release:

* **13 AI agents** functioning end‑to‑end.
* **Voice command pipeline** using Whisper STT and text‑to‑voice with Piper.
* **FastAPI backend** coupled with Electron/React frontend delivered in one
  installer.
* **10 canonical workflows:**
  - Open a specific application and create a new document
  - Send an email with dictated content
  - Search the web and open a result
  - Create a React project scaffold in VS Code
  - Schedule a calendar event
  - Scan installed applications and list them
  - Take a screenshot and save to disk
  - Automate file renaming in Explorer
  - Deploy a script via PowerShell
  - Generate a performance report from Excel data
* **Workflow learning with suggestions** after repeated commands.
* **Real‑time execution panel** showing step numbers, progress bars, and logs.
* **Desktop `.exe` installer** with optional model download on first run.

Excluded (for later versions):

* Cloud integrations (e.g., Gmail API, Slack).  
* Mobile or web client.  
* Multi‑user collaboration.  
* Non‑Windows platforms.


## 4. Key Features & Requirements

### Functional Requirements

* **Natural voice input** transcribed to text, routed through RAG for planning.
* **Clarification agent** queries user if intent unclear (<0.7 confidence).
* **Semantic parameter annotation** resolves placeholders from context and
  recent interactions.
* **Action analyzer** chooses appropriate execution method (API vs
  keystrokes vs shell).
* **Execution agent** performs actions, verifies results using screenshots and
  moondream vision model.
* **Observation agent** monitors OS state for unexpected popups or crashes and
  alerts or pauses execution.
* **Safety agent** guards against dangerous commands (e.g. delete everything).
* **Workflow learner** saves and reuses past step sequences, recommending them
  to the user.
* **App registry** caches installed applications from the Windows registry.
* **Persistent context** stored in SQLite, including conversation history,
  execution logs, snapshots for recovery.
* **WebSocket UI** with eight message types feeds the Electron frontend.
* **Voice UI** with eight animated states using Canvas and CSS animations.
* **Installer** detects system, installs Python runtime, downloads models, and
  writes configuration and registry entries.

### Non‑Functional Requirements

* **Performance:** Median end‑to‑end response <5 s; WebSocket messages <200 ms.
* **Offline support:** All core capabilities operate without internet.
* **Security:** No sensitive data leaves the machine; context stored locally.
* **Reliability:** Capable of recovering from mid‑execution restarts.
* **Usability:** Voice UI must clearly indicate listening, thinking, speaking.
* **Portability:** Installer should run on Windows 10/11 (x64) with 8 GB RAM.
* **Size:** Installer <1 GB (models optional post‑install).


## 5. Enhanced Use Cases

1. **"Create new React project with Material‑UI"**
   * Jarvis opens VS Code, runs `npm create vite`, installs dependencies, and
     scaffolds a basic component.
2. **"Email John my daily report"**
   * Opens Outlook or web client, composes email, attaches latest report, and
     sends after confirmation.
3. **"Scan my system for outdated software"**
   * App registry returns list of installed packages, filters by version, and
     offers to open download pages.
4. **"Set up a meeting next Monday at 2"**
   * Creates calendar event, invites attendees, and sends a reminder email.
5. **"Summarize this PDF"**
   * Converts PDF to text, uses RAG to generate summary, reads it aloud.
6. **Accessibility scenario:**
   * "Read my latest email" → transcribes email and speaks via Piper.
7. **Developer workflow:**
   * "Deploy the staging build" → opens terminal, runs deployment script,
     watches for success, logs output.

Each use case demonstrates Jarvis understanding, planning, execution, and
feedback. The system learns these flows and suggests them when similar
commands are given.


## 6. Risks & Mitigations (Enhanced)

* **Installer bloat:** models are large; provide opt‑out and download manager.
* **AI model drift:** regularly test LLM outputs and include fallback prompts.
* **Permission issues:** require elevation only when absolutely necessary;
  warn user before PowerShell commands.
* **UI latency:** optimize WebSocket and front‑end rendering; provide 
  progressive feedback ("Thinking…").
* **Data privacy:** encrypt context database optionally; allow purge.


## 7. Success Metrics

* **User productivity:** time‑to‑complete workflows drops by 60% after
  learning.
* **Reliability:** >95% of workflows complete without listing an error.
* **Performance:** 90% of commands handled within 7 s; WebSocket <200 ms.
* **Adoption:** at least 10 daily active workflows per user in beta.
* **Installer adoption:** >1,000 installs first month with <2% uninstall rate.


## 8. Next Steps (reinforced)

1. Run SKAD workflows to capture this brief in machine‑readable form.
2. Proceed with `/create-prd` to convert these requirements into a formal PRD.
3. Follow the 10‑week roadmap described in the integration documents.


---

*This brief extended the previous version with explicit desktop‑exe scope,
enhanced user personas (added accessibility), and richer use‑case examples
inspired by the three Jarvis documents. It remains consistent with the step
structure of the SKAD `product-brief` workflow (init step only; further steps
would cover vision, users, metrics, etc.).*

Feel free to continue the SKAD-guided process by manually working through
subsequent steps or using the CLI `--action` flag with the appropriate
workflow names.