# JARVIS AI - DEVELOPER QUICK START (AMELIA)
## What to Build, When, and How Starting Monday
**For:** Amelia (Developer)  
**Date:** February 24, 2026  
**Sprint:** 3-week production implementation  
**Total Effort:** 40 days = 3 weeks  

---

## 🎯 Your Mission

**In 3 weeks, implement missing code to make JARVIS production-ready.**

**Current State:**
- ✅ Architecture documented (perfect)
- ✅ Backend infrastructure (working)
- ✅ Frontend UI (working)
- ❌ **13 agents not implemented (0% code)**
- ❌ **Execution engine missing (0% code)**
- ❌ **Vision integration missing (0% code)**

**Your Goal:**
Write ~6,200 lines of Python code that makes these work so users can say "Open Gmail" and it actually opens.

---

## 📋 What Exists (Use These)

### Already Working
- `backend/app/services/ollama_service.py` - Calls LLM ✅
- `backend/app/agents/protocol.py` - BaseAgent template ✅
- `backend/app/agents/registry.py` - Can register agents ✅
- `backend/app/agents/orchestrator.py` - Can dispatch to agents ✅
- `backend/core/database.py` - 18 tables, async ORM ✅
- Frontend React app - 167 tests passing ✅
- Electron app built - `frontend/dist/JARVIS AI Portable.exe` ✅

### Already Configured But Not Used
- `backend/app/services/recovery_engine.py` - Framework exists, needs callbacks
- `backend/app/services/voice_service.py` - Framework exists, needs transcription code

### Doesn't Exist (You Build)
- `backend/app/agents/rag_agent.py` - RAG agent (YOU)
- `backend/app/agents/ea_agent.py` - Execution agent (YOU)
- `backend/app/agents/oa_agent.py` - Observer agent (YOU)
- `backend/app/agents/safety_agent.py` - Safety rules (YOU)
- `backend/app/agents/cma_agent.py` - Context management (YOU)
- `backend/app/agents/web_search_agent.py` - Web search (YOU)
- `backend/app/agents/clarification_agent.py` - Ask questions (YOU)
- `backend/app/agents/spa_agent.py` - Semantic annotation (YOU)
- `backend/app/agents/saa_agent.py` - Action selection (YOU)
- `backend/app/agents/workflow_learner_agent.py` - Learn workflows (YOU)
- `backend/app/agents/app_registry_agent.py` - List apps (YOU)
- `backend/app/agents/user_agent.py` - I/O handling (YOU)
- `backend/app/services/screenshot_service.py` - Capture screenshots (YOU)
- `backend/app/services/vision_service.py` - moondream integration (YOU)

---

## 📅 WEEK-BY-WEEK BREAKDOWN

# WEEK 1: CORE EXECUTION (5 days)

## Monday: RAG Agent
**What:** Plan generation from user input  
**File:** Create `backend/app/agents/rag_agent.py` (150 lines)  
**Tests:** Write 10 unit tests  
**Time:** 1 day

```python
# What to write (pseudocode)
class RAGAgent(BaseAgent):
    async def process(self, user_input):
        # Call ollama_service
        # Send: "Break this into steps: ${user_input}"
        # Get back: structured step list
        # Validate each step has: action, target, confidence
        # Return: {"plan": [...], "confidence": 0.92}
```

**Acceptance Criteria:**
- Input: "Open Notepad and type hello"
- Output: 
  ```json
  {
    "steps": [
      {"action": "open_app", "app": "notepad"},
      {"action": "wait", "seconds": 2},
      {"action": "type", "text": "hello"}
    ],
    "confidence": 0.95
  }
  ```

**Debug:** Call ollama from command line first:
```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"qwen2.5:3b", "prompt":"List steps to open Notepad"}'
```

---

## Tuesday-Wednesday: Execution Agent
**What:** Actually execute actions on desktop  
**File:** Create `backend/app/agents/ea_agent.py` (250 lines)  
**Tests:** Write 25 unit tests + 5 E2E tests  
**Time:** 2 days

```bash
# Install first
pip install pyautogui pillow pygetwindow pywin32
```

```python
# What to write
class ExecutionAgent(BaseAgent):
    async def process(self, step):
        action = step['action']
        
        if action == 'click':
            # pyautogui.click(step['x'], step['y'])
            pass
        elif action == 'type':
            # pyautogui.typewrite(step['text'])
            pass
        elif action == 'screenshot':
            # image = pil.ImageGrab.grab()
            # image.save(f"screenshots/{timestamp}.png")
            pass
        elif action == 'open_app':
            # subprocess.run(f"start {step['app']}")
            pass
        
        return {"success": True, "screenshot": "path/to/image.png"}
```

**Testing:** 
- Test 1: Click coordinates → Mouse moves
- Test 2: Type text → Text appears  
- Test 3: Screenshot → File created
- Test 4: Open app → Process starts
- Test 5: Real workflow → All work together

**Critical:** Test on real desktop, not mocked!

---

## Thursday: Observer Agent
**What:** Verify actions succeeded  
**File:** Create `backend/app/agents/oa_agent.py` (120 lines)  
**Tests:** Write 10 unit tests  
**Time:** 1 day

```python
# What to write
class ObserverAgent(BaseAgent):
    async def process(self, step_result):
        # step_result contains: {"step": {...}, "screenshot": "path"}
        # Analyze screenshot to see if action succeeded
        # Return: {"success": True/False, "confidence": 0.85}
        pass
```

---

## Thursday Afternoon: Orchestrator
**What:** Coordinate agents in sequence  
**File:** Modify `backend/app/agents/orchestrator.py` (100 lines added)  
**Tests:** Write 10 integration tests  
**Time:** 1 day

```python
# Pseudocode
async def execute(user_input):
    # 1. RAG: Generate plan
    plan = await rag.process(user_input)
    
    # 2. For each step: EA → OA
    for step in plan['steps']:
        result = await ea.process(step)
        observation = await oa.process(result)
        log_to_db(result, observation)
    
    # 3. Return execution log
    return execution_log
```

**Friday PM:** Demo for the team
- User speaks: "Open Notepad"
- System plans it
- System executes it
- System confirms success
- Everyone cheers 🎉

---

# WEEK 2: VISION & INTELLIGENCE (5 days)

## Monday: Screenshot Service
**What:** Capture desktop state  
**File:** Create `backend/app/services/screenshot_service.py` (80 lines)  
**Time:** 0.5 days

```python
def take_screenshot(self) -> str:
    """Returns path to screenshot"""
    image = PIL.ImageGrab.grab()
    timestamp = datetime.now().isoformat().replace(':', '-')
    path = f"screenshots/{timestamp}.png"
    image.save(path)
    return path
```

---

## Monday-Tuesday: Vision Service (moondream)
**What:** Analyze screenshots with AI vision  
**File:** Create `backend/app/services/vision_service.py` (250 lines)  
**Tests:** Write 20 unit tests  
**Time:** 1.5 days

```python
# Key challenge: moondream integration
# Model is already downloaded: ollama run moondream

class VisionService:
    def __init__(self):
        # Load moondream model (first run takes time)
        self.model = load_moondream()
    
    async def analyze(self, image_path):
        """Send screenshot to moondream and get analysis"""
        # Call moondream with: "What's on this screen? List elements."
        # Parse response
        # Return structured data
        
        # Example output:
        {
            "elements": [
                {"name": "Notepad window", "type": "window"},
                {"name": "File menu", "type": "button", "x": 50, "y": 20},
                {"name": "Text area", "type": "textarea", "contains": "hello"}
            ],
            "page_title": "Untitled - Notepad",
            "analysis": "Notepad is open with 'hello' typed"
        }
```

**Testing:** Use real screenshots from Week 1
- Screenshot with Notepad open
- Screenshot with email client
- Screenshot with error dialog
- Verify all elements detected

---

## Wednesday: Connect Vision to Execution
**What:** Use vision to verify actions worked  
**File:** Modify `backend/app/agents/oa_agent.py` (add 50 lines)  
**Time:** 1 day

Update OA to use VisionService instead of guessing:
```python
# Before: Guessing if action worked
# After: Asking vision "Did this work?"

async def analyze_screenshot(self, screenshot_path):
    analysis = await vision_service.analyze(screenshot_path)
    # Now you have real data about what happened
    return {"success": True, "evidence": analysis}
```

---

## Thursday: Web Search Agent
**What:** Google search capability  
**File:** Create `backend/app/agents/web_search_agent.py` (80 lines)  
**Time:** 1 day

```bash
pip install requests beautifulsoup4
```

```python
class WebSearchAgent(BaseAgent):
    async def process(self, query):
        # Search Google
        # Return top 3 results
        # Cache to avoid duplicate searches
        
        # Example: Query "how to create React app"
        # Returns: [
        #   {"title": "...", "url": "...", "snippet": "..."},
        #   ...
        # ]
```

---

## Friday: Safety + Context
**Story 3.1 + 3.2:** Safety guardrails + Error handling  
**File:** Create `backend/app/agents/safety_agent.py` (80 lines)  
**Time:** 1 day

```python
class SafetyAgent(BaseAgent):
    async def process(self, command):
        # Block dangerous: "rm -rf /", "delete system32"
        # Allow safe: "open notepad"
        
        dangerous_keywords = [
            "rm -rf", "format", "delete system32", "sudo"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in command:
                return {"allowed": False, "reason": "Dangerous command"}
        
        return {"allowed": True}
```

---

# WEEK 3: LEARNING & LAUNCH (5 days)

## Monday-Tuesday: Context & Recovery
**File:** Modify existing `backend/app/services/recovery_engine.py` (add 150 lines)  
**Time:** 2 days

Current state: Recovery framework exists, callbacks not implemented

```python
# Add actual recovery logic to each level:

class RecoveryEngine:
    async def recover(self, failure):
        level = failure['level']
        
        if level == 1:
            # RETRY: Run step again
            return await self.retry_step()
        
        elif level == 2:
            # ROLLBACK: Undo last action
            return await self.undo_and_retry()
        
        elif level == 3:
            # SCREENSHOT: Take screenshot, analyze with vision
            screenshot = await screenshot_service.take_screenshot()
            analysis = await vision_service.analyze(screenshot)
            return await self.adjust_and_retry(analysis)
        
        elif level == 4:
            # RETHINK: Re-plan from current state
            return await self.replan_workflow()
        
        # ... etc
```

**Test:** Simulate failures and verify recovery
- Click non-existent button → Retry (L1) ✅
- Type into closed window → Re-plan (L4) ✅

---

## Wednesday: Learning + Voice
**Files:** 
- Create `backend/app/agents/workflow_learner_agent.py` (100 lines)
- Create `backend/app/agents/app_registry_agent.py` (60 lines)  
- Add to `backend/app/services/voice_service.py` (100 lines)

**Time:** 1 day

```python
# Workflow Learner
class WorkflowLearnerAgent(BaseAgent):
    async def process(self, completed_workflow):
        # Store successful workflow to database
        # Next time user says something similar,
        # suggest: "Should I use this workflow?"
        pass

# App Registry
class AppRegistryAgent(BaseAgent):
    async def process(self, query):
        # Query Windows registry for installed apps
        # Return list of app names
        # Use subprocess: Get-AppxPackage (PowerShell)
        pass

# Voice Service (add transcription)
async def transcribe_audio(self, audio_file):
    # Call Whisper via ollama
    # Return transcribed text
    # Test: Record "hello" → Should return "hello"
```

---

## Thursday: Full Test Suite
**Your job:** Run tests with Quinn, verify coverage

```bash
# Run all tests
cd backend
pytest tests/ -v --cov=app --cov-report=html

# Should see: >80% coverage
# Result file: htmlcov/index.html
```

Expected result: 250-300 tests passing ✅

---

## Friday: Launch Preparation
**Checklist before shipping:**
- [ ] All tests passing (100% green)
- [ ] Code coverage >80%
- [ ] No unhandled exceptions in logs
- [ ] Performance <5 seconds end-to-end
- [ ] Recovery success rate >90%
- [ ] User workflows work (demo)

**If all ✅:** Proceed to production deployment

---

## 🏗️ Best Practices (DO THIS)

### 1. **Always Run Tests First**
```bash
pytest tests/test_agents/test_rag_agent.py -v
```
Before committing, verify your tests pass.

### 2. **Use Type Hints**
```python
# GOOD
async def process(self, input_data: dict) -> dict:
    pass

# BAD
async def process(self, input_data):
    pass
```

### 3. **Add Logging**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Starting RAG agent with input: {user_input}")
logger.error(f"Failed to click at {x},{y}: {error}")
```

### 4. **Error Handling**
```python
# GOOD
try:
    pyautogui.click(x, y)
except Exception as e:
    logger.error(f"Click failed: {e}")
    return {"success": False, "error": str(e)}

# BAD
pyautogui.click(x, y)  # Will crash if x,y invalid
```

### 5. **Commit Often**
```bash
git add backend/app/agents/rag_agent.py
git commit -m "feat: RAG agent basic implementation"
```
Every 2-3 hours, commit your work so you don't lose it.

### 6. **Get Code Review from Winston**
After writing code, ask Winston to review before testing:
- Is this correct architecture?
- Are there performance issues?
- Did I miss error cases?

### 7. **Work with Quinn on Tests**
Quinn writes tests while you write code (parallel):
- You write code Friday
- Quinn writes tests Friday
- Both merged Monday if both pass

---

## 🔧 Development Environment Setup (Do This Monday Morning)

```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt
pip install pyautogui pillow pygetwindow pywin32

# 2. Start backend server (separate terminal)
cd backend
python -m uvicorn app.main:app --port 9000 --reload

# 3. Test it's running
curl http://localhost:9000/health

# 4. Run existing tests
pytest tests/ -v

# 5. You're ready to code!
```

---

## 🎯 Success Metrics (HOW YOU'LL BE JUDGED)

### Sprint 1 (Week 1)
- ✅ RAG generates plans
- ✅ EA executes actions
- ✅ OA observes results
- ✅ 60 tests passing
- ✅ Real demo works

### Sprint 2 (Week 2)
- ✅ Screenshots working
- ✅ moondream analyzing
- ✅ 133 cumulative tests
- ✅ Vision feedback loop working

### Sprint 3 (Week 3)
- ✅ Recovery working >90%
- ✅ Workflows learning
- ✅ 300 total tests passing
- ✅ Production-ready checklist complete

---

## ⚠️ Common Pitfalls (DON'T DO THIS)

### ❌ Don't Block on Async/Await
```python
# WRONG
result = ollama_service.call_model(...)  # Blocks!

# RIGHT
result = await ollama_service.call_model(...)  # Non-blocking
```

### ❌ Don't Mock Everything
```python
# WRONG (in tests)
pyautogui.click = Mock()  # Can't test real clicks

# RIGHT
Test on real desktop at least once
```

### ❌ Don't Ignore Error Handling
```python
# WRONG
screenshot = PIL.ImageGrab.grab()  # Crashes if screen locked

# RIGHT
try:
    screenshot = PIL.ImageGrab.grab()
except Exception as e:
    logger.error(f"Screenshot failed: {e}")
    return None
```

### ❌ Don't Skip Tests
```python
# WRONG
Write code, skip tests, hope it works

# RIGHT
Test-driven development: tests first, then code
```

---

## 📞 Getting Help

### If You're Stuck
**Before asking for help:**
1. Read the error message carefully
2. Google it
3. Check existing similar code
4. Try print debugging
5. Then ask

**Who to ask:**
- **Architecture questions:** Winston
- **Testing questions:** Quinn
- **Product questions:** John
- **Planning questions:** Bob

---

## 📈 Your Weekly Goals

| Week | Primary Goals | Deliverables |
|------|---------------|--------------|
| 1 | Agents talk to each other, basic execution works | RAG + EA + OA agents, 60 tests |
| 2 | System can see and understand | Screenshot + Vision services, 73 new tests |
| 3 | System smart & robust, ready to ship | Learning + Recovery, 155 new tests, launch ready |

---

## 🚀 Ready?

**Monday Morning:**
1. Attend standup @ 9 AM
2. Get this story assigned: Story 1.1 (RAG Agent)
3. Create branch: `git checkout -b story/1.1-rag-agent`
4. Start coding
5. Have Quinn write tests in parallel

**You've got this! 💪**

---

**Created By:** John (Product Manager) + Bob (Scrum Master)  
**For:** Amelia (Developer)  
**Timeline:** 3 weeks to production  
**Story:** Change how people use computers locally, with AI

