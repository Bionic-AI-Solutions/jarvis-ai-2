# JARVIS AI - EPICS & STORIES (SPRINT PLAN)
## Created by: John (Product Manager) following SKAD Framework
**Date:** February 24, 2026  
**Sprint Duration:** 3 weeks (15 days)  
**Status:** Ready for Sprint Planning (Bob) → Development (Amelia) → QA (Quinn) → Review (Winston)

---

# EPIC 1: Core Planning & Execution Pipeline
**Epic Lead:** Winston (Architect)  
**Duration:** Week 1 + 2 days Week 2  
**Story Points:** 13  
**Objective:** Enable basic user command → plan → execute → observe cycle  
**Success Criteria:** User speaks "Open Notepad and type hello" → system executes all 3 steps

---

## Story 1.1: Implement RAG (Reasoning & Generation) Agent
**Story Points:** 3  
**Priority:** 🔴 CRITICAL  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **user**, I want the system to **understand what I'm asking and create a step-by-step plan** so that **the system knows what to do before attempting it**.

### Acceptance Criteria

- [ ] **GIVEN** user input "Open Gmail and check inbox"
- [ ] **WHEN** RAG agent processes it
- [ ] **THEN** system returns structured plan:
  ```json
  {
    "goal": "Check Gmail inbox",
    "steps": [
      {"order": 1, "action": "click", "target": "Chrome icon"},
      {"order": 2, "action": "navigate", "url": "gmail.com"},
      {"order": 3, "action": "wait", "seconds": 3},
      {"order": 4, "action": "screenshot"}
    ],
    "confidence": 0.92,
    "reasoning": "User wants to check email. Gmail typically accessed via browser..."
  }
  ```

- [ ] Generated plan must have:
  - Minimum 2 steps, maximum 15 steps
  - Each step has action, target, and optional parameters
  - Confidence score 0.7-1.0
  - Reasoning explanation

- [ ] Plan format validates against schema: `PlanSchema` (defined in `backend/app/schemas.py`)

- [ ] System gracefully handles invalid inputs:
  - Empty input → Error response
  - Profanity/harmful intent → Safety agent flags before RAG processes
  - Ambiguous input → Returns with low confidence (<0.7) for Clarification agent

### Implementation Details

**File Location:** `backend/app/agents/rag_agent.py` (new file)

**Class Structure:**
```python
from app.agents.protocol import BaseAgent

class RAGAgent(BaseAgent):
    """RAG = Reasoning & Generation.
    Takes user input, generates structured action plan."""
    
    def __init__(self, ollama_service):
        self.ollama_service = ollama_service
        self.model = "qwen2.5:3b"  # LLM for reasoning
        self.max_steps = 15
        self.min_confidence = 0.7
    
    async def process(self, input_data):
        # 1. Extract user prompt
        # 2. Call LLM with planning prompt
        # 3. Parse response into structured steps
        # 4. Validate steps
        # 5. Return results
        pass
```

**Dependencies to Add:**
- Already have: `app.services.ollama_service`
- Already have: `pydantic` for schema validation

**Test Requirements:**

| Test Case | Expected Behavior | Status |
|-----------|-------------------|--------|
| Simple command | Generates 2-5 steps | ❌ Write test |
| Complex command | Generates 5-10 steps | ❌ Write test |
| Ambiguous input | Returns low confidence | ❌ Write test |
| Invalid input | Error response | ❌ Write test |
| Performance | Response <2 seconds | ❌ Write performance test |

**Tests to Create:**
- `tests/test_agents/test_rag_agent.py` (15 unit tests)

**Completion Checklist:**
- [ ] `rag_agent.py` implemented (150 lines)
- [ ] 15 unit tests written and passing
- [ ] Agent registered in `registry.py`
- [ ] Integration test with orchestrator
- [ ] Performance test (<2s response)
- [ ] Code review by Winston

**Success Metric:** 
- Generate plans for 5 sample user commands
- All plans have 2-15 steps with confidence >0.7
- Response time <2 seconds

---

## Story 1.2: Implement Execution Agent (EA) - Core Actions
**Story Points:** 5  
**Priority:** 🔴 CRITICAL (Blocker for everything else)  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **execute user-requested actions on the desktop** so that **the system can actually do things instead of just planning**.

### Acceptance Criteria

- [ ] **GIVEN** a step from the execution plan
- [ ] **WHEN** EA (Execution Agent) receives it
- [ ] **THEN** EA executes the action and returns confirmation

**Supported Actions:**

1. **CLICK** - Move mouse to coordinates and click
   - Input: `{action: "click", x: 100, y: 200}`
   - Output: `{success: true, new_screenshot: <path>}`
   - Must handle: Out-of-bounds coordinates (x > screen_width)

2. **TYPE** - Type text into focused window
   - Input: `{action: "type", text: "Hello world"}`
   - Output: `{success: true, typed_chars: 11}`
   - Must handle: Special characters, newlines

3. **SCREENSHOT** - Capture current desktop
   - Input: `{action: "screenshot"}`
   - Output: `{success: true, image: <path>, timestamp: <iso>}`
   - Must handle: Screen unavailable (locked, sleeping)

4. **OPEN_APP** - Launch application via PowerShell
   - Input: `{action: "open_app", app: "notepad"}`
   - Output: `{success: true, pid: 1234}`
   - Must handle: App not found, permissions denied

5. **WAIT** - Pause between actions
   - Input: `{action: "wait", seconds: 2}`
   - Output: `{success: true, waited_seconds: 2.01}`

- [ ] All actions have try/catch error handling
- [ ] All errors logged with context
- [ ] All actions log to execution_log table

### Implementation Details

**File Location:** `backend/app/agents/ea_agent.py` (new file)

**Dependencies to Add:**
```bash
pip install pyautogui pillow pygetwindow pywin32
```

**Architecture:**
```python
class ExecutionAgent(BaseAgent):
    
    async def process(self, step):
        """Execute a single step from the plan."""
        action = step['action']
        
        if action == 'click':
            return await self._handle_click(step)
        elif action == 'type':
            return await self._handle_type(step)
        elif action == 'screenshot':
            return await self._handle_screenshot(step)
        elif action == 'open_app':
            return await self._handle_open_app(step)
        elif action == 'wait':
            return await self._handle_wait(step)
        else:
            return {"success": false, "error": f"Unknown action: {action}"}
    
    async def _handle_click(self, step):
        try:
            x = step.get('x')
            y = step.get('y')
            pyautogui.click(x, y)
            await asyncio.sleep(0.5)  # Let UI respond
            screenshot = await self._take_screenshot()
            return {"success": true, "screenshot": screenshot}
        except Exception as e:
            return {"success": false, "error": str(e)}
    
    # ... etc for other actions
```

**Test Requirements:**

| Test Case | Expected Behavior |
|-----------|-------------------|
| Click valid coordinate | Mouse moves and clicks |
| Click out of bounds | Returns error gracefully |
| Type ASCII text | All text appears |
| Type special chars | Handles @#$%^&* |
| Screenshot succeeds | Image file created |
| Open notepad | Process starts (pid returned) |
| Open missing app | Returns error, not crash |
| Wait 2 seconds | Returns after 2+ seconds |

**Tests to Create:**
- `tests/test_agents/test_ea_agent.py` (30 unit tests)
- `tests/test_integration/test_ea_execution.py` (10 E2E tests)

**Completion Checklist:**
- [ ] `ea_agent.py` implemented (250 lines)
- [ ] Dependencies installed
- [ ] 30 unit tests written and passing
- [ ] 10 E2E tests passing on real desktop
- [ ] Error handling for all edge cases
- [ ] Agent registered
- [ ] Code review by Winston

**Success Metric:**
- Execute 5 real actions on desktop (click, type, screenshot)
- 95%+ success rate on all 5 actions
- No crashes on invalid input

---

## Story 1.3: Implement Observer Agent (OA)
**Story Points:** 2  
**Priority:** 🟠 HIGH  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **observe whether each action succeeded** so that **I can decide what to do next**.

### Acceptance Criteria

- [ ] **GIVEN** step executed by EA
- [ ] **WHEN** OA (Observer Agent) analyzes the result
- [ ] **THEN** OA returns: success (true/false), evidence (screenshot), analysis

**Required Analysis:**

- [ ] For CLICK actions:
  - Did target element respond? (color change, state change)
  - Did we navigate to new page?
  - Did dialog/menu appear?

- [ ] For TYPE actions:
  - Did text appear in focused element?
  - Were all characters typed correctly?

- [ ] For OPEN_APP actions:
  - Did window open?
  - Did window appear in taskbar?

- [ ] For SCREENSHOT actions:
  - Was image captured?
  - Is image readable (not corrupted)?

### Implementation Details

**File Location:** `backend/app/agents/oa_agent.py` (new file)

**Architecture:**
```python
class ObserverAgent(BaseAgent):
    
    async def process(self, step_with_result):
        """
        Receives: {step: {...}, result: {...}, screenshot: <path>}
        Returns: {success: bool, confidence: 0-1, analysis: str}
        """
        step_action = step_with_result['step']['action']
        result = step_with_result['result']
        screenshot_path = step_with_result['screenshot']
        
        if step_action == 'click':
            return await self._analyze_click(screenshot_path, step_with_result)
        # ... etc
```

**Test Requirements:**
- `tests/test_agents/test_oa_agent.py` (15 tests)

**Completion Checklist:**
- [ ] `oa_agent.py` implemented (120 lines)
- [ ] 15 unit tests passing
- [ ] Integration with EA
- [ ] Registered in registry

**Success Metric:**
- Correctly identifies success/failure in 10 test screenshots
- ≥90% accuracy rate

---

## Story 1.4: Implement Orchestrator Dispatch Logic
**Story Points:** 3  
**Priority:** 🔴 CRITICAL  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **coordinate all agents in the right sequence** so that **user command → plan → execute → observe → complete works seamlessly**.

### Acceptance Criteria

- [ ] **GIVEN** user command
- [ ] **WHEN** orchestrator processes it
- [ ] **THEN** runs sequence:
  1. RAG generates plan
  2. For each step in plan:
     - EA executes step
     - OA observes result
  3. Returns execution log with all results

- [ ] Orchestrator handles errors gracefully:
  - If step fails, logs error
  - If agent crashes, catches exception
  - If timeout exceeds 5 minutes, abort

### Implementation Details

**File Location:** Modify `backend/app/agents/orchestrator.py`

**Update dispatch logic:**
```python
async def dispatch_workflow(self, user_input):
    # Phase 1: Planning
    rag_result = await self.registry.get_agent('rag').process(user_input)
    if not rag_result['success']:
        return {"error": "Failed to plan"}
    
    plan = rag_result['plan']
    execution_log = []
    
    # Phase 2: Execution
    for step in plan['steps']:
        # Execute
        ea_result = await self.registry.get_agent('ea').process(step)
        
        # Observe
        oa_result = await self.registry.get_agent('oa').process({
            'step': step,
            'result': ea_result
        })
        
        execution_log.append({
            'step': step,
            'executed': ea_result,
            'observed': oa_result
        })
        
        # If step failed, could trigger recovery (Week 2 feature)
        if not oa_result['success']:
            pass  # TODO: Recovery logic
    
    return {
        'success': true,
        'plan': plan,
        'execution_log': execution_log
    }
```

**Test Requirements:**
- `tests/test_integration/test_orchestrator.py` (10 integration tests)

**Success Metric:**
- Orchestrate 3 end-to-end workflows
- All agents called in correct sequence
- Execution log correctly populated

---

## Story 1.5: Frontend Integration - Display Execution
**Story Points:** 2  
**Priority:** 🟡 MEDIUM  
**Assigned To:** React Frontend Developer  

### Narrative
As a **user**, I want to **see the execution happening in real-time** so that **I know the system is working**.

### Acceptance Criteria

- [ ] When user clicks "Execute":
  - Step 1: Shows "Planning..."
  - Step 2: Shows "Executing step 1 of 5: Open Notepad"
  - Step 3: Shows "Observing result..."
  - Step 4: Shows execution log with screenshots

- [ ] Real-time updates via WebSocket
- [ ] Screenshots displayed in sequence
- [ ] Total execution time shown

### Tests
- WebSocket integration tests
- UI component tests

---

---

# EPIC 2: Vision & Intelligent Feedback
**Epic Lead:** Winston (Architect)  
**Duration:** Week 2  
**Story Points:** 8  
**Objective:** Enable moondream vision analysis so system can make intelligent decisions  
**Success Criteria:** System can describe what's on screen and decide what to do next

---

## Story 2.1: Implement Screenshot Service
**Story Points:** 1  
**Priority:** 🟠 HIGH  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **capture desktop screenshots reliably** so that **I can see what's on the screen**.

### Acceptance Criteria

- [ ] Takes screenshot of entire desktop
- [ ] Saves to timestamped file (`screenshots/2026-02-24_14-30-45.png`)
- [ ] Returns path to saved image
- [ ] Handles errors: Screen locked, no GPU, etc.
- [ ] Screenshot should be <5MB (compress if needed)

### Implementation
**File Location:** `backend/app/services/screenshot_service.py` (new file)

```python
class ScreenshotService:
    def take_screenshot(self) -> str:
        """Returns: path to saved screenshot"""
        try:
            screenshot = pil.ImageGrab.grab()
            timestamp = datetime.now().isoformat().replace(':', '-')
            path = f"screenshots/{timestamp}.png"
            screenshot.save(path, optimize=True)
            return path
        except Exception as e:
            raise ScreenshotError(f"Failed: {e}")
```

**Tests:**
- 10 unit tests

---

## Story 2.2: Implement Vision Service (moondream Integration)
**Story Points:** 3  
**Priority:** 🔴 CRITICAL  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **analyze screenshots with moondream** so that **I can understand what's on the screen and make intelligent decisions**.

### Acceptance Criteria

- [ ] **GIVEN** a screenshot
- [ ] **WHEN** VisionService analyzes it
- [ ] **THEN** returns structured analysis:
  ```json
  {
    "elements": [
      {"name": "Gmail logo", "type": "image", "confidence": 0.95},
      {"name": "Inbox button", "type": "button", "location": [100, 50], "state": "enabled"},
      {"name": "email list", "type": "list", "count": 15}
    ],
    "page_title": "Gmail - Inbox",
    "detected_text": ["Inbox (5)", "Sent", "Drafts"],
    "analysis": "Gmail interface is loaded and ready to use"
  }
  ```

- [ ] Analysis quality:
  - Identifies 80%+ of visible UI elements
  - Locates clickable buttons with 85%+ accuracy
  - Confidence scores 0-1 for uncertain elements

### Implementation
**File Location:** `backend/app/services/vision_service.py` (new file)

```python
class VisionService:
    def __init__(self):
        self.model = load_model("moondream")  # Ollama
    
    async def analyze(self, screenshot_path: str) -> dict:
        """Analyze screenshot with moondream"""
        image = Image.open(screenshot_path)
        
        prompt = """Analyze this screenshot and return:
        1. List all UI elements (buttons, text fields, images)
        2. For each clickable element, estimate its location (x, y)
        3. Describe the current state of the interface
        4. Identify any errors or warnings
        
        Format as structured data."""
        
        analysis = self.model.generate(image, prompt)
        return parse_analysis(analysis)
    
    async def find_element(self, name: str, screenshot_path: str):
        """Find specific element in screenshot"""
        analysis = await self.analyze(screenshot_path)
        for elem in analysis['elements']:
            if name.lower() in elem['name'].lower():
                return elem
        return None
```

**Tests:**
- 20 unit tests
- 5 E2E tests with real screenshots

---

## Story 2.3: Connect Vision to Execution Loop
**Story Points:** 2  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **use vision feedback to improve execution** so that **I can click the right buttons even if their positions change**.

### Acceptance Criteria

- [ ] After each action, vision analyzes if it succeeded
- [ ] If element not found, system retries or backtracks
- [ ] Execution log includes visual confirmation

### Implementation
- Update EA agent to use VisionService
- Add retry logic
- Update OA to use vision analysis

---

## Story 2.4: Implement Web Search Agent
**Story Points:** 2  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **search the web for information** so that **I can find how-to guides when I don't know how to do something**.

### Acceptance Criteria

- [ ] Search Google for tutorial
- [ ] Return top 3 results with titles and snippets
- [ ] Cache search results to avoid duplicate requests

---

---

# EPIC 3: Safety, Context & Error Handling
**Epic Lead:** Winston (Architect)  
**Duration:** Week 2 + 3  
**Story Points:** 10  
**Objective:** Prevent harmful actions, persist state, and recover from failures  
**Success Criteria:** System recovers from 90% of failures without user intervention

---

## Story 3.1: Implement Safety Agent
**Story Points:** 2  
**Priority:** 🔴 CRITICAL  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **prevent dangerous commands from executing** so that **I don't delete files or disable the system**.

### Acceptance Criteria

- [ ] Blocks commands: "rm -rf /", "delete system32"
- [ ] Blocks commands: "sudo", "format C:"
- [ ] Allows: "open notepad", "create file test.txt"
- [ ] Returns clear error message for blocked commands

---

## Story 3.2: Implement Context Management Agent (CMA)
**Story Points:** 2  
**Priority:** 🟠 HIGH  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **remember what happened during execution** so that **I can recover if something fails**.

### Acceptance Criteria

- [ ] Store execution state after each step
- [ ] On failure, retrieve previous state
- [ ] Persist context to database

---

## Story 3.3: Implement Recovery Engine Callbacks
**Story Points:** 3  
**Priority:** 🟠 HIGH  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **recover from failures automatically** so that **I don't give up on the first error**.

### Acceptance Criteria

Recovery Levels (from architecture):
- [ ] **L1: Retry** - Run step again (max 2x)
- [ ] **L2: Rollback** - Undo last action, try different approach
- [ ] **L3: Screenshot** - Take screenshot, call vision, reassess
- [ ] **L4: Rethink** - Re-plan from current state
- [ ] **L5: Safety Check** - Verify not in dangerous state
- [ ] **L6: Abort** - Give up, report to user

### Implementation Details

```python
class RecoveryEngine:
    async def recover(self, failure):
        """failure = {step, error, screenshot, context}"""
        
        if failure['level'] == 1:
            # Retry once more
            return await ea.process(failure['step'])
        
        elif failure['level'] == 2:
            # Undo last action
            await self.undo_last_action()
            return await self.rethink_approach()
        
        elif failure['level'] == 3:
            # Analyze with vision
            analysis = await vision.analyze(failure['screenshot'])
            return await self.adjust_and_retry(analysis)
        
        # ... etc
```

**Tests:**
- 25 error scenario tests

---

## Story 3.4: Implement Error Handling for All Edge Cases
**Story Points:** 2  
**Priority:** 🟠 HIGH  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **handle errors gracefully** so that **crashes don't break the user experience**.

### Acceptance Criteria

- [ ] No unhandled exceptions in agents
- [ ] All errors logged to database
- [ ] All errors reported to user with context
- [ ] System continues after non-critical errors

---

---

# EPIC 4: Learning & Workflow Persistence
**Epic Lead:** Winston (Architect)  
**Duration:** Week 3  
**Story Points:** 6  
**Objective:** Enable system to learn and reuse workflows  
**Success Criteria:** System can repeat workflows without re-planning

---

## Story 4.1: Implement Workflow Learning Agent
**Story Points:** 2  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **remember successful workflows** so that **I can reuse them when the user asks for the same thing**.

### Acceptance Criteria

- [ ] After successful execution, store workflow to database
- [ ] When user asks similar command, recognize it
- [ ] Suggest: "I did this before, should I use that workflow?"
- [ ] User can accept or request new plan

---

## Story 4.2: Implement App Registry Agent
**Story Points:** 1  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **know which applications are installed** so that **I don't try to open apps that don't exist**.

### Acceptance Criteria

- [ ] Query Windows to list installed apps
- [ ] Cache results for performance
- [ ] Update cache on new app installation

---

## Story 4.3: Implement Voice Transcription (Whisper)
**Story Points:** 1  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **user**, I want to **speak commands instead of typing** so that **system is more hands-free**.

### Acceptance Criteria

- [ ] Record audio from microphone
- [ ] Send to Whisper for transcription
- [ ] Return text
- [ ] Accuracy ≥90% for clear speech

---

---

# EPIC 5: Testing & Quality Assurance
**Epic Lead:** Quinn (QA Engineer)  
**Duration:** Parallel with Epics 1-4  
**Story Points:** 15  
**Objective:** Comprehensive test coverage  
**Success Criteria:** >80% code coverage, 215 tests passing

---

## Story 5.1: Write Unit Tests for All Agents
**Story Points:** 5  
**Priority:** 🔴 CRITICAL  
**Assigned To:** Quinn (QA Engineer)  

### Narrative
As a **developer**, I want to **have clear test cases for each agent** so that **I know my code works**.

### Acceptance Criteria

- [ ] 150 unit tests total
- [ ] Each agent has 10-15 unit tests
- [ ] Tests verify: success path, error cases, edge cases

**Test Files to Create:**
- `tests/test_agents/test_rag_agent.py` (15 tests)
- `tests/test_agents/test_ea_agent.py` (30 tests)
- `tests/test_agents/test_oa_agent.py` (15 tests)
- `tests/test_agents/test_safety_agent.py` (10 tests)
- `tests/test_agents/test_cma_agent.py` (10 tests)
- `tests/test_agents/test_web_search_agent.py` (10 tests)
- `tests/test_agents/test_workflow_learner.py` (10 tests)
- `tests/test_services/test_screenshot_service.py` (10 tests)
- `tests/test_services/test_vision_service.py` (20 tests)
- `tests/test_services/test_recovery_engine.py` (25 tests)

---

## Story 5.2: Write Integration Tests
**Story Points:** 4  
**Priority:** 🟠 HIGH  
**Assigned To:** Quinn (QA Engineer)  

### Narrative
As a **developer**, I want to **test agents working together** so that **I know the orchestration works**.

### Acceptance Criteria

- [ ] 40 integration tests
- [ ] E2E workflow tests (user input → execution)
- [ ] Agent communication tests
- [ ] Database persistence tests

---

## Story 5.3: Write End-to-End Workflow Tests
**Story Points:** 3  
**Priority:** 🟠 HIGH  
**Assigned To:** Quinn (QA Engineer)  

### Narrative
As a **QA engineer**, I want to **test real workflows** so that **users will have a working system**.

### Acceptance Criteria

- [ ] 25 E2E tests covering:
  - "Open Notepad and type hello"
  - "Create a new file"
  - "Open and close application"
  - "Navigate website"
  - Error scenarios

---

## Story 5.4: Performance & Load Testing
**Story Points:** 2  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Quinn (QA Engineer)  

### Narrative
As a **DevOps engineer**, I want to **know system performance** so that **I can optimize before launch**.

### Acceptance Criteria

- [ ] End-to-end latency <5 seconds
- [ ] Agent response time <1 second each
- [ ] Screenshot analysis <2 seconds
- [ ] No memory leaks after 1 hour of use

---

---

# EPIC 6: Clarification & Semantic Understanding
**Epic Lead:** John (Product Manager)  
**Duration:** Week 2 + 3  
**Story Points:** 4  
**Objective:** Handle ambiguous user requests intelligently  
**Success Criteria:** System asks clarifying questions when needed

---

## Story 6.1: Implement Clarification Agent
**Story Points:** 1  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **ask clarifying questions when user request is ambiguous** so that **I execute the right action**.

### Acceptance Criteria

- [ ] Recognize ambiguous requests
- [ ] Ask specific clarifying questions
- [ ] Incorporate user answers into plan
- [ ] Example: User: "Send email"
  - System: "To whom? What message?"
  - User: "To Alice, say hello"
  - System: (updated plan)

---

## Story 6.2: Implement Semantic Plan Annotation Agent (SPA)
**Story Points:** 1  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **add business context to plans** so that **I understand why I'm doing something**.

### Acceptance Criteria

- [ ] Annotate each step with business context
- [ ] Example: Step "Click button" → Context "This completes the email sending"
- [ ] Use context for smarter recovery decisions

---

## Story 6.3: Implement System-Action-Agent (SAA)
**Story Points:** 1  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **select the best specific action per situation** so that **generic plans become situational**.

### Acceptance Criteria

- [ ] RAG produces generic plan
- [ ] SAA selects actual implementation
- [ ] Example: Generic "Click Submit" → SAA picks "Press Enter" (in this situation)

---

## Story 6.4: Implement User Agent
**Story Points:** 1  
**Priority:** 🟡 MEDIUM  
**Assigned To:** Amelia (Developer)  

### Narrative
As a **system**, I want to **handle user input/output elegantly** so that **communication is clear**.

### Acceptance Criteria

- [ ] Accept voice, text, UI input
- [ ] Format output for each channel (text, voice, UI)
- [ ] Handle interrupts ("Stop!", "Faster!")

---

---

# TESTING BREAKDOWN (Per Quinn)

## Summary

| Test Type | Count | Coverage | Ownership |
|-----------|-------|----------|-----------|
| Unit tests | 150 | Individual agents/services | Quinn |
| Integration tests | 40 | Agent communication | Quinn |
| E2E tests | 25 | Full workflows | Quinn |
| Performance tests | 10 | Latency, throughput | Quinn |
| Error scenario tests | 30 | Recovery validation | Quinn |
| **TOTAL** | **255** | **>80% coverage** | **Quinn** |

---

# SPRINT TIMELINE

## Week 1: Core Pipeline
- Mon-Tue: Design & setup (John + Winston)
- Wed-Fri: RAG + EA + OA agents (Amelia)
- Parallel: Unit tests (Quinn)

**Completion:** Basic execution works (user command → execute → observe)

---

## Week 2: Vision & Intelligence
- Mon-Tue: Screenshot + Vision services (Amelia)
- Wed-Fri: Web Search, Safety, Recovery L1-L3 (Amelia)
- Parallel: Integration tests (Quinn)

**Completion:** System can see and make smart decisions

---

## Week 3: Learning & Polish
- Mon-Tue: Workflow learning + Voice (Amelia)
- Wed: Error handling + E2E testing (Amelia + Quinn)
- Thu-Fri: Performance testing + Bug fixes + Launch prep (Amelia + Quinn)

**Completion:** Production-ready system

---

# ACCEPTANCE CRITERIA FOR RELEASE

Before shipping to users, ALL must be true:

- [ ] 255 tests passing (100% green)
- [ ] Code coverage >80%
- [ ] 10 real workflows tested with real users
- [ ] End-to-end latency <5 seconds (measured, not theoretical)
- [ ] Error recovery success rate >90%
- [ ] No unhandled exceptions in production logs
- [ ] Architecture approved by Winston
- [ ] Product requirements verified by John
- [ ] QA sign-off by Quinn

---

# NOTES FOR DEVELOPMENT

## Async/Await Requirements
- Every agent must be async
- Every database call must be async
- Never block with sync operations

## Database Persistence
- Every action logged to database
- Every context snapshot saved
- Every error logged with full context

## Error Handling
- Try/catch on all network calls
- Try/catch on all file operations
- Try/catch on all subprocess calls
- Must never crash on user input

## Deployment
- Build docker images for each service
- Use docker-compose for local development
- Test on Windows 10/11 (primary target)

---

**Created by:** John (Product Manager), with input from Winston, Amelia, Quinn, Mary  
**Status:** Ready for Sprint Planning (Bob)  
**Next Step:** `/sprint-planning` command to organize into sprints

