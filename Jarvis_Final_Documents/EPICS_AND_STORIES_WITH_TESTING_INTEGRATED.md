# EPICS & STORIES: JARVIS AI DEVELOPMENT WITH INTEGRATED TESTING
## Complete 25-Story Sprint Plan (3-4 weeks, 3 sprints)

**Created By:** John (Product Manager) + Bob (Scrum Master) + Quinn (QA Engineer)  
**Date:** February 24, 2026  
**Methodology:** SKAD (Stories → Kick-off → Assignment → Develop)  
**Testing Strategy:** 150+ unit tests + 40+ integration tests + 25+ E2E tests = 215+ total  
**Coverage Target:** >80% backend code coverage, zero regressions

---

# 📋 EPIC STRUCTURE

```
EPIC 1: Planning Pipeline (5 agents generate execution steps)
├─ Story 1.1: RAG Agent (understand intent → structured plan)
├─ Story 1.2: Clarification Agent (ask clarifying questions)  
├─ Story 1.3: Web Search Agent (find how-to information)
├─ Story 1.4: SPA Agent (add business context)
└─ Story 1.5: SAA Agent (select specific actions)

EPIC 2: Execution Pipeline (real-time feedback loop)
├─ Story 2.1: Execution Agent - Click/Type/Open (EA primitives)
├─ Story 2.2: Screenshot Service + moondream (vision feedback)
├─ Story 2.3: Observer Agent (validate step success)
├─ Story 2.4: Orchestra Integration (agent sequencing)
└─ Story 2.5: WebSocket Real-Time (stream execution to frontend)

EPIC 3: Support & Recovery (safety, recovery, learning)
├─ Story 3.1: Safety Agent (block dangerous commands)
├─ Story 3.2: Recovery Engine (6-level failure backtracking)
├─ Story 3.3: Context Manager (CMA - persistence across failures)
├─ Story 3.4: Workflow Learner (remember & reuse workflows)
├─ Story 3.5: App Registry (list installed applications)

EPIC 4: Infrastructure & Services (backend foundation)
├─ Story 4.1: Logging Service (complete structlog setup)
├─ Story 4.2: Voice Service (Whisper transcription)
├─ Story 4.3: Database Service (async SQLAlchemy queries)
├─ Story 4.4: Error Handling (consistent error codes)
└─ Story 4.5: Configuration Management (12-factor app)

EPIC 5: End-to-End & Production (complex workflows, performance)
├─ Story 5.1: Complex Workflow Test Suite (5 real scenarios)
├─ Story 5.2: Performance Optimization (<5s end-to-end)
├─ Story 5.3: Chat Session Management (isolation, history)
├─ Story 5.4: Workflow Persistence & Replay (save, recognize, replay)
└─ Story 5.5: Production Readiness (security, monitoring, deployment)
```

---

# 🎯 STORY TEMPLATE

Each story follows this format:

```
### Story X.Y: [Title]
**Epic:** X - [Epic Name]  
**Points:** N  
**Owner:** [Amelia=Dev, Quinn=QA, Winston=Architecture]  
**Sprint:** 1/2/3  
**Duration:** [Days]

**Description:**  
[What this story does and why it matters]

**Acceptance Criteria:**  
- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (testable)  
- [ ] Criterion 3 (testable)

**Testing:**
📊 Unit Tests: N (test [components])
📊 Integration Tests: N (test [interactions])
📊 E2E Tests: N (test [real scenarios])

**Backend Coverage:**
- Module: [module_name] (% of code covered)
- Tables: [table_names]
- Services: [service_names]

**Dependencies:**
- Requires Story X.Y (for prerequisites)

**Risks:**
- Risk 1: Mitigation
```

---

# EPIC 1: PLANNING PIPELINE
## Stories 1.1 - 1.5 (Generate execution steps from user intent)

---

### Story 1.1: RAG Agent Implementation
**Epic:** 1 - Planning Pipeline  
**Points:** 5  
**Owner:** Amelia (Development)  
**Sprint:** 1  
**Duration:** 2 days (Mon-Tue Week 1)

**Description:**  
Implement the RAG (Retrieval-Augmented Generation) Agent. This agent takes user input ("Open Chrome and go to Gmail"), retrieves relevant context from knowledge base, and generates a structured execution plan with 1-8 steps. This is the first critical agent in the planning pipeline.

**Acceptance Criteria:**
- [ ] RAG agent class inherits from `BaseAgent`
- [ ] `process()` method accepts user input and returns structured plan
- [ ] Plan format: `{ "steps": [...], "confidence": 0.0-1.0, "reasoning": "..." }`
- [ ] Generates 1-8 steps for common requests
- [ ] Confidence score based on input clarity (0.95+ for clear, 0.7+ for complex)
- [ ] Handles ambiguous input (suggests clarification)
- [ ] All calls to LLM are logged (ollama_service integration)
- [ ] Empty input returns error (no crash)
- [ ] Unicode input handled correctly (emoji, special chars)

**Testing:**

📊 **Unit Tests (30 tests):**
- `test_rag_agent_init.py` (5 tests)
  - [x] Agent initializes with LLM service
  - [x] Agent registers in registry
  - [x] Invalid config raises ConfigError
  - [x] Context is empty on init
  - [x] Async methods properly defined
  
- `test_rag_agent_simple_requests.py` (8 tests)
  - [x] "Open Chrome" → 1 step (confidence 0.99)
  - [x] "Draft email" → 3-4 steps (confidence 0.95)
  - [x] "Check Gmail" → 2 steps (confidence 0.98)
  - [x] "Open random website" → 2 steps (confidence 0.90)
  - [x] "Turn off computer" → 1 step (confidence 0.99)
  - [x] "Print document" → 3 steps (confidence 0.92)
  - [x] "Take screenshot" → 1 step (confidence 0.99)
  - [x] "Wait 5 seconds" → 1 step (confidence 0.99)

- `test_rag_agent_complex_requests.py` (8 tests)
  - [x] Complex: "Draft email saying I'm on vacation and rescheduling meeting"
  - [x] Complex: "Open 3 websites and take screenshots of each"
  - [x] Complex: "Fill out form with name, email, phone, submit"
  - [x] Complex: "Search Gmail for important emails from last month"
  - [x] Complex: "Download and organize files from Downloads folder"
  - [x] Complex: "Create new folder, move files, backup to cloud"
  - [x] Complex: "Track package and send update email" (requires search)
  - [x] Complex: "Multi-app workflow: Calendar → Email → Slack notification"

- `test_rag_agent_error_handling.py` (7 tests)
  - [x] Empty string returns error (confidence 0.0)
  - [x] Malicious input: "rm -rf /" → blocked or indicated
  - [x] Very long input (>10K chars) handled
  - [x] Special characters: emoji, Unicode, symbols
  - [x] Duplicate requests use cache (performance)
  - [x] LLM timeout (5s) returns cached or error
  - [x] Invalid JSON response from LLM → fallback plan

- `test_rag_agent_llm_integration.py` (2 tests)
  - [x] Calls ollama_service.generate_plan() correctly
  - [x] Prompt includes enough context (user_id, session_id, previous_context)

📊 **Integration Tests (8 tests):**
- `test_rag_with_database.py` (4 tests)
  - [x] Plan saved to database (plans table)
  - [x] Plan retrieval by session_id works
  - [x] Plan history preserved (multiple requests same session)
  - [x] Foreign key integrity (session_id exists in chat_sessions)

- `test_rag_with_logging.py` (2 tests)
  - [x] Plan generation logged to execution_logs table
  - [x] LLM call logged with prompt, response, latency

- `test_rag_with_context_manager.py` (2 tests)
  - [x] RAG can read previous context (context_manager)
  - [x] RAG updates context with new plan

📊 **E2E Tests (3 tests):**
- `test_rag_agent_e2e_scenarios.py`
  - [x] Scenario 1: User says "Open Chrome" → receives valid 1-step plan
  - [x] Scenario 2: User says "Draft an email to john@example.com saying hello" → receives valid 4-step plan
  - [x] Scenario 3: Plan includes correct action types (open_app, click, type, screenshot, wait)

**Backend Coverage:**
- Module: `app/agents/rag_agent.py` (~150 lines, target 90%+)
- Module: `app/agents/protocol.py` (BaseAgent interface, 20 lines, 100%)
- Module: `app/services/ollama_service.py` (LLM calling, existing ~50 lines, verify working)
- Module: `app/agents/registry.py` (registration, ~10 lines, 100%)
- Tables: 
  - `plans` (schema: id, session_id, user_input, steps_json, confidence, created_at)
  - `chat_sessions` (session_id linkage)
  - `execution_logs` (logging plan generation step)
- Services: ollama_service (existing), logging_service (existing)

**Dependencies:**
- BaseAgent protocol (exists)
- ollama_service working (exists, tested separately)
- plans table schema created
- registry.register() function working

**Risks:**
- **Risk 1:** LLM latency too high (5s+)  
  Mitigation: Cache plans for duplicate requests, use local Ollama
- **Risk 2:** Step generation too verbose (10+ steps)  
  Mitigation: Prompt engineering to constrain steps to 1-8 range
- **Risk 3:** Confidence score not calibrated  
  Mitigation: Tuning via test scenarios, compare to human judgement

**Story Point Justification:** 5 SP = 2 days
- 1 day: Write 30 unit tests (TDD approach)
- 0.5 day: Implement RAG agent to pass tests
- 0.5 day: Fix bugs, improve confidence scoring
- 1 day: Integration testing + database + logging

---

### Story 1.2: Clarification Agent Implementation
**Epic:** 1 - Planning Pipeline  
**Points:** 3  
**Owner:** Amelia (Development)  
**Sprint:** 1  
**Duration:** 1 day (Wed Week 1)

**Description:**  
When RAG agent detects ambiguous input (confidence <0.75), Clarification Agent asks targeted questions to disambiguate. Example: User says "Send message" → Agent asks "To whom? Via Email, Slack, or Text?" This improves plan accuracy.

**Acceptance Criteria:**
- [ ] Accepts input with low confidence from RAG agent
- [ ] Generates 1-3 clarifying questions
- [ ] Questions are specific and answerable
- [ ] Returns to RAG with enhanced context when user answers
- [ ] Timeout (30s) returns best-guess plan from RAG
- [ ] Questions logged and tracked in database

**Testing:**

📊 **Unit Tests (15 tests):**
- `test_clarification_agent.py`
  - [x] Detects ambiguity (confidence <0.75)
  - [x] Generates 1-3 questions
  - [x] Different ambiguities produce different questions
  - [x] Handles timeout gracefully
  - [x] Caches clarifications (same user, same ambiguity)
  - [x] Questions database insertable
  - [x] Response parsing (user answers questions)
  - [x] No questions for high-confidence input (skip CA)
  - [x] No infinite loop (max 2 clarification rounds)
  - [x] Edge cases: empty results, malformed response
  - [x] Unicode in questions/answers
  - [x] Very long question/answer handling
  - [x] Context preservation across clarification
  - [x] User abandonment (no response) returns timeout
  - [x] Statistics: which questions asked most often

📊 **Integration Tests (5 tests):**
- `test_clarification_with_rag.py` (2 tests)
  - [x] RAG confidence <0.75 triggers CA
  - [x] CA response feeds back to RAG for refined plan

- `test_clarification_with_database.py` (2 tests)
  - [x] Questions saved to database
  - [x] Answers linked to questions via foreign key

- `test_clarification_with_logging.py` (1 test)
  - [x] Clarification flow logged

📊 **E2E Tests (1 test):**
- `test_clarification_e2e.py`
  - [x] Ambiguous request → questions asked → user responds → refined plan generated

**Backend Coverage:**
- Module: `app/agents/clarification_agent.py` (~100 lines, target 85%+)
- Tables: `clarification_questions`, `clarification_responses`
- Services: logging_service

**Dependencies:**
- Story 1.1 (RAG agent working, returns confidence scores)

**Risks:**
- **Risk 1:** Questions not helpful (user confused)  
  Mitigation: A/B test different question phrasings with beta users

---

### Story 1.3: Web Search Agent Implementation
**Epic:** 1 - Planning Pipeline  
**Points:** 3  
**Owner:** Amelia (Development)  
**Sprint:** 1  
**Duration:** 1 day (Thu Week 1)

**Description:**  
When user needs external information ("What's the weather?" or "Find cheapest flights to NYC"), Web Search Agent retrieves relevant information and incorporates it into the plan. Uses external API (BingSearch or similar) or local web scraping.

**Acceptance Criteria:**
- [ ] Detects requests requiring external info (keywords: "find", "search", "what's", "how much")
- [ ] Performs web search safely
- [ ] Results formatted and cached
- [ ] Results integrated into execution plan
- [ ] Search failures graceful (returns "information not available")
- [ ] Rate limiting respected (max 5 searches/minute)

**Testing:**

📊 **Unit Tests (15 tests):**
- Detect search-requiring requests (6 tests)
- Format search results (4 tests)
- Cache search results (3 tests)
- Handle search failures (2 tests)

📊 **Integration Tests (4 tests):**
- Web Search → RAG integration
- Search results → plan integration
- Database storage of searches
- Logging of search activity

📊 **E2E Tests (1 test):**
- Real scenario: "Find weather for New York" → search → integrated into plan

**Backend Coverage:**
- Module: `app/agents/web_search_agent.py` (~150 lines)
- Tables: `web_searches`, `search_results`
- External Service: Web API (mocked in tests, real in integration)

**Dependencies:**
- Story 1.1 (RAG agent)

---

### Story 1.4: SPA (Semantic Plan Annotator) Agent Implementation
**Epic:** 1 - Planning Pipeline  
**Points:** 3  
**Owner:** Amelia (Development)  
**Sprint:** 1  
**Duration:** 1 day (Fri Week 1)

**Description:**  
Takes the execution plan from RAG/Clarification/WebSearch and annotates each step with semantic metadata: priority, timeout, retry_count, error_recovery_strategy. This enriches the plan for safer execution.

**Acceptance Criteria:**
- [ ] Adds priority to each step (critical, high, medium, low)
- [ ] Adds timeout (default 5s, adjustable per action type)
- [ ] Adds retry_count (0-3, default 1)
- [ ] Adds error strategy (skip, abort, retry, ask_user)
- [ ] Marks steps that require vision feedback
- [ ] Marks steps that could collide with other workflows
- [ ] Annotated plan usable by other agents

**Testing:**

📊 **Unit Tests (18 tests):**
- Add priority annotations (6 tests)
- Add timeout annotations (6 tests)
- Add retry/error strategy (6 tests)

📊 **Integration Tests (3 tests):**
- RAG plan → SPA annotations
- Annotations → EA agent
- Database storage

📊 **E2E Tests (1 test):**
- Full plan: RAG → SPA → annotated plan with all metadata

**Backend Coverage:**
- Module: `app/agents/spa_agent.py` (~120 lines)

**Dependencies:**
- Story 1.1 (RAG agent produces plans)

---

### Story 1.5: SAA (System-Action-Agent) Agent Implementation
**Epic:** 1 - Planning Pipeline  
**Points:** 3  
**Owner:** Amelia (Development)  
**Sprint:** 1  
**Duration:** 1 day (Fri Week 1)

**Description:**  
Final planning agent. Takes the annotated plan and selects specific action executables from the system (which version of Chrome? Firefox? Safari?). Checks available applications via App Registry and selects best match.

**Acceptance Criteria:**
- [ ] Queries App Registry for available apps
- [ ] Selects best match for generic actions (e.g., "open_browser" → Chrome if available, else Firefox)
- [ ] Handles missing applications gracefully
- [ ] Adds executable paths to plan steps
- [ ] Validates action availability before returning

**Testing:**

📊 **Unit Tests (12 tests):**
- Select Chrome vs Firefox (4 tests)
- Handle missing apps (4 tests)
- Add executable paths (4 tests)

📊 **Integration Tests (4 tests):**
- SAA → App Registry
- SAA → database
- SAA → logging

📊 **E2E Tests (1 test):**
- Full workflow: RAG → Clarification → WebSearch → SPA → SAA → final executable plan

**Backend Coverage:**
- Module: `app/agents/saa_agent.py` (~100 lines)
- Module: `app/agents/app_registry.py` (~80 lines)
- Tables: `available_apps`

**Dependencies:**
- Story 1.1-1.4

---

## **EPIC 1 SUMMARY**
- **Total Points:** 17 SP
- **Duration:** 5 days (Mon-Fri Week 1)
- **Stories:** 5 (RAG, Clarification, WebSearch, SPA, SAA)
- **Tests:** 30+15+15+18+12 = 90 unit tests
- **Tests:** 8+5+4+3+4 = 24 integration tests
- **Tests:** 3+1+1+1+1 = 7 E2E tests
- **Total Tests:** 121 tests
- **Backend Coverage:** All 5 planning agents complete (~650 lines total), >85% coverage

---

# EPIC 2: EXECUTION PIPELINE
## Stories 2.1 - 2.5 (Execute plans with real-time feedback)

---

### Story 2.1: Execution Agent - Primitives Implementation
**Epic:** 2 - Execution Pipeline  
**Points:** 5  
**Owner:** Amelia (Development)  
**Sprint:** 2 (Mon-Tue)  
**Duration:** 2 days

**Description:**  
Implement the Execution Agent (EA) with core primitives: click, type, open_app, wait, screenshot, keyboard_shortcut. These are the atomic building blocks that all workflows are composed of. This is a Windows-specific implementation using pyautogui + subprocess.

**Acceptance Criteria:**
- [ ] `click(x, y)` - Left-click at coordinates
- [ ] `type(text)` - Type text with special character support
- [ ] `open_app(app_path)` - Launch an application
- [ ] `wait(seconds)` - Pause execution
- [ ] `screenshot()` - Capture screen to file
- [ ] `keyboard_shortcut(keys)` - Ctrl+C, Alt+Tab, etc.
- [ ] All actions logged with timestamp, input, result
- [ ] All actions return success/failure status
- [ ] All actions handle errors gracefully (no crash)
- [ ] Implements timeout per action

**Testing:**

📊 **Unit Tests (35 tests):**
- `test_ea_primitives_click.py` (8 tests)
  - [x] Click at valid coordinates
  - [x] Click at invalid coordinates (out of bounds)
  - [x] Click rapidly (double-click)
  - [x] Click returns success status
  - [x] Click logged to database
  - [x] Click timeout handling
  - [x] Click with delay
  - [x] Click on non-existent window

- `test_ea_primitives_type.py` (8 tests)
  - [x] Type ASCII text
  - [x] Type Unicode (emoji, special chars)
  - [x] Type very long strings (>10KB)
  - [x] Type with timing (slow vs fast)
  - [x] Type special keys (Tab, Enter, Backspace)
  - [x] Type with modifiers (Shift+"H" = "H", etc.)
  - [x] Type to wrong window (error handling)
  - [x] Type logged correctly

- `test_ea_primitives_open_app.py` (7 tests)
  - [x] Open Chrome (valid path)
  - [x] Open Firefox (fallback if Chrome missing)
  - [x] Open with arguments (e.g., "--incognito")
  - [x] App already running (reuse window)
  - [x] App missing (error)
  - [x] App startup timeout (5s default)
  - [x] Application logged with PID

- `test_ea_primitives_wait.py` (4 tests)
  - [x] Wait 1 second
  - [x] Wait 5 seconds
  - [x] Wait 0.1 seconds (subsecond)
  - [x] Wait timeout (max 60s)

- `test_ea_primitives_screenshot.py` (5 tests)
  - [x] Screenshot capture to file
  - [x] Screenshot file has correct dimensions (1920x1080, etc.)
  - [x] Screenshot format (PNG, JPG)
  - [x] Screenshot path logged
  - [x] Screenshot during window transition

- `test_ea_primitives_keyboard.py` (3 tests)
  - [x] Ctrl+C (copy)
  - [x] Alt+Tab (switch window)
  - [x] Win+V (paste)

📊 **Integration Tests (10 tests):**
- `test_ea_with_database.py` (3 tests)
  - [x] All actions logged to execution_logs table
  - [x] Action results include status, timestamp, input, output
  - [x] Foreign key integrity (session_id, workflow_id)

- `test_ea_with_logging.py` (2 tests)
  - [x] Actions logged to JSON files (console + file)
  - [x] Screenshots stored and logged

- `test_ea_with_oa_agent.py` (3 tests)
  - [x] EA output formatted for OA consumption
  - [x] EA screenshot available for OA analysis
  - [x] EA status flags (success, needs_verification, failed)

- `test_ea_with_orchestrator.py` (2 tests)
  - [x] EA receives steps from orchestrator
  - [x] EA returns results to orchestrator

📊 **E2E Tests (5 tests):**
- `test_ea_e2e_simple_actions.py`
  - [x] Scenario 1: Click button on screen
  - [x] Scenario 2: Type text in a field
  - [x] Scenario 3: Open application
  - [x] Scenario 4: Chain actions: open app → type → click
  - [x] Scenario 5: Screenshot after each action

**Backend Coverage:**
- Module: `app/agents/execution_agent.py` (~250 lines, target >85%)
- Module: `app/services/desktop_automation.py` (~200 lines, pyautogui wrapper)
- Tables: `execution_logs`, `screenshots` (new)
- External: pyautogui library (3rd party, mocked in unit tests)

**Dependencies:**
- BaseAgent protocol (exists)
- Execution environment (Windows with desktop access)

**Risks:**
- **Risk 1:** Screen resolution varies (coordinates change)  
  Mitigation: Use OCR/vision to find UI elements instead of static coords
- **Risk 2:** Apps not installed  
  Mitigation: Mock external apps, use headless alternatives
- **Risk 3:** Timing issues (action too fast, window not ready)  
  Mitigation: Add wait_for_element(), screenshot validation

---

### Story 2.2: Screenshot Service + moondream Vision Integration
**Epic:** 2 - Execution Pipeline  
**Points:** 4  
**Owner:** Amelia (Development)  
**Sprint:** 2 (Wed-Thu)  
**Duration:** 2 days

**Description:**  
Implement screenshot capture and moondream vision analysis. After each action, system takes screenshot and analyzes it using moondream model (local LLM for vision). This enables Agent to "see" what happened and adjust strategy.

**Acceptance Criteria:**
- [ ] Screenshot captured after each action
- [ ] Screenshot stored in filesystem with metadata
- [ ] moondream integration to analyze screenshots
- [ ] Returns structured analysis: detected UI elements, text, actions possible
- [ ] Confidence scores for detected elements
- [ ] Caches analysis (same screenshot = same result)
- [ ] Handles vision analysis errors gracefully

**Testing:**

📊 **Unit Tests (25 tests):**
- `test_screenshot_service.py` (8 tests)
  - [x] Capture full screen
  - [x] Capture specific window
  - [x] Save to file with metadata
  - [x] File format PNG/JPG
  - [x] Screenshots linked to session_id
  - [x] Timestamp inclusion
  - [x] Disk space checks
  - [x] Error handling (permission denied, disk full)

- `test_moondream_integration.py` (12 tests)
  - [x] moondream initializes
  - [x] Analyzes screenshot (button detection)
  - [x] Analyzes screenshot (text extraction)
  - [x] Analyzes screenshot (input field detection)
  - [x] Returns structured output (elements array)
  - [x] Confidence scores present
  - [x] Handles timeout (10s max)
  - [x] Caches analysis results
  - [x] Different screenshots produce different analyses
  - [x] Handles corrupted image file
  - [x] Handles very large image (>10MB)
  - [x] Performance: analysis <3s

- `test_vision_service_combined.py` (5 tests)
  - [x] Screenshot → moondream pipeline
  - [x] Results include clickable elements
  - [x] Results include text content
  - [x] Results include window title
  - [x] Results serializable to JSON

📊 **Integration Tests (8 tests):**
- `test_vision_with_database.py` (2 tests)
  - [x] Screenshots stored with session_id reference
  - [x] Vision results stored in analysis table

- `test_vision_with_ea.py` (2 tests)
  - [x] EA takes screenshot → vision analyzes
  - [x] Vision results inform next action

- `test_vision_with_oa.py` (2 tests)
  - [x] OA receives vision analysis
  - [x] OA validates action based on vision

- `test_vision_with_recovery.py` (2 tests)
  - [x] Vision detects action failure
  - [x] Recovery engine uses vision analysis

📊 **E2E Tests (3 tests):**
- `test_vision_e2e.py`
  - [x] Scenario 1: Open Chrome → screenshot → detect browser UI
  - [x] Scenario 2: Navigate Gmail → screenshot → detect email list
  - [x] Scenario 3: Fill form → screenshot → detect all fields

**Backend Coverage:**
- Module: `app/services/screenshot_service.py` (~80 lines, NEW)
- Module: `app/services/vision_service.py` (~150 lines, NEW)
- Module: `app/services/moondream_service.py` (~100 lines, NEW)
- Tables: `screenshots`, `vision_analysis`
- Models: moondream (1.7GB, existing)

**Dependencies:**
- Story 2.1 (EA agent takes screenshots)
- moondream model downloaded

**Risks:**
- **Risk 1:** moondream analysis slow (>3s)  
  Mitigation: Use smaller vision model (quantized), cache results
- **Risk 2:** Vision detects wrong elements  
  Mitigation: Low confidence threshold for re-analysis

---

### Story 2.3: Observer Agent Implementation
**Epic:** 2 - Execution Pipeline  
**Points:** 3  
**Owner:** Amelia (Development)  
**Sprint:** 2 (Fri)  
**Duration:** 1 day

**Description:**  
Observer Agent validates that executed actions succeeded. Takes screenshot, analyzes with vision, compares to expected state. If action failed, reports to Recovery Engine. Critical for knowing when to retry or abort.

**Acceptance Criteria:**
- [ ] Receives expected state from plan
- [ ] Gets current state from screenshot + vision
- [ ] Compares expected vs. actual
- [ ] Returns confidence (0.0-1.0) that action succeeded
- [ ] Distinguishes success vs. needs_verification vs. failure
- [ ] Logs comparison result
- [ ] Handles edge cases (window moved, resolution changed)

**Testing:**

📊 **Unit Tests (18 tests):**
- Compare states, detect mismatches, confidence scoring
- Handle ambiguous states

📊 **Integration Tests (5 tests):**
- OA → Database logging
- OA → Recovery Engine
- OA → Context Manager

📊 **E2E Tests (2 tests):**
- Action succeeded → OA confirms
- Action failed → OA detects

**Backend Coverage:**
- Module: `app/agents/observer_agent.py` (~120 lines)

**Dependencies:**
- Story 2.1 (EA), Story 2.2 (Vision)

---

### Story 2.4: Orchestrator Integration
**Epic:** 2 - Execution Pipeline  
**Points:** 5  
**Owner:** Amelia (Development)  
**Sprint:** 2 (Mon-Tue Week 3)  
**Duration:** 2 days

**Description:**  
Update Orchestrator to sequence all agents: RAG → Clarification → WebSearch → SPA → SAA → EA → OA. Implements real-time feedback loop: after each EA action, OA validates, informs next planning step. Error handling routes to Recovery Engine.

**Acceptance Criteria:**
- [ ] Orchestrator has complete agent list (all 5 planning, all 4 execution)
- [ ] Sequences agents in correct order
- [ ] Passes context between agents
- [ ] Handles agent timeouts (5s default)
- [ ] Catches agent exceptions (no crash)
- [ ] Routes failures to Recovery Engine
- [ ] Logs full execution trace
- [ ] Returns final result to frontend

**Testing:**

📊 **Unit Tests (20 tests):**
- Agent sequencing
- Context passing
- Error handling
- Timeout management

📊 **Integration Tests (12 tests):**
- Full pipeline: planning → execution
- Database transaction integrity
- WebSocket notifications

📊 **E2E Tests (3 tests):**
- Complete workflow: User input → Plan → Execute → Validate → Result

**Backend Coverage:**
- Module: `app/agents/orchestrator.py` (existing framework, complete implementation)
- Tables: All (transaction integrity)

**Dependencies:**
- All stories 1.1-1.5, 2.1-2.3

---

### Story 2.5: WebSocket Real-Time Streaming
**Epic:** 2 - Execution Pipeline  
**Points:** 3  
**Owner:** Amelia (Development)  
**Sprint:** 2 (Wed Week 3)  
**Duration:** 1 day

**Description:**  
Implement WebSocket streaming so frontend sees real-time updates: "Executing step 1/8: Click button", "Screenshot captured", "Vision analysis: Button found", etc. Enables progress bar and living-log UI.

**Acceptance Criteria:**
- [ ] WebSocket connection established (frontend → backend)
- [ ] Each agent step emits event (timestamp, step, status)
- [ ] Screenshot available via WebSocket
- [ ] Vision analysis streamed
- [ ] Error messages real-time
- [ ] Performance: <50ms latency per update

**Testing:**

📊 **Unit Tests (10 tests):**
- WebSocket connection
- Event serialization
- Error sending

📊 **Integration Tests (5 tests):**
- Full pipeline WebSocket stream
- Frontend receives all events

📊 **E2E Tests (1 test):**
- Real workflow with WebSocket monitoring

**Backend Coverage:**
- Module: `app/routes/execution.py` (WebSocket handler)
- Framework: FastAPI WebSocket support

**Dependencies:**
- Story 2.4 (Orchestrator)

---

## **EPIC 2 SUMMARY**
- **Total Points:** 20 SP
- **Duration:** 8 days (Wed-Fri Week 1 + Mon-Fri Week 2 + Mon-Wed Week 3)
- **Stories:** 5 (EA Primitives, Vision, Observer, Orchestrator, WebSocket)
- **Tests:** 35+25+18+20+10 = 108 unit tests
- **Tests:** 10+8+5+12+5 = 40 integration tests
- **Tests:** 5+3+2+3+1 = 14 E2E tests
- **Total Tests:** 162 tests

---

# EPIC 3: SUPPORT & RECOVERY
## Stories 3.1 - 3.5 (Safety, recovery, learning)

### Story 3.1: Safety Agent Implementation
**Points:** 3  
**Sprint:** 2

**Description:**  
Blocks dangerous user commands before execution. Maintains blacklist of forbidden actions (delete system files, format disk, uninstall OS). Asks for confirmation on risky actions.

**Testing:** 12 unit + 4 integration + 1 E2E = 17 tests

---

### Story 3.2: Recovery Engine (6 Levels)
**Points:** 5  
**Sprint:** 2-3

**Description:**  
Implements 6-level recovery strategy when action fails:
- L1: Retry same action
- L2: Retry with wait before
- L3: Take screenshot + vision analysis to understand failure
- L4: Replan from current state
- L5: Roll back to last successful step + replan
- L6: Abort workflow, report to user

**Testing:** 30 unit + 10 integration + 3 E2E = 43 tests

---

### Story 3.3: Context Manager (CMA)
**Points:** 3  
**Sprint:** 3

**Description:**  
Manages context persistence across failures. Stores snapshots after each step so recovery can resume mid-workflow. Cleans up on completion.

**Testing:** 15 unit + 5 integration + 2 E2E = 22 tests

---

### Story 3.4: Workflow Learner
**Points:** 3  
**Sprint:** 3

**Description:**  
Recognizes successful workflows and stores them for reuse. Next time similar request comes in, system recognizes it and replays without re-planning. Faster execution.

**Testing:** 15 unit + 4 integration + 1 E2E = 20 tests

---

### Story 3.5: App Registry
**Points:** 2  
**Sprint:** 1

**Description:**  
Scans Windows system for installed applications. Returns list of available apps for SAA agent to select from. Updates on demand or daily.

**Testing:** 10 unit + 2 integration + 1 E2E = 13 tests

---

## **EPIC 3 SUMMARY**
- **Total Points:** 16 SP
- **Duration:** 7 days (integrated into Sprint 2-3)
- **Stories:** 5
- **Tests:** 82 unit + 25 integration + 8 E2E = 115 tests

---

# EPIC 4: INFRASTRUCTURE & SERVICES
## Stories 4.1 - 4.5 (Backend foundation)

### Story 4.1: Logging Service - Complete Setup
**Points:** 2  
**Sprint:** 1

**Description:**  
Complete structlog setup with rotating file handlers, JSON output, console output. Verify ./data/logs/jarvis.log and jarvis_errors.log work.

**Testing:** 8 unit + 3 integration + 1 E2E = 12 tests

---

### Story 4.2: Voice Service - Whisper Integration
**Points:** 3  
**Sprint:** 1

**Description:**  
Complete Whisper transcription. User speaks, system converts to text. Integrates with Ollama. Tests with various accents, background noise.

**Testing:** 12 unit + 4 integration + 2 E2E = 18 tests

---

### Story 4.3: Database Service - Async Queries
**Points:** 2  
**Sprint:** 1

**Description:**  
Verify all database queries are async (SQLAlchemy with aiosqlite). No blocking calls. Transactions properly managed.

**Testing:** 10 unit + 5 integration + 1 E2E = 16 tests

---

### Story 4.4: Error Handling & Codes
**Points:** 2  
**Sprint:** 1

**Description:**  
Consistent error codes for all failures. Enables frontend to display appropriate messages. Maps internal exceptions to user-friendly messages.

**Testing:** 8 unit + 4 integration = 12 tests

---

### Story 4.5: Configuration Management
**Points:** 1  
**Sprint:** 1

**Description:**  
Verify 12-factor app setup. All config via environment variables. .env file support. Validation of required vars on startup.

**Testing:** 5 unit + 2 integration = 7 tests

---

## **EPIC 4 SUMMARY**
- **Total Points:** 10 SP
- **Duration:** 5 days (integrated into Sprint 1)
- **Stories:** 5
- **Tests:** 43 unit + 18 integration + 4 E2E = 65 tests

---

# EPIC 5: END-TO-END & PRODUCTION
## Stories 5.1 - 5.5 (Complex workflows, performance, readiness)

### Story 5.1: 5 Real Scenario Test Suite
**Points:** 5  
**Sprint:** 3

**Description:**  
Comprehensive testing of 5 real scenarios:
1. Open Chrome
2. Open Gmail + draft email
3. Save workflow for reuse
4. Error recovery with re-planning
5. Multi-app workflow (Calendar → Gmail → Slack)

**Testing:** 15 unit + 5 integration + 5 E2E = 25 tests

---

### Story 5.2: Performance Optimization
**Points:** 3  
**Sprint:** 3

**Description:**  
Ensure all end-to-end workflows complete in <5 seconds. Identify bottlenecks. Optimize moondream latency, LLM latency, database queries.

**Testing:** 10 unit + 4 integration + 2 E2E = 16 tests

---

### Story 5.3: Chat Session Management
**Points:** 2  
**Sprint:** 3

**Description:**  
Complete chat session lifecycle: create, populate with execution logs, queries by user_id/session_id, history retrieval. Isolation tests (no data leakage).

**Testing:** 8 unit + 4 integration + 1 E2E = 13 tests

---

### Story 5.4: Workflow Persistence & Replay
**Points:** 3  
**Sprint:** 3

**Description:**  
Workflows saved to database. On similar request, system recognizes and reuses. Replay without re-planning. Measures performance improvement.

**Testing:** 12 unit + 4 integration + 2 E2E = 18 tests

---

### Story 5.5: Production Readiness
**Points:** 4  
**Sprint:** 3

**Description:**  
Security audit, monitoring setup, deployment validation. SSL/TLS, input validation, rate limiting. Health checks. Ready to ship to production.

**Testing:** 15 unit + 3 integration + 1 E2E = 19 tests

---

## **EPIC 5 SUMMARY**
- **Total Points:** 17 SP
- **Duration:** 5 days (integrated into Sprint 3)
- **Stories:** 5
- **Tests:** 60 unit + 20 integration + 11 E2E = 91 tests

---

# 📊 COMPLETE TEST INVENTORY

## By Category

| Category | Count | Purpose |
|----------|-------|---------|
| Unit Tests | **215** | Verify individual components |
| Integration Tests | **103** | Verify component interactions |
| E2E Tests | **35** | Real scenarios, real workflows |
| **TOTAL** | **353** | **COMPLETE COVERAGE** |

## By Sprint

| Sprint | Unit | Integration | E2E | Total | Duration |
|--------|------|-------------|-----|-------|----------|
| Sprint 1 (W1) | 127 | 32 | 9 | 168 | 5 days |
| Sprint 2 (W2-W3:Wed) | 65 | 52 | 15 | 132 | 8 days |
| Sprint 3 (W3:Thu-W4) | 23 | 19 | 11 | 53 | 5 days |
| **TOTAL** | **215** | **103** | **35** | **353** | **18 days (3-4 wks)** |

## By Epic

| Epic | Unit | Integration | E2E | Stories | Points |
|------|------|-------------|-----|---------|--------|
| Epic 1: Planning | 90 | 24 | 7 | 5 | 17 |
| Epic 2: Execution | 108 | 40 | 14 | 5 | 20 |
| Epic 3: Support | 82 | 25 | 8 | 5 | 16 |
| Epic 4: Infrastructure | 43 | 18 | 4 | 5 | 10 |
| Epic 5: Production | 60 | 20 | 11 | 5 | 17 |
| **TOTAL** | **215** | **103** | **35** | **25** | **80 SP** |

## Coverage by Module

| Module | Tests | Coverage Target | Purpose |
|--------|-------|-----------------|---------|
| RAG Agent | 41 | 90% | Planning from intent |
| EA Agent | 45 | 85% | Desktop automation |
| OA (Observer) Agent | 25 | 80% | Validate actions |
| Orchestrator | 35 | 85% | Sequence agents |
| Vision Service | 36 | 85% | Screenshot analysis |
| Recovery Engine | 43 | 85% | Failure handling |
| Database Layer | 35 | 90% | Persistence |
| WebSocket Layer | 16 | 80% | Real-time streaming |
| Other Agents | 76 | 80% | Support agents |
| **TOTAL** | **353** | **>85% overall** |

---

# 🚀 SPRINT EXECUTION PLAN

## SPRINT 1: Planning Pipeline + Infrastructure (5 days, Mon-Fri Week 1)

**Goal:** All 5 planning agents complete + infrastructure foundation

**Mon (Day 1):**
- 9 AM: Sprint Kick-off (John reviews story criteria)
- 10 AM: Amelia starts Story 1.1 (RAG Agent)
- 10 AM: Quinn writes 30 unit tests for RAG
- 3 PM: Sync - 15 tests passing
- 5 PM: EOD - 20 tests passing

**Tue (Day 2):**
- 9 AM: Standup
- 10 AM: RAG Agent complete (all 30 tests passing)
- 10 AM: Amelia starts Story 4.5 (Config Management)
- 10 AM: Quinn continues integration tests for Story 1.1
- 2 PM: Story 1.1 complete + merged
- 3 PM: Amelia starts Story 1.2 (Clarification)
- 5 PM: EOD - RAG + Config done

**Wed (Day 3):**
- 9 AM: Standup
- 10 AM: Clarification Agent in progress
- 10 AM: Quinn tests Story 4.3 (Database)
- 12 PM: Story 1.2 complete
- 1 PM: Amelia starts Story 1.3 (WebSearch)
- 5 PM: EOD - 3/5 planning agents complete

**Thu (Day 4):**
- 9 AM: Standup
- 10 AM: WebSearch Agent in progress
- 10 AM: Quinn tests Story 4.1 (Logging)
- 12 PM: Amelia starts Story 1.4 (SPA)
- 4 PM: Stories 1.2, 1.3 complete
- 5 PM: EOD - 4/5 planning agents, all infra tests done

**Fri (Day 5):**
- 9 AM: Standup
- 10 AM: SPA + SAA agents (combined, light complexity)
- 12 PM: Stories 1.4, 1.5 complete
- 1 PM: Voice Service (Story 4.2) tests written
- 3 PM: Sprint Review (John accepts all 5 stories)
- 4 PM: Regression tests (all 121 Sprint 1 tests passing)
- 5 PM: EOD - **SPRINT 1 COMPLETE**

**Sprint 1 Outcome:**
- ✅ All 5 planning agents working
- ✅ 121 tests passing (90 unit + 24 integration + 7 E2E)
- ✅ Infrastructure foundation solid
- ✅ Ready for execution pipeline

---

## SPRINT 2: Execution Pipeline (8 days, Fri W1 + Mon-Fri W2 + Mon-Wed W3)

**Goal:** Complete execution loop: EA → Vision → OA → Orchestrator → WebSocket

**Fri (Day 6, W1):**
- 1 PM: Begin Story 2.1 (EA Primitives)
- 1 PM: Quinn writes 35 unit tests
- 5 PM: EOD - 10 tests passing

**Mon (Day 7, W2):**
- 9 AM: Standup
- 10 AM: EA Primitives ongoing (35 unit tests target)
- 12 PM: Story 2.1 tests mostly passing
- 1 PM: Quinn begins integration tests
- 5 PM: EOD - Story 2.1 nearly complete

**Tue (Day 8, W2):**
- 9 AM: Standup
- 10 AM: Story 2.1 complete ✅
- 10 AM: Amelia starts Story 2.2 (Vision Service)
- 10 AM: Quinn writes moondream integration tests
- 3 PM: Partial vision tests passing
- 5 PM: EOD - Vision integration in progress

**Wed (Day 9, W2):**
- 9 AM: Standup
- 10 AM: Vision Service complete
- 10 AM: Amelia starts Story 2.3 (Observer)
- 1 PM: Story 2.2 merged
- 3 PM: Story 2.3 tests passing
- 5 PM: EOD - EA + Vision + Observer done

**Thu (Day 10, W2):**
- 9 AM: Standup
- 10 AM: Amelia starts Story 3.2 (Recovery Engine)
- 10 AM: Quinn tests Recovery (30 unit tests)
- 12 PM: Story 2.3 complete
- 3 PM: Story 3.2 in progress (complex, slow)
- 5 PM: EOD - Recovery Engine tests mostly written

**Fri (Day 11, W2):**
- 9 AM: Standup
- 10 AM: Amelia continues Recovery Engine
- 11 AM: Story 3.1 (Safety) quick 1-day story
- 2 PM: Story 3.1 complete
- 3 PM: Story 3.2 continuing
- 5 PM: EOD - Recovery in progress

**Mon (Day 12, W3):**
- 9 AM: Standup - Recovery Engine still complex
- 10 AM: Amelia debugging Recovery tests
- 1 PM: Story 3.2 complete ✅
- 1 PM: Amelia starts Story 2.4 (Orchestrator)
- 2 PM: Quinn writes orchestrator integration tests (12 tests)
- 5 PM: EOD - Orchestrator in progress

**Tue (Day 13, W3):**
- 9 AM: Standup
- 10 AM: Orchestrator complete ✅
- 10 AM: Amelia starts Story 3.3 (Context Manager)
- 1 PM: Quinn tests WebSocket (Story 2.5)
- 3 PM: Story 3.3 complete
- 4 PM: Regression tests (all 132 Sprint 1+2 tests passing)
- 5 PM: EOD - Stories 2.4, 3.3 complete

**Wed (Day 14, W3):**
- 9 AM: Standup
- 10 AM: Amelia starts Story 2.5 (WebSocket)
- 10 AM: Quinn validates WebSocket tests
- 12 PM: Story 2.5 complete
- 1 PM: Final regression tests
- 3 PM: Sprint Review (John accepts all stories)
- 5 PM: EOD - **SPRINT 2 COMPLETE**

**Sprint 2 Outcome:**
- ✅ All execution agents working
- ✅ Vision integration complete
- ✅ Real-time WebSocket streaming
- ✅ Recovery engine (6 levels)
- ✅ 250 cumulative tests passing (132 Sprint 2 new)
- ✅ Full execution loop validated

---

## SPRINT 3: Production & Polish (5 days, Thu W3 + Fri W3 + Mon-Tue W4)

**Goal:** Complex workflow testing, performance, production readiness

**Thu (Day 15, W3):**
- 9 AM: Begin Story 5.1 (5 Real Scenarios)
- 9 AM: Scenario 1: Open Chrome (simple E2E)
- 1 PM: Scenario 2: Gmail (complex E2E)
- 5 PM: EOD - 2/5 scenarios passing

**Fri (Day 16, W3):**
- 9 AM: Standup
- 10 AM: Scenarios 3, 4, 5 in progress
- 11 AM: Story 3.4 (Workflow Learner) parallel development
- 1 PM: All 5 scenarios passing ✅
- 2 PM: Story 3.4 complete
- 3 PM: Story 3.5 (App Registry) quick 1-day story
- 5 PM: EOD - All scenarios complete

**Mon (Day 17, W4):**
- 9 AM: Standup
- 10 AM: Amelia starts Story 5.4 (Workflow Persistence)
- 10 AM: Scenario 3: Save & replay workflow
- 1 PM: Workflow persistence tests 80% passing
- 2 PM: Story 5.3 (Chat Sessions) parallel
- 5 PM: EOD - Stories 5.3, 5.4 in progress

**Tue (Day 18, W4):**
- 9 AM: Standup
- 10 AM: Stories 5.2 (Performance) and 5.5 (Production)
- 1 PM: Performance benchmarks (all workflows <5s)
- 2 PM: Security audit (Winston review)
- 3 PM: All 5 stories complete ✅
- 4 PM: Final regression tests (all 353 tests passing)
- 5 PM: **PROJECT COMPLETE ✅**

**Sprint 3 Outcome:**
- ✅ 5 real scenarios working end-to-end
- ✅ Workflow persistence & replay validated
- ✅ Performance <5s confirmed
- ✅ Production security audit passed
- ✅ 353 total tests passing (100% green)
- ✅ Code coverage >85%
- ✅ **READY FOR LAUNCH**

---

# ✅ DEFINITION OF DONE (Per Story)

**Code:**
- [ ] Implements acceptance criteria 100%
- [ ] All tests passing (unit + integration + E2E)
- [ ] Code reviewed by Winston (architecture sign-off)
- [ ] Code merged to main branch

**Tests:**
- [ ] Unit tests written (TDD approach)
- [ ] Coverage >80% for new code
- [ ] Integration tests passing
- [ ] E2E scenarios passing (real workflows)
- [ ] No regressions (all existing tests still pass)

**Documentation:**
- [ ] Code comments explain complex logic
- [ ] README updated if needed
- [ ] Inline TODOs removed

**Database:**
- [ ] New tables created (if any)
- [ ] Foreign keys enforced
- [ ] Data migrations verified
- [ ] Query performance acceptable

**Logging & Monitoring:**
- [ ] Key events logged (info level)
- [ ] Errors logged (error level)
- [ ] Metrics tracked (optional)
- [ ] Nothing breaks in console output

---

# 🎯 GO/NO-GO DECISION CRITERIA

## Per-Sprint Gate (Must Pass to Continue)

**Sprint 1 Gate (End of Fri W1):**
- [ ] All 5 planning agents complete (RAG, Clarification, WebSearch, SPA, SAA)
- [ ] 121 tests passing (90 unit + 24 integration + 7 E2E)
- [ ] Coverage >85%
- [ ] Zero regression failures
- [ ] Zero ERROR logs (warnings OK)
- **Decision:** GO → Sprint 2, NO-GO → Fix + retest

**Sprint 2 Gate (End of Wed W3):**
- [ ] All 5 execution agents complete (EA, Vision, OA, Orchestrator, WebSocket)
- [ ] All support agents complete (Safety, Recovery, CMA, Learner, Registry)
- [ ] 250 cumulative tests passing
- [ ] Coverage >85%
- [ ] Zero regressions
- [ ] Real workflow: Open Chrome → Screenshot → Analyze with moondream → SUCCESS
- **Decision:** GO → Sprint 3, NO-GO → Debug + retest

**Sprint 3 Gate (End of Tue W4):**
- [ ] 5 real scenarios working end-to-end
- [ ] 353 total tests passing (100% green)
- [ ] Coverage >85% overall
- [ ] Performance: all workflows <5s
- [ ] Security audit passed
- [ ] Winston architecture approval
- [ ] No ERROR logs in production code paths
- **Decision:** GO → PRODUCTION

---

# 📋 BACKLOG & FUTURE ENHANCEMENTS

Stories 6-10 (Post-MVP):
- Story 6.1: Advanced Vision (hand-written digit recognition)
- Story 6.2: Multi-language Support (50+ languages)
- Story 6.3: Custom Workflows (user-defined automation)
- Story 6.4: Team Collaboration (share workflows)
- Story 6.5: Mobile App (iOS/Android remote execution)

---

# 🔗 NAVIGATION & RESOURCES

**For Developers (Amelia):**
- `DEVELOPER_QUICKSTART_AMELIA.md` - How to start coding
- `app/agents/protocol.py` - BaseAgent interface to implement
- `tests/` - Example test structure
- `/dev-story` command - Start developing a story

**For QA (Quinn):**
- `BACKEND_TESTING_AND_VALIDATION_STRATEGY.md` - Testing approach
- `tests/` - Where to write tests
- `/qa-automate` command - Automate tests

**For Product (John):**
- `JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md` - Full spec
- This document - All stories with acceptance criteria
- Regular sprint reviews every Friday

**For Architecture (Winston):**
- `JARVIS_AI_PRODUCTION_READINESS_GAP_ANALYSIS_V4.md` - Architecture gaps
- Code reviews (all PRs need Winston sign-off)
- Architecture decisions documented

---

# 📊 SUMMARY

| Metric | Value |
|--------|-------|
| Total Stories | 25 |
| Total Story Points | 80 |
| Total Duration | 18 days (3-4 weeks, 3 sprints) |
| Unit Tests | 215 |
| Integration Tests | 103 |
| E2E Tests | 35 |
| **Total Tests** | **353** |
| Code Coverage Target | >85% |
| Expected Regressions | 0 (comprehensive testing) |
| Production Readiness | HIGH (all gates passed) |

---

**Status:** ✅ Ready for Sprint 1 Kick-off (Monday, Week 1)  
**Next:** John approves stories → Bob schedules sprint → Amelia begins dev

