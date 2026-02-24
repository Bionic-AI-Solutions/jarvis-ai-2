# Product Brief – JARVIS AI

**Project name:** Jarvis AI Desktop Assistant
**Date:** 2026-02-23
**Author:** [Your Name]

## 1. Overview & Vision

JARVIS AI is a voice-driven desktop automation agent that allows users to control
Windows applications and perform complex workflows through natural language.
Leveraging a network of specialized AI agents, real‑time streaming, and
persistent context, Jarvis aims to reduce repetitive tasks and make
power‑users more productive.

This greenfield project builds a production‑ready system from an empty Express+
Electron shell, culminating in a single `.exe` installer delivering a
FastAPI backend, Electron/React frontend, local AI models, and 13 autonomous
agents.

Key differentiators:

* **Multi‑agent architecture** – 13 distinct agents (RAG, Clarification,
  Execution, Observation, etc.) coordinate via a bidirectional mesh.
* **Real‑time feedback** – WebSocket streaming with eight message types keeps
  the user informed of every step.
* **Voice‑centric UX** – Whisper STT + Piper TTS, eight animated voice states,
  and audio‑visual synchronization create an immersive experience.
* **Self‑healing workflows** – a six‑level backtracking system automatically
  retries, clarifies or escalates when actions fail.
* **Workflow learning** – the system remembers previous executions and
  suggests reusing them, improving efficiency over time.
* **Local, shipped AI models** – qwen2.5:3b via Ollama, Whisper, moondream, and
  others run entirely on the user’s machine.


## 2. Users & Personas

1. **Developer Automation** – software engineers using Jarvis for coding,
   building, testing, and deployment tasks.
2. **Business Power‑User** – office professionals automating email, data
   entry, reporting, and scheduling workflows.
3. **IT Administrator** – system operators managing installations,
   diagnostics, and configurations.

Each persona expects reliability, low latency (<5 s end‑to‑end), and
transparent step‑by‑step feedback.


## 3. Scope of MVP

* Core functionality of all 13 agents with orchestration and persistence.
* Voice recognition and TTS with >90 % accuracy using Whisper and Piper.
* Real‑time execution panel in Electron showing step numbers and logs.
* Local workflow learning and app registry for intelligent planning.
* Windows‑only installation packaged as a single setup `.exe` with model
  downloader.
* Ten representative workflows implemented (e.g. opening applications,
  sending email, creating files).


## 4. Key Features & Requirements

### Functional Requirements

* **Voice commands** are transcribed and routed through RAG to generate an
  execution plan (JSON steps).  
* **Clarification** occurs automatically if RAG confidence <0.7.  
* **Semantic Parameter Annotation** resolves variables from context.  
* **Execution Agent** runs PowerShell/RobotJS interactions and verifies results
  using screenshots + moondream.  
* **Observer Agent** monitors OS state and alerts on unexpected popups or
  crashes.  
* **Web Search Agent** fetches real‑time information with 24‑hour caching.  
* **Backtracking** levels provide retries, alternative methods, or user prompts
  as failures occur.  
* **Workflow Learning** stores executed step sequences and matches future
  intents.  
* **App Registry** scans Windows registry for installed applications.  
* **Real‑time UI** with WebSocket updates, chat history, and animated voice
  states.  
* **Session persistence** allows restarting mid‑execution.  
* **Installer** sets up Python runtime, models, and shortcuts.

### Non‑Functional Requirements

* Average response time <5 s, WebSocket latency <200 ms.
* Offline-capable AI models; no cloud calls required for core operation.
* SQLite database with 11 tables for history, logs, and workflows.
* Robust error handling and logging; no crash should lose context.
* Able to run on Windows 10/11 with 8 GB RAM, 4‑core CPU.
* Installer must not require admin rights except for model download path.


## 5. Risks & Mitigations

* **Model latency** – use local inference and timeouts with backtracking.
* **OS state changes** – continuous observation and rollback strategies.
* **Transcript errors** – ask clarifying questions using Clarification Agent.
* **Installer size** – allow optional model download post‑installation.
* **Workflow drift** – store snapshots and use versioned migrations.


## 6. Success Metrics

* **User productivity:** 66 % time saved on repeated workflows.
* **Reliability:** >95 % of commands complete without manual intervention.
* **Performance:** median latency <4 s, 95 % under 7 s.
* **Adoption:** 10 representative workflows completed in the first beta week.
* **Stability:** no data loss when restarting during execution.


## 7. Next Steps

1. Initialize SKAD planning workflows (product brief, PRD, architecture) in the
   project using the SKAD CLI or by following the workflow markdown.
2. Carry out sprint planning to break this brief into epics and stories.
3. Begin development as per the 10‑week roadmap documented earlier.


---

*Product brief created via manual synthesis of existing Jarvis documents and
guided by the SKAD `product-brief` workflow structure (step‑01‑init).
* Document saved as `product-brief-JarvisAI-2026-02-23.md`.

Feel free to refine or extend this brief with additional input or SKAD
workflows once the CLI is working.*
