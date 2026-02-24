# JARVIS AI — COMPREHENSIVE EPICS & USER STORIES BACKLOG

**Version:** 1.0  
**Date:** February 24, 2026  
**Source:** JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md (PART 24 + Party-Mode Synthesis)  
**Status:** Ready for Sprint Planning  

---

## TABLE OF CONTENTS

1. [Backlog Overview](#backlog-overview)
2. [Epic Summaries](#epic-summaries)
3. [Epic 1: Voice Input & Recognition](#epic-1-voice-input--recognition)
4. [Epic 2: Workflow Execution & Feedback](#epic-2-workflow-execution--feedback)
5. [Epic 3: Error Handling & Recovery](#epic-3-error-handling--recovery)
6. [Epic 4: Workflow Management](#epic-4-workflow-management)
7. [Epic 5: Security & Locking](#epic-5-security--locking)
8. [Epic 6: Learning & Intelligence](#epic-6-learning--intelligence)
9. [Epic 7: Infrastructure & Integration](#epic-7-infrastructure--integration)
10. [Backlog CSV](#backlog-csv-format)
11. [Sprint Planning Guide](#sprint-planning-guide)
12. [Dependency Graph](#dependency-graph)

---

## BACKLOG OVERVIEW

### Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Epics** | 7 |
| **Total Stories** | 68 |
| **Total Story Points** | 320 |
| **MUST-Have Stories** | 24 stories, 148 pts (46% of total) |
| **SHOULD-Have Stories** | 24 stories, 104 pts (33% of total) |
| **COULD-Have Stories** | 20 stories, 68 pts (21% of total) |
| **MVP Scope** | 24 MUST stories, 148 pts |
| **Est. MVP Timeline** | 4 sprints (4 weeks) at 20 pts/sprint |
| **Full Phase 1 Timeline** | 16 sprints (16 weeks) including SHOULD + COULD |

### Priority Distribution

```
MUST (46%)  ████████████████████ 148 pts
SHOULD (33%) ███████████ 104 pts
COULD (21%)  ███████ 68 pts
```

### Velocity Assumptions

- **Team Size:** 4 developers (Amelia, Barry, +2)
- **Sprint Duration:** 1 week (5 working days)
- **Ceremonies Overhead:** ~5 hrs/week
- **Net Dev Capacity:** ~35 hrs/week per developer
- **Expected Velocity:** 20 pts/sprint (4-person team)

### Critical Success Factors

✅ **MUST Complete Before Phase 1:**
- All 24 MUST-have stories
- All story AC passing 100%
- Zero critical bugs
- All 6 backtracking levels tested

✅ **GATE:** Cannot start Phase 1 without resolving PART 28 blockers:
- API contract defined
- Agent protocol finalized
- Error codes cataloged
- Story points + dependencies complete
- MVP definition clear
- Test infrastructure ready
- Moondream PoC validated
- Voice pipeline PoC validated

---

## EPIC SUMMARIES

### Epic 1: Voice Input & Recognition (8 Stories, 33 pts)

**Objective:** Enable hands-free voice command activation with high accuracy transcription.

**User Value:** "I can control JARVIS by speaking naturally without touching the keyboard."

**Business Value:** Voice-first UX differentiates from competitors; accessibility feature.

**Owner:** Amelia (Dev Lead)

**Key Stories:**
- 1.1: Voice hotkey activation (MUST, 5 pts)
- 1.2: Whisper STT transcription (MUST, 8 pts)
- 1.3: Voice pause & resume (SHOULD, 3 pts)
- 1.4: Silence detection (SHOULD, 5 pts)

**Critical Dependency:** Hotkey (1.1) must work before transcription (1.2) can be tested.

**Acceptance Gate:** 85%+ transcription accuracy across 5 different accents.

---

### Epic 2: Workflow Execution & Feedback (12 Stories, 56 pts)

**Objective:** Execute workflows with real-time user visibility and step-by-step progress tracking.

**User Value:** "I can see exactly what JARVIS is doing while executing my workflow."

**Business Value:** Transparency builds trust; users can verify results in real-time.

**Owner:** Barry (Quick-Dev)

**Key Stories:**
- 2.1: Real-time step progress (MUST, 5 pts)
- 2.2: Screenshot capture & storage (MUST, 5 pts)
- 2.3: Step execution logging (SHOULD, 3 pts)
- 2.4: Execution timeline view (SHOULD, 5 pts)

**Critical Dependency:** Progress visibility (2.1) required before screenshots (2.2) useful.

**Acceptance Gate:** All steps show status in <500ms; screenshots capture 99% of actions.

---

### Epic 3: Error Handling & Recovery (10 Stories, 48 pts)

**Objective:** Implement 6-level deterministic recovery framework for workflow failures.

**User Value:** "When something fails, JARVIS tries multiple recovery strategies automatically before asking me."

**Business Value:** Workflow reliability critical; robust error handling reduces manual intervention 80%.

**Owner:** Amelia (Security/Core Logic)

**Key Stories:**
- 3.1: Timeout recovery L1 (MUST, 5 pts)
- 3.2: Alternative method L2 (MUST, 8 pts)
- 3.3–3.6: Recovery levels 3–6 (MUST, 13 pts)
- 3.7–3.10: Advanced recovery (SHOULD/COULD, 14 pts)

**Critical Dependency:** Linear dependency chain (L1 → L2 → L3 → L4 → L5 → L6).

**Acceptance Gate:** All 6 levels tested with real failures; no infinite loops.

---

### Epic 4: Workflow Management (10 Stories, 43 pts)

**Objective:** Allow users to save, organize, and reuse workflows easily.

**User Value:** "I can save workflows and run them instantly next time instead of recreating them."

**Business Value:** Recurring automation only valuable if saved persistently.

**Owner:** Barry (Quick-Dev)

**Key Stories:**
- 4.1: Save workflow (MUST, 5 pts)
- 4.2: Load & execute (MUST, 8 pts)
- 4.3: Workflow parameters (SHOULD, 5 pts)
- 4.4: Tags & search (SHOULD, 5 pts)
- 4.5: Pre-built templates (SHOULD, 8 pts)

**Critical Dependency:** Save (4.1) required; then load (4.2).

**Acceptance Gate:** Workflows persist across app restarts; can rerun with same success rate.

---

### Epic 5: Security & Locking (9 Stories, 41 pts)

**Objective:** Prevent unauthorized execution and maintain audit trail of all actions.

**User Value:** "My system is locked unless I enter my passphrase—nobody else can automate tasks."

**Business Value:** Security compliance; user trust; GDPR audit logging.

**Owner:** Amelia (Security Focus)

**Key Stories:**
- 5.1: Passphrase authentication (MUST, 8 pts)
- 5.2: Locked mode activation (MUST, 3 pts)
- 5.3: Brute-force protection (SHOULD, 5 pts)
- 5.4: Request queue while locked (SHOULD, 3 pts)
- 5.5: Audit logging (SHOULD, 5 pts)

**Critical Dependency:** Passphrase (5.1) must exist before locking (5.2).

**Acceptance Gate:** Bcrypt hashing (cost 12), audit log immutable, 3 auth failures → 60s lockout.

---

### Epic 6: Learning & Intelligence (7 Stories, 38 pts)

**Objective:** System learns from execution history and suggests workflows intelligently.

**User Value:** "Over time, JARVIS learns my patterns and suggests workflows I haven't explicitly saved."

**Business Value:** AI-assisted productivity; retention (stickiness).

**Owner:** Barry (ML/Analytics)

**Note:** Deferred to Phase 1.1 (not MVP).

**Key Stories:**
- 6.1: Workflow pattern learning (COULD, 8 pts)
- 6.2: Suggest workflows (COULD, 5 pts)
- 6.3: Confidence learning (COULD, 5 pts)

**Acceptance Gate:** 70%+ of suggested workflows accepted by users.

---

### Epic 7: Infrastructure & Integration (12 Stories, 51 pts)

**Objective:** Set up backend API, database, and system integration infrastructure.

**User Value:** "JARVIS works seamlessly; I don't think about infrastructure."

**Business Value:** Enables all other features; foundation of reliability.

**Owner:** Amelia (API/DB) + Barry (Installer)

**Key Stories:**
- 7.1: API server setup (MUST, 5 pts)
- 7.2: Database setup (MUST, 5 pts)
- 7.3: WebSocket real-time (MUST, 5 pts)
- 7.4: Installation wizard (MUST, 8 pts)
- 7.5: Model pre-detection (MUST, 5 pts)
- 7.6: Agent protocol (MUST, 8 pts)
- 7.7–7.12: Monitoring, backup, export (SHOULD/COULD, 10 pts)

**Critical Dependency:** API (7.1) and database (7.2) required first; then all others build on them.

**Acceptance Gate:** API responds <200ms; database persists reliably; installer handles common scenarios.

---

## EPIC 1: VOICE INPUT & RECOGNITION

### 1.1: Voice Activation via Hotkey

```
Title: User can activate voice listening with hotkey
As a  busy developer
I want  to press a single hotkey to start voice listening
So that  I can keep my hands on the keyboard

Story Points: 5
Priority: MUST (MVP)
Depends On: None
Complexity: Medium
Owner: Amelia

Acceptance Criteria:
  ✓ Default hotkey is configurable (Ctrl+Shift+Alt+S)
  ✓ Hotkey works even when Jarvis window not focused (global hotkey)
  ✓ Pressing hotkey launches Voice Mode immediately (<100ms)
  ✓ Microphone access requested on first use (OS permission dialog)
  ✓ Voice Mode state persists across app restarts (user preference saved)
  ✓ User can change hotkey in Settings menu
  ✓ Conflicting hotkeys denied with error message (e.g., "Ctrl+Shift+Alt+S already used by Windows")

Definition of Done:
  - Unit test: Hotkey registration verified with 10 unique key combinations
  - Integration test: Hotkey triggers Voice Mode from background (app not focused)
  - QA: Tested on Windows 10 21H2, Windows 11 (2 machines each)
  - Documentation: Hotkey behavior + customization in README
  - No crashes or undefined behavior on invalid hotkey
  - Microphone permission dialog appears on first use (platform-specific)

Technical Notes:
  - Use Windows Hook (SetWindowsHookEx) for global hotkey
  - Store preference in SQLite settings table
  - Validate hotkey against Windows reserved keys
  - Handle conflicts gracefully (suggest alternative)

Estimated Dev Time: 3 days (Amelia)
Estimated QA Time: 1 day (Quinn)
```

---

### 1.2: Whisper STT Transcription

```
Title: User's voice is transcribed to text with confidence score
As a  user with strong accent
I want  to see what the system heard (with confidence score)
So that  I can confirm or correct misheard commands before execution

Story Points: 8
Priority: MUST (MVP)
Depends On: 1.1 (hotkey must activate voice first)
Complexity: High
Owner: Amelia

Acceptance Criteria:
  ✓ Whisper model returns transcription + confidence score (0–100%)
  ✓ Confidence displayed in chat: "You: [text] (confidence: 92%)"
  ✓ If confidence <80%, suggest re-speak: "Can you repeat that? I'm not sure."
  ✓ If confidence >90%, auto-accept without confirmation prompt
  ✓ Support for 99 languages (English default, others available in settings)
  ✓ Multilingual input auto-detected (no language selection needed)
  ✓ Fallback to text input if audio quality poor (user types instead)
  ✓ Max audio duration: 30 seconds per input (truncate longer)
  ✓ Whisper model loaded before first use (async on app startup)

Definition of Done:
  - Unit test: Whisper confidence scoring with 10 test audio samples
  - Unit test: Language detection on multilingual samples
  - Performance test: Latency <3 seconds GPU, <10 seconds CPU
  - QA: Tested with 5 different accents; 85%+ accuracy on standard English
  - QA: Tested with 10 different languages; >80% accuracy per language
  - Integration test: Confidence <80% triggers re-speak suggestion
  - Documentation: Language support matrix + accent limitations documented

Technical Notes:
  - Use Whisper-medium model (~1.5GB, runs on GPU/CPU)
  - Confidence = Whisper output probability, not manual calibration
  - Load model async on app startup (don't block UI)
  - Cache model in memory after first load
  - Support inference on GPU (CUDA) + CPU fallback

Estimated Dev Time: 5 days (Amelia)
Estimated QA Time: 2 days (Quinn)

Performance Target:
  - GPU inference: <2 seconds average (3-sec audio)
  - CPU inference: <8 seconds average
  - P99 latency: <4 seconds (GPU), <12 seconds (CPU)
```

---

### 1.3: Voice Pause & Resume

```
Title: User can pause/resume during voice input
As a  user who might be interrupted
I want  to pause listening and resume later
So that  I don't lose my voice command if interrupted

Story Points: 3
Priority: SHOULD (Phase 1, Week 3–4)
Depends On: 1.1 (hotkey to activate)
Complexity: Low
Owner: Barry

Acceptance Criteria:
  ✓ Pause button visible during voice listening (big button, easy to click)
  ✓ Click Pause: Microphone stops, UI shows "Paused" (breathing animation pauses)
  ✓ During pause, audio not recorded (button remains highlighted)
  ✓ Resume button appears instead of Pause (same location, easy to resume)
  ✓ Click Resume: Same session continues listening (concatenate audio)
  ✓ If pause >5 minutes, auto-resume without user action (timeout config?)
  ✓ Partial transcription shown while paused (user sees what's been captured)
  ✓ User can discard and start fresh (new button: "Clear & Restart")

Definition of Done:
  - Integration test: Pause -> Resume state machine verified (5+ cycles)
  - QA: Tested pause/resume with interruption (simulated)
  - QA: Tested auto-timeout (5 min pause)
  - Documentation: Screenshot of Pause/Resume UI

Technical Notes:
  - State machine: Listening → Paused → Listening → Transcribing
  - Store partial audio buffer in memory during pause
  - Timeout configurable (default 5 min)
  - Discard button clears buffer + resets UI

Estimated Dev Time: 2 days (Barry)
Estimated QA Time: 1 day (Quinn)
```

---

### 1.4: Silence Detection

```
Title: System recognizes when user stops speaking
As a  user
I want  silence to automatically end my voice input
So that  I don't have to press Stop manually

Story Points: 5
Priority: SHOULD (Phase 1, Week 3–4)
Depends On: 1.2 (Whisper transcription)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Silence detection threshold: acoustic energy <5 dB for 1.5 seconds
  ✓ After silence detected, system auto-submits audio to Whisper (no user action)
  ✓ Immediate feedback: "Transcribing..." message shown in chat
  ✓ User can override: Press Stop button anytime (manual end)
  ✓ Threshold configurable in Settings (conservative, standard, aggressive)
  ✓ Test with background noise (fan, traffic, office ambience)
  ✓ False-positive rate <5% (silence detected when user still speaking)
  ✓ False-negative rate <10% (silence not detected, user must press Stop)

Definition of Done:
  - Unit test: Silence detection algorithm with 20 test audio samples
  - Integration test: Auto-submit confirmed when silence detected
  - QA: Tested in quiet environment (false positive rate)
  - QA: Tested in noisy environment (fan, office background)
  - QA: Tested with pauses mid-sentence (edge case)
  - Performance test: Latency <500ms from silence detection to "Transcribing..." visible
  - Documentation: Silence threshold + noise handling documented

Technical Notes:
  - Use RMS (root mean square) energy detection or VAD (Voice Activity Detection)
  - Configurable thresholds: Conservative (<3dB), Standard (<5dB), Aggressive (<7dB)
  - Running average over 1.5-second window
  - Fallback: If autodetection unreliable, require manual Stop button

Estimated Dev Time: 3 days (Barry)
Estimated QA Time: 1 day (Quinn)

Edge Cases:
  - User speaks naturally with pauses: Should NOT trigger end (needs 1.5s+ silence)
  - User whispers: May need aggressive threshold
  - Noisy room: May need manual Stop (fallback)
```

---

### 1.5: Voice Confidence Threshold

```
Title: User can set minimum confidence for auto-accepting transcription
As a  user in noisy environment
I want  to configure how confident Whisper must be before auto-accepting
So that  I don't get misheard commands in loud places

Story Points: 3
Priority: SHOULD (Phase 1)
Depends On: 1.2 (confidence scoring)
Complexity: Low
Owner: Barry

Acceptance Criteria:
  ✓ Settings menu has "Voice Confidence Threshold" slider (0–100%)
  ✓ Default: 90% (high confidence auto-accepts)
  ✓ Adjustable range: 70–100%
  ✓ User can set per-device profile (e.g., "Office", "Home", "Car")
  ✓ Updated in real-time (no restart needed)
  ✓ Threshold persists across sessions (saved in database)

Definition of Done:
  - UI test: Slider works, value persists
  - Integration test: Threshold applies to next voice input
  - QA: Test with 70%, 80%, 90%, 100% thresholds
  - Documentation: Settings menu screenshot included

Estimated Dev Time: 2 days (Barry)

UI Mockup:
  Voice Confidence Threshold: [==70%====] (Low) [==========90%=] (High) [Default]
    Options: [Office profile] [Home profile] [Car profile]
```

---

### 1.6: Multilingual Voice Input

```
Title: User can speak in different languages
As a  multilingual user
I want  to speak in Spanish, German, Japanese (etc.) seamlessly
So that  I don't have to switch input methods

Story Points: 8
Priority: COULD (Phase 1.2 or later)
Depends On: 1.2 (Whisper transcription)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Whisper detects language automatically (no user selection needed)
  ✓ Support for 50+ languages (Whisper supports 99)
  ✓ RAG Agent processes command in detected language
  ✓ If language not supported: Fallback to English (user notified)
  ✓ Language preference can be saved (default language for user)
  ✓ Accuracy >80% on tested languages (English, Spanish, German, Japanese)

Definition of Done:
  - Integration test: Auto-detection on 10 languages
  - QA: Tested Spanish, German, Japanese, Mandarin
  - Documentation: Supported language list
  - Edge case: Mixed language (English + Spanish) → handled gracefully

Estimated Dev Time: 5 days (Barry)

Note: Deferred to Phase 1.2 (not MVP).
```

---

### 1.7: Voice Input History

```
Title: User can see and replay past voice inputs
As a  user
I want  to review what I said earlier
So that  I can learn from patterns

Story Points: 5
Priority: COULD (Phase 1.2 or later)
Depends On: 1.2 (transcription)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Voice input history stored (transcription + audio file + timestamp)
  ✓ History accessible via menu: "Voice History"
  ✓ Show last 100 voice inputs (pagination)
  ✓ Each entry shows: Timestamp, Text, Confidence, Language
  ✓ Click entry to replay audio
  ✓ Search by text (find past commands)
  ✓ Auto-delete history >30 days old (configurable)

Definition of Done:
  - Database schema: voice_history table
  - QA: Tested pagination, search, delete
  - Documentation: Voice history access instructions

Estimated Dev Time: 3 days (Barry)

Note: Optional feature, deferred to Phase 1.2.
```

---

### 1.8: Fallback to Text Input

```
Title: If voice fails, user can type instead
As a  user in environment where voice doesn't work
I want  to type my command if microphone unavailable
So that  I can still automate tasks without voice

Story Points: 2
Priority: SHOULD (Phase 1)
Depends On: 1.1, 1.2 (voice foundation)
Complexity: Low
Owner: Amelia

Acceptance Criteria:
  ✓ Chat box always visible (can type even if voice active)
  ✓ User can type intent directly (no voice needed)
  ✓ If microphone not available: Hide voice hotkey, show text input
  ✓ Typed input processed same as voice (through RAG Agent)
  ✓ Typed intent shows: "You: [text] (typed)" (labeled as typed, not voice)

Definition of Done:
  - Integration test: Text input processed correctly
  - QA: Tested with microphone unavailable
  - Documentation: Text input option documented

Estimated Dev Time: 1 day (Amelia)
```

---

## EPIC 2: WORKFLOW EXECUTION & FEEDBACK

### 2.1: Real-Time Step Progress

```
Title: User sees real-time progress as workflow executes
As a  user
I want  to see each step's status (in progress, complete, failed)
So that  I understand what's happening

Story Points: 5
Priority: MUST (MVP)
Depends On: None (independent)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Each step displays: [Step N/M: Description] (e.g., "Step 3/7: Click Save Button")
  ✓ Status indicator: ⏳ In Progress → ✓ Complete → ❌ Failed
  ✓ Real-time updates: Chat updates every 500ms (configurable)
  ✓ WebSocket latency <200ms average (<500ms P99)
  ✓ Confidence score shown after step complete (e.g., "Confidence: 87%")
  ✓ Duration shown: "[Step X completed in 2.3 seconds]"
  ✓ Screenshot thumbnail shown for verification steps (clickable)
  ✓ Current step highlighted (visual emphasis)
  ✓ Completed steps collapsible (user can minimize)

Definition of Done:
  - Integration test: Real-time updates verified (WebSocket latency)
  - Performance test: WebSocket latency verified <200ms (average), <500ms (P99)
  - QA: Tested on slow internet (simulated 100ms latency)
  - QA: Tested with 20-step workflow (UI doesn't lag)
  - UX review: Feedback visible, clear, non-distracting
  - Documentation: Progress display screenshot included

Technical Notes:
  - Use WebSocket for real-time updates (not polling)
  - Server sends progress every 500ms (or on state change)
  - Client renders immediately (no lag)
  - Handle network disconnections gracefully (reconnect + catch up)

Estimated Dev Time: 3 days (Barry)
Estimated QA Time: 1 day (Quinn)
```

---

### 2.2: Screenshot Capture & Storage

```
Title: System captures screenshots before/after each action
As a  user
I want  screenshots of before/after each step
So that  I can verify actions completed as expected

Story Points: 5
Priority: MUST (MVP)
Depends On: 2.1 (progress display)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Before-action screenshot: Baseline state captured
  ✓ After-action screenshot: Result state captured
  ✓ Screenshot metadata: Timestamp, Step#, Action, Duration
  ✓ File naming: [timestamp]_step[N]_before.jpg, [timestamp]_step[N]_after.jpg
  ✓ Storage: [DATA_PATH]\screenshots\session_[id]\ (organized by session)
  ✓ Auto-cleanup: Delete screenshots >7 days old (configurable, default 30 days)
  ✓ Screenshot quality: 80% JPEG compression (balance size/quality)
  ✓ Max screenshot size: 5MB (alert if exceeds)
  ✓ Batch operations: Up to 100 screenshots per workflow (configurable)
  ✓ User can manually export screenshots from UI (ZIP download)

Definition of Done:
  - Unit test: Screenshot file format verified (JPEG, metadata)
  - Integration test: Capture + save latency <500ms
  - QA: Verified storage, auto-cleanup, export
  - QA: Tested with 100+ screenshots (performance)
  - Integration test: Cleanup daemon runs daily (scheduled task)
  - Documentation: Screenshot storage documented

Technical Notes:
  - Use PIL/Pillow for screenshot capture (Python)
  - Compress with Quality=80 for JPEG
  - Store metadata in JSON sidecar file
  - Auto-cleanup via scheduled task (daily at 2 AM)
  - User can configure cleanup threshold

Estimated Dev Time: 3 days (Barry)
Estimated QA Time: 1 day (Quinn)

Configuration Options:
  - Screenshot quality: 60–95% JPEG compression (default 80%)
  - Retention: 7–90 days (default 30 days)
  - Auto-cleanup enabled/disabled
```

---

### 2.3: Step Execution Logging

```
Title: System logs detailed execution data for each step
As a  QA engineer / user
I want  to see detailed logs of what happened in each step
So that  I can debug failures and understand behavior

Story Points: 3
Priority: SHOULD (Phase 1, Week 3–4)
Depends On: 2.1 (progress display)
Complexity: Low
Owner: Quinn

Acceptance Criteria:
  ✓ Each step logs: Timestamp, Agent, Action, Input, Output, Duration, Exit Code
  ✓ Log format: Structured JSON (machine-readable) + plaintext (human-readable)
  ✓ Storage: [DATA_PATH]\logs\execution_[workflowID].log
  ✓ Log rotation: Daily (or 50MB, whichever first); keep 30 days
  ✓ User can view logs in UI: "Details" tab in progress view
  ✓ Logs never contain plaintext passwords (redact sensitive data)
  ✓ Queryable: Filter by step#, agent, status (success/failure)

Definition of Done:
  - Integration test: Logs captured correctly for all agents
  - QA: Verified sensitive data redaction (passwords, API keys)
  - Documentation: Log format + structure documented

Technical Notes:
  - Use Python logging module (StreamHandler + FileHandler)
  - JSON format for structured logging (index-friendly)
  - Redaction regex: Replace passwords, API keys with [REDACTED]

Estimated Dev Time: 2 days (Quinn)
```

---

### 2.4: Execution Timeline View

```
Title: User sees visual timeline of workflow execution
As a  user
I want  to see an interactive timeline of major events
So that  I can understand the overall flow

Story Points: 5
Priority: SHOULD (Phase 1)
Depends On: 2.1, 2.2
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Timeline shows major milestones: Start, RAG Planning, EA Execution, Complete
  ✓ Each milestone shows duration + confidence
  ✓ Interactive: Click milestone to jump to that section in chat
  ✓ Color-coded: Green (success), Red (failed), Yellow (in progress)
  ✓ Handles nested steps: Parent steps expandable
  ✓ Export timeline as image (PNG)

Definition of Done:
  - UI test: Timeline renders correctly
  - QA: Timeline matches actual execution time
  - Documentation: Timeline feature screenshot

Estimated Dev Time: 3 days (Barry)
```

---

### 2.5: Per-Step Confidence Score

```
Title: Each step has confidence score indicating success likelihood
As a  user analyzing past workflows
I want  to know how confident the system was about each step
So that  I can identify risky steps

Story Points: 3
Priority: SHOULD (Phase 1)
Depends On: 2.1 (progress display)
Complexity: Low
Owner: Amelia

Acceptance Criteria:
  ✓ Each completed step shows confidence: "Confidence: 87%"
  ✓ Confidence calculated: Moondream + Backtracking level + System state check
  ✓ Low confidence (<70%): Yellow warning badge
  ✓ High confidence (>90%): Green badge
  ✓ Hover shows: "Why 87%? Moondream detected button (80%), System verified click (95%)"
  ✓ User can analyze: Which steps are risky?

Definition of Done:
  - Integration test: Confidence scoring verified
  - QA: Manual spot-check on 10 workflows
  - Documentation: Confidence scoring methodology

Estimated Dev Time: 2 days (Amelia)
```

---

### 2.6: Workflow Pause During Execution

```
Title: User can pause a running workflow
As a  user
I want  to pause execution in the middle
So that  I can inspect the current state or handle interruption

Story Points: 5
Priority: COULD (Phase 1.2 or later)
Depends On: 2.1 (progress display)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Pause button visible during execution
  ✓ Click Pause: Current step completes, then halts
  ✓ State preserved: Can resume from next step
  ✓ Resume button appears (same behavior as pause)
  ✓ Click Resume: Workflow continues from next step
  ✓ Timeout: Auto-resume after 30 minutes (configurable)
  ✓ Abort option: User can cancel workflow entirely

Definition of Done:
  - Integration test: Pause/Resume state machine
  - QA: Tested pause/resume/abort
  - Documentation: Pause feature described

Estimated Dev Time: 3 days (Barry)

Note: Deferred to Phase 1.2.
```

---

### 2.7: Execution Rollback

```
Title: User can undo executed steps after completion
As a  user
I want  to undo the last N steps
So that  I can correct mistakes or reverse side effects

Story Points: 8
Priority: COULD (Phase 1.2 or later)
Depends On: 2.1, 2.2, 2.3
Complexity: High
Owner: Amelia

Acceptance Criteria:
  ✓ User can select "Undo Last 3 Steps"
  ✓ System reverses actions (e.g., Undo "Delete File" → Restore File)
  ✓ Screenshot comparison shows before/after
  ✓ Not all steps reversible (e.g., "Send Email" cannot unsend)
  ✓ Reversible steps marked with [Reversible] badge
  ✓ Undo history: User can pick any state within last 30 minutes

Definition of Done:
  - Rollback logic for common actions (file ops, window management)
  - Non-reversible detection (email, external APIs)
  - QA: Tested rollback on 5+ common workflows
  - Documentation: Limitations noted (some actions irreversible)

Estimated Dev Time: 5 days (Amelia)

Note: High complexity, deferred to Phase 1.2.
```

---

### 2.8: Step Skip Capability

```
Title: User can skip optional steps during execution
As a  user
I want  to skip a step if it's no longer needed
So that  workflows remain flexible

Story Points: 3
Priority: SHOULD (Phase 1)
Depends On: 2.1 (progress display)
Complexity: Low
Owner: Barry

Acceptance Criteria:
  ✓ Skip button on each step (greyed out for critical steps)
  ✓ Click Skip: Step marked as skipped, continue to next
  ✓ Skipped steps don't affect downstream (no failed dependency)
  ✓ Confirmation dialog: "Skip 'Delete Temp Files'? (Non-critical)"
  ✓ Log recorded: "Step 5 skipped by user"

Definition of Done:
  - Integration test: Skip logic verified
  - QA: Tested skip on critical vs. non-critical steps
  - Documentation: Skip feature described

Estimated Dev Time: 2 days (Barry)
```

---

### 2.9: Execution Metrics Dashboard

```
Title: User can see execution statistics over time
As a  power user
I want  to analyze my workflow performance
So that  I can optimize and identify patterns

Story Points: 8
Priority: COULD (Phase 1.2 or later)
Depends On: 2.1, 2.3
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Dashboard shows: Total executions, Success rate, Avg duration, Error frequency
  ✓ Charts: Success rate over time (line chart), Error types (pie chart)
  ✓ Filters: By workflow, date range, status
  ✓ Trends: Which workflows most reliable? Which fail most?
  ✓ Export: Download metrics as CSV

Definition of Done:
  - UI test: Dashboard renders correctly
  - Integration test: Metrics calculated accurately
  - QA: Verified charts on 100+ executions
  - Documentation: Dashboard guide

Estimated Dev Time: 5 days (Barry)

Note: Deferred to Phase 1.2.
```

---

### 2.10: Live Artifact Capture

```
Title: System captures workflow artifacts (files, logs, output)
As a  user
I want  to see what files/artifacts were created or modified
So that  I can verify results

Story Points: 5
Priority: SHOULD (Phase 1)
Depends On: 2.2 (screenshots)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Artifacts detected: Files created/modified during workflow
  ✓ Captured: File path, Size, Timestamp, Hash (MD5)
  ✓ Displayed in UI: "Artifacts Created" section
  ✓ User can download artifacts from UI
  ✓ Diff comparison: Before/after file content (for text files)

Definition of Done:
  - Integration test: Artifact detection verified
  - QA: Tested with file create/modify/delete
  - Documentation: Artifacts feature described

Estimated Dev Time: 3 days (Barry)
```

---

### 2.11: Execution Notifications

```
Title: System sends desktop notifications on execution completion
As a  user
I want  to be notified when workflows complete
So that  I don't have to watch the screen constantly

Story Points: 3
Priority: COULD (Phase 1.2)
Depends On: 2.1 (progress tracking)
Complexity: Low
Owner: Barry

Acceptance Criteria:
  ✓ Desktop notification: "[Workflow] Completed successfully in 2m 34s"
  ✓ Click notification: Jump to workflow results
  ✓ Sound alert option (configurable)
  ✓ Notify on: Success, Failure, Timeout

Definition of Done:
  - QA: Tested notifications on Windows 10, 11
  - Documentation: Notification settings

Estimated Dev Time: 2 days (Barry)

Note: Deferred to Phase 1.2.
```

---

### 2.12: Video Recording of Execution

```
Title: System can record video of workflow execution
As a  user
I want  to see a video replay of what happened
So that  I can share or archive execution proof

Story Points: 8
Priority: COULD (Phase 1.2+)
Depends On: 2.2 (screenshots)
Complexity: High
Owner: Barry

Acceptance Criteria:
  ✓ Record video of workflow (screen capture + audio commentary)
  ✓ Frame rate: 5 fps (balance quality/filesize)
  ✓ Format: MP4 (H.264)
  ✓ Auto-cleanup: Delete videos >30 days old
  ✓ User can export video (download)

Definition of Done:
  - QA: Video recording tested
  - Performance: Video encoding doesn't slow execution

Estimated Dev Time: 5 days (Barry)

Note: High complexity, deferred to Phase 1.2+.
```

---

## EPIC 3: ERROR HANDLING & RECOVERY

### 3.1: Timeout Recovery (Level 1)

```
Title: System retries when command times out
As a  user
I want  timeouts to auto-retry instead of failing immediately
So that  temporary slowness doesn't break workflows

Story Points: 5
Priority: MUST (MVP)
Depends On: None
Complexity: Medium
Owner: Amelia

Acceptance Criteria:
  ✓ Timeout threshold: Configurable per step (default 30 seconds)
  ✓ On timeout: Auto-retry with +50% longer timeout
  ✓ Max retries: 3 attempts per step
  ✓ User feedback: "Retrying... (Attempt 1/3 [=====>____])"
  ✓ If retry succeeds: Workflow continues (no user action)
  ✓ If all retries fail: Escalate to Level 2 (alternative method)
  ✓ Log all retry attempts with timestamps
  ✓ Metrics: Retry success rate tracked

Definition of Done:
  - Unit test: Timeout detection verified
  - Integration test: Retry logic verified (success on 2nd attempt, fail escalation)
  - Performance test: Retry doesn't incur overhead
  - QA: Tested with network latency simulation
  - Documentation: Retry behavior documented

Technical Notes:
  - Use Python's timeout decorator (threading.Timer or asyncio.wait_for)
  - Exponential backoff: 30s → 45s → 67.5s (1.5x multiplier)
  - Log with millisecond precision

Estimated Dev Time: 3 days (Amelia)
Estimated QA Time: 1 day (Quinn)

Timeout Hierarchy:
  Level 1 (Retry): Same method, longer timeout
  → Level 2 (Alternative): Different method
  → Level 3 (Re-verify): Check system state
  → Level 4 (Replan): New strategy
  → Level 5 (User): Ask human
  → Level 6 (Impossible): Give up
```

---

### 3.2: Alternative Method Recovery (Level 2)

```
Title: System tries alternative method on failure
As a  user
I want  failed commands to try alternatives
So that  package manager issues don't halt workflows

Story Points: 8
Priority: MUST (MVP)
Depends On: 3.1 (timeout recovery must try first)
Complexity: High
Owner: Amelia

Acceptance Criteria:
  ✓ Primary method fails after 3 retries
  ✓ SAA recommends alternative method if available
  ✓ Execute alternative (e.g., npm → yarn, PowerShell → CMD)
  ✓ User feedback: "Trying alternative: [method name]"
  ✓ If alternative succeeds: Continue workflow
  ✓ If alt also fails: Escalate to Level 3
  ✓ Log which method used + success/failure
  ✓ Metrics: Alternative success rate tracked

Definition of Done:
  - Integration test: Alternative method selection verified
  - QA: Test npm/yarn swap, PowerShell/CMD swap, curl/wget
  - Documentation: Supported alternatives documented
  - Logic: 5+ common alternatives pre-configured

Technical Notes:
  - Hardcoded alternatives for common tools:
    - npm ↔ yarn
    - PowerShell ↔ CMD
    - curl ↔ wget
    - git ↔ gh (GitHub CLI)
  - SAA Agent recommends based on error message

Estimated Dev Time: 5 days (Amelia)
Estimated QA Time: 1 day (Quinn)

Common Alternatives:
  npm → yarn, pnpm
  PowerShell → cmd, bash (WSL)
  curl → wget, Invoke-WebRequest (PS)
  git → gh (GitHub CLI)
```

---

### 3.3: Re-Verification with Screenshots (Level 3)

```
Title: System re-takes screenshot to verify outcome
As a  user
I want  the system to double-check outcomes visually
So that  misdetections don't cascade

Story Points: 5
Priority: MUST (MVP)
Depends On: 3.1, 3.2 (escalate here if L1, L2 fail)
Complexity: Medium
Owner: Amelia

Acceptance Criteria:
  ✓ After action fails verification (L1, L2), take new screenshot
  ✓ Analyze screenshot with moondream: "Was the button clicked?"
  ✓ Check file system: "Was file created?"
  ✓ Compare with baseline: Did screen change?
  ✓ Confidence threshold: If >75% match → ACCEPT
  ✓ If <75% confidence: Escalate to Level 4
  ✓ Log screenshot + analysis for debugging

Definition of Done:
  - Integration test: Re-screenshot + analysis verified
  - QA: Tested with 10 failure scenarios
  - Documentation: Screenshot verification logic

Technical Notes:
  - Take fresh screenshot after 500ms delay (allow UI to update)
  - Use moondream to analyze new screenshot
  - Compare with expected outcome image (pre-computed)

Estimated Dev Time: 3 days (Amelia)
```

---

### 3.4: Replan with SAA (Level 4)

```
Title: System replans workflow after multiple failures
As a  user
I want  JARVIS to think of alternative approaches
So that  workflows can adapt to obstacles

Story Points: 8
Priority: MUST (MVP)
Depends On: 3.1, 3.2, 3.3
Complexity: High
Owner: Amelia

Acceptance Criteria:
  ✓ After L1, L2, L3 fail: Call SAA (Strategic Analysis Agent)
  ✓ SAA re-analyzes: "Why did [action] fail? What's alternative?"
  ✓ Generate new sub-plan: 3–5 alternative steps
  ✓ User shown: "Replanning approach. Trying: [new steps]"
  ✓ If new plan succeeds: Continue from there
  ✓ If new plan also fails: Escalate to Level 5
  ✓ Log all replanning attempts

Definition of Done:
  - Integration test: Replan logic verified
  - QA: Tested with 5 complex failure scenarios
  - Documentation: Replan examples shown

Technical Notes:
  - Invoke SAA Agent with context: "Failed to click button. Screenshot attached."
  - SAA generates 3 alternatives using qwen2.5:3b
  - Pick highest-confidence alternative
  - Execute with enhanced error handling

Estimated Dev Time: 5 days (Amelia)

Example Replan:
  Original: Click button, wait, verify
  Failed (L1–L3): Button not clickable
  
  New Plan (L4): Use keyboard shortcut instead
    1. Press Tab (focus button)
    2. Press Enter (activate)
    3. Wait for action
    4. Verify differently (check file system, not visual)
```

---

### 3.5: User Confirmation Dialog (Level 5)

```
Title: System asks user for confirmation when automation unsure
As a  user
I want  to verify risky actions manually
So that  I retain control

Story Points: 3
Priority: MUST (MVP)
Depends On: 3.1–3.4 (escalate here after all auto-recovery attempts)
Complexity: Low
Owner: Amelia

Acceptance Criteria:
  ✓ After L1–L4 fail: Show user confirmation dialog
  ✓ Dialog shows: Screenshot, "What should I do?", Options
  ✓ Options: [Retry], [Skip step], [Cancel workflow]
  ✓ User can inspect screenshot, ask for advice
  ✓ Choice logged + respected

Definition of Done:
  - UI test: Dialog renders correctly
  - QA: Dialog shown on L5 escalation
  - Documentation: User confirmation feature

Estimated Dev Time: 2 days (Amelia)

UI Mockup:
  ┌─────────────────────────────────┐
  │ ❓ Need Your Help               │
  │                                 │
  │ [Screenshot image here]         │
  │                                 │
  │ Step 5 failed after multiple    │
  │ attempts. What should I do?     │
  │                                 │
  │ [Retry]  [Skip Step]  [Cancel]  │
  └─────────────────────────────────┘
```

---

### 3.6: Mark Impossible (Level 6)

```
Title: System gives up gracefully after all recovery attempts
As a  user
I want  clear communication when something can't be automated
So that  I can manually intervene

Story Points: 2
Priority: MUST (MVP)
Depends On: 3.5 (user confirms or gives up)
Complexity: Low
Owner: Amelia

Acceptance Criteria:
  ✓ After L1–L5 all fail: Mark step as "IMPOSSIBLE"
  ✓ Display: "✗ Workflow cannot complete. Last attempt at Step 5."
  ✓ Show: What was attempted, why it failed, suggestion
  ✓ Offer: [Try manually], [Abort workflow], [Save for later]
  ✓ Log marked impossible for analysis

Definition of Done:
  - QA: Mark impossible shown after all recovery
  - Documentation: Level 6 behavior

Estimated Dev Time: 1 day (Amelia)

Example Output:
  ✗ Workflow Cannot Complete
  
  Step 5 Failed: Click "Save" button
  Attempts:
    1. Timeout retry: Failed (button timeout)
    2. Alt method: Failed (keyboard shortcut not available)
    3. Re-verify: Failed (moondream confidence 45%)
    4. Replan: Failed (no alternative found)
    5. User confirm: User chose [Skip]
  
  Outcome: IMPOSSIBLE
  Reason: Button not responding to any method
  
  Next: [Try manually] [Abort] [Save workflow for later]
```

---

### 3.7–3.10: Advanced Recovery Features

(Continuing with SHOULD/COULD stories...)

**3.7: Error Context Capture** (3 pts, SHOULD)
- Capture detailed context when error occurs (system state, memory, processes)
- Help debugging + analysis

**3.8: Recovery Suggestions AI** (5 pts, SHOULD)
- SAA suggests recovery strategies based on error type
- "File not found" → "Check file path", "Create file", "Use alt location"

**3.9: Retry Configuration Per Step** (3 pts, COULD)
- Workflow author can specify retry behavior per step
- E.g., "Retry up to 5 times", "Use exponential backoff"

**3.10: Circuit Breaker Pattern** (3 pts, COULD)
- Stop retrying after N consecutive failures
- "If step fails 3x in a row, stop trying and escalate"

---

## EPIC 4: WORKFLOW MANAGEMENT

### 4.1: Save Workflow

```
Title: User can save successful workflow for reuse
As a  user
I want  to save automated workflows
So that  I can run them instantly next time

Story Points: 5
Priority: MUST (MVP)
Depends On: None (independent)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ After successful execution: "Save workflow?" prompt
  ✓ Default name: Auto-generated from intent (e.g., "Create React App")
  ✓ User can edit name before saving (max 255 chars)
  ✓ Save to database: workflows table
  ✓ Metadata saved: Steps, parameters, tags, confidence, owner
  ✓ Timestamp: created_at, last_executed_at
  ✓ Stored in: SQLite (jarvis.db)
  ✓ User cannot save incomplete workflows (failure during execution)
  ✓ Duplicate names: Auto-version (e.g., "Create React App (2)")
  ✓ User can add tags: #react #dev #quick (hashtag format)

Definition of Done:
  - Unit test: Workflow serialization verified
  - Integration test: Save → Load → Execute verified
  - QA: Tested on various machines/OS
  - Database: Workflow schema implemented
  - Documentation: Save workflow feature described

Technical Notes:
  - Serialize workflow steps to JSON
  - Store in SQLite workflows table
  - Unique constraint on (owner_id, workflow_name)
  - Tags stored in separate workflows_tags table (many-to-many)

Database Schema:
  workflows:
    - id (UUID, PK)
    - owner_id (FK)
    - name (VARCHAR 255)
    - description (TEXT)
    - steps (JSON)
    - tags (ARRAY)
    - created_at (TIMESTAMP)
    - last_executed_at (TIMESTAMP)
    - success_rate (FLOAT)
    - confidence (FLOAT)

Estimated Dev Time: 3 days (Barry)
Estimated QA Time: 1 day (Quinn)
```

---

### 4.2: Load & Execute Workflow

```
Title: User can load and re-execute saved workflow
As a  user with saved workflows
I want  to run them with one click or voice command
So that  I can automate recurring tasks instantly

Story Points: 8
Priority: MUST (MVP)
Depends On: 4.1 (workflows must exist to load)
Complexity: High
Owner: Barry

Acceptance Criteria:
  ✓ Workflows panel shows all saved workflows (alphabetically sorted)
  ✓ Click [Run] button or say "Run [workflow name]"
  ✓ If parameters needed: Prompt user (modal dialog)
  ✓ Execute saved steps (same as original)
  ✓ Track execution: success_rate, last_executed_at updated
  ✓ Execution time: Display and compare to previous runs
  ✓ User can skip steps: "Skip step 3" (modal confirmation)
  ✓ Fallback to re-planning if step times out

Definition of Done:
  - Integration test: Load → Execute verified
  - QA: Executed various workflow types
  - Performance test: Load latency <1 second
  - Documentation: Load/Execute workflow flow

Estimated Dev Time: 5 days (Barry)
Estimated QA Time: 1 day (Quinn)
```

---

**(Continuing with Stories 4.3–4.10 ...)**

**4.3: Workflow Parameters** (5 pts, SHOULD)
- Pass variables to workflows
- Re-use with different inputs (e.g., "Create folder for [NAME]")

**4.4: Workflow Tags & Search** (5 pts, SHOULD)
- Organize workflows with tags
- Search by tag or name

**4.5: Workflow Templates** (8 pts, SHOULD)
- Pre-built templates (e.g., "Daily Report", "Backup Files")
- Users clone templates + customize

**4.6–4.10: Advanced Workflow Management** (COULD)
- Versioning, sharing, duplication, archiving, recommendations

---

## EPIC 5: SECURITY & LOCKING

### 5.1: Passphrase Authentication

```
Title: User can lock system with passphrase
As a  security-conscious user
I want  to require passphrase before executing workflows
So that  others can't automate tasks on my machine

Story Points: 8
Priority: MUST (MVP)
Depends On: None (independent)
Complexity: High
Owner: Amelia

Acceptance Criteria:
  ✓ Lock mode: Configurable in Settings
  ✓ Set passphrase: User creates 8+ character string
  ✓ Hash storage: Bcrypt (cost factor 12), never plaintext
  ✓ Plaintext never stored or logged
  ✓ Lock activation: Hotkey or manual button
  ✓ Unlock: Type passphrase → Verify
  ✓ Incorrect attempts: Max 3, then lockout 60 seconds
  ✓ UI feedback: Passphrase strength meter (weak → strong)
  ✓ Recovery: PIN as alternative (if passphrase forgotten)
  ✓ Timeout: Auto-lock after 30 min inactivity (configurable)
  ✓ Force change: Password expiration (optional, every 90 days)

Definition of Done:
  - Unit test: Passphrase hashing verified
  - Security test: Bcrypt cost factor verified (cost ≥12)
  - Integration test: Lock → Unlock flow
  - QA: Test brute force prevention (3 failures → lockout)
  - Security audit: Passphrase never logged or leaked
  - Documentation: Passphrase setup guide

Technical Notes:
  - Use bcrypt library (python-bcrypt)
  - Cost factor: 12 (~250ms hashing time)
  - Store hash in SQLite security table
  - Clear plaintext from memory after hashing

Database Schema:
  security:
    - passphrase_hash (BLOB, bcrypt hash)
    - is_locked (BOOLEAN)
    - failed_auth_attempts (INT)
    - last_auth_attempt (TIMESTAMP)
    - auto_lock_timeout_mins (INT, default 30)

Estimated Dev Time: 5 days (Amelia)
Estimated QA Time: 2 days (Quinn, security focus)
```

---

### 5.2: Locked Mode Activation

```
Title: User can activate locked mode to prevent execution
As a  user leaving computer unattended
I want  to lock JARVIS so nobody can execute workflows
So that  my system is protected from unauthorized use

Story Points: 3
Priority: MUST (MVP)
Depends On: 5.1 (passphrase must exist)
Complexity: Low
Owner: Amelia

Acceptance Criteria:
  ✓ Lock button visible in UI (lock icon)
  ✓ Click lock: System locked, passphrase prompt appears
  ✓ UI shows: Padlock icon (large, center)
  ✓ Locked features: Voice input disabled, execution blocked
  ✓ Queued requests: Stored but not executed until unlocked
  ✓ Unlock: Type passphrase → System active again
  ✓ Indication: Visual/audio feedback when locked/unlocked

Definition of Done:
  - Integration test: Locked mode engages/disengages
  - QA: Tested execution blocking while locked
  - Documentation: Locked mode described

Estimated Dev Time: 2 days (Amelia)
```

---

**(Continuing with Stories 5.3–5.9 ...)**

**5.3: Brute-Force Protection** (5 pts, SHOULD)
- 3 failed attempts → 60 second lockout
- Exponential backoff (1st fail, 2nd fail, 3rd fail → 60s timeout)

**5.4: Request Queue** (3 pts, SHOULD)
- Requests queued while system locked
- Executed in order after unlock

**5.5: Audit Logging** (5 pts, SHOULD)
- Log all actions: Who, What, When, Result
- Immutable audit trail (hash verification)

**5.6–5.9: Advanced Security** (COULD)
- PIN auth, voice auth, admin mode (master passphrase)

---

## EPIC 6: LEARNING & INTELLIGENCE

### 6.1: Workflow Pattern Learning

```
Title: System learns common workflow patterns
As a  frequent user
I want  JARVIS to suggest workflows based on my habits
So that  I can automate tasks I didn't explicitly save

Story Points: 8
Priority: COULD (Phase 1.2 or later)
Depends On: 4.1, 4.2, 2.1 (workflows saved + executed)
Complexity: High
Owner: Barry

Acceptance Criteria:
  ✓ After each execution: Record in execution_records table
  ✓ Extract patterns: Intent, steps, frequency, success rate
  ✓ Suggest workflows: "I see you frequently [pattern]. Save as workflow?"
  ✓ Confidence: Only suggest if pattern confidence >70%
  ✓ Learn preferences: Frameworks, tools, styles user prefers
  ✓ Context matching: Suggest based on time of day, app in focus, etc.
  ✓ Metrics: Track suggestion acceptance rate

Definition of Done:
  - Integration test: Pattern extraction verified
  - QA: Test with 50+ execution history
  - Documentation: Learning mechanism explained

Technical Notes:
  - Use clustering algorithm (K-means on workflow embeddings)
  - Minimum 3 similar executions to suggest
  - Confidence = cluster cohesion + user feedback

Estimated Dev Time: 5 days (Barry)

Note: DEFERRED to Phase 1.2 (not MVP).
```

---

**(Stories 6.2–6.7 are COULD-priority, deferred to Phase 1.2+)**

---

## EPIC 7: INFRASTRUCTURE & INTEGRATION

### 7.1: API Server Setup (FastAPI)

```
Title: Backend API server running on localhost
As a  developer
I want  FastAPI backend serving REST endpoints
So that  frontend can communicate with backend

Story Points: 5
Priority: MUST (MVP)
Depends On: None (independent)
Complexity: Medium
Owner: Amelia

Acceptance Criteria:
  ✓ FastAPI server running on localhost:9000
  ✓ All endpoints from PART 28.2 API spec implemented
  ✓ Response time: <200ms average (P99 <500ms)
  ✓ Rate limiting: Configured per endpoint (from PART 28.2)
  ✓ CORS enabled: Frontend can call backend
  ✓ Error responses: Consistent format (from PART 28.4)
  ✓ Logging: All requests logged (DEBUG level)
  ✓ Health check: GET /health returns server status

Definition of Done:
  - Unit test: API endpoints validate input/output
  - Integration test: End-to-end API calls verified
  - Performance test: Latency <200ms measured
  - QA: All 25+ endpoints tested
  - Documentation: API startup instructions

Technical Notes:
  - Use FastAPI + Uvicorn
  - Python 3.10+ required
  - Dependencies: fastapi, uvicorn, pydantic, sqlalchemy
  - Start: `python -m uvicorn app:app --host 127.0.0.1 --port 9000`

API Endpoints (from PART 28.2):
  - GET /api/chats
  - POST /api/chats
  - POST /api/chats/{chatId}/messages
  - GET /api/workflows
  - POST /api/workflows
  - GET /api/workflows/{workflowId}
  - ... (25+ endpoints total)

Estimated Dev Time: 3 days (Amelia)
Estimated QA Time: 1 day (Quinn)
```

---

### 7.2: Database Setup (SQLite)

```
Title: SQLite database initialized with schema
As a  system
I want  persistent data storage
So that  workflows, chats, and settings persist

Story Points: 5
Priority: MUST (MVP)
Depends On: 7.1 (API references DB)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ SQLite database file: jarvis.db (in [DATA_PATH])
  ✓ Schema initialized: 14 tables created (from PART 6)
  ✓ Relationships: Foreign keys configured
  ✓ Migrations: Schema versioning (Alembic)
  ✓ Indexes: Performance indexes on frequently-queried columns
  ✓ Backup: Automated daily backups (from PART 7.7)

Definition of Done:
  - Database schema implemented (14 tables)
  - Integration test: CRUD operations verified
  - Performance test: Query latency <100ms
  - Documentation: Database schema documented

Technical Notes:
  - Use SQLAlchemy ORM
  - Alembic for migrations
  - Connection pooling (QueuePool, max 5 connections)
  - WAL mode enabled (concurrent reads)

Database Tables (from PART 6):
  1. users
  2. workflows
  3. workflow_steps
  4. executions
  5. execution_steps
  6. chats
  7. chat_messages
  8. settings
  9. security (passphrase hash, lock state)
  10. audit_logs
  11. screenshots
  12. agents
  13. agent_runs
  14. backups

Estimated Dev Time: 3 days (Barry)
Estimated QA Time: 1 day (Quinn)
```

---

### 7.3: WebSocket Real-Time Updates

```
Title: WebSocket connection for real-time progress updates
As a  frontend
I want  real-time updates without polling
So that  UI stays in sync with backend

Story Points: 5
Priority: MUST (MVP)
Depends On: 7.1 (API serves WebSocket)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ WebSocket endpoint: ws://localhost:9000/ws
  ✓ Real-time updates: Progress, step completion, errors
  ✓ Message format: JSON with type, payload, timestamp
  ✓ Latency: <200ms average (message sent to UI rendered)
  ✓ Reconnection: Automatic on disconnect (exponential backoff)
  ✓ Heartbeat: Keep-alive every 30 seconds

Definition of Done:
  - Integration test: WebSocket messages verified
  - Performance test: Latency <200ms
  - QA: Tested on slow network (simulated)
  - Documentation: WebSocket message format

WebSocket Message Types:
  - progress: Step completion, status
  - error: Error message, suggestion
  - complete: Workflow finished
  - screenshot: New screenshot available
  - log: Execution log entry

Estimated Dev Time: 3 days (Barry)
```

---

### 7.4: Installation Wizard

```
Title: User-friendly installer for first-time setup
As a  end user
I want  to install JARVIS with a step-by-step wizard
So that  installation is painless

Story Points: 8
Priority: MUST (MVP)
Depends On: None (independent)
Complexity: High
Owner: Barry

Acceptance Criteria:
  ✓ Installer workflow: 9 screens (from PART 3)
  ✓ Screen 1: Welcome
  ✓ Screen 2: Requirements check (Windows 10+, 8GB RAM, 10GB disk)
  ✓ Screen 3: Drive selection (where to install)
  ✓ Screen 4: Model pre-detection (from 7.5)
  ✓ Screen 5: Model download (if not found)
  ✓ Screen 6: Permissions (microphone, admin)
  ✓ Screen 7: Hotkey configuration
  ✓ Screen 8: First test (try voice input)
  ✓ Screen 9: Done (launch app)
  ✓ Uninstall option (remove app + data)

Definition of Done:
  - Installer tested on Windows 10, 11
  - QA: All 9 screens functional
  - Error handling: Graceful failures
  - Documentation: Installation guide

Technical Notes:
  - Use NSIS (Nullsoft Installer System) or PyInstaller
  - Generate EXE installer (~2.5GB with models)
  - Auto-detect OS version, RAM, disk space
  - Registry entries for uninstall + auto-start (optional)

Estimated Dev Time: 5 days (Barry)
Estimated QA Time: 2 days (Quinn)
```

---

### 7.5: Model Pre-Detection (Ollama)

```
Title: Installer detects if Ollama/models already installed
As a  user
I want  the installer to reuse existing Ollama
So that  I don't have to re-download 8GB of models

Story Points: 5
Priority: MUST (MVP)
Depends On: 7.4 (installer calls detection)
Complexity: Medium
Owner: Barry

Acceptance Criteria:
  ✓ Check: Ollama running on port 11434?
  ✓ Check: Models loaded? (qwen2.5:3b, Whisper-medium, Piper, moondream)
  ✓ If found: Reuse existing
  ✓ If not found: Offer download
  ✓ If user declines: Graceful error + instructions

Definition of Done:
  - Integration test: Detection verified
  - QA: Tested with/without Ollama installed
  - Documentation: Model pre-detection explained

Technical Notes:
  - HTTP GET http://localhost:11434/api/tags (list models)
  - Parse response JSON for model names
  - Store Ollama path in registry/config

Estimated Dev Time: 3 days (Barry)
```

---

### 7.6: Agent Communication Protocol

```
Title: Establish communication between 13 agents
As a  system
I want  agents to call each other via REST
So that  workflows can orchestrate multi-agent reasoning

Story Points: 8
Priority: MUST (MVP)
Depends On: 7.1 (API server as intermediary)
Complexity: High
Owner: Amelia

Acceptance Criteria:
  ✓ Local REST protocol: http://localhost:91XX/agent/{agent_id}
  ✓ Request format: JSON with requestId, target, action, payload
  ✓ Timeout: 30 seconds per request (configurable)
  ✓ Retry: Exponential backoff (30s → 45s → 67.5s)
  ✓ Error handling: Transient vs. permanent errors
  ✓ Service discovery: Agent registry maintained
  ✓ Health checks: Periodic ping every 5 seconds
  ✓ Concurrency: Max N concurrent agents (configurable per agent)

Definition of Done:
  - Integration test: Agent-to-agent communication verified
  - Performance test: Latency <200ms inter-agent
  - QA: Tested with 3 concurrent workflows
  - Documentation: Agent protocol documented

Technical Notes:
  - Use requests library for HTTP client
  - JSON serialization/deserialization
  - Timeout context manager (signal.alarm or asyncio.wait_for)
  - Retry logic with exponential backoff

Agent Endpoints:
  Listening on: http://localhost:91XX/agent/{agent_id}
  POST /agent/{agent_id}/process
  GET /agent/{agent_id}/health

Estimated Dev Time: 5 days (Amelia)
Estimated QA Time: 1 day (Quinn)
```

---

**(Stories 7.7–7.12 continue with SHOULD/COULD priorities...)**

**7.7: Backup & Restore** (5 pts, SHOULD)
- Daily SQLite backups
- User can restore from backup (Settings → Backups)

**7.8: Health Monitoring** (3 pts, SHOULD)
- GET /health endpoint checking DB, Ollama, disk space
- Alert if health degraded

**7.9: Error Logging & Analysis** (3 pts, SHOULD)
- Centralized error log (file + DB)
- Analysis dashboard (Phase 1.2)

**7.10: Settings Persistence** (3 pts, SHOULD)
- User settings saved to database
- Load on startup

**7.11: Electron UI Shell** (5 pts, MUST)
- Electron app wrapping React frontend
- Communicates with FastAPI backend

**7.12: Data Export** (3 pts, COULD)
- Export workflows, chats, settings as JSON/CSV

---

## BACKLOG CSV FORMAT

```csv
StoryID,Title,Epic,Points,Priority,Dependencies,Status,Owner,Category,EstDays,AC_Count,ComplexityLevel
1.1,Voice Activation via Hotkey,1,5,MUST,None,Backlog,Amelia,User_Interface,3,7,Medium
1.2,Whisper STT Transcription,1,8,MUST,1.1,Backlog,Amelia,Core_Feature,5,8,High
1.3,Voice Pause & Resume,1,3,SHOULD,1.1,Backlog,Barry,UX_Enhancement,2,8,Low
1.4,Silence Detection,1,5,SHOULD,1.2,Backlog,Barry,Core_Feature,3,8,Medium
1.5,Voice Confidence Threshold,1,3,SHOULD,1.2,Backlog,Barry,Settings,2,6,Low
1.6,Multilingual Voice Input,1,8,COULD,1.2,Backlog,Barry,Expansion,5,7,High
1.7,Voice Input History,1,5,COULD,1.2,Backlog,Barry,Analytics,3,5,Medium
1.8,Fallback to Text Input,1,2,SHOULD,1.1;1.2,Backlog,Amelia,Accessibility,1,4,Low
2.1,Real-Time Step Progress,2,5,MUST,None,Backlog,Barry,User_Feedback,3,7,Medium
2.2,Screenshot Capture & Storage,2,5,MUST,2.1,Backlog,Barry,Core_Feature,3,8,Medium
2.3,Step Execution Logging,2,3,SHOULD,2.1,Backlog,Quinn,Debugging,2,6,Low
2.4,Execution Timeline View,2,5,SHOULD,2.1;2.2,Backlog,Barry,Analytics,3,6,Medium
2.5,Per-Step Confidence Score,2,3,SHOULD,2.1,Backlog,Amelia,Transparency,2,5,Low
2.6,Workflow Pause During Execution,2,5,COULD,2.1,Backlog,Barry,UX_Enhancement,3,6,Medium
2.7,Execution Rollback,2,8,COULD,2.1;2.2;2.3,Backlog,Amelia,Advanced,5,7,High
2.8,Step Skip Capability,2,3,SHOULD,2.1,Backlog,Barry,Flexibility,2,4,Low
2.9,Execution Metrics Dashboard,2,8,COULD,2.1;2.3,Backlog,Barry,Analytics,5,8,Medium
2.10,Live Artifact Capture,2,5,SHOULD,2.2,Backlog,Barry,Verification,3,6,Medium
2.11,Execution Notifications,2,3,COULD,2.1,Backlog,Barry,UX_Enhancement,2,4,Low
2.12,Video Recording of Execution,2,8,COULD,2.2,Backlog,Barry,Archive,5,5,High
3.1,Timeout Recovery (Level 1),3,5,MUST,None,Backlog,Amelia,Resilience,3,7,Medium
3.2,Alternative Method Recovery (Level 2),3,8,MUST,3.1,Backlog,Amelia,Resilience,5,8,High
3.3,Re-Verification (Level 3),3,5,MUST,3.1;3.2,Backlog,Amelia,Resilience,3,6,Medium
3.4,Replan with SAA (Level 4),3,8,MUST,3.1;3.2;3.3,Backlog,Amelia,Resilience,5,7,High
3.5,User Confirmation (Level 5),3,3,MUST,3.1;3.2;3.3;3.4,Backlog,Amelia,Resilience,2,5,Low
3.6,Mark Impossible (Level 6),3,2,MUST,3.5,Backlog,Amelia,Resilience,1,4,Low
3.7,Error Context Capture,3,3,SHOULD,3.1,Backlog,Quinn,Debugging,2,6,Low
3.8,Recovery Suggestions AI,3,5,SHOULD,3.4,Backlog,Barry,AI,3,7,Medium
3.9,Retry Config Per Step,3,3,COULD,3.1,Backlog,Amelia,Advanced,2,5,Low
3.10,Circuit Breaker Pattern,3,3,COULD,3.1;3.6,Backlog,Amelia,Advanced,2,4,Low
4.1,Save Workflow,4,5,MUST,None,Backlog,Barry,Core_Feature,3,8,Medium
4.2,Load & Execute Workflow,4,8,MUST,4.1,Backlog,Barry,Core_Feature,5,8,High
4.3,Workflow Parameters,4,5,SHOULD,4.1;4.2,Backlog,Barry,Flexibility,3,7,Medium
4.4,Workflow Tags & Search,4,5,SHOULD,4.1,Backlog,Barry,Organization,3,6,Medium
4.5,Workflow Templates,4,8,SHOULD,4.1;4.2,Backlog,Barry,Onboarding,5,7,High
4.6,Workflow Versioning,4,5,COULD,4.1,Backlog,Barry,Advanced,3,6,Medium
4.7,Workflow Sharing,4,5,COULD,4.1,Backlog,Barry,Collaboration,3,5,Medium
4.8,Workflow Duplication,4,3,SHOULD,4.1,Backlog,Barry,UX,2,4,Low
4.9,Workflow Deletion & Archive,4,3,SHOULD,4.1,Backlog,Barry,Management,2,5,Low
4.10,Recommend Workflows,4,5,COULD,4.1;4.2,Backlog,Barry,AI,3,6,Medium
5.1,Passphrase Authentication,5,8,MUST,None,Backlog,Amelia,Security,5,8,High
5.2,Locked Mode Activation,5,3,MUST,5.1,Backlog,Amelia,Security,2,6,Low
5.3,Brute-Force Protection,5,5,SHOULD,5.1,Backlog,Amelia,Security,3,7,Medium
5.4,Request Queue While Locked,5,3,SHOULD,5.2,Backlog,Barry,Security,2,5,Low
5.5,Audit Logging,5,5,SHOULD,None,Backlog,Quinn,Security,3,7,Medium
5.6,PIN Authentication,5,3,COULD,5.1,Backlog,Amelia,Security,2,4,Low
5.7,Voice Authentication,5,8,COULD,5.1,Backlog,Amelia,Security,5,5,High
5.8,Session Timeout Auto-Lock,5,3,SHOULD,5.1;5.2,Backlog,Amelia,Security,2,5,Low
5.9,Admin Mode,5,5,COULD,5.1,Backlog,Amelia,Security,3,4,Medium
6.1,Workflow Pattern Learning,6,8,COULD,4.1;4.2;2.1,Backlog,Barry,AI,5,7,High
6.2,Suggest Workflows,6,5,COULD,6.1,Backlog,Barry,AI,3,6,Medium
6.3,Confidence Threshold Learning,6,5,COULD,None,Backlog,Barry,AI,3,6,Medium
6.4,User Preference Learning,6,3,COULD,6.1,Backlog,Barry,AI,2,5,Low
6.5,Success Prediction,6,5,COULD,6.1,Backlog,Barry,AI,3,5,Medium
6.6,Feedback Loop (Ratings),6,3,COULD,6.1;6.2,Backlog,Barry,AI,2,4,Low
6.7,Smart Retry Thresholds,6,3,COULD,3.1,Backlog,Amelia,AI,2,4,Low
7.1,API Server Setup (FastAPI),7,5,MUST,None,Backlog,Amelia,Infrastructure,3,6,Medium
7.2,Database Setup (SQLite),7,5,MUST,7.1,Backlog,Barry,Infrastructure,3,7,Medium
7.3,WebSocket Real-Time Updates,7,5,MUST,7.1,Backlog,Barry,Infrastructure,3,6,Medium
7.4,Installation Wizard,7,8,MUST,None,Backlog,Barry,Onboarding,5,8,High
7.5,Model Pre-Detection,7,5,MUST,7.4,Backlog,Barry,Onboarding,3,7,Medium
7.6,Agent Communication Protocol,7,8,MUST,7.1,Backlog,Amelia,Infrastructure,5,7,High
7.7,Backup & Restore,7,5,SHOULD,7.2,Backlog,Quinn,Operations,3,6,Medium
7.8,Health Monitoring,7,3,SHOULD,7.1,Backlog,Quinn,Operations,2,5,Low
7.9,Error Logging & Analysis,7,3,SHOULD,7.1,Backlog,Quinn,Debugging,2,5,Low
7.10,Settings Persistence,7,3,SHOULD,7.2,Backlog,Barry,Infrastructure,2,5,Low
7.11,Electron UI Shell,7,5,MUST,None,Backlog,Barry,Frontend,3,6,Medium
7.12,Data Export,7,3,COULD,7.2,Backlog,Barry,Operations,2,5,Low
```

---

## SPRINT PLANNING GUIDE

### MVP Sprint Breakdown (4 Weeks @ 20 pts/sprint)

**SPRINT 1 (Week 1): Voice Input Foundation + Progress Display**

| Story | Points | Dev Days | Owner | Dependencies |
|-------|--------|----------|-------|---|
| 1.1 - Voice Hotkey | 5 | 3 | Amelia | None |
| 1.2 - Whisper STT | 8 | 5 | Amelia | 1.1 |
| 2.1 - Progress UI | 5 | 3 | Barry | None |
| 7.4 - Installer (partial) | 2 | 1 | Barry | None |
| **Subtotal** | **20** | **12** | — | — |

**SPRINT 2 (Week 2): Screenshots + Error Recovery L1–L2**

| Story | Points | Dev Days | Owner | Dependencies |
|-------|--------|----------|-------|---|
| 2.2 - Screenshots | 5 | 3 | Barry | 2.1 |
| 3.1 - Timeout (L1) | 5 | 3 | Amelia | None |
| 3.2 - Alternative (L2) | 8 | 5 | Amelia | 3.1 |
| 1.8 - Text Fallback | 2 | 1 | Amelia | 1.1, 1.2 |
| **Subtotal** | **20** | **12** | — | — |

**SPRINT 3 (Week 3): Recovery L3–L6 + Voice Enhancements**

| Story | Points | Dev Days | Owner | Dependencies |
|-------|--------|----------|-------|---|
| 3.3 - Re-verify (L3) | 5 | 3 | Amelia | 3.1, 3.2 |
| 3.4 - Replan (L4) | 8 | 5 | Amelia | 3.1–3.3 |
| 1.3 - Pause/Resume | 3 | 2 | Barry | 1.1 |
| 1.4 - Silence Detection | 5 | 3 | Barry | 1.2 |
| (Note: 3 extra pts for contingency) | — | — | — | — |
| **Subtotal** | **20** | **13** | — | — |

**SPRINT 4 (Week 4): Workflow Management + Security**

| Story | Points | Dev Days | Owner | Dependencies |
|-------|--------|----------|-------|---|
| 3.5–3.6 - User Confirm + Impossible (L5–L6) | 5 | 3 | Amelia | 3.1–3.4 |
| 4.1 - Save Workflow | 5 | 3 | Barry | None |
| 4.2 - Load & Execute | 8 | 5 | Barry | 4.1 |
| 5.1 - Passphrase Auth | 8 | 5 | Amelia | None |
| 5.2 - Locked Mode | 3 | 2 | Amelia | 5.1 |
| **Subtotal (overflow)** | **29** | **18** | — | — |
| **Actually fit in Sprint 4** | **20** | **12** | — | — |
| (Overflow: 4.2 shifted to Phase 1.1 or compressed) | — | — | — | — |

**Phase 1.1 (Week 5+): SHOULD-Have Stories**

- 1.5: Voice Confidence Threshold (3 pts)
- 1.6+: Multilingual, History, etc.
- 2.3–2.5: Execution enhancements
- 4.3–4.5: Workflow features
- 5.3–5.5: Advanced security
- 7.7–7.10: Infrastructure

---

## DEPENDENCY GRAPH

```
EPIC 1: Voice Input
├─ 1.1 (Hotkey) ← START
│  └─ 1.2 (Whisper) ← Depends: 1.1
│     ├─ 1.3 (Pause) ← Depends: 1.1
│     ├─ 1.4 (Silence) ← Depends: 1.2
│     ├─ 1.5 (Threshold) ← Depends: 1.2
│     ├─ 1.6 (Multilingual) ← Depends: 1.2
│     ├─ 1.7 (History) ← Depends: 1.2
│     └─ 1.8 (Text Fallback) ← Depends: 1.1, 1.2

EPIC 2: Execution
├─ 2.1 (Progress) ← Independent, can start early
│  ├─ 2.2 (Screenshots) ← Depends: 2.1
│  ├─ 2.3 (Logging) ← Depends: 2.1
│  ├─ 2.4 (Timeline) ← Depends: 2.1, 2.2
│  ├─ 2.5 (Confidence) ← Depends: 2.1
│  ├─ 2.6 (Pause) ← Depends: 2.1
│  ├─ 2.7 (Rollback) ← Depends: 2.1, 2.2, 2.3
│  ├─ 2.8 (Skip) ← Depends: 2.1
│  ├─ 2.9 (Metrics) ← Depends: 2.1, 2.3
│  ├─ 2.10 (Artifacts) ← Depends: 2.2
│  ├─ 2.11 (Notifications) ← Depends: 2.1
│  └─ 2.12 (Video) ← Depends: 2.2

EPIC 3: Error Recovery
├─ 3.1 (L1 Retry) ← Independent, can start early
│  └─ 3.2 (L2 Alt) ← Depends: 3.1
│     └─ 3.3 (L3 Verify) ← Depends: 3.1, 3.2
│        └─ 3.4 (L4 Replan) ← Depends: 3.1, 3.2, 3.3
│           └─ 3.5 (L5 User) ← Depends: 3.1–3.4
│              └─ 3.6 (L6 Impossible) ← Depends: 3.5

EPIC 4: Workflows
├─ 4.1 (Save) ← Independent, can start early
│  └─ 4.2 (Load&Execute) ← Depends: 4.1
│     ├─ 4.3 (Parameters) ← Depends: 4.1, 4.2
│     ├─ 4.4 (Search) ← Depends: 4.1
│     └─ 4.5 (Templates) ← Depends: 4.1, 4.2

EPIC 5: Security
├─ 5.1 (Passphrase) ← Independent, can start early
│  ├─ 5.2 (Lock) ← Depends: 5.1
│  ├─ 5.3 (Brute-force) ← Depends: 5.1
│  ├─ 5.4 (Queue) ← Depends: 5.2
│  ├─ 5.5 (Audit) ← Independent
│  ├─ 5.6 (PIN) ← Depends: 5.1
│  ├─ 5.7 (Voice) ← Depends: 5.1
│  └─ 5.8 (Timeout) ← Depends: 5.1, 5.2

EPIC 6: Learning
├─ 6.1 (Pattern Learn) ← Depends: 4.1, 4.2, 2.1
│  ├─ 6.2 (Suggest) ← Depends: 6.1
│  ├─ 6.3 (Confidence Learn) ← Independent
│  ├─ 6.4 (Preference) ← Depends: 6.1
│  ├─ 6.5 (Success Predict) ← Depends: 6.1
│  └─ 6.6 (Feedback) ← Depends: 6.1, 6.2
│  └─ 6.7 (Smart Retry) ← Depends: 3.1

EPIC 7: Infrastructure
├─ 7.1 (API) ← Independent, start FIRST
│  ├─ 7.3 (WebSocket) ← Depends: 7.1
│  ├─ 7.6 (Agent Protocol) ← Depends: 7.1
│  └─ (All others depend on 7.1)
├─ 7.2 (Database) ← Independent, can start early (before 7.1 API)
│  ├─ 7.7 (Backup) ← Depends: 7.2
│  ├─ 7.10 (Settings) ← Depends: 7.2
│  └─ 7.12 (Export) ← Depends: 7.2
├─ 7.4 (Installer) ← Independent, start FIRST
│  └─ 7.5 (Model Pre-detect) ← Depends: 7.4
├─ 7.8 (Monitoring) ← Depends: 7.1
├─ 7.9 (Logging) ← Depends: 7.1
└─ 7.11 (Electron) ← Independent (connects to 7.1 backend)

CRITICAL PATH:
  7.1 (API) → 7.6 (Agent Protocol)
  +
  3.1 (L1 Retry) → 3.2 (L2) → 3.3 (L3) → 3.4 (L4) → 3.5 (L5) → 3.6 (L6)
  +
  1.1 (Hotkey) → 1.2 (Whisper)
  +
  4.1 (Save) → 4.2 (Load)
  
  Total Critical Path: ~35 pts (3+ sprints)
```

---

## NEXT STEPS

1. ✅ **Export CSV:** Copy backlog CSV above for Jira/Azure DevOps import
2. ✅ **Review with Team:** Bob + Amelia confirm story points + owners
3. ✅ **Sprint Planning:** Finalize Sprint 1 stories (lock by Day 1 Phase 1)
4. ✅ **Kickoff:** Team standup, acceptance of stories, development begins

---

**Document Generated:** February 24, 2026  
**Party Mode Consensus:** Ready for implementation  
**MVP Status:** ✅ APPROVED FOR PHASE 1 DEVELOPMENT

---

## BUG LOG — Sprint Implementation Defects

> Bugs found during sprint-by-sprint implementation, logged for traceability.

### BUG-001 — Sprint 1: MissingGreenlet lazy load error
- **Sprint:** 1 (Database Layer)
- **Story:** 2.3 (Basic Orchestration)
- **Severity:** Blocker
- **Description:** SQLAlchemy async sessions raised `MissingGreenlet` errors when accessing relationships lazily. Models loaded via lazy loading triggered synchronous IO in an async context.
- **Root Cause:** Default lazy loading on relationships is incompatible with `asyncio` sessions.
- **Fix:** Added `selectinload()` eager loading on all relationship queries and `db.refresh()` after inserts. Set `expire_on_commit=False` on session factory.
- **Status:** ✅ RESOLVED

### BUG-002 — Sprint 2: Agent dispatch field mismatches
- **Sprint:** 2 (Agent Protocol)
- **Story:** 2.1–2.4
- **Severity:** Major
- **Description:** Orchestrator and registry tests failed due to field name mismatches (`agent_name` vs `agent`, `data` vs `output`, `_agents.clear()` vs `.agents.clear()`).
- **Root Cause:** Schema and protocol definitions evolved; tests referenced old field names.
- **Fix:** Aligned test field names with actual protocol/schema definitions.
- **Status:** ✅ RESOLVED

### BUG-003 — Sprint 3: Duplicate DB fixture override
- **Sprint:** 3 (Security)
- **Story:** 3.x (Auth/Security)
- **Severity:** Minor
- **Description:** Sprint 3 test file defined a local `client` fixture that conflicted with the shared conftest `client` fixture, causing dependency injection failures.
- **Root Cause:** Copy-paste of fixture from conftest into test file.
- **Fix:** Removed local fixture, used shared conftest client.
- **Status:** ✅ RESOLVED

### BUG-004 — Sprint 4: scrollIntoView jsdom crash
- **Sprint:** 4 (Electron Frontend)
- **Story:** 4.x (Chat UI)
- **Severity:** Minor
- **Description:** `scrollIntoView` is not implemented in jsdom, causing test crashes on chat message rendering.
- **Root Cause:** jsdom doesn't implement `scrollIntoView`.
- **Fix:** Added guard `typeof el.scrollIntoView === 'function'` before calling.
- **Status:** ✅ RESOLVED

### BUG-005 — Sprint 5: Bearer token redaction order
- **Sprint:** 5 (Execution Logger)
- **Story:** 5.1 (Execution Logger)
- **Severity:** Minor
- **Description:** Sensitive data redactor was not redacting Bearer tokens correctly because the pattern order allowed a more generic pattern to match first.
- **Root Cause:** Regex pattern ordering — generic patterns matched before the specific Bearer token pattern.
- **Fix:** Reordered `REDACT_PATTERNS` to put Bearer token pattern first.
- **Status:** ✅ RESOLVED

### BUG-006 — Sprint 5: Floating-point precision in confidence
- **Sprint:** 5 (Frontend)
- **Story:** 5.3 (StepConfidence)
- **Severity:** Trivial
- **Description:** `calculateConfidence([0.80, 0.90])` returned `0.8500000000000001` instead of `0.85`, causing exact `toBe()` assertion failure.
- **Root Cause:** IEEE 754 floating-point arithmetic.
- **Fix:** Changed assertion to `toBeCloseTo(0.85)`.
- **Status:** ✅ RESOLVED

### BUG-007 — Sprint 6: Silence detection threshold mismatch
- **Sprint:** 6 (Voice)
- **Story:** 1.4 (Silence Detection)
- **Severity:** Minor
- **Description:** Silence detection tests failed because test data (amplitude=1 in 16-bit PCM) produces ~5.69 dB via the formula `20*log10(1/32768)+96`, which exceeded the default 5.0 dB threshold.
- **Root Cause:** Test threshold (5.0 dB) was too low for the test data's actual dB level.
- **Fix:** Changed test silence_db_threshold from 5.0 to 10.0 to correctly classify amplitude=1 as silent.
- **Status:** ✅ RESOLVED

### BUG-008 — Sprint 6: Orchestrator L5 recovery hangs tests
- **Sprint:** 6 (Recovery Engine)
- **Story:** 3.5 (L5 User Confirmation)
- **Severity:** Major
- **Description:** Sprint 2 orchestrator test `test_execute_step_l2_skip` hung indefinitely after Sprint 6 refactoring. The new recovery engine's L5 creates an `asyncio.Future` with 300s timeout waiting for user input that nobody resolves during unit tests.
- **Root Cause:** Orchestrator always provides `user_confirm_fn` which creates a blocking Future. Old tests expected rapid L1→L2 skip behavior, but new 6-level chain blocks at L5.
- **Fix:** Created `_FastRecoveryEngine` subclass in tests that overrides `_l5_user_confirm` to auto-skip for skippable steps.
- **Status:** ✅ RESOLVED

---

