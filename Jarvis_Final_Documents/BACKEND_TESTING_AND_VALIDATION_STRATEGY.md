# BACKEND TESTING & VALIDATION STRATEGY
## Comprehensive Testing Plan for Entire Backend Development
**Created By:** Bob (Scrum Master) & Quinn (QA Engineer)  
**Date:** February 24, 2026  
**Purpose:** Ensure all backend changes work correctly with REAL workflows before deployment  

---

# 📋 LOGGING CONFIGURATION CONFIRMED

## Where Logs Are Stored

### **Main Application Logs**
**Location:** `./data/logs/jarvis.log`  
**Format:** JSON (structured, queryable)  
**Rotation:** 10 MB per file, 5 backups (50 MB max)  
**Level:** INFO (configurable via `JARVIS_LOG_LEVEL` or code)

### **Error Logs (Dedicated)**
**Location:** `./data/logs/jarvis_errors.log`  
**Format:** JSON (structured, same format)  
**Rotation:** 5 MB per file, 3 backups (15 MB max)  
**Level:** ERROR only (critical issues separated)

### **Database Execution Records**
**Location:** `./data/jarvis.db` (SQLite)  
**Tables:**
- `execution_logs` - Every step executed + result
- `chat_sessions` - Every conversation
- `workflows` - Saved successful workflows
- `workflow_executions` - Execution history
- `context_snapshots` - State for recovery

### **Console Output**
**Format:** Human-readable (colored, dev-friendly)  
**When:** Real-time as code runs

### **Access Logs**
**Location:** `./data/logs/` (via FastAPI access logging)  
**Format:** JSON or text
**Contains:** HTTP requests, responses, latencies

---

## Log Flow Example

```
User Action: "Open Notepad and type hello"
    ↓
[1] Console Output (real-time):
    INFO: RAG agent processing: "Open Notepad and type hello"
    INFO: Plan generated: 3 steps
    INFO: EA executing step 1/3: open_app
    ✓ Success

[2] JSON Log File (jarvis.log):
    {
      "timestamp": "2026-02-24T14:30:45.123Z",
      "level": "INFO",
      "agent": "rag_agent",
      "event": "plan_generated",
      "steps": 3,
      "confidence": 0.95
    }

[3] Database (execution_logs):
    INSERT INTO execution_logs (
      workflow_id, step_number, action, status, timestamp
    ) VALUES (
      '550e8400', 1, 'open_app', 'success', '2026-02-24T14:30:45Z'
    )

[4] Chat Session (chat_sessions table):
    INSERT INTO chat_sessions (
      user_id, message, status, created_at
    ) VALUES (
      'user_123', 'Open Notepad and type hello', 'completed', ...
    )

[5] Workflow Saved (workflows table) IF successful:
    INSERT INTO workflows (
      name, steps, success_rate, created_at
    ) VALUES (
      'Open Notepad and type', [...], 1.0, ...
    )
```

---

# 🎯 BACKEND TESTING STRATEGY

## Testing Pyramid

```
                      ▲
                     /│\
                    / │ \
                   /  │  \        E2E Tests (5 high-value workflows)
                  /───┼───\       - Real user scenarios
                 /    │    \      - Chrome + Gmail + Draft Email
                /─────┼─────\     - File operations
               /      │      \    - System integration
              /───────┼───────\
             /        │        \
            /   Integration    \   Integration Tests (40 tests)
           /          │          \ - Agent communication
          /───────────┼───────────\ - Database persistence
         /            │            \ - Recovery chains
        /─────────────┼─────────────\ - Context snapshots
       /    Unit Tests (150 tests)   \
      /________________________ ______\
     |  Foundations: Code works      |
     |  - Each module isolated       |
     |━━━━━━━━━━━━━━━━━━━━━━━━━━━━━|
     +─ Performance: <5s latency
     +─ Code coverage: >80%
     +─ Error handling: All paths
     +─ Data integrity: No corruption
     +─ Regression: No broken features
```

---

# 📊 COMPREHENSIVE TEST SCENARIOS

## Category 1: Core Functionality Tests

### Scenario 1.1: Open Application (Chrome)
**File:** `tests/test_scenarios/test_open_chrome.py`  
**Test Type:** E2E + Integration  
**Complexity:** Medium  

```python
"""
Test: User says "Open Chrome"

Steps:
1. RAG Agent: Parse "Open Chrome" → Plan: [{"action": "open_app", "app": "chrome"}]
2. EA Agent: Execute open_app → Process started
3. OA Agent: Take screenshot → Verify Chrome window appeared
4. Context: Store execution in database
5. Verification: Check execution_logs table

Assertions:
- ✓ Plan generated with correct steps
- ✓ Chrome process started (get PID)
- ✓ Window appears in screenshot within 3 seconds
- ✓ execution_logs table has record
- ✓ chat_sessions table shows "completed"
- ✓ Total time <5 seconds

Complex Inputs to Test:
- Exact name: "Open Chrome" ✓
- Lowercase: "open chrome" ✓
- With path: "Open C:\Program Files\Chrome\chrome.exe" ✓
- With parameters: "Open Chrome and go to Google" ✓
- Typos: "Open Chrom" (should fail gracefully) ✓
```

**Success Criteria:**
- [ ] Chrome window opens
- [ ] Execution logged to console (JSON)
- [ ] Database records created
- [ ] Workflow can be replayed

---

### Scenario 1.2: Open Gmail in Chrome
**File:** `tests/test_scenarios/test_open_gmail.py`  
**Test Type:** E2E (High Value)  
**Complexity:** High (multiple steps)  

```python
"""
Test: User says "Open Gmail"

Expected Plan (RAG Generated):
[
  {"order": 1, "action": "open_app", "app": "chrome"},
  {"order": 2, "action": "wait", "seconds": 3},
  {"order": 3, "action": "screenshot"},
  {"order": 4, "action": "navigate", "url": "https://gmail.com"},
  {"order": 5, "action": "wait", "seconds": 3},
  {"order": 6, "action": "screenshot"}
]

Each Step Verification:
1. Open Chrome:
   ✓ Process starts
   ✓ Screenshot shows window
   ✓ execution_logs records: {action: "open_app", status: "success"}

2. Wait 3 seconds:
   ✓ Waits exactly 3 seconds
   ✓ execution_logs records: {action: "wait", duration: 3}

3. Take screenshot:
   ✓ Screenshot file created
   ✓ File size > 100KB (not empty/corrupted)
   ✓ execution_logs records with filename

4. Navigate to Gmail:
   ✓ URL typed into address bar
   ✓ execution_logs records: {action: "navigate", url: "..."}

5. Wait 3 seconds:
   ✓ Page loads
   ✓ Screenshot shows Gmail interface
   ✓ moondream analysis shows: "Gmail interface detected"

6. Screenshot of result:
   ✓ Gmail UI visible
   ✓ execution_logs records final state

Database Verification:
- chat_sessions: 1 record, status="completed"
- execution_logs: 6 records (one per step)
- workflows: 1 record (saved for reuse)
- context_snapshots: 6 records (state after each step)

Assertions:
✓ All 6 steps completed
✓ No errors in execution_logs
✓ No errors in jarvis.log
✓ No errors in jarvis_errors.log
✓ Total time <10 seconds
✓ Workflow can be replayed identically

Complex Input Testing:
- "Open Gmail" → Auto-opens Chrome + navigates ✓
- "Open Gmail in Firefox" → Use Firefox instead ✓
- "Open Gmail in incognito mode" → Parameters passed ✓
- "I want to check my email" → Ambiguous, ask clarification ✓
"""
```

**Success Criteria:**
- [ ] Gmail interface loads
- [ ] All 6 steps logged
- [ ] Workflow stored for reuse
- [ ] moondream identifies Gmail correctly
- [ ] Can replay same workflow

---

### Scenario 2.1: Draft Email in Gmail
**File:** `tests/test_scenarios/test_draft_email_gmail.py`  
**Test Type:** E2E (Critical Path)  
**Complexity:** Very High  

```python
"""
Test: User says "Draft an email to john@example.com saying hello"

Expected Workflow:
[
  {"action": "click", "target": "Compose button"},
  {"action": "type", "target": "To field", "text": "john@example.com"},
  {"action": "click", "target": "Subject field"},
  {"action": "type", "text": "Hello"},
  {"action": "click", "target": "Body"},
  {"action": "type", "text": "Hello John, just saying hi. Best regards."},
  {"action": "click", "target": "Save Draft button"},
  {"action": "screenshot"}
]

Step-by-Step Verification:

1. RAG Agent Planning:
   ✓ Understands: email, recipient, message
   ✓ Generates: 8 steps with click/type actions
   ✓ Confidence score >0.9
   ✓ Logged: {event: "plan_generated", steps: 8}

2. Click "Compose":
   ✓ Mouse moves to button
   ✓ Screenshot before: Gmail inbox visible
   ✓ Mouse clicks
   ✓ Screenshot after: Compose window opened
   ✓ OA Agent verifies: "Compose window appeared"
   ✓ Logged: {action: "click", location: [100, 50], status: "success"}

3. Type Email Address:
   ✓ "john@example.com" typed character by character
   ✓ Each character logged in database
   ✓ Screenshot shows: Email in To field
   ✓ OA Agent verifies: "Email address entered correctly"
   ✓ Logged: {action: "type", text: "john@example.com", chars_typed: 18}

4. Click Subject Field:
   ✓ Mouse moves and clicks
   ✓ Field becomes active (cursor visible)
   ✓ Logged: {action: "click", status: "success"}

5. Type Subject:
   ✓ "Hello" typed
   ✓ Screenshot shows text in subject
   ✓ Logged: {action: "type", text: "Hello"}

6. Click Body:
   ✓ Mouse to message body
   ✓ Field active
   ✓ Logged: {action: "click"}

7. Type Message:
   ✓ Full message typed with newlines
   ✓ No character loss
   ✓ Logged: {action: "type", text_length: 49}

8. Save Draft:
   ✓ Click Save button
   ✓ Draft saved to Gmail
   ✓ Screenshot shows "Draft saved" confirmation
   ✓ OA Agent: "Draft successfully saved"
   ✓ Logged: {action: "click_save", status: "success"}

Database Records Created:
- chat_sessions[1]: message="Draft email...", status="completed"
- execution_logs[8]: All 8 steps with timestamps
- workflows[1]: "Draft email" workflow saved
- context_snapshots[8]: Full state at each step for recovery
- workflow_executions[1]: Execution record linking session to workflow

Verification:
✓ All 8 steps completed
✓ No errors in any log file
✓ Draft visible in Gmail (manual verification possible)
✓ Workflow saved for reuse
✓ Total time <15 seconds
✓ All data integrity checks pass

Complex Input Scenarios:
- "Draft an email" → Ask who to send to
- "Email john@example.com" → Partial input, ask for message
- "Reply to: Hello [long message]" → Handle reply workflow
- "Draft to john with attachment" → Edge case: no file ops yet
- Multiple recipients → "john@ex.com and jane@ex.com"
- Special characters → "Test & verify!"
- Very long message → 1000+ characters
"""
```

**Success Criteria:**
- [ ] Email drafted completely
- [ ] All 8 steps logged
- [ ] Workflow saved & reusable
- [ ] Database integrity maintained
- [ ] Complex inputs handled gracefully

---

## Category 2: Workflow Persistence Tests

### Scenario 3.1: Save and Replay Workflow
**File:** `tests/test_scenarios/test_workflow_persistence.py`  
**Test Type:** Integration  

```python
"""
Test: Save a workflow and replay it

Phase 1 - Initial Execution:
User: "Open Notepad and type hello world"

Step 1: Execute workflow
- RAG plans: Open Notepad + Type "hello world"
- EA executes both steps
- OA verifies both succeeded
- Workflow saved to workflows table with:
  {
    "name": "Open Notepad and type hello world",
    "steps": [
      {"action": "open_app", "app": "notepad"},
      {"action": "type", "text": "hello world"}
    ],
    "success_rate": 1.0,
    "created_at": "2026-02-24T14:30:00Z",
    "times_executed": 1
  }

Database Check:
✓ workflows table: 1 new record
✓ execution_logs: 2 records for this execution
✓ context_snapshots: 2 records
✓ chat_sessions: 1 record marked "completed"

Phase 2 - Workflow Recognition:
User 5 minutes later: "Open Notepad and type hello world" (exact same request)

Step 1: RAG Agent processes
- Recognizes this is a similar request
- Queries workflows table for matches
- Finds exact match with 100% success rate
- Returns: "I've done this before! Want me to reuse it?"

Step 2: User accepts (automatic in test)
- Workflow retrieved from database
- Executed step-by-step (same 2 steps)
- All steps succeed
- execution_logs updated
- workflows table updated: times_executed = 2

Database Check:
✓ workflows[same_record].times_executed: 2
✓ execution_logs: 2 new records (different session)
✓ context_snapshots: 2 new records
✓ Execution time: FASTER (no re-planning) - verify <3 seconds

Assertions:
✓ Workflow recognized from database
✓ Execution without re-planning
✓ All steps succeeded
✓ Logged correctly
✓ Performance improved (cache benefit)

Phase 3 - Variation Handling:
User: "Open Notepad and type something different"

Step 1: RAG Agent
- Recognizes "Open Notepad" is similar to saved workflow
- But "different" is not "hello world"
- Suggests: "I can open Notepad, but what should I type?"
- User: "Type: new message"

Result:
✓ Partially reused workflow (first step)
✓ New step added
✓ All executed successfully
✓ New workflow saved: "Open Notepad and type new message"

Final Database State:
✓ workflows table: 2 records (original + variation)
✓ Each has success history
✓ Can reuse either at any time
"""
```

**Success Criteria:**
- [ ] Workflows saved to database
- [ ] Recognized on repeat requests
- [ ] Replayed without errors
- [ ] Performance improvement verified
- [ ] Variations handled correctly

---

## Category 3: Chat Session Management Tests

### Scenario 4.1: Single Chat Session
**File:** `tests/test_scenarios/test_chat_session_single.py`  
**Test Type:** Integration  

```python
"""
Test: Complete chat session lifecycle

Step 1: Session Start
- User initiates: "Open Gmail"
- Backend creates chat_sessions record:
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "test_user_123",
    "created_at": "2026-02-24T14:30:00Z",
    "title": "Open Gmail",
    "status": "in_progress",
    "message_count": 1
  }
- Stored in database

Step 2: Execution
- Workflow executes (open Chrome + navigate Gmail)
- Each step logged
- ExecutionLogs linked to this session
- ContextSnapshots linked to this session

Step 3: Completion
- Workflow finishes successfully
- chat_sessions updated:
  {
    ...,
    "status": "completed",
    "completed_at": "2026-02-24T14:35:00Z",
    "duration_seconds": 300,
    "message_count": 1,
    "steps_executed": 3
  }

Database Verification:
✓ chat_sessions[session_id].status = "completed"
✓ chat_sessions[session_id].completed_at is set
✓ execution_logs filtered by session_id: 3 records
✓ context_snapshots filtered by session_id: 3 records
✓ All records timestamped correctly
✓ No orphaned records (all linked to session)

Assertions:
✓ Session created
✓ Execution linked to session
✓ Session properly closed
✓ All data integrity maintained
✓ Can retrieve full session history
"""
```

**Success Criteria:**
- [ ] Session created & tracked
- [ ] All execution linked to session
- [ ] Session properly closed
- [ ] Full history retrievable

---

### Scenario 4.2: Multiple Sessions (No Data Leakage)
**File:** `tests/test_scenarios/test_chat_session_multiple.py`  
**Test Type:** Integration (Data Integrity)  

```python
"""
Test: Multiple concurrent/sequential sessions don't interfere

Setup:
- Create User_A, User_B
- Each has multiple sessions

Session 1 (User_A): "Open Gmail"
Session 2 (User_B): "Open Outlook" (concurrent or sequential)
Session 3 (User_A): "Draft email"
Session 4 (User_B): "Search email"

Verification:

1. No Data Mixing:
   ✓ User_A chat_sessions: Only 2 records
   ✓ User_B chat_sessions: Only 2 records
   ✓ No cross-user data visible
   ✓ execution_logs properly filtered by session_id

2. Data Isolation:
   ✓ Session 1 exec logs: Only Gmail steps
   ✓ Session 2 exec logs: Only Outlook steps
   ✓ Session 3 exec logs: Only email draft steps
   ✓ Session 4 exec logs: Only search steps

3. Workflow Isolation:
   ✓ Workflows saved per session
   ✓ User_A workflows not visible to User_B
   ✓ Context snapshots isolated per session

4. Cleanup:
   ✓ After sessions complete, verify no memory leaks
   ✓ Verify database cleanup (old sessions archived)
   ✓ Verify no orphaned records

Database Integrity Checks:
✓ Foreign key constraints: All sessions have valid user_id
✓ Referential integrity: All exec_logs have valid session_id
✓ No orphaned records: Every record linked to parent
✓ Timestamp consistency: Created < Completed
✓ No NULL values in required fields
"""
```

**Success Criteria:**
- [ ] No data mixing between sessions
- [ ] Complete isolation maintained
- [ ] Data accessible only to correct user
- [ ] Database constraints enforced

---

## Category 4: Error Handling & Recovery Tests

### Scenario 5.1: Action Fails - Recovery
**File:** `tests/test_scenarios/test_error_recovery.py`  
**Test Type:** Integration (Critical)  

```python
"""
Test: System recovers gracefully when action fails

Scenario: User says "Click on non-existent button"

Step 1: Planning
- RAG: "Click button at location [500, 500]"
- Confidence: 0.7 (lower since no visual confirmation yet)
- Plan: [{"action": "click", "location": [500, 500]}]

Step 2: Execution Attempt
- EA: Click at [500, 500]
- But button doesn't exist (user made up location)

Step 3: Failure Detection
- OA: Takes screenshot
- Analyzes: "Nothing changed, click may have failed"
- Returns: {success: false, confidence: 0.4}
- Logged: {action: "click", status: "failed", reason: "no_ui_change"}

Step 4: Recovery Level 1 (RETRY)
- Recovery engine: Retry same action once more
- Result: Still fails
- Logged: {recovery_level: 1, status: "failed", attempt: 2}

Step 5: Recovery Level 2 (ROLLBACK)
- Recovery: Undo last action
- But nothing to undo (first action)
- Move to Level 3

Step 6: Recovery Level 3 (SCREENSHOT + REANALYZE)
- Takes screenshot
- Calls moondream: "What's visible? Where can I click?"
- moondream returns: "I see Notepad, menu bar, but no button at [500, 500]"
- Logged: {recovery_level: 3, analysis: "..."}

Step 7: Recovery Level 4 (RETHINK)
- Re-plan from current state
- RAG: "Button not found, suggest alternatives"
- New plan: "Try clicking visible button instead"
- Logged: {recovery_level: 4, new_plan: [...]}

Step 8: Recovery Level 5 (SAFETY CHECK)
- Verify system not in bad state
- Check: No files deleted, no permissions broken
- Status: OK to continue
- Logged: {recovery_level: 5, status: "safe"}

Step 9: Recovery Level 6 (ABORT)
- If all recovery failed, abort gracefully
- Return error message to user: "Couldn't find button. Try again."
- Logged: {recovery_level: 6, status: "aborted", user_message: "..."}

Database Logging:
✓ execution_logs: All steps + recovery attempts
✓ error_logs: Specific record for this failure
✓ recovery_attempts: Tracked in separate table
✓ No exceptions thrown (all handled)

File Logging:
✓ jarvis.log: All INFO messages + recovery flow
✓ jarvis_errors.log: ERROR level record of failure
✓ Both files properly formatted JSON

User Experience:
✓ No system crash
✓ Clear error message
✓ Option to retry or try different approach
✓ Full execution history available for debugging

Assertions:
✓ Recovery attempted (all levels)
✓ Logged completely
✓ No unhandled exceptions
✓ System remains stable
✓ User can understand what happened
"""
```

**Success Criteria:**
- [ ] Recovery attempted at all levels
- [ ] Graceful failure (no crash)
- [ ] Clear error messages
- [ ] Complete logging
- [ ] System stable after error

---

## Category 5: Complex Input Scenarios

### Scenario 6.1: Long Message with Special Characters
**File:** `tests/test_scenarios/test_complex_inputs.py`  
**Test Type:** Unit + Integration  

```python
"""
Test: System handles complex, unusual inputs

Input 1: Very Long Message
- 2000+ characters
- Multiple paragraphs
- Newlines and tabs
Test: ✓ System doesn't truncate
Test: ✓ All characters preserved
Test: ✓ Database stores correctly (TEXT field, not VARCHAR(100))

Input 2: Special Characters
- "Test!@#$%^&*()"
- Unicode: "你好世界" (Chinese)
- Emoji: "😀🎉✨"
Test: ✓ Characters preserved
Test: ✓ No encoding errors
Test: ✓ Screenshots show correctly

Input 3: Multiple Actions in One Request
- "Open Chrome, go to Gmail, draft email, save draft"
- One complex request, should break into multiple steps
Test: ✓ RAG breaks into 4+ steps
Test: ✓ All executed in order
Test: ✓ Each logged separately

Input 4: Ambiguous Intent
- "Do the thing with the email"
- System doesn't know what "thing" or which "email"
Test: ✓ Clarification Agent asks: "Which action? Which email?"
Test: ✓ Conversation captured in chat_sessions
Test: ✓ After clarification, execution succeeds

Input 5: Contradictory Instructions
- "Close Chrome but I need to check Gmail"
Test: ✓ Safety Agent or Clarification asks which is primary
Test: ✓ System doesn't execute destructive action immediately
Test: ✓ User clarifies intent

Database Verification:
✓ Text fields handle 2000+ chars
✓ Unicode stored correctly
✓ Special chars not escaped/corrupted
✓ No SQL injection (parameterized queries)
✓ No log encoding errors

Assertions:
✓ All inputs handled safely
✓ No corruption or loss
✓ Clear responses to ambiguous inputs
✓ Logged completely
"""
```

**Success Criteria:**
- [ ] Long messages handled
- [ ] Special characters preserved
- [ ] Unicode/emoji work
- [ ] Ambiguous inputs get clarification
- [ ] No data loss or corruption

---

# 🔍 REGRESSION TEST SUITE

**To run before every merge:**

```bash
# Quick smoke test (5 min)
pytest tests/test_scenarios/ -m "smoke" -v

# Full regression suite (30 min)
pytest tests/test_scenarios/ -v --cov=app --cov-report=html

# Critical path tests (10 min) - MUST PASS
pytest tests/test_scenarios/test_open_chrome.py \
       tests/test_scenarios/test_draft_email_gmail.py \
       tests/test_scenarios/test_workflow_persistence.py -v
```

---

# 📋 TEST EXECUTION CHECKLIST (Per Sprint)

## Before Starting Each Sprint

- [ ] **Database Reset** (clean state)
  ```bash
  rm -f ./data/jarvis.db
  rm -f ./data/logs/*.log*
  ```

- [ ] **Test Environment Setup**
  ```bash
  cd backend
  pip install -r requirements.txt
  python -m pytest tests/ --collect-only  # Verify all tests load
  ```

- [ ] **Server Health Check**
  ```bash
  python -m uvicorn app.main:app --port 9000 &
  curl http://localhost:9000/health
  ```

## During Each Sprint (Daily)

- [ ] **Run regression tests** (after code changes)
  ```bash
  pytest tests/test_scenarios/ -x -v
  ```

- [ ] **Check log files** (after each test run)
  ```bash
  tail -100 ./data/logs/jarvis.log
  tail -20 ./data/logs/jarvis_errors.log
  ```

- [ ] **Verify database** (no orphaned records)
  ```bash
  sqlite3 ./data/jarvis.db
  > SELECT COUNT(*) FROM execution_logs;
  > SELECT COUNT(*) FROM chat_sessions;
  > SELECT COUNT(*) FROM workflows;
  ```

- [ ] **Check code coverage**
  ```bash
  pytest tests/ --cov=app --cov-report=term-missing
  ```

## End of Each Sprint (Friday)

- [ ] **Full test suite passes** (100% green)
  ```bash
  pytest tests/ -v --tb=short
  ```

- [ ] **Code coverage >80%**
  ```bash
  pytest tests/ --cov=app --cov-report=term
  # Must show: TOTAL 80%+
  ```

- [ ] **All 5 E2E scenarios pass**
  - [ ] Open Chrome
  - [ ] Open Gmail
  - [ ] Draft Email
  - [ ] Save Workflow
  - [ ] Replay Workflow

- [ ] **No errors in logs**
  ```bash
  grep "ERROR\|CRITICAL" ./data/logs/*.log
  # Should return empty
  ```

- [ ] **Database integrity check**
  - [ ] No orphaned records
  - [ ] All foreign keys valid
  - [ ] Timestamps consistent
  - [ ] No NULL values in required fields

- [ ] **Log files intact**
  ```bash
  wc -l ./data/logs/jarvis.log
  wc -l ./data/logs/jarvis_errors.log
  ```

---

# 🚀 SPRINT INTEGRATION - Updated Stories

## Updated Story 1.2: Execution Agent + Comprehensive Testing

**Original:** 5 SP (4 days)  
**Updated:** 5 SP + 2 SP testing (6 days)  
**New Total:** Story 1.2 = 7 SP

**Additional Testing Requirements:**

1. **Real Desktop Action Tests** (NEW)
   - [ ] Click on real Notepad button (not mocked)
   - [ ] Type real text into Notepad
   - [ ] Screenshot capture verified (not empty)
   - [ ] Open real application (Notepad, Chrome)
   - [ ] Verify in database: Each action logged

2. **Error Cases** (NEW)
   - [ ] Click outside screen → Error handled
   - [ ] Type into closed window → Error handled
   - [ ] Open missing app → Error returned gracefully
   - [ ] Each error logged to error log file

3. **Database Integrity** (NEW)
   - [ ] execution_logs table populated
   - [ ] Each record has correct timestamps
   - [ ] No NULL values in required fields
   - [ ] Foreign keys valid

---

## Updated Sprint 1 Timeline

| Day | Story | Original SP | Testing (NEW) | Total | Revised Time |
|-----|-------|------------|---------------|-------|--------------|
| Mon | 1.1 RAG | 3 | +1 | 4 | 1.5 days (Mon-Tue AM) |
| Tue-Wed | 1.2 EA | 5 | +2 | 7 | 3 days (Tue-Thu) |
| Thu | 1.3 OA | 2 | +1 | 3 | 1 day (Thu AM) |
| Thu-Fri | 1.4 Orchestrator | 3 | +1 | 4 | 1.5 days (Thu PM-Fri) |
| Fri | 1.5 Frontend + Demo | 2 | +1 | 3 | Fri (1 day) |
| **TOTAL** | | **15 SP** | **+6 SP** | **21 SP** | **8 days** |

**Issue:** Original Sprint 1 was 5 days, now 8 days. This OVERRUNS the sprint!

**Solution:** Sprint 1 extends into following week

---

## Revised 3-Week Timeline

**SPRINT 1: "Core Execution with Validation"** 
- Duration: 1.5 weeks (8 days Mon-Fri Week 1 + Mon-Tue Week 2)
- Stories: 1.1 - 1.5
- Points: 21 SP
- Tests: 120 tests (60 unit + 60 integration/E2E)
- Goal: Core loop works + verified with real workflows

**SPRINT 2: "Vision & Safety with Full Testing"**
- Duration: 1.5 weeks (Wed Week 2 - Fri Week 3 + Mon-Tue Week 4)
- Stories: 2.1 - 2.4, 3.1 - 3.2
- Points: 11 SP + 4 SP testing = 15 SP
- Tests: 100 tests
- Goal: Vision working + all backend tested

**SPRINT 3: "Production Ready"**
- Duration: 1 week (Wed Week 4 - Fri Week 4 + early Week 5)
- Stories: 3.3, 4.1-4.3, 5.1-5.4
- Points: 13 SP + 5 SP testing = 18 SP
- Tests: Full 288 test suite
- Goal: Ship production-ready

**Total Timeline: 3-4 weeks (not 3 weeks originally estimated)**

---

# ✅ BACKEND VERIFICATION CHECKLIST

### Before Every Story Merge

- [ ] **Code Quality**
  - [ ] No hardcoded values
  - [ ] Error handling on all paths
  - [ ] Type hints for all functions
  - [ ] Docstrings for public APIs
  - [ ] Logging at key points

- [ ] **Database**
  - [ ] All changes backward compatible
  - [ ] No schema modifications without migration
  - [ ] Foreign key constraints working
  - [ ] No orphaned records

- [ ] **Logging**
  - [ ] All important events logged (INFO level)
  - [ ] Errors logged (ERROR level)
  - [ ] Debug info when needed (DEBUG level)
  - [ ] Logs are valid JSON (structured)

- [ ] **Testing**
  - [ ] Unit tests for new code (>80% coverage)
  - [ ] Integration tests if multi-component
  - [ ] No regressions (all existing tests pass)
  - [ ] Error cases tested

- [ ] **Workflow Execution**
  - [ ] Test workflow saves to database
  - [ ] Test workflow retrieval works
  - [ ] Test workflow replay works
  - [ ] Test chat session linked correctly

---

# 📊 SUCCESS METRICS

## Per Story

| Metric | Target | How to Verify |
|--------|--------|---|
| Tests Passing | 100% | `pytest tests/` shows all green |
| Code Coverage | >80% | `pytest --cov=app` shows % |
| Logs Valid | 100% | Parse jarvis.log as JSON |
| Database Clean | No errors | `grep "ERROR" jarvis_errors.log` = empty |
| E2E Scenarios | Pass | Manual test: "Open Chrome" works |
| No Regressions | 100% | All existing tests still pass |

## Per Sprint

| Sprint | Tests | Coverage | E2E Pass | Ready to Ship |
|--------|-------|----------|----------|--------------|
| Sprint 1 | 120/120 | >80% | 3/3 ✓ | No, needs vision |
| Sprint 2 | 220/220 | >80% | 5/5 ✓ | No, needs learning |
| Sprint 3 | 288/288 | >80% | 10/10 ✓ | YES ✅ |

---

# 🎯 CONFIDENCE LEVEL

After this comprehensive testing strategy is implemented:

**Backend Quality Assurance: 95%+**
- We KNOW code works (not guessing)
- We KNOW workflows are stored correctly
- We KNOW logging is complete
- We KNOW complex scenarios work
- We KNOW no regressions introduced

**User Experience: Confident**
- Users won't experience crashes
- Errors handled gracefully
- Full execution history available
- Workflows can be replayed
- Complex intents understood (or clarified)

---

**This testing strategy REPLACES the assumption-based approach with PROOF-BASED confidence.**

No more guessing. No more "should work". Everything VERIFIED.

