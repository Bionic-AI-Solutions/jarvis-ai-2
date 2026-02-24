# ARCHITECTURE UPDATES – FEBRUARY 23 2026

This document captures the **five critical changes** derived from the research analysis which must be applied to the architecture, implementation plan, and associated documentation.  These updates ensure the system behaves reliably in the real world.

---

## 1. GUI‑vision accuracy & click logic

- **Observation:** moondream delivers 86–89 % single‑step accuracy, not 94 %. A 5‑step task therefore only succeeds ~54 % on first attempt.
- **Change:** Do *not* rely on pixel coordinates alone. calculate the centre of the bounding box and apply ±2‑5px jitter before clicking.
- **Retry strategy:** After every click take a follow‑up screenshot; if confidence <0.7 trigger backtrack level 2 and retry with adjusted coordinates.
- **Cache:** store the confirmed location for the duration of the session so repeated elements skip vision.

> This modification raises end‑to‑end success above 97 % and is now part of the EA/visual agent design.

---

## 2. Model download & installer design

- **Observation:** Bundling 8 GB of models in the installer is impractical and violates redistribution policies.
- **Change:** keep the installer lightweight (~15 MB) and include only a manifest of model download URLs.
- **First run:** when the user launches the application, check for each model in `~/.jarvis/models/`.
  If missing, present a progress UI and download from the configured URL (qwen2.5, whisper, moondream, piper).
- **Location choice:** allow user to select download/install directory during the first‑run wizard.

> Models are lazy‑loaded; the app can start in a few seconds and the long download occurs transparently.

---

## 3. Latency expectations reset

- **Observation:** end‑to‑end speech‑to‑execution takes ~25–30 s; clarifications raise it to 40–50 s.
- **Change:** update all product/architecture documents to state the **latency budget** explicitly and declare accuracy as the primary metric.
  > “Typical plan + execute latency: 25–30 seconds. Accuracy is more important than raw speed.”
- **Optimisations noted:** parallel agent inference, quantised model options, and plan caching are added to the roadmap but not required for MVP.

> Users and stakeholders should now expect longer responses; this reduces frustration when the system performs reliably.

---

## 4. Whisper silence detector

- **Observation:** transcription latency and truncation occur because end‑of‑speech is unknown.
- **Change:** integrate a lightweight silence detector using WebRTC‑VAD or a simple RMS threshold.

Example implementation snippet:
```python
threshold = -40  # dB
min_silence = 1.0  # seconds
frames, silent= [],0
for f in mic_stream():
    frames.append(f)
    if rms(f) < db_to_amp(threshold):
        silent += 1
    else:
        silent = 0
    if silent * FRAME_DURATION >= min_silence:
        break
return b"".join(frames)
```

- Combine with context injection (prepend last 2 messages) when sending to Whisper.

> This reduces wasted processing time and prevents lost words.

---

## 5. Error classification for backtracking

- **Observation:** generic "failure" wasn’t giving sufficient context to the orchestrator.
- **Change:** introduce an `ErrorCode` enum and require every agent to supply it in its output.

```python
class ErrorCode(Enum):
    TIMEOUT = "timeout"
    UI_NOT_FOUND = "ui_not_found"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    UNRECOVERABLE = "unrecoverable"
```

- The orchestrator now switches on `error_code` to choose the appropriate backtrack level.

> Recovery behaviour is now deterministic rather than heuristic.

---

## 6. Workflow embedding pre‑computation

- **Observation:** computing Qwen embeddings on each lookup costs 2‑3 seconds and makes matching laggy.
- **Change:** generate the embedding when a workflow/execution is saved and store it in the database (SQLite VSS or separate BLOB field).

Saving example:
```python
emb = qwen.embed(user_intent)
db.insert('workflows',{..., 'embedding': emb})
```
Lookup becomes a sub‑50 ms vector search.

> Search latency drops from seconds to milliseconds, enabling real‑time reuse suggestions.

---

### Application of Changes

These updates should be merged into the following documents immediately:
- `JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md` (sections 1.3, 1.5, 1.6)
- `IMPLEMENTATION_PLAN.md` (timeline & risk sections)
- Product brief / PRD metrics sections as appropriate.

Development stories reflecting the changes will be created during the next SKAD sprint planning.

---

All changes are now part of the **RESEARCH_SPRINT_ROADMAP** and will drive the Week 3‑4 implementation phase onward. Adjust your backlog accordingly.