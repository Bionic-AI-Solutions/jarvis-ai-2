"""Agent Pipeline — Routes user messages through the 13-agent mesh.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 5
The CRITICAL piece: connects chat messages to the full agent processing.

Full Pipeline Flow (Architecture V3):
  User Message
    → CMA Agent (context enrichment)
    → Workflow Learning Agent (check for cached workflow)
    → RAG Agent (plan generation)
    → Clarification Agent (if confidence 50-80%)
    → Safety Agent (pre-execution gate)
    → SPA Agent (plan annotation)
    → SAA Agent (execution method selection)
    → Execution Agent (desktop automation)
    → Observer Agent (verification)
    → Workflow Learning Agent (auto-save successful execution)
    → CMA Agent (store event)
    → Assistant Response

For conversational (non-actionable) messages:
  User Message → Ollama LLM → Assistant Response
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

from app.agents.registry import agent_registry
from app.core.logging_config import get_logger
from app.services.ollama_service import OllamaService
from app.services.vision_service import VisionService

logger = get_logger(__name__)


class AgentPipeline:
    """Orchestrates user messages through the full 13-agent mesh.

    This is the bridge between JARVIS chat and the agent architecture.
    Every user message flows through here.
    """

    def __init__(self, ollama_service: OllamaService | None = None):
        self.ollama = ollama_service or OllamaService()
        self.vision = VisionService()

    def _classify_intent(self, message: str) -> str:
        """Classify whether a message is conversational or actionable.

        Uses the same logic as UserAgent._quick_classify() to avoid
        sending simple chat messages through the heavy execution pipeline.

        Returns:
            'conversational' | 'system_command' | 'file_operation' |
            'web_operation' | 'screenshot' | 'general'
        """
        text = message.lower().strip()

        # Conversational / greeting patterns
        conversational_patterns = [
            "hello", "hi", "hey", "good morning", "good evening", "good afternoon",
            "good night", "how are you", "what can you do", "help", "who are you",
            "thanks", "thank you", "bye", "goodbye", "what are you", "tell me about",
            "what is", "who is", "why", "how does", "can you explain",
            "what's up", "how's it going", "nice", "great", "ok", "okay",
            "cool", "sure", "yes", "no", "maybe", "please",
        ]
        # Exact matches or starts-with for conversational
        if any(text == g or text.startswith(g + " ") or text.startswith(g + "?")
               or text.startswith(g + ",") or text.startswith(g + "!")
               for g in conversational_patterns):
            return "conversational"

        # Questions that are informational (not commands)
        question_starters = ["what is", "what are", "who is", "who are", "why is",
                             "why are", "how does", "how do", "can you explain",
                             "explain", "tell me about", "describe"]
        if any(text.startswith(q) for q in question_starters):
            return "conversational"

        # System commands — these need the full pipeline
        system_kw = ["open", "close", "launch", "start", "run", "execute", "kill",
                      "stop", "restart"]
        if any(text.startswith(kw + " ") or text == kw for kw in system_kw):
            return "system_command"

        # File operations
        file_kw = ["create file", "delete file", "move file", "copy file", "rename",
                    "make folder", "create folder", "mkdir", "copy ", "move ", "delete ",
                    "remove "]
        if any(text.startswith(kw) for kw in file_kw):
            return "file_operation"

        # Web / search
        web_kw = ["search", "google", "browse", "navigate to", "go to", "open url",
                   "website"]
        if any(kw in text for kw in web_kw):
            return "web_operation"

        # Screenshot / vision
        if "screenshot" in text or text == "screen":
            return "screenshot"

        # Short messages (1-3 words, no action verbs) are likely conversational
        words = text.split()
        if len(words) <= 3:
            action_verbs = {"open", "close", "copy", "move", "delete", "create",
                            "run", "start", "stop", "kill", "type", "click", "press",
                            "take", "list", "show", "launch", "execute", "remove"}
            if not any(w in action_verbs for w in words):
                return "conversational"

        return "general"

    async def process_message(
        self,
        user_message: str,
        session_id: str | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Process a user message through the full agent pipeline.

        Returns:
            {
                "response": str,
                "plan": dict | None,
                "execution": dict | None,
                "observation": dict | None,
                "pipeline_stages": [...],
                "duration_ms": float,
                "message_type": str,
            }
        """
        start = time.perf_counter()
        pipeline_stages = []
        ctx = context or {}

        # ── Stage -1: Intent Classification (fast-path for chat) ──
        intent = self._classify_intent(user_message)
        pipeline_stages.append(f"classify:{intent}")
        logger.info("pipeline_intent_classified", intent=intent, message=user_message[:80])

        if intent == "conversational":
            # Fast path: skip the entire execution pipeline for conversational messages
            response = await self._conversational_response(user_message, ctx)
            return {
                "response": response,
                "plan": None,
                "execution": None,
                "observation": None,
                "pipeline_stages": pipeline_stages + ["llm_conversational"],
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                "message_type": "chat",
            }

        # ── Stage 0: CMA — Enrich context from session memory ──
        cma = agent_registry.get_instance("cma_agent")
        if cma:
            try:
                cma_result = await cma.process({
                    "operation": "get_context",
                    "session_id": session_id or "default",
                })
                if cma_result.get("status") == "success":
                    ctx.update(cma_result.get("context", {}))
                    pipeline_stages.append("cma_context")
            except Exception as e:
                logger.debug(f"CMA context enrichment skipped: {e}")

        # ── Stage 0b: Workflow Learning — Check for cached workflow ──
        wf_learner = agent_registry.get_instance("workflow_learning_agent")
        if wf_learner:
            try:
                match_result = await wf_learner.process({
                    "operation": "match",
                    "intent": user_message,
                    "context": ctx,
                })
                if match_result.get("status") == "exact_match":
                    cached_wf = match_result.get("workflow", {})
                    logger.info(
                        "workflow_cache_hit",
                        intent=user_message,
                        confidence=match_result.get("confidence"),
                    )
                    pipeline_stages.append("workflow_cache_hit")
                    # Use the cached plan directly — skip RAG
                    ctx["cached_plan"] = cached_wf.get("plan")
            except Exception as e:
                logger.debug(f"Workflow matching skipped: {e}")

        # ── Stage 1: RAG Agent — Generate plan ──────────────
        rag = agent_registry.get_instance("rag_agent")
        if rag is None:
            logger.warning("rag_agent_not_registered, falling back to LLM chat")
            response = await self._conversational_response(user_message, ctx)
            return {
                "response": response,
                "plan": None,
                "execution": None,
                "observation": None,
                "pipeline_stages": ["llm_fallback"],
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                "message_type": "chat",
            }

        # If we have a cached plan, use it; otherwise generate new
        if ctx.get("cached_plan"):
            plan = ctx["cached_plan"]
            rag_result = {"status": "success", "plan": plan, "confidence": 1.0}
        else:
            rag_result = await rag.process({
                "user_intent": user_message,
                "context": ctx,
            })
        pipeline_stages.append("rag_agent")
        logger.info(
            "pipeline_rag_complete",
            status=rag_result.get("status"),
            confidence=rag_result.get("confidence"),
        )

        plan = rag_result.get("plan", {})
        confidence = rag_result.get("confidence", 0.0)
        status = rag_result.get("status", "failure")

        # If RAG couldn't generate a plan, treat as conversational
        if status == "failure" or not plan.get("steps"):
            response = await self._conversational_response(user_message, ctx)
            return {
                "response": response,
                "plan": plan,
                "execution": None,
                "observation": None,
                "pipeline_stages": pipeline_stages + ["llm_conversational"],
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                "message_type": "chat",
            }

        # ── Stage 1b: Clarification Agent (if confidence 50-80%) ──
        if status == "needs_clarification" or (0.50 <= confidence < 0.80):
            clarification = agent_registry.get_instance("clarification_agent")
            if clarification:
                try:
                    clar_result = await clarification.process({
                        "ambiguous_request": user_message,
                        "context": ctx,
                        "reason_for_clarification": plan.get("reasoning", "Low confidence"),
                        "session_id": session_id or "default",
                    })
                    pipeline_stages.append("clarification_agent")

                    if clar_result.get("status") == "needs_input":
                        questions = clar_result.get("questions", [])
                        question_text = "\n".join(f"  • {q}" for q in questions)
                        response = (
                            f"I'm not entirely sure what you want me to do. "
                            f"Could you clarify:\n{question_text}"
                        )
                        return {
                            "response": response,
                            "plan": plan,
                            "execution": None,
                            "observation": None,
                            "pipeline_stages": pipeline_stages,
                            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                            "message_type": "clarification",
                        }
                except Exception as e:
                    logger.debug(f"Clarification skipped: {e}")
            else:
                # No clarification agent, use old behavior
                response = (
                    f"I'm not entirely sure what you want me to do. "
                    f"Here's what I understood: {plan.get('reasoning', 'unclear intent')}. "
                    f"Could you rephrase or be more specific?"
                )
                return {
                    "response": response,
                    "plan": plan,
                    "execution": None,
                    "observation": None,
                    "pipeline_stages": pipeline_stages + ["clarification_needed"],
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    "message_type": "clarification",
                }

        # ── Stage 2: Safety Agent — Pre-execution check ────
        safety = agent_registry.get_instance("safety_agent")
        if safety:
            safety_result = await safety.process({"plan": plan})
            pipeline_stages.append("safety_agent")
            logger.info(
                "pipeline_safety_complete",
                status=safety_result.get("status"),
            )

            if safety_result.get("status") == "blocked":
                evaluation = safety_result.get("evaluation", {})
                # safety_agent returns "steps_blocked" (list of indices) and "step_evaluations" (list of dicts)
                blocked_indices = evaluation.get("steps_blocked", evaluation.get("blocked_steps", []))
                step_evals = evaluation.get("step_evaluations", [])
                reason = evaluation.get("reason", "Safety policy violation")
                if blocked_indices and step_evals:
                    reasons = [
                        e.get("reason", "blocked")
                        for e in step_evals
                        if e.get("decision") == "block"
                    ]
                    if reasons:
                        reason = "; ".join(reasons)
                return {
                    "response": f"I can't do that — safety check blocked the operation: {reason}",
                    "plan": plan,
                    "execution": None,
                    "observation": None,
                    "safety_evaluation": evaluation,
                    "pipeline_stages": pipeline_stages,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    "message_type": "safety_blocked",
                }

        # ── Stage 2b: SPA — Annotate plan with metadata ────
        spa = agent_registry.get_instance("spa_agent")
        if spa:
            try:
                spa_result = await spa.process({
                    "raw_plan": plan.get("steps", []),
                    "user_intent": user_message,
                    "context": ctx,
                })
                if spa_result.get("status") == "success":
                    # Update plan steps with annotations
                    plan["steps"] = spa_result.get("annotated_plan", plan.get("steps", []))
                    pipeline_stages.append("spa_agent")
            except Exception as e:
                logger.debug(f"SPA annotation skipped: {e}")

        # ── Stage 2c: SAA — Select execution methods ───────
        saa = agent_registry.get_instance("saa_agent")
        if saa:
            try:
                saa_result = await saa.process({
                    "annotated_plan": plan.get("steps", []),
                    "context": ctx,
                })
                if saa_result.get("status") == "success":
                    plan["execution_plan"] = saa_result.get("execution_plan", [])
                    pipeline_stages.append("saa_agent")
            except Exception as e:
                logger.debug(f"SAA method selection skipped: {e}")

        # ── Stage 3: Execution Agent — Run the plan ────────
        ea = agent_registry.get_instance("execution_agent")
        execution_result = None
        if ea:
            # Wire vision service for moondream verification fallback
            if hasattr(ea, "set_vision_service") and self.vision:
                ea.set_vision_service(self.vision)
            
            ea_result = await ea.process({"plan": plan})
            pipeline_stages.append("execution_agent")
            execution_result = ea_result.get("result", {})
            logger.info(
                "pipeline_execution_complete",
                status=ea_result.get("status"),
                success=execution_result.get("success"),
            )
        else:
            logger.warning("execution_agent_not_registered, skipping execution")

        # ── Stage 4: Observer Agent — Verify results ────────
        observation_result = None
        oa = agent_registry.get_instance("observer_agent")
        if oa and execution_result:
            steps = plan.get("steps", [])
            step_results = execution_result.get("step_results", [])
            
            for i, step in enumerate(steps):
                if i < len(step_results):
                    obs = await oa.process({
                        "step": step,
                        "exec_result": step_results[i],
                    })
                    observation_result = obs.get("observation")
            pipeline_stages.append("observer_agent")

        # ── Stage 5: Workflow Learning — Auto-save successful execution ──
        if wf_learner and execution_result and execution_result.get("success"):
            try:
                await wf_learner.process({
                    "operation": "save",
                    "intent": user_message,
                    "plan": plan.get("steps", []),
                    "execution_result": execution_result,
                    "session_id": session_id or "default",
                })
                pipeline_stages.append("workflow_save")
            except Exception as e:
                logger.debug(f"Workflow save skipped: {e}")

        # ── Stage 6: CMA — Store execution event ───────────
        if cma:
            try:
                await cma.process({
                    "operation": "store_event",
                    "session_id": session_id or "default",
                    "event": {
                        "type": "execution",
                        "user_message": user_message,
                        "plan_steps": len(plan.get("steps", [])),
                        "success": execution_result.get("success") if execution_result else False,
                        "pipeline_stages": pipeline_stages,
                    },
                })
            except Exception as e:
                logger.debug(f"CMA event storage skipped: {e}")

        # ── Build response ──────────────────────────────────
        response = self._build_response(plan, execution_result, observation_result)

        # Determine message type based on execution outcome
        exec_success = execution_result.get("success", False) if execution_result else False
        if exec_success:
            msg_type = "task_success"
        elif execution_result:
            msg_type = "task_error"
        else:
            msg_type = "task"

        return {
            "response": response,
            "plan": plan,
            "execution": execution_result,
            "observation": observation_result,
            "pipeline_stages": pipeline_stages,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            "message_type": msg_type,
        }

    async def _conversational_response(
        self,
        user_message: str,
        context: Dict[str, Any],
    ) -> str:
        """Generate a conversational response via Ollama LLM.
        
        Used when the user's message isn't an actionable command.
        Includes chat history for context awareness.
        """
        system_prompt = (
            "You are JARVIS, an AI desktop automation assistant. "
            "You help users by executing tasks on their Windows computer — "
            "opening applications, managing files, typing text, clicking, and more. "
            "If the user asks what you can do, explain your capabilities. "
            "If the user gives a greeting, respond warmly. "
            "Keep responses concise and helpful. "
            "If the user seems to want an action but you're unsure what, "
            "ask them to be more specific. "
            "Remember the conversation context when responding."
        )

        # Build prompt with chat history for context
        chat_history = context.get("chat_history", [])
        history_text = ""
        if chat_history:
            history_text = "Previous conversation:\n"
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = "You" if msg["role"] == "assistant" else "User"
                history_text += f"{role}: {msg['content']}\n"
            history_text += "\n"
        
        full_prompt = history_text + f"User: {user_message}"

        try:
            response = await self.ollama.generate(
                prompt=full_prompt,
                system=system_prompt,
                temperature=0.7,
                max_tokens=512,
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Ollama LLM call failed: {e}")
            return (
                "I'm JARVIS, your desktop automation assistant. "
                "I can open applications, manage files, type text, and more. "
                "Try saying something like 'Open Chrome' or 'Copy file X to Y'. "
                "(Note: My language model is currently unavailable for conversation.)"
            )

    def _build_response(
        self,
        plan: Dict[str, Any],
        execution_result: Optional[Dict[str, Any]],
        observation_result: Optional[Dict[str, Any]],
    ) -> str:
        """Build a human-readable response from pipeline results."""
        steps = plan.get("steps", [])
        
        if execution_result is None:
            return f"I generated a plan with {len(steps)} step(s) but couldn't execute it (execution agent not available)."

        success = execution_result.get("success", False)
        steps_executed = execution_result.get("steps_executed", 0)
        steps_total = execution_result.get("steps_total", len(steps))
        duration_ms = execution_result.get("duration_ms", 0)

        if success:
            descriptions = []
            for step in steps:
                descriptions.append(step.get("description", step.get("action", "unknown")))
            steps_text = "\n".join(f"  ✓ {d}" for d in descriptions)
            response = f"Done! Completed {steps_total} step(s) in {duration_ms:.0f}ms:\n{steps_text}"
            
            # Add verification status
            if observation_result:
                if observation_result.get("verified"):
                    response += "\n\nVerification: All steps confirmed successful."
                else:
                    response += "\n\nVerification: Some steps may not have completed as expected."
        else:
            # Partial or full failure
            step_results = execution_result.get("step_results", [])
            succeeded = sum(1 for r in step_results if r.get("success"))
            failed = [r for r in step_results if not r.get("success")]
            
            if succeeded > 0:
                response = f"Partially completed: {succeeded}/{steps_total} steps succeeded."
            else:
                response = "I wasn't able to complete the task."
            
            if failed:
                first_error = failed[0].get("error", "Unknown error")
                response += f"\nError: {first_error}"

        return response
