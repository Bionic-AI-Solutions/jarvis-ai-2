# JARVIS AI - IMPLEMENTATION ROADMAP WITH RESEARCH FINDINGS
## Detailed Sprint Breakdown Incorporating Research Results

**Date:** February 23, 2026  
**Status:** Research-Validated Roadmap  
**Duration:** 12 Weeks (realistic)  

---

## PHASE 1: SETUP & PLANNING (Weeks 1-2) ✅ COMPLETE

### What's Already Done:
- ✅ Product brief (with enhanced desktop + voice UX focus)
- ✅ Complete architecture specification
- ✅ 13-agent system design
- ✅ Database schema (11 tables)
- ✅ Real-time streaming architecture
- ✅ Voice UI state machine (8 states)

### What Research Added:
- ✅ Latency budgets with realistic numbers
- ✅ Accuracy expectations (86-89% vs 94% spec)
- ✅ Failure recovery rates (50% first-try, 95% with backtrack)
- ✅ Risk mitigation strategies
- ✅ Timeline adjusted: 10 → 12-13 weeks

### Immediate Next Step:
**Proceed to Phase 2 with 5 architectural changes locked in**

---

## PHASE 2: FOUNDATION (Weeks 3-4)

### Sprint Goals:
1. FastAPI backend scaffold with async support
2. SQLite database + ORM (SQLAlchemy)
3. Orchestrator state machine (core routing logic)
4. Agent registry pattern (self-registration)
5. WebSocket server (real-time streaming)
6. CMA agent (context management)

### Research-Based Additions:
1. **Error classification enum** (enables proper backtrack routing)
2. **Metrics instrumentation** (track latency, success rates from day 1)
3. **Silence detector skeleton** (ready for Whisper integration)
4. **Lazy-model loader** (won't actually load models yet, just infrastructure)

### Timeline:
- FastAPI + SQLAlchemy: 1.5 days
- Orchestrator core: 2 days
- Agent registry: 0.5 days
- WebSocket setup: 1 day
- CMA agent: 1.5 days
- Testing + fixes: 2.5 days
- **Total: 9 days (~1.3 weeks)**

### Definition of Done:
```bash
$ pytest tests/agents/ -v
# Output: All agents respond to execute() method

$ python backend/main.py
# Output: FastAPI running on localhost:8000
# WebSocket listening at /ws
# SQLite database initialized: jarvis.db

# Manual test:
POST /api/test_agent/execute
{
  "input": "open notepad",
  "context": {}
}
# Response: Agent accepted input, queued for orchestrator
```

---

## PHASE 3: PLANNING AGENTS (Weeks 5-6)

### Sprint Goals:
1. RAG agent (intent → structured plan)
2. Clarification agent (user questioning)
3. Web Search agent (HTTP + caching)
4. SPA agent (semantic annotation)
5. SAA agent (action selection)

### Research-Based Adjustments:

**RAG Agent Timing:**
- Qwen2.5:3b inference: 8-12 seconds ✅ matches spec
- Web search integration: 1-3 seconds (add async calls)
- Total: 12-15 seconds (acceptable)

**SPA Agent Timing:**
- Semantic mapping: 5-8 seconds ✅ matches spec
- Parameter binding: 1-2 seconds
- Verification logic injection: <1 second

**Error Classification Integration:**
Each agent returns both result AND potential error codes:
```python
class AgentOutput:
    status: str  # 'success', 'deferred', 'failed'
    result: dict
    error_code: Optional[ErrorCode]  # For orchestrator to route backtrack
    confidence: float  # 0-1.0
```

### Timeline:
- RAG agent: 2 days
- Clarification agent: 1.5 days
- Web Search agent: 1 day
- SPA agent: 1.5 days
- SAA agent: 1.5 days
- Integration testing: 1.5 days
- Debug fixes: 1 day
- **Total: 10 days (~1.4 weeks)**

### Definition of Done:
```bash
# End-to-end test: User input → Plan
POST /api/orchestrate
{
  "user_intent": "open chrome and go to github",
  "context": {},
  "mode": "voice"
}

# Response (after 15-20 seconds):
{
  "status": "plan_ready",
  "plan": [
    {"n": 1, "action": "open_app", "app": "chrome", "tool": "powershell"},
    {"n": 2, "action": "wait_for_app", "duration_ms": 3000},
    {"n": 3, "action": "type_url", "url": "github.com", "tool": "keyboard"},
    {"n": 4, "action": "press_key", "key": "enter"}
  ],
  "total_steps": 4,
  "confidence": 0.88,
  "estimated_duration_seconds": 12
}
```

---

## PHASE 4: EXECUTION LAYER (Week 7)

### Sprint Goals:
1. EA agent (Execution Agent) with 12-step pipeline
2. OA agent (Observation/Monitoring)
3. Safety agent (guardrails)
4. moondream integration (screenshot analysis)
5. RobotJS binding (mouse/keyboard)
6. PowerShell wrapper (command execution)

### Research-Based Implementation:

**moondream Fuzzy Matching (CRITICAL):**
```python
def click_detected_element(screenshot_path, element_description):
    """
    Research finding: moondream accuracy 86-89%, pixel coords often off by 10-15px
    Solution: Use bounding box center, not exact pixel
    """
    
    result = moondream.detect(screenshot_path, element_description)
    
    # Get bounding box instead of exact pixel
    bbox = result['bounding_box']  # [x1, y1, x2, y2]
    
    # Calculate center
    center_x = (bbox[0] + bbox[2]) // 2
    center_y = (bbox[1] + bbox[3]) // 2
    
    # Add ±2px jitter to avoid pathologies
    actual_x = center_x + random.randint(-2, 2)
    actual_y = center_y + random.randint(-2, 2)
    
    # Click and wait for UI response
    pyautogui.click(actual_x, actual_y)
    time.sleep(0.3)
    
    # Verify with moondream
    screenshot_after = take_screenshot()
    verify_result = moondream.analyze(screenshot_after, f"Did {element_description} happen?")
    
    return {
        'clicked': True,
        'verified': verify_result['confidence'] > 0.7,
        'confidence': verify_result['confidence']
    }
```

**Screenshot Delay Tuning:**
Research shows 300ms minimum wait after click, but:
- PowerShell commands: wait 500ms-2s for result
- UI clicks: wait 300ms
- Form submissions: wait 1-2s
→ Implement dynamic wait based on action type

**moondream Timeout:**
- Spec says 3 seconds
- Research: 5 seconds safer for complex screenshots
- Change: timeout_ms: 5000 (with 3s as fast-path)

### Timeline:
- EA agent (core 12-step): 3 days
- moondream integration + fuzzy matching: 2 days
- RobotJS/PyAutoGUI binding: 1 day
- PowerShell wrapper: 1 day
- OA agent: 1 day
- Safety agent: 0.5 days
- Testing: 1.5 days
- **Total: 10 days (~1.4 weeks)**

### Definition of Done:
```bash
# Execute a simple workflow
POST /api/orchestrate/execute
{
  "plan": [...],  # from planning phase
  "context": {}
}

# Response (streaming via WebSocket):
WebSocket Events:
- step_started: {step: 1, action: "open_chrome"}
- step_progress: {step: 1, message: "Taking screenshot..."}
- step_progress: {step: 1, message: "Analyzing with moondream..."}
- step_completed: {step: 1, duration: 2.5, confidence: 0.94}
- step_started: {step: 2, action: "wait"}
- ... (more steps)
- execution_completed: {total_duration: 12.3, success: true}

# Failure case triggers backtrack:
WebSocket Events:
- step_started: {step: 3, action: "type_url"}
- step_progress: {message: "Click mismatch detected, confidence 0.62"}
- backtrack_initiated: {level: 2, reason: "low_confidence"}
- step_started: {step: 3, action: "type_url"}  # retry
- step_completed: {step: 3, duration: 1.8, confidence: 0.91}
```

---

## PHASE 5: REAL-TIME UI (Weeks 8-9)

### Sprint Goals:
1. React chat component
2. Voice UI (8 animated states)
3. Execution panel (real-time step tracking)
4. WebSocket client + reconnection logic
5. Electron window management
6. Audio waveform visualization

### Research-Based Guidance:

**WebSocket Latency Target:**
- Research: 80-150ms is achievable
- Success criteria: <200ms for most messages
- Implementation: Check with devtools Network tab

**Voice UI State Transitions:**
Research validated all 8 states are implementable with Canvas:
- Listening → Audio Detected: 0-2 seconds
- Audio Detected → Recognized: <1 second
- Recognized → Thinking: auto-advance
- Thinking → Speaking: when TTS ready
- Speaking → Complete: when audio ends

**Waveform Animation Sync:**
- Use Web Audio API `AnalyserNode`
- Sample at 10-30 fps
- Frequency bins to bar heights

### Timeline:
- React chat component: 1.5 days
- Voice UI animations: 2.5 days
- Execution panel: 1.5 days
- WebSocket client: 1 day
- Electron setup: 1 day
- Integration testing: 1.5 days
- **Total: 9 days (~1.3 weeks)**

### Definition of Done:
```bash
# Frontend loads
npm run dev  # Starts Electron dev server

# User interaction flow:
1. Click microphone icon → listening state (waveform breathing)
2. Say "open Chrome" → audio detected (waveform reacting to voice)
3. Speech finishes → recognized state (green checkmark flash)
4. Thinking state (pulsing orb + orbiting particles)
5. Execution panel shows: "Step 1/4: Opening Chrome"
6. Real-time: "Step 2/4: Taking screenshot"
7. Complete state (checkmark + confetti)
8. Chat shows: "Opened Chrome successfully"
9. TTS plays: "Opened Chrome successfully"

# All streaming via WebSocket in real-time
```

---

## PHASE 6: INTELLIGENCE LAYER (Week 10)

### Sprint Goals:
1. App Registry agent (Windows registry scan)
2. Workflow Learner agent (silent auto-save + matching)
3. 6-Level Backtracking system (full implementation + testing)
4. Workflow reuse optimization

### Research-Based Implementation:

**Workflow Learning Embeddings (CRITICAL):**
Query-time embedding costs 2-3 seconds:
```python
# OLD (slow):
def find_similar_workflows(user_intent):
    embedding = qwen_model.embed(user_intent)  # 2-3 seconds
    
    # Then search SQLite
    similar = db.query("...", embedding)  # Fast but slow setup

# NEW (fast):
def find_similar_workflows(user_intent):
    # Pre-computed embedding stored in DB
    embedding = db.cache.get(user_intent)  # ~10ms cache hit
    if not embedding:
        embedding = qwen_model.embed(user_intent)  # 2-3 seconds, then cache
    
    similar = db.query("...", embedding)  # Fast
    
# Saves: 2-3 seconds on workflow lookup
```

**Backtracking Test Coverage:**
Research shows backtracking success rates:
- Level 1 (longer timeout): 85-90% success
- Level 2 (alternative method): 80-85% success
- Level 3 (clarification): 90%+ (user provides info)
- Level 4 (exponential backoff): 70-75% success
- Level 5 (elevation): 95%+ (user confirms)
- Level 6 (manual): 100% (user handles)

Must test all 6 levels on real workflows (tedious but essential).

### Timeline:
- App Registry agent: 1 day
- Workflow Learner (silent save): 1 day
- Workflow Learner (semantic matching): 1.5 days
- 6-Level Backtracking testing: 2 days
- Integration: 0.5 days
- **Total: 6 days (~1 week)**

### Definition of Done:
```bash
# Workflow learning active
1. User says: "Send email to john@company.com with subject Q1 Report"
   → System executes, logs with embedding in execution_records

2. User says (30 min later): "Email john the quarterly report"
   → System finds previous execution (0.89 similarity)
   → Suggests: "Reuse previous workflow?" [1-click approval]

3. User clicks approval
   → System skips RAG/SPA/SAA (saves 20-30 seconds)
   → Goes directly to EA with cached params
   → Email sent in 5 seconds (instead of 45)

# Backtracking tested:
- L1 timeout retry: Confirmed 85-90% success
- L2 alt method: Confirmed 80-85% success
- L3 clarification: Confirmed user interaction works
- L4 exponential backoff: Confirmed network hangs recovery
- L5 elevation: Confirmed UAC dialog handling
- L6 manual: Confirmed error display + user options
```

---

## PHASE 7: SETUP & PACKAGING (Week 11)

### Sprint Goals:
1. NSIS installer script
2. Model download manager (lazy-load)
3. electron-builder configuration
4. Installer workflow (location selection, model download, app launch)
5. Registry integration (app icon, Start menu)

### Research-Based Changes:

**Lazy-Load Model Strategy:**
```
setup.exe (15MB)
├─ Install FastAPI runtime
├─ Install Electron app
├─ Install dependencies
└─ Config folder for models

First app run:
├─ Check: Ollama installed?
├─ Check: Models exist?
├─ If missing:
│  ├─ `ollama pull qwen2.5:3b` (~30 min, 4.2GB)
│  ├─ `ollama pull whisper-medium` (~8 min, 1.5GB)
│  ├─ `ollama pull moondream` (~10 min, 2.1GB)
│  └─ `pip install piper-tts` (~2 min, 0.5GB)
└─ App ready (50 min one-time wait)

Subsequent runs:
└─ Instant (~2 seconds)
```

### Timeline:
- NSIS installer: 1.5 days
- Model download manager: 1.5 days
- electron-builder config: 1 day
- Installer testing (3 Windows versions): 1.5 days
- Debugging: 1 day
- **Total: 6.5 days (~1 week)**

### Definition of Done:
```bash
# Generate .exe
npm run build

# Result: JARVIS_AI_Setup_4.0.exe (15MB)

# User flow:
1. Run setup.exe
2. Choose install location
3. Setup completes (5 minutes)
4. Launch app for first time
5. See: "Checking for models..."
6. Download progress: Qwen, Whisper, moondream (50 min total)
7. App ready, main window opens
8. User can start speaking commands
```

---

## PHASE 8: TESTING & RELEASE (Week 12)

### Sprint Goals:
1. E2E testing (10 core workflows)
2. Load testing (concurrent sessions)
3. Edge case testing (network failures, timeouts, crashes)
4. Documentation + user guide
5. Release checklist

### Core Workflows to Test:
1. "Open Chrome"
2. "Open Chrome and go to GitHub"
3. "Send email to [recipient]"
4. "Create a new document"
5. "Find a file by name"
6. "Set a reminder"
7. "Take a screenshot and copy to clipboard"
8. "Open VS Code and create new project"
9. "Schedule a meeting"
10. "Read text from clipboard"

### Research-Based Test Scenarios:
```
Each workflow tested across:
- Perfect conditions (clean speech, good network)
- Noisy conditions (office background, Zoom running)
- Slow conditions (network lag, CPU loaded)
- Failure scenarios (model timeout, click missed, app crash)
- Recovery scenarios (backtrack to level 2, 4, 6)

Success criteria:
- 80%+ of workflows succeed first-try
- 95%+ succeed within 3 retries (backtracking)
- No catastrophic failures (app crash, data loss)
- Error messages clear to user
```

### Timeline:
- Test plan creation: 1 day
- Workflow E2E tests: 2 days
- Load testing: 1 day
- Edge case testing: 1.5 days
- Documentation: 1.5 days
- Final fixes: 1.5 day
- **Total: 8 days (~1.1 weeks)**

### Definition of Done:
```bash
# All tests pass
pytest tests/e2e/ -v
# Output: 10 workflows ✓, no critical failures

# Load test passes
> 100 concurrent sessions, <500ms latency sustained

# Manual verification:
- [ ] Voice input works (test with accent, noise)
- [ ] GUI automation succeeds 80%+ first-try
- [ ] Backtracking recovers from failures
- [ ] WebSocket real-time updates smooth
- [ ] .exe installer works on Windows 10, 11, Server 2022
- [ ] Model download completes without error
- [ ] App persists across restarts
- [ ] Documentation complete + user guide clear

# Release ready
JARVIS_AI_Setup_4.0.exe ready for distribution
```

---

## CONTINGENCY WEEK (Week 13 - If Needed)

**Reserved for:**
- Moondream accuracy tuning (if <85% in testing)
- WebSocket latency optimization (if >250ms)
- Electron packaging issues (Windows-specific)
- Model download manager bugs
- Backtracking corner cases

**Exit Criteria:**
- If used: address top 2-3 issues, ship minimal MVP
- If not used: early release + team celebrates 🎉

---

## METRICS TO TRACK (From Week 3 Onward)

### Performance Metrics:
```
Track weekly:
- Median latency (target: 25-30s)
- P95 latency (target: <50s)
- First-try success rate (target: >70%)
- Post-backtrack success rate (target: >95%)
- WebSocket latency (target: <200ms)
- Model inference times per agent
```

### Quality Metrics:
```
Track weekly:
- moondream accuracy on UI detection
- Whisper transcription accuracy
- Backtracking effectiveness (% recovered)
- Error rate by category
- User satisfaction (if testing with users)
```

### Development Metrics:
```
Track weekly:
- Velocity per sprint (story points/week)
- Cycle time (days from story start to merge)
- Blocker resolution time (hours from reported to fixed)
- Test coverage (target: >80%)
```

---

## RISK MITIGATION TIMELINE

| Risk | Week to Mitigate | Action |
|------|-----------------|--------|
| moondream accuracy low | Week 5-6 | Prototype fuzzy matching early |
| Whisper silence detection fails | Week 3-4 | Test librosa + WebRTC early |
| .exe packaging bugs | Week 8-9 | Test electron-builder on target Windows versions |
| WebSocket latency spikes | Week 8 | Load test early, optimize if >250ms |
| Model download slow | Week 11 | Parallel downloads tested early |
| Backtracking logic fails | Week 10 | Test all 6 levels thoroughly |

---

## FINAL TIMELINE SUMMARY

```
Week 1-2:   ✅ Planning (DONE)
Week 3-4:   Foundation backend
Week 5-6:   Planning agents
Week 7:     Execution layer
Week 8-9:   Frontend + real-time
Week 10:    Intelligence + backtracking
Week 11:    Setup & packaging
Week 12:    E2E testing + release
Week 13:    Contingency (if needed)

Total: 12-13 weeks
```

**Start Date:** Next Monday  
**Projected Release:** End of Week 12 (likely mid-April 2026)

---

**This roadmap incorporates ALL research findings and is ready for SKAD Sprint Planning.**
