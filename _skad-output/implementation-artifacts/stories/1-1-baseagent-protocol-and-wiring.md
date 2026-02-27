# Story 1.1: BaseAgent Protocol & Agent Wiring

Status: ready-for-dev

## Story

As a developer,
I want a consistent BaseAgent interface that all agents implement with a unified process() method,
so that the orchestrator can dispatch to any agent uniformly without HTTP calls.

## Acceptance Criteria

1. BaseAgent abstract class exists in protocol.py with async process(input_data: dict) → dict
2. All existing agents (RAG, ExecutionAgent, ObserverAgent, SafetyAgent) inherit from BaseAgent
3. Each agent's process() method wraps their existing logic (rag.process, ea.execute_step, etc.)
4. Agent registration happens in-memory (not HTTP-based)
5. Orchestrator dispatches via direct agent.process() calls (not HTTP POST)
6. All agent input/output follows the architecture V3 Part 4 format

## Tasks / Subtasks

- [ ] Task 1: Create BaseAgent abstract class (AC: #1)
  - [ ] Add abstract async process(input_data: dict) → dict to protocol.py
  - [ ] Add agent_name, agent_type, description properties
  - [ ] Add health_check() method
- [ ] Task 2: Refactor RAG Agent to inherit BaseAgent (AC: #2, #3)
  - [ ] RAGAgent(BaseAgent) with process() wrapping existing logic
  - [ ] Input format: {user_intent, context}
  - [ ] Output format: {status, plan, confidence, next_agent}
- [ ] Task 3: Refactor Execution Agent to inherit BaseAgent (AC: #2, #3)
  - [ ] ExecutionAgent(BaseAgent) with process() wrapping execute_step()
  - [ ] Input format: {step_n, action, command, timeout}
  - [ ] Output format: {step_n, status, result, elapsed}
- [ ] Task 4: Refactor Observer Agent to inherit BaseAgent (AC: #2, #3)
  - [ ] ObserverAgent(BaseAgent) with process() wrapping observe()
  - [ ] Input format: {step, execution_result}
  - [ ] Output format: {verified, confidence, details}
- [ ] Task 5: Refactor Safety Agent to inherit BaseAgent (AC: #2, #3)
  - [ ] SafetyAgent(BaseAgent) with process() wrapping evaluate()
  - [ ] Input format: {proposed_action, proposed_command, context}
  - [ ] Output format: {safety_status, reason, proceed}
- [ ] Task 6: Refactor AgentRegistry for local dispatch (AC: #4, #5)
  - [ ] register() accepts BaseAgent instances (not HTTP URLs)
  - [ ] get() returns agent instances for direct calls
  - [ ] Remove HTTP health check (agents are in-process)
- [ ] Task 7: Refactor Orchestrator for local dispatch (AC: #5)
  - [ ] _dispatch_to_agent() calls agent.process() directly
  - [ ] Remove httpx HTTP POST calls
  - [ ] Keep WebSocket broadcasting
- [ ] Task 8: Write unit tests (AC: all)
  - [ ] Test BaseAgent contract enforcement
  - [ ] Test each refactored agent's process() method
  - [ ] Test registry local dispatch
  - [ ] Test orchestrator local call chain

## Dev Notes

- **Architecture Reference:** JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4
- **Key Finding from Audit:** protocol.py currently has message schemas but NO BaseAgent class
- **Key Finding from Audit:** Orchestrator uses HTTP POST to localhost:91XX — agents don't run as services
- **Key Finding from Audit:** Agents have inconsistent interfaces: process(), evaluate(), execute_step(), observe()
- **The fix:** Create BaseAgent, have all agents inherit it, orchestrator calls locally
- **Existing agent quality:** RAG (307 lines, good), EA (152 lines, good), OA (303 lines, good), Safety (334 lines, good)
- **What NOT to change:** Don't modify the underlying agent logic — only wrap it with BaseAgent interface
- **Models used:** qwen2.5:3b via OllamaService for RAG Agent LLM calls

### References

- [Source: Jarvis_Final_Documents/JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md#Part-4]
- [Source: backend/app/agents/protocol.py] - Current message schemas
- [Source: backend/app/agents/registry.py] - Current HTTP-based registry
- [Source: backend/app/agents/orchestrator.py] - Current HTTP dispatch

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

### Completion Notes List

### File List

