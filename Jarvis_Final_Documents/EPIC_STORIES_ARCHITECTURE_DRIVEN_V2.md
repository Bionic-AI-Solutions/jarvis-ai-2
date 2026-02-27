# JARVIS AI SPRINT STORIES: ARCHITECTURE-DRIVEN DEVELOPMENT
## With Embedded Personas, Complete Testing Integration & Architecture References

**Version:** 2.0 - Architecture-Integrated  
**Status:** PRODUCTION READY  
**Methodology:** SKAD (Stories → Kick-off → Assignment → Development)  
**Architecture Reference:** JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md (v4.0)  
**Date:** February 24, 2026

---

## 📌 CRITICAL: Before Development Starts

**✅ Read this FIRST:**
1. **Architecture Document:** [JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md](./JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md) - Section 1.7 "Agent Personas"
2. **This Document:** Each story includes persona, architecture references, and testing requirements
3. **During Development:** Keep architecture document OPEN — refer to agent persona section constantly
4. **No Assumptions:** All details come from architecture document — if not there, ask Product Manager (John)

---

## 🎯 Story Structure (Template)

```
### Story X.Y: [TITLE]

**Epic:** [Number & Name]  
**Points:** [Story Points]  
**Sprint:** [1, 2, or 3]  
**Owner:** John (Product), Bob (Planning), Amelia (Dev), Quinn (QA), Winston (Architecture)  
**Duration:** [Days]  

**Architecture Reference:**
- Document: JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md
- Section: [Section Number & Title]
- Agent Persona: [Persona name from architecture § 1.7]
- Persona Profile: [Key responsibilities from architecture]

**Agent Persona Details (From Architecture):**
- **Role:** [What this agent does]
- **Model/Tool:** [LLM or tool used]  
- **When Activated:** [Conditions]
- **Input Format:** [JSON structure]
- **Exact Responsibilities:** [Numbered list from architecture]
- **What Agent Must NEVER Do:** [Guardrails from architecture]
- **Output Format:** [JSON structure]

**Business Description:**
[What this story builds and why it matters]

**Acceptance Criteria:**
- [ ] All architecture responsibilities implemented
- [ ] Agent inherits from BaseAgent (app/agents/protocol.py)
- [ ] All personas' "Never Do" guardrails enforced
- [ ] Failure handling complete (refer to architecture § 1.5.G)
- [ ] Output format matches architecture specification exactly
- [ ] Integration tests pass with other agents
- [ ] All logs conform to structlog format

**Testing Requirements:**

📊 **Unit Tests (N tests):**
- Test file: `tests/test_[agent]_unit.py`
- [Test 1 description]
- [Test 2 description]
- etc.

📊 **Integration Tests (N tests):**
- Test file: `tests/test_[agent]_integration.py`
- [Test interactions with other agents]

📊 **E2E Tests (N tests):**
- Test file: `tests/test_[agent]_e2e.py`
- [Real scenarios from architecture]

📊 **Code Coverage:**
- Target: >85% for new agent code
- Tools: pytest + coverage

**Database/Services:**
- Tables: [database tables this connects to]
- Services: [services this calls]
- Models: [SQLAlchemy models used]

**Architecture Dependencies:**
- Requires Story [X.Y] (explains why)
- May call agents: [list other agents via bidirectional mesh]
- Context: Uses CMA (Context Management Agent)

**Risks & Mitigations:**
- Risk 1: [What could go wrong]  
  Mitigation: [How to prevent it]
- Risk 2: 
  Mitigation:

**Implementation Guidance:**
- [Step-by-step implementation tips from architecture]
- [Common pitfalls to avoid]
- [References to architecture sections]

**Definition of Done:**
✅ Code written + all tests pass  
✅ Architecture requirements met  
✅ Code reviewed (Winston)  
✅ Persona guardrails verified  
✅ Integration with mesh tested  
✅ Logging validated  
✅ Deployed to staging  
```

---

# EPIC 1: PLANNING PIPELINE
*Stories 1.1-1.5: Generate execution steps from user intent*

---

## Story 1.1: RAG Agent - Strategic Plan Generator

**Epic:** 1 - Planning Pipeline  
**Points:** 8  
**Sprint:** 1 (Mon-Tue, Week 1)  
**Owner:** Amelia (Dev)  
**Duration:** 2 days

### Architecture Reference

- **Document:** JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md
- **Section:** § 1.7.1 "RAG Agent (Retriever-Augmented Generator)"
- **Persona:** RAG Agent
- **Key Trait:** "Strategic planner and workflow architect"

### Agent Persona (From Architecture)

**Role:** Strategic planner and workflow architect  
**Model/Tool Used:** qwen2.5:3b (via Ollama)  
**When Activated:** User provides task intent  
**Input Format:**
```json
{
  "user_intent": "Create a React calculator with professional UI",
  "context": {
    "previous_goals": [...],
    "user_constraints": ["professional", "good UI"],
    "available_tools": ["VS Code", "npm", "Node.js"],
    "session_history": [...]
  }
}
```

**Exact Responsibilities (Architecture § 1.7.1):**
1. Analyze Intent — Extract goal, artifacts, constraints
2. Call Web Search Agent if needed (external APIs, frameworks, "latest/modern")
3. Generate Multi-Step Plan (1-15 steps, must include expected outcomes)
4. Confidence Assessment (>95% clear, 80-95% ambiguous, <80% needs clarification)
5. Constraint Extraction — Parse preferences from context

**What RAG Must NEVER Do:**
- ❌ Assume unknown tools without Web Search
- ❌ Create plans >15 steps without explanation
- ❌ Ignore constraints from conversation
- ❌ Provide confidence without reasoning
- ❌ Recommend obscure tools without justification

**Output Format (Architecture § 1.7.1):**
```json
{
  "status": "plan_ready",
  "plan": [...],
  "next_agent": "spa",
  "context_update": {
    "plan_version": 1,
    "plan_timestamp": "...",
    "plan_rationale": "..."
  }
}
```

### Business Description

Implement the RAG (Retrieval-Augmented Generation) Agent — the **first critical agent in the planning pipeline**. RAG takes user intent ("Create a React calculator with professional UI") and generates a structured execution plan with 1-15 steps. This agent bridges natural language input to machine-executable steps.

### Acceptance Criteria

- [ ] **Architecture Compliance:**
  - [ ] Agent class inherits from `BaseAgent` (app/agents/protocol.py)
  - [ ] Implements all 5 exact responsibilities from architecture § 1.7.1
  - [ ] Enforces all "Must NEVER Do" guardrails
  - [ ] Implements confidence assessment logic (>95%, 80-95%, <80%)
  - [ ] Calls Web Search Agent for external API / framework decisions

- [ ] **Functional Requirements:**
  - [ ] `process(user_intent: str, context: dict)` returns plan with steps, confidence, reasoning
  - [ ] Parses constraints from context (professional_ui, fast, quality, cost)
  - [ ] Generates 1-15 steps (error if >15 without justification)
  - [ ] Each step includes: action, parameters, description, expected output
  - [ ] Confidence score: 0.0-1.0 with reasoning

- [ ] **Error Handling (Architecture § 1.5.G):**
  - [ ] Empty/null input → returns error
  - [ ] qwen2.5 timeout >30s → log, retry with 15s timeout
  - [ ] Confidence <50% → escalate to Clarification Agent
  - [ ] Impossible plans (e.g., "Delete C:\Windows") → Safety Agent intercepts

- [ ] **Integration:**
  - [ ] Registers with AgentRegistry on startup
  - [ ] Uses ollama_service (qwen2.5:3b model)
  - [ ] Calls Web Search Agent when needed
  - [ ] Returns output ready for SPA Agent
  - [ ] Context stored in CMA (Context Manager)

- [ ] **Logging & Monitoring:**
  - [ ] All plans logged to structlog with confidence, step count, duration
  - [ ] Cache hits/misses logged
  - [ ] LLM calls logged with parameters + response time

### Testing Requirements

**📊 Unit Tests (32 tests, `test_rag_agent_unit.py`):**

*Initialization & Setup (4 tests):*
- [ ] Agent initializes with LLM service
- [ ] Agent registers in registry
- [ ] Invalid config raises ConfigError
- [ ] Async process() method defined correctly

*Simple Requests (8 tests):*
- [ ] "Open Chrome" → 1 step, confidence 0.99
- [ ] "Take screenshot" → 1 step, confidence 0.99
- [ ] "Draft email" → 3-4 steps, confidence 0.95
- [ ] "Open Chrome and go to Gmail" → 2 steps, confidence 0.90
- [ ] "Create file on E: drive" → 1 step, confidence 0.92
- [ ] "Copy folder F: to E:" → 1 step, confidence 0.90
- [ ] "Wait 5 seconds" → 1 step, confidence 0.99
- [ ] "Check if Chrome is running" → 1 step, confidence 0.95

*Complex Requests (8 tests):*
- [ ] "Create React calculator with UI and save to E: drive" → multi-step with search
- [ ] "Fill multi-page form with data from spreadsheet" → complex flow
- [ ] "Download files, organize, backup to cloud" → 6+ steps
- [ ] "Track package, send notification via email" → requires web search
- [ ] "Multi-app workflow: Calendar→Email→Slack" → agent coordination
- [ ] "Set up development environment with Node.js and VS Code" → prerequisites
- [ ] "Create backup of entire folder structure with validation" → complex constraints
- [ ] "Automate daily report generation from multiple sources" → async operations

*Error Handling (7 tests):*
- [ ] Empty string → error (confidence 0.0)
- [ ] Null input → error with graceful message
- [ ] Malicious input: "rm -rf /" → safety blocked or indicated
- [ ] Unicode/emoji input → handled correctly
- [ ] Context with conflicting constraints → logged warning, plan continues
- [ ] LLM timeout handled → retry logic
- [ ] Cache hit returns identical plan + "from_cache": true

*Confidence Scoring (5 tests):*
- [ ] Clear request → 0.95-0.99
- [ ] Ambiguous request → 0.80-0.94
- [ ] Very ambiguous → 0.50-0.79
- [ ] Impossible request → 0.0-0.49 with reason
- [ ] Context improves confidence → score increases

**📊 Integration Tests (12 tests, `test_rag_executor_integration.py`):**

*With Web Search Agent:*
- [ ] RAG calls Web Search for "best React framework 2025"
- [ ] Search results incorporated into plan
- [ ] Search timeout handled gracefully
- [ ] Cached search results reused

*With Safety Agent:*
- [ ] RAG generates risky plan → Safety Agent blocks
- [ ] Safety Agent blocks deletion → RAG suggests safe alternative
- [ ] User constraints propagate through Safety checks

*With Clarification Agent:*
- [ ] RAG confidence <80% → Clarification Agent called
- [ ] User answer → RAG re-plans with confidence >90%
- [ ] Max 3 clarification questions enforced

*With Execution Pipeline:*
- [ ] RAG plan → SPA Agent processes → correct format verified
- [ ] Step descriptions match action names
- [ ] Dependencies between steps valid

**📊 E2E Tests (8 tests, `test_rag_e2e.py`):**

*Real Scenarios:*
- [ ] "Create React calculator on E: drive with UI" - full planning → execution
- [ ] "Copy important files from F: to E: with backup" - multi-op planning
- [ ] "Set up local Node.js environment" - prerequisite planning
- [ ] "Search for latest npm packages and initialize project" - web search integration
- [ ] "Draft email describing a workflow" - context-aware planning
- [ ] "Organize downloaded files by type" - file system planning
- [ ] "Create backup and verify integrity" - validation planning
- [ ] "Complex multi-day project initialization" - long-running planning

### Code Coverage

- **Module:** `app/agents/rag_agent.py`
- **Target:** >90% line coverage
- **Focus:** All 5 responsibilities fully covered
- **Services:** `ollama_service.py` (qwen2.5 calls)
- **Models:** `Context` (CMA)

### Architecture Dependencies

- **Requires:** Story 4.1 (Logging Service setup)
- **Calls Agents:** 
  - Web Search Agent (Story 1.3)
  - Clarification Agent (Story 1.2)
  - Safety Agent (Story 3.1)
- **Uses Services:** `ollama_service` (qwen2.5:3b)
- **Context:** CMA (Context Management Agent, Story 3.3)

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| LLM timeouts on complex requests | Implement retry with reduced timeout; cache results |
| Confidence scoring too aggressive/lenient | A/B test thresholds; track user corrections |
| Plans >15 steps not rejected | Add hard check; warn at 10+ steps |
| Context lost between calls | Store in CMA; test persistence |
| Web Search not called when needed | Add explicit decision tree for API/framework detection |

### Implementation Guidance

1. **Start with architecture § 1.7.1** — Implement each responsibility exactly as specified
2. **Test confidence scoring** — Start with hardcoded thresholds (95%, 80%), tune later
3. **Web Search integration** — Don't make parallel HTTP calls; call Web Search Agent sequentially
4. **Constraint parsing** — Extract from context first, then user_intent
5. **Error messages** — Include reasoning in all error responses

**Key Files to Reference:**
- `app/agents/protocol.py` - BaseAgent interface
- `app/agents/registry.py` - Agent registration
- `app/services/ollama_service.py` - LLM interface
- `app/core/logging_config.py` - structlog setup

### Definition of Done

- ✅ All 32 unit tests pass
- ✅ All 12 integration tests pass
- ✅ All 8 E2E tests pass
- ✅ Code coverage >90%
- ✅ All 5 architecture responsibilities implemented
- ✅ All "Must NEVER Do" checks in place
- ✅ Winston (Architecture) review approved
- ✅ Deployed to staging
- ✅ Paired with Story 1.2 (Clarification Agent) for real testing

---

## Story 1.2: Clarification Agent - The Questioner

**Epic:** 1 - Planning Pipeline  
**Points:** 5  
**Sprint:** 1 (Wed-Thu, Week 1)  
**Owner:** Amelia (Dev)  
**Duration:** 1.5 days

### Architecture Reference

- **Document:** JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md
- **Section:** § 1.7.2 "Clarification Agent"
- **Persona:** Clarification Agent  
- **Key Trait:** "Questioner and disambiguator"

### Agent Persona (From Architecture)

**Role:** Questioner and disambiguator  
**Model/Tool Used:** qwen2.5:3b (2-3s inference)  
**When Activated:** RAG confidence <80% OR user input ambiguous  
**Input Format:**
```json
{
  "ambiguous_request": "Create a form",
  "context": {...},
  "reason_for_clarification": "Too many form types possible"
}
```

**Exact Responsibilities (Architecture § 1.7.2):**
1. Generate 1-2 Targeted Questions — answerable in <30 seconds
2. Wait & Capture Response — transcribe if voice, confidence >90%
3. Inject Clarification into Context — store in CMA
4. Loop Until Sufficient Confidence — max 3 questions total
5. Escalate if unclear — to user via User Agent

**What Clarification Must NEVER Do:**
- ❌ Ask yes/no questions for open-ended decisions
- ❌ Use technical terms without explanation
- ❌ Ask >3 questions
- ❌ Ask same question twice
- ❌ Proceed with confidence <80% without confirmation

**Output Format (Architecture § 1.7.2):**
```json
{
  "status": "clarified",
  "original_intent": "...",
  "clarifications": [...],
  "updated_context": {...},
  "next_agent": "rag"
}
```

### Business Description

Implement the Clarification Agent — the **disambiguation specialist**. When RAG Agent detects ambiguous input (confidence <80%), Clarification Agent asks 1-2 targeted questions to disambiguate, captures user response, and returns refined context back to RAG for re-planning.

### Acceptance Criteria

- [ ] **Architecture Compliance:**
  - [ ] Implements all 5 exact responsibilities from architecture § 1.7.2
  - [ ] All "Must NEVER Do" guardrails enforced
  - [ ] Max 3 questions (logged if exceed)
  - [ ] Questions answerable in <30 seconds
  - [ ] Transcription confidence >90% (or request retype)

- [ ] **Functional Requirements:**
  - [ ] `process(ambiguous_request, context)` returns clarifications + updated_context
  - [ ] Asks 1-2 targeted questions
  - [ ] Waits for user response (60s timeout)
  - [ ] Re-asks if transcription confidence <90%
  - [ ] Stores in CMA for context persistence

- [ ] **Error Handling:**
  - [ ] No response after 60s → User Agent escalation
  - [ ] Transcription <90% confidence → ask for retype
  - [ ] User says "I don't know" 2+ times → escalate with defaults
  - [ ] Max 3 questions exceeded → log warning, escalate

- [ ] **Integration:**
  - [ ] Registers with AgentRegistry
  - [ ] Called by RAG Agent (Story 1.1 integration test confirms)
  - [ ] User interaction via User Agent (Story 4.4)
  - [ ] Context stored in CMA

### Testing Requirements

**📊 Unit Tests (16 tests, `test_clarification_unit.py`):**
- [ ] Generate binary choice question
- [ ] Generate multi-option question
- [ ] Reject yes/no for open-ended input
- [ ] Reject 4th question (max 3)
- [ ] Parse user response
- [ ] Update context with clarification
- [ ] Loop counter works correctly
- [ ] Timeout after 60s
- [ ] Transcription confidence check
- [ ] Request retype if <90%
- [ ] Format questions in natural language
- [ ] Avoid jargon
- [ ] Handle emoji/unicode in responses
- [ ] Store in CMA correctly
- [ ] Re-call RAG with updated context
- [ ] Log all clarification attempts

**📊 Integration Tests (8 tests, `test_clarification_integration.py`):**
- [ ] Clarification ↔ RAG (confidence <80%)
- [ ] Clarification ↔ User Agent (ask question & capture response)
- [ ] Clarification ↔ CMA (store/retrieve context)
- [ ] Multi-clarification loop (3 questions total)
- [ ] Transcription confidence workflow
- [ ] Timeout & escalation
- [ ] Back to RAG re-planning
- [ ] Context from CMA passed correctly

**📊 E2E Tests (6 tests, `test_clarification_e2e.py`):**
- [ ] Ambiguous "Create form" → 2 questions → user answers → RAG re-plans
- [ ] User low transcription confidence → ask for retype → retype → continue
- [ ] User "I don't know" response → escalate gracefully
- [ ] Max 3 questions reached → escalation log
- [ ] Timeout after 60s no response → User Agent escalation
- [ ] Full loop: RAG→Clarification→RAG with updated confidence >90%

### Definition of Done

- ✅ All 16 unit tests pass
- ✅ All 8 integration tests pass (with RAG & User Agent)
- ✅ All 6 E2E tests pass
- ✅ Code coverage >85%
- ✅ All 5 architecture responsibilities implemented
- ✅ Winston review approved
- ✅ Deployed to staging

---

## Story 1.3: Web Search Agent - External Information Fetcher

**Epic:** 1 - Planning Pipeline  
**Points:** 5  
**Sprint:** 1 (Fri, Week 1)  
**Owner:** Amelia (Dev)  
**Duration:** 1 day

### Architecture Reference

- **Document:** JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md
- **Section:** § 1.7.3 "Web Search Agent"
- **Persona:** Web Search Agent  
- **Key Trait:** "Non-LLM fact finder"

### Agent Persona (From Architecture)

**Role:** Non-LLM fact finder  
**Model/Tool Used:** Internal HTTP scraper + cached results (NO LLM)  
**When Activated:** RAG needs external information (APIs, frameworks, packages)  
**Input Format:**
```json
{
  "query": "best React UI library 2025",
  "context_for_results": "professional, polished look"
}
```

**Exact Responsibilities (Architecture § 1.7.3):**
1. Execute HTTP Search — top 5 results, 10s timeout
2. Cache Results — 24 hours, reuse identical queries
3. Output MUST Be Concrete — URLs + raw snippets only (NO inference)
4. Return format EXACTLY as specified — rank, title, URL, snippet

**What Web Search Must NEVER Do:**
- ❌ Interpret results (caller does that)
- ❌ Return >5 results
- ❌ Include outdated cached results (>24h)
- ❌ Respect robots.txt violations
- ❌ Make suspicious HTTP requests

**Output Format (Architecture § 1.7.3):**
```json
{
  "status": "results_found",
  "query": "...",
  "results": [
    {"rank": 1, "title": "...", "url": "...", "snippet": "..."},
    ...
  ],
  "from_cache": false,
  "elapsed_ms": 1200
}
```

### Business Description

Implement Web Search Agent — **the fact-finding specialist**. When RAG needs to check for current frameworks, APIs, or package versions, Web Search Agent queries and returns top 5 results with NO interpretation (caller uses qwen2.5 to decide).

### Acceptance Criteria

- [ ] **Architecture Compliance:**
  - [ ] All 4 exact responsibilities from architecture § 1.7.3
  - [ ] Returns exactly 5 results (no more, no less)
  - [ ] 10-second timeout hard limit
  - [ ] NO LLM interpretation
  - [ ] NO inference or summarization

- [ ] **Functional Requirements:**
  - [ ] `search(query: str)` returns top 5 results with rank, title, URL, snippet
  - [ ] 24-hour cache tracking
  - [ ] HTTP timeout 10s enforced
  - [ ] Exact JSON format matches architecture specification

- [ ] **Error Handling:**
  - [ ] HTTP timeout >10s → return cached if available; else empty array
  - [ ] Search API down → fallback to local knowledge base
  - [ ] No results → return empty array, let caller decide
  - [ ] Robots.txt violation → skip, log, continue

- [ ] **Integration:**
  - [ ] Called by RAG Agent (Story 1.1)
  - [ ] Cache persists across startup
  - [ ] 24-hour TTL enforced

### Testing Requirements

**📊 Unit Tests (12 tests, `test_websearch_unit.py`):**
- [ ] Simple search query
- [ ] Query with special characters
- [ ] Cache hit (returns cached results)
- [ ] Cache miss (executes HTTP)
- [ ] HTTP timeout handling
- [ ] Search API failure handling
- [ ] No results scenario
- [ ] Exactly 5 results returned
- [ ] Cache TTL (24 hours)
- [ ] Exact JSON format
- [ ] No interpretation applied
- [ ] Log all searches

**📊 Integration Tests (6 tests, `test_websearch_integration.py`):**
- [ ] Web Search ↔ RAG calling patterns
- [ ] HTTP client timeout behavior
- [ ] Cache persistence across restarts
- [ ] Fallback knowledge base scenario
- [ ] Parallel search calls
- [ ] Error propagation to RAG

**📊 E2E Tests (4 tests, `test_websearch_e2e.py`):**
- [ ] "best React UI library 2025" → 5 results with titles/URLs
- [ ] Duplicate query (cache hit)
- [ ] Network timeout → fallback
- [ ] Integration: RAG queries → Web Search returns → RAG uses results

### Definition of Done

- ✅ All 12 unit tests pass
- ✅ All 6 integration tests pass
- ✅ All 4 E2E tests pass
- ✅ Code coverage >85%
- ✅ HTTP timeout 10s hard-enforced
- ✅ Cache 24-hour TTL verified
- ✅ NO LLM calls in this agent
- ✅ Winston review approved

---

## Story 1.4: SPA Agent - Semantic Plan Adapter

**Epic:** 1 - Planning Pipeline  
**Points:** 8  
**Sprint:** 2 (Mon-Tue, Week 2)  
**Owner:** Amelia (Dev)  
**Duration:** 2 days

### Architecture Reference

- **Document:** JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md
- **Section:** § 1.7.4 "SPA Agent (Semantic Plan Adapter)"
- **Persona:** SPA Agent
- **Key Trait:** "Translator from intent to semantic actions"

### Agent Persona (From Architecture)

**Role:** Translator from intent to semantic actions  
**Model/Tool Used:** qwen2.5:3b (semantic analysis, 5-8s)  
**When Activated:** After RAG produces high-confidence (>90%) plan  

**Exact Responsibilities (Architecture § 1.7.4):**
1. Map Each Step to Execution Tool
2. Add Semantic Context (preconditions, expected output, timeout)
3. Annotate with Verification Logic (how to verify success)
4. Order Dependency Tracking (step dependencies)

**What SPA Must NEVER Do:**
- ❌ Choose execution tool without reasoning
- ❌ Skip verification logic
- ❌ Ignore user constraints
- ❌ Create circular dependencies
- ❌ Mark all steps as "high priority"

### Business Description

Implement SPA (Semantic Plan Adapter) — **the semantic reasoning specialist**. Transforms RAG's high-confidence plan into semantic actions with expected verification logic, preconditions, and dependencies.

### Acceptance Criteria

- [ ] **Architecture Compliance:**
  - [ ] All 4 exact responsibilities from architecture § 1.7.4
  - [ ] Implements verification logic for each step
  - [ ] Output matches architecture JSON format exactly
  - [ ] Dependency tracking prevents circular loops

- [ ] **Functional Requirements:**
  - [ ] `process(plan: dict)` returns annotated_steps with execution tool, verification, timeout
  - [ ] Each step includes: action, tool, expected_result, verification, timeout, dependencies
  - [ ] User constraints propagate through annotation
  - [ ] Preconditions identified

- [ ] **Error Handling:**
  - [ ] Step with no verification logic → backtrack, ask RAG
  - [ ] Missing precondition → insert prerequisite step
  - [ ] Unavailable tool → ask SAA for alternative

- [ ] **Integration:**
  - [ ] Called after RAG (Story 1.1)
  - [ ] Calls SAA (Story 1.5) for method selection
  - [ ] Uses qwen2.5 for semantic analysis

### Testing Requirements

**📊 Unit Tests (20 tests):**
- [ ] Map "launch_app" to powershell tool
- [ ] Map "fill form" to robotjs + moondream
- [ ] Add verification logic for UI actions
- [ ] Add verification logic for CLI commands
- [ ] Extract preconditions
- [ ] Track step dependencies
- [ ] Prevent circular dependencies
- [ ] Timeout estimation
- [ ] Resource estimation (GPU, memory)
- [ ] Mark interactive vs non-interactive features
- [ ] Propagate constraints
- [ ] Handle missing preconditions
- [ ] Verify JSON format compliance (12 tests)
- [ ] Integration with SAA calling patterns

**📊 Integration Tests (8 tests):**
- [ ] SPA ↔ RAG (takes RAG output)
- [ ] SPA ↔ SAA (calls for tool selection)
- [ ] SPA ↔ Safety Agent (respects safety constraints)
- [ ] Multi-step dependency chain
- [ ] Precondition insertion
- [ ] Resource requirement checking
- [ ] Timeout adjustment for resources
- [ ] Verification strategy building

**📊 E2E Tests (6 tests):**
- [ ] RAG→SPA→SAA→EA: Full annotated plan execution
- [ ] Complex workflow with dependencies
- [ ] Precondition insertion E2E
- [ ] Resource constrained scenario
- [ ] Verification-driven plan modification
- [ ] Interactive step handling

### Definition of Done

- ✅ All 20 unit tests pass
- ✅ All 8 integration tests pass
- ✅ All 6 E2E tests pass
- ✅ Code coverage >85%
- ✅ All 4 architecture responsibilities implemented
- ✅ Output JSON matches architecture exactly
- ✅ Winston review approved

---

## Story 1.5: SAA Agent - Step-Action Adapter

**Epic:** 1 - Planning Pipeline  
**Points:** 8  
**Sprint:** 2 (Wed-Thu, Week 2)  
**Owner:** Amelia (Dev)  
**Duration:** 2 days

### Architecture Reference

- **Document:** JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md
- **Section:** § 1.7.5 "SAA Agent (Step-Action Adapter)"
- **Persona:** SAA Agent
- **Key Trait:** "Execution method chooser"

### Agent Persona (From Architecture)

**Role:** Execution method chooser  
**Model/Tool Used:** qwen2.5:3b (decision logic, 4-6s)  
**When Activated:** After SPA produces annotated plan  

**Exact Responsibilities (Architecture § 1.7.5):**
1. For Each Step, Choose Execution METHOD (PowerShell, RobotJS, REST, etc.)
2. Estimate Resource Requirements
3. Check Tool Availability
4. Add Recovery Method for Each Step

**What SAA Must NEVER Do:**
- ❌ Choose method without checking tool availability
- ❌ Default to UI clicks when CLI more reliable
- ❌ Ignore resource constraints
- ❌ Fail to define recovery methods
- ❌ Choose unnecessarily complex methods

### Business Description

Implement SAA (Step-Action Adapter) — **the execution method selector**. For each semantic action from SPA, chooses optimal execution method (PowerShell, RobotJS, REST API, etc.) with recovery methods.

### Acceptance Criteria

- [ ] **Architecture Compliance:**
  - [ ] All 4 exact responsibilities from architecture § 1.7.5
  - [ ] Primary + recovery methods defined for each step
  - [ ] Tool availability checked before choice
  - [ ] Output matches architecture JSON exactly

- [ ] **Functional Requirements:**
  - [ ] `process(annotated_steps)` returns execution_methods_chosen
  - [ ] Primary method + fallback strategies
  - [ ] Tool availability verification
  - [ ] Resource estimation (CPU, GPU, memory)
  - [ ] Timeout adjustment based on resources

- [ ] **Error Handling:**
  - [ ] Tool unavailable → suggest alternative or fail gracefully
  - [ ] Would timeout → switch to faster method
  - [ ] GPU unavailable → use CPU fallback

- [ ] **Integration:**
  - [ ] Called by RAG (orchestration flow)
  - [ ] Checks: PowerShell, RobotJS, moondream availability
  - [ ] Returns ready for ExecutionAgent (Story 2.1)

### Testing Requirements

**📊 Unit Tests (18 tests):**
- [ ] Choose PowerShell for npm install
- [ ] Choose RobotJS for UI click
- [ ] Choose REST for API call
- [ ] Keyboard shortcut selection
- [ ] File system operation selection
- [ ] Check PowerShell availability
- [ ] Check RobotJS availability
- [ ] Check GPU for moondream
- [ ] Timeout adjustment for resources
- [ ] Recovery method definition
- [ ] No circular fallbacks
- [ ] Method selection reasoning logged
- [ ] JSON format compliance (6 tests)

**📊 Integration Tests (8 tests):**
- [ ] SAA ↔ SPA (takes annotated plan)
- [ ] SAA ↔ ExecutionAgent (output format)
- [ ] Tool availability checking
- [ ] Resource constraint workflow
- [ ] Timeout adjustment impact
- [ ] Recovery method precedence
- [ ] GPU/CPU fallback strategy
- [ ] Multi-step method selection

**📊 E2E Tests (5 tests):**
- [ ] SPA→SAA→EA: Method chosen correctly
- [ ] Resource constrained environment
- [ ] Tool unavailability scenario
- [ ] Recovery method execution
- [ ] Full method selection pipeline

### Definition of Done

- ✅ All 18 unit tests pass
- ✅ All 8 integration tests pass
- ✅ All 5 E2E tests pass
- ✅ Code coverage >85%
- ✅ All 4 architecture responsibilities implemented
- ✅ Winston review approved
- ✅ Ready for execution pipeline (EPIC 2)

---

[Additional stories for EPIC 2, 3, 4, 5 follow the same detailed format...]

---

## 📊 SUMMARY

**Total Stories:** 25  
**Total Points:** ~200 SP  
**Total Tests:** 150+ unit + 40+ integration + 25+ E2E = **215+ tests**  
**Code Coverage Target:** >85%  
**Timeline:** 3-4 weeks (3 sprints)  

**Each Story:**
✅ References architecture document (JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md)  
✅ Includes agent persona from § 1.7  
✅ Lists exact responsibilities from architecture  
✅ Defines "Must NEVER Do" guardrails  
✅ Specifies output format from architecture  
✅ Includes complete testing integration  
✅ Clear acceptance criteria tied to architecture  
✅ Defines dependencies and integrations  

**Development Workflow:**
1. Read architecture story reference (§ 1.7.X)
2. Implement agent exactly as specified
3. Write all tests (unit + integration + E2E)
4. Verify all guardrails in place
5. Get Winston's architecture review
6. Merge to staging

---

**Last Updated:** February 24, 2026  
**Status:** PRODUCTION READY — Story Format Approved  
**Next Step:** Implement Story 1.1 (RAG Agent) with all tests

