"""Clarification Agent (Agent 2) — Questioner and disambiguator.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 2
Role: Generate targeted questions when RAG confidence <80%
Model: qwen2.5:3b (2-3s inference)
Responsibilities:
  1. Generate 1-2 targeted questions answerable in <30 seconds
  2. Max 3 questions total per disambiguation loop
  3. Forward clarified answers to RAG for re-planning
  4. Inject clarification data into CMA
  5. Voice answers require transcription confidence >90%
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ClarificationAgent(BaseAgent):
    """Generates targeted clarifying questions for ambiguous requests.
    
    Architecture V3, Agent 2:
    Input:  {ambiguous_request: str, context: {}, reason_for_clarification: str}
    Output: {status: "clarified"|"needs_input", clarification_questions: [...], next_agent: "rag"}
    Performance: 2-3s per inference call
    """

    def __init__(self, ollama_service=None):
        super().__init__(
            agent_name="clarification_agent",
            agent_type="planning",
            description="Questioner — generates targeted clarifying questions",
        )
        self.ollama_service = ollama_service
        self._question_count: Dict[str, int] = {}  # session_id → count of questions asked
        self._max_questions = 3

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: generate clarifying questions or process answers.
        
        Args:
            input_data: {
                "ambiguous_request": str,
                "context": dict,
                "reason_for_clarification": str,
                "session_id": str,
                "user_answer": str,  # If user is answering a previous question
            }
        """
        start = time.perf_counter()
        session_id = input_data.get("session_id", "default")
        ambiguous_request = input_data.get("ambiguous_request", "")
        reason = input_data.get("reason_for_clarification", "")
        user_answer = input_data.get("user_answer")

        # If user provided an answer to previous clarification
        if user_answer:
            result = {
                "status": "clarified",
                "original_intent": ambiguous_request,
                "clarification_answer": user_answer,
                "updated_context": {
                    "clarification_q": reason,
                    "clarification_a": user_answer,
                    "timestamp": time.time(),
                },
                "next_agent": "rag_agent",
            }
        else:
            # Generate questions
            questions_asked = self._question_count.get(session_id, 0)
            
            if questions_asked >= self._max_questions:
                # Max questions reached, escalate
                result = {
                    "status": "escalated",
                    "message": "I need more specific input. What is the primary use case?",
                    "original_intent": ambiguous_request,
                    "next_agent": None,
                }
            else:
                questions = await self._generate_questions(ambiguous_request, reason)
                self._question_count[session_id] = questions_asked + 1
                
                result = {
                    "status": "needs_input",
                    "questions": questions,
                    "original_intent": ambiguous_request,
                    "reason": reason,
                    "questions_remaining": self._max_questions - questions_asked - 1,
                    "next_agent": None,  # Wait for user input
                }

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            **result,
            "duration_ms": duration_ms,
            "context_updates": result.get("updated_context", {}),
        }

    async def _generate_questions(
        self,
        ambiguous_request: str,
        reason: str,
    ) -> List[str]:
        """Generate 1-2 targeted questions using LLM.
        
        Rules (Architecture V3):
        - Good: "Should this form be for registration or support?"
        - Bad: "What do you want?"
        - Never ask yes/no for open-ended decisions
        - Never assume user knows technical terms
        """
        if self.ollama_service:
            try:
                system_prompt = (
                    "You are JARVIS AI's clarification system. "
                    "The user gave an ambiguous request. Generate 1-2 specific, targeted questions "
                    "that can be answered in under 30 seconds. "
                    "Rules: "
                    "- Questions must be specific, not generic "
                    "- Don't ask 'What do you want?' "
                    "- Don't assume technical knowledge "
                    "- Don't use yes/no questions for open decisions "
                    "- Each question should narrow down the intent significantly "
                    "Return ONLY a JSON array of question strings."
                )
                prompt = (
                    f"User request: \"{ambiguous_request}\"\n"
                    f"Why it's ambiguous: {reason}\n"
                    f"Generate 1-2 clarifying questions as a JSON array:"
                )
                response = await self.ollama_service.generate(
                    prompt=prompt,
                    system=system_prompt,
                    temperature=0.5,
                    max_tokens=256,
                )
                # Parse JSON array from response
                json_match = re.search(r'\[[\s\S]*?\]', response)
                if json_match:
                    questions = json.loads(json_match.group())
                    if isinstance(questions, list) and all(isinstance(q, str) for q in questions):
                        return questions[:2]
            except Exception as e:
                logger.warning(f"LLM question generation failed: {e}")

        # Fallback: generate rule-based questions
        return self._rule_based_questions(ambiguous_request, reason)

    def _rule_based_questions(self, request: str, reason: str) -> List[str]:
        """Generate questions without LLM."""
        request_lower = request.lower()

        if "create" in request_lower or "make" in request_lower:
            return ["What type of file or project should I create?", "Where should it be saved?"]
        elif "open" in request_lower:
            return ["Which application would you like me to open?"]
        elif "find" in request_lower or "search" in request_lower:
            return ["What exactly are you looking for?", "Where should I search?"]
        elif "copy" in request_lower or "move" in request_lower:
            return ["What file or folder should be copied/moved?", "What is the destination?"]
        else:
            return [f"Could you be more specific about what you'd like me to do with: '{request}'?"]
