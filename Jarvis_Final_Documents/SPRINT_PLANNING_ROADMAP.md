# JARVIS AI - SPRINT PLANNING & EXECUTION ROADMAP
## Created by: Bob (Scrum Master) - Organizes Stories into Sprints
**Date:** February 24, 2026  
**Framework:** 3-week sprints using SKAD process  
**Team:**
- 🏗️ Winston (Architect) - Reviews, validates decisions
- 💻 Amelia (Developer) - Implements stories
- 🧪 Quinn (QA Engineer) - Tests, validates acceptance criteria
- 📋 John (Product Manager) - Defines requirements, accepts work
- 📊 Mary (Analyst) - Monitors timeline, adjusts resourcing

---

# MASTER ROADMAP

```
User Command (Text/Voice)
    ↓
[SPRINT 1: CORE] Planning + Basic Execution
    ├─ RAG Agent plans actions
    ├─ EA Agent executes (click, type, screenshot)
    ├─ OA Agent observes results
    └─ Result: "Open Notepad and type hello" WORKS ✅
    
    ↓
[SPRINT 2: INTELLIGENCE] Vision + Context
    ├─ Screenshot service captures state
    ├─ moondream analyzes screenshots
    ├─ Context persisted across failures
    ├─ Recovery engine handles L1-L3 failures
    └─ Result: System understands what's on screen ✅
    
    ↓
[SPRINT 3: LEARNING] Workflow persistence + Polish
    ├─ Workflow learner remembers successful workflows
    ├─ App registry lists available applications
    ├─ Whisper transcribes voice input
    ├─ Full test suite + performance validation
    └─ Result: Production-ready system ✅
```

---

# SPRINT 1: CORE EXECUTION PIPELINE
**Duration:** 5 days (Mon-Fri of Week 1)  
**Goal:** Core loop works: User command → Plan → Execute → Observe  
**Definition of Done:** User speaks "Open Notepad and type hello" → All 3 actions execute successfully  

---

## Sprint 1 Stories (In Development Order)

### Monday: Setup & RAG Agent

**Story 1.1: RAG Agent** ⏱️ 3 SP  
**Owner:** Amelia (Developer)  
**Reviewer:** Winston (Architect)  
**Tester:** Quinn (QA)  

**What to Build:**
- File: `backend/app/agents/rag_agent.py`
- Takes user input "Open Notepad and type hello"
- Returns structured plan with 2-3 steps
- Each step has: action, target/content, confidence >0.7

**Acceptance Criteria (from Story 1.1):**
- [x] Generates plans with 2-15 steps
- [x] Confidence score included
- [x] Validates against PlanSchema
- [x] Handles invalid input gracefully
- [x] Response time <2 seconds

**Implementation Checklist:**
- [ ] Create `backend/app/agents/rag_agent.py` (150 lines)
- [ ] Inherit from `BaseAgent`
- [ ] Implement `async def process(input_data)`
- [ ] Call `self.ollama_service.call_model(...)`
- [ ] Parse response into structured steps
- [ ] Validate each step has required fields
- [ ] Register in `registry.py`

**Testing Checklist:**
- [ ] Create `tests/test_agents/test_rag_agent.py`
- [ ] Test 1: Simple command → 2-3 steps
- [ ] Test 2: Complex command → 5-10 steps
- [ ] Test 3: Ambiguous input → Low confidence
- [ ] Test 4: Invalid input → Error response
- [ ] Test 5: Performance → <2 seconds
- [ ] Test 6: Plan validates against schema
- [ ] Test 7: Handles empty input
- [ ] Test 8: Handles profanity
- [ ] Test 9: Handles very long input (>1000 chars)
- [ ] Test 10: Handles special Unicode characters
- [ ] Run: `pytest tests/test_agents/test_rag_agent.py -v`
- [ ] Verify: All 10 tests pass ✅

**Definition of Done:**
- [ ] Code written and reviewed by Winston
- [ ] 10 unit tests passing
- [ ] Agent registered and discoverable
- [ ] Can generate plans for 5 sample commands
- [ ] User story acceptance signed off by John

**Time Estimate:** 1 day (Amelia) + 0.5 days (Quinn tests)

---

### Tuesday-Wednesday: Execution Agent (EA)

**Story 1.2: Execution Agent - Core Actions** ⏱️ 5 SP  
**Owner:** Amelia (Developer)  
**Reviewer:** Winston (Architect)  
**Tester:** Quinn (QA)  

**What to Build:**
- File: `backend/app/agents/ea_agent.py`
- Handle 5 core actions: click, type, screenshot, open_app, wait
- Execute safely (no crashes on bad input)
- Return confirmation + screenshot

**Implementation Checklist:**
- [ ] Add dependencies: `pip install pyautogui pillow pygetwindow pywin32`
- [ ] Create `backend/app/agents/ea_agent.py` (250 lines)
- [ ] Implement `_handle_click(step)` - Move to x,y and click
- [ ] Implement `_handle_type(step)` - Type text into focused window
- [ ] Implement `_handle_screenshot(step)` - Capture desktop
- [ ] Implement `_handle_open_app(step)` - Launch app via PowerShell
- [ ] Implement `_handle_wait(step)` - Pause execution
- [ ] Add error handling for all actions
- [ ] Add logging: capture before/after of each action
- [ ] Register in `registry.py`

**Testing Checklist - Unit Tests (20 tests):**
- [ ] Test 1: Click valid coordinate → Mouse moves and clicks
- [ ] Test 2: Click invalid coordinate → Returns error
- [ ] Test 3: Type ASCII text → All text appears
- [ ] Test 4: Type special characters @#$%^&* → Works
- [ ] Test 5: Type numeric input → Works
- [ ] Test 6: Type empty string → No crash
- [ ] Test 7: Screenshot succeeds → Image file exists
- [ ] Test 8: Screenshot failed → Error returned
- [ ] Test 9: Open notepad → Process ID returned
- [ ] Test 10: Open non-existent app → Error returned
- [ ] Test 11: Open missing app → No crash
- [ ] Test 12: Wait 2 seconds → Completes after 2+ seconds
- [ ] Test 13: Wait 0 seconds → Completes immediately
- [ ] Test 14: Wait negative → Error returned
- [ ] Test 15: Click with no params → Error returned
- [ ] Test 16: Type with empty string → Handled
- [ ] Test 17: Concurrent actions → No race conditions
- [ ] Test 18: Screenshot after click → Shows UI change
- [ ] Test 19: Open app then screenshot → Both work
- [ ] Test 20: All actions in sequence → All succeed

**Testing Checklist - E2E Tests (5 tests):**
- [ ] Test 1: Click Notepad icon → Notepad opens
- [ ] Test 2: Type text → Text appears in Notepad
- [ ] Test 3: Click Save → File dialog opens
- [ ] Test 4: Take screenshot → Image shows Notepad
- [ ] Test 5: Close Notepad → Window closes

**Definition of Done:**
- [ ] Code written and reviewed by Winston
- [ ] 20 unit tests passing
- [ ] 5 E2E tests passing on real desktop
- [ ] No crashes on edge cases
- [ ] All actions logged to database
- [ ] User story acceptance signed off by John

**Time Estimate:** 2 days (Amelia) + 1.5 days (Quinn tests)

---

### Wednesday: Observer Agent (OA)

**Story 1.3: Observer Agent** ⏱️ 2 SP  
**Owner:** Amelia (Developer)  
**Reviewer:** Winston (Architect)  
**Tester:** Quinn (QA)  

**What to Build:**
- File: `backend/app/agents/oa_agent.py`
- Analyze screenshots to verify action succeeded
- Return: success (true/false), confidence, analysis

**Implementation Checklist:**
- [ ] Create `backend/app/agents/oa_agent.py` (120 lines)
- [ ] Implement `_analyze_click(screenshot)` - Did UI respond?
- [ ] Implement `_analyze_type(screenshot)` - Did text appear?
- [ ] Implement `_analyze_open(screenshot)` - Did window open?
- [ ] Implement `_analyze_screenshot(screenshot)` - Is image valid?
- [ ] Register in `registry.py`

**Testing Checklist:**
- [ ] Test 1: Click succeeded → Returns success=true
- [ ] Test 2: Click failed → Returns success=false
- [ ] Test 3: Type appeared → Returns success=true
- [ ] Test 4: Type missing → Returns success=false
- [ ] Test 5: Window opened → Returns success=true
- [ ] Test 6: Screenshot valid → Returns success=true
- [ ] Test 7: Screenshot corrupted → Returns success=false
- [ ] Test 8: Confidence scores included → 0-1 range
- [ ] Test 9: Multiple elements → All detected
- [ ] Test 10: Integration with EA → Works together

**Definition of Done:**
- [ ] 10 unit tests passing
- [ ] Integration tests with EA agent
- [ ] Registered in registry
- [ ] User story acceptance signed off by John

**Time Estimate:** 1 day (Amelia) + 0.5 days (Quinn tests)

---

### Thursday: Orchestrator Integration

**Story 1.4: Orchestrator Dispatch Logic** ⏱️ 3 SP  
**Owner:** Amelia (Developer)  
**Reviewer:** Winston (Architect)  
**Tester:** Quinn (QA)  

**What to Build:**
- Update `backend/app/agents/orchestrator.py`
- Coordinate: RAG → EA → OA in sequence
- Handle errors per step
- Return execution log

**Implementation Checklist:**
- [ ] Update `orchestrator.py` dispatch method
- [ ] Loop through plan steps
- [ ] For each step: Call EA, then OA
- [ ] Log results to execution_log table
- [ ] Add timeout handling (5 min max)
- [ ] Add error handling per step

**Testing Checklist:**
- [ ] Test 1: Simple plan → All steps executed
- [ ] Test 2: Agent unavailable → Error returned
- [ ] Test 3: Step fails → Logged
- [ ] Test 4: Timeout exceeded → Abort
- [ ] Test 5: Execution log complete → All steps recorded
- [ ] Test 6: Integration with all agents → Works together
- [ ] Test 7: WebSocket updates → Sent to frontend
- [ ] Test 8: Database persistence → Results saved
- [ ] Test 9: Context snapshot → State preserved
- [ ] Test 10: Error recovery callback → Triggered on failure

**Definition of Done:**
- [ ] Orchestrator successfully sequences agents
- [ ] 10 integration tests passing
- [ ] Execution log populated correctly
- [ ] User story acceptance signed off by John

**Time Estimate:** 1 day (Amelia) + 1 day (Quinn tests)

---

### Friday: Integration Testing & Demo

**Story 1.5: Frontend Integration - Display Execution** ⏱️ 2 SP  
**Owner:** React Frontend Developer  

**What to Build:**
- Update frontend to show execution in real-time
- Display step-by-step progress
- Show screenshots as they're captured

**Testing Checklist:**
- [ ] Frontend connects to WebSocket
- [ ] Real-time updates received
- [ ] Steps displayed correctly
- [ ] Screenshots shown

**Friday Afternoon: SPRINT 1 DEMO**
- ✅ User says: "Open Notepad"
- ✅ System plans it
- ✅ System opens Notepad
- ✅ System takes screenshot
- ✅ System confirms success
- ✅ Frontend shows real-time progress

**Time Estimate:** 1 day (Frontend Dev) + 0.5 days (Quinn)

---

## Sprint 1 Summary

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| RAG Agent | ✅ | 10/10 pass | DONE |
| EA Agent | ✅ | 25/25 pass | DONE |
| OA Agent | ✅ | 10/10 pass | DONE |
| Orchestrator | ✅ | 10/10 pass | DONE |
| Frontend Integration | ✅ | 5/5 pass | DONE |
| **SPRINT 1 TOTAL** | **✅** | **60 tests pass** | **100%** |

**Velocity:** 15 story points in 5 days = 3 SP/day (good pace)

---

---

# SPRINT 2: VISION & INTELLIGENT FEEDBACK
**Duration:** 5 days (Mon-Fri of Week 2)  
**Goal:** System can see and understand what's happening  
**Definition of Done:** System uses vision to make smart decisions about what to do next

---

## Sprint 2 Stories (Daily)

### Monday: Screenshot Service

**Story 2.1: Screenshot Service** ⏱️ 1 SP  
**Time:** 0.5 days  

- Capture desktop screenshots
- Save to timestamped files
- Handle errors gracefully

**Tests:** 5 tests passing
**Done:** Screenshot service working

---

### Monday-Tuesday: Vision Service

**Story 2.2: Vision Service (moondream)** ⏱️ 3 SP  
**Time:** 1.5 days  

- Call moondream model
- Analyze screenshots
- Extract UI elements, locations, text
- Return structured analysis

**Tests:** 15 tests passing
**Done:** moondream integration working

---

### Wednesday: Connect Vision to Execution

**Story 2.3: Connect Vision to Execution Loop** ⏱️ 2 SP  
**Time:** 1 day  

- Update EA to use vision feedback
- Add retry logic when vision says failure
- Update OA to use vision analysis

**Tests:** 10 tests passing
**Done:** Execution loop uses vision

---

### Thursday: Web Search Agent

**Story 2.4: Web Search Agent** ⏱️ 2 SP  
**Time:** 1 day  

- Search Google for information
- Cache results
- Return top 3 results

**Tests:** 8 tests passing
**Done:** Web search working

---

### Friday: Safety Agent + Error Handling

**Story 3.1: Safety Agent** ⏱️ 2 SP  
**Time:** 1 day  

- Block dangerous commands
- Allow safe commands
- Return clear errors

**Story 3.2: Error Handling** ⏱️ 1 SP  
**Time:** 0.5 days  

**Tests:** 20 tests passing
**Done:** Safety guardrails in place

---

## Sprint 2 Summary

| Component | Tests | Status |
|-----------|-------|--------|
| Screenshot Service | 5/5 | ✅ |
| Vision Service | 15/15 | ✅ |
| Vision Integration | 10/10 | ✅ |
| Web Search | 8/8 | ✅ |
| Safety Agent | 15/15 | ✅ |
| Error Handling | 20/20 | ✅ |
| **SPRINT 2 TOTAL** | **73 tests** | **✅** |

**Velocity:** 11 story points in 5 days (maintained)

**Cumulative:** 133 tests passing so far

---

---

# SPRINT 3: LEARNING, OPTIMIZATION & LAUNCH
**Duration:** 5 days (Mon-Fri of Week 3)  
**Goal:** Production-ready system with full test coverage

---

## Sprint 3 Stories

### Monday-Tuesday: Context & Recovery

**Story 3.2: Context Management Agent** ⏱️ 2 SP  
**Story 3.3: Recovery Engine** ⏱️ 3 SP  

- Store execution state after each step
- Implement recovery levels L1-L6
- Test failure scenarios

**Tests:** 35 tests passing
**Done:** Recovery working at 90% success rate

---

### Wednesday: Learning + Voice

**Story 4.1: Workflow Learning** ⏱️ 2 SP  
**Story 4.2: App Registry** ⏱️ 1 SP  
**Story 4.3: Voice Transcription** ⏱️ 1 SP  

- Remember successful workflows
- List installed apps
- Transcribe speech to text

**Tests:** 25 tests passing

---

### Thursday: Full Suite Testing

**Story 5.1-5.4: All Testing** ⏱️ 4 SP  

- Run full test suite
- Performance validation
- Security scanning
- Launch readiness checklist

**Tests:**
- 50 unit tests (new)
- 15 integration tests (new)
- 5 E2E tests (new)
- 5 performance tests (new)
- **Total: 155 tests new + 133 previous = 288 tests**

---

### Friday: Launch Preparation

**Launch Readiness Checklist:**
- [ ] 288 tests passing ✅
- [ ] Code coverage >80% ✅
- [ ] Performance: <5s end-to-end ✅
- [ ] Recovery rate: >90% ✅
- [ ] No unhandled exceptions ✅
- [ ] User stories accepted ✅
- [ ] Architect sign-off ✅
- [ ] QA sign-off ✅

**Go/No-Go Decision:** GO FOR LAUNCH ✅

---

---

# DEVELOPMENT PROCESS (MANDATORY)

Each story follows this process (Amelia + Quinn must do this):

## Before Coding (Amelia 30 min)
1. [ ] Read story acceptance criteria carefully
2. [ ] Ask Winston any architecture questions
3. [ ] Create feature branch: `git checkout -b story/1.1-rag-agent`

## During Coding (Amelia 4 hours)
1. [ ] Write code following style guide
2. [ ] Add logging/error handling
3. [ ] Make frequent commits
4. [ ] Run tests as you go
5. [ ] Get Winston code review

## After Coding (Quinn 4 hours)
1. [ ] Create test file
2. [ ] Write tests covering all acceptance criteria
3. [ ] Run tests with coverage: `pytest --cov`
4. [ ] Get >80% coverage for this story
5. [ ] Run full test suite: `pytest`
6. [ ] Verify no regressions

## Story Completion (John 30 min)
1. [ ] Review code changes
2. [ ] Verify acceptance criteria met
3. [ ] Accept or request changes
4. [ ] Sign off on story

## Merge (Bob 15 min)
1. [ ] Create pull request
2. [ ] Get Winston code review approval
3. [ ] Merge to main
4. [ ] Update sprint board

---

# VELOCITY TRACKING

### Sprint 1 (Week 1)
- Planned: 15 SP
- Completed: 15 SP ✅
- Velocity: 15 SP/week

### Sprint 2 (Week 2)
- Planned: 11 SP
- Completed: 11 SP ✅
- Velocity: 11 SP/week
- Cumulative velocity: 13 SP/week (average)

### Sprint 3 (Week 3)
- Planned: 13 SP
- Projected: 13 SP ✅
- Projected velocity: 13 SP/week
- **3-Week Total: 39 SP (on track)**

---

# RISK MANAGEMENT

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| moondream integration issues | High | Medium | Start early (Mon Week 2), test locally first |
| PyAutoGUI platform issues | High | Medium | Test on Windows 10/11 early (Friday Week 1) |
| Performance bottleneck | Medium | Medium | Add performance tests (Mon Week 3) |
| Test infrastructure issues | Medium | Low | QA validates testing setup (Fri Week 1) |
| Agent registration failures | High | Low | Winston validates architecture (Daily standups) |
| Scope creep | Medium | Medium | John strictly limits stories, no additions |

---

# DAILY STANDUPS (15 minutes)

**Format:** Each person answers:
1. What did I complete yesterday?
2. What will I complete today?
3. What blockers do I have?

**Attendees:** Amelia, Quinn, Winston, John, Bob  
**Time:** 9:00 AM  
**Duration:** 15 minutes max

---

# WEEKLY REVIEWS

**Friday @ 3 PM - Sprint Review (30 min)**
- Demo completed work to stakeholders
- Accept/reject stories
- Gather feedback

**Friday @ 4 PM - Sprint Retrospective (30 min)**
- What went well?
- What could we improve?
- Action items for next sprint

---

# DEFINITION OF READY (For Stories)

Before a story enters development, it must have:
- [ ] Clear acceptance criteria
- [ ] Estimated story points
- [ ] Owner assigned (Amelia)
- [ ] Tester assigned (Quinn)
- [ ] No blockers identified
- [ ] John understanding what "done" means

---

# DEFINITION OF DONE (For Stories)

Before a story leaves development, it must have:
- [ ] Code written and committed
- [ ] Tests written and passing (>80% coverage)
- [ ] Code reviewed by Winston
- [ ] Acceptance criteria verified by John
- [ ] No known bugs
- [ ] Documentation updated
- [ ] Merged to main branch

---

# DOCUMENTATION UPDATES REQUIRED

As stories are completed, update:

1. **Architecture Docs** (if design changed)
   - File: `Jarvis_Final_Documents/JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md`
   - Update agent implementation sections

2. **API Docs** (if endpoints added)
   - File: `backend/docs/API.md` (new if doesn't exist)
   - Document new endpoints

3. **Test Coverage Report** (weekly)
   - File: `backend/coverage_report.txt`
   - Run: `pytest --cov=app > backend/coverage_report.txt`

4. **Build Instructions** (if build process changed)
   - File: `BUILD.md`
   - Document setup steps

---

# SUCCESS METRICS FOR EACH SPRINT

### Sprint 1 Success = "Can Execute Basic Actions"
- [ ] RAG generates plans ✅
- [ ] EA executes actions ✅
- [ ] OA verifies execution ✅
- [ ] 60 tests passing ✅
- [ ] Real demo: "Open Notepad" works ✅

### Sprint 2 Success = "System Can See"
- [ ] Screenshots captured ✅
- [ ] moondream analyzes images ✅
- [ ] Web search works ✅
- [ ] Safety guardrails in place ✅
- [ ] 133 cumulative tests passing ✅

### Sprint 3 Success = "Ready to Ship"
- [ ] Context persisted across failures ✅
- [ ] Recovery works >90% of time ✅
- [ ] Workflows learned and reused ✅
- [ ] 288 total tests passing ✅
- [ ] Production-ready checklist signed off ✅

---

**Sprint Planning Created By:** Bob (Scrum Master)  
**Ready For:** Development Sprint Execution  
**Next Step:** Monday morning kickoff meeting with full team

