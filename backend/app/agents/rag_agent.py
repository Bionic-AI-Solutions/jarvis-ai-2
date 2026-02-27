"""RAG Agent — Understands user intent and generates structured execution plans.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 1
Role: Strategic planner and workflow architect
Model: qwen2.5:3b (8-12s inference via Ollama)
Responsibilities:
  1. Analyze Intent → extract goal, artifacts, constraints
  2. Call Web Search Agent if needed
  3. Generate multi-step plan (1-15 steps)
  4. Confidence assessment (>95% clear, 80-95% ambiguous, <80% needs clarification)
  5. Constraint extraction from context
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RAGAgent(BaseAgent):
    """Retrieval-Augmented Generation agent for plan generation.
    
    Generates structured execution plans from natural language user input.
    Uses rule-based parsing for known patterns, falls back to LLM for complex requests.
    
    Architecture V3, Agent 1:
    Input:  {user_intent: str, context: {previous_goals, user_constraints, available_tools, session_history}}
    Output: {status: "plan_ready", plan: {steps[], confidence, estimated_time}, next_agent: "spa"}
    """

    def __init__(self, ollama_service=None):
        super().__init__(
            agent_name="rag_agent",
            agent_type="planning",
            description="Strategic planner - converts user intent to execution plans",
        )
        self.ollama_service = ollama_service
        self._plan_cache: Dict[str, Dict] = {}

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: process user input and return execution plan.
        
        Args:
            input_data: {
                "user_intent": str,  # The user's natural language command
                "context": dict      # Optional context from CMA
            }
            
        Returns:
            {
                "status": "plan_ready" | "needs_clarification" | "failure",
                "plan": {"steps": [...], "confidence": float, "reasoning": str},
                "next_agent": "spa" | "clarification",
                "context_updates": {...}
            }
        """
        start = time.perf_counter()
        user_intent = input_data.get("user_intent", "")
        context = input_data.get("context", {})
        
        # Call the existing planning logic
        plan = await self._generate_plan(user_intent, context)
        
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)
        
        # Determine next agent based on confidence (Architecture V3)
        confidence = plan.get("confidence", 0.0)
        if confidence >= 0.80:
            status = "plan_ready"
            next_agent = "safety_agent"  # Goes through safety check before execution
        elif confidence >= 0.50:
            status = "needs_clarification"
            next_agent = "clarification_agent"
        else:
            status = "failure"
            next_agent = None
        
        return {
            "status": status,
            "plan": plan,
            "next_agent": next_agent,
            "confidence": confidence,
            "duration_ms": duration_ms,
            "context_updates": {
                "last_plan": plan,
                "plan_confidence": confidence,
                "user_intent": user_intent,
            },
        }

    async def _generate_plan(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Core planning logic - rule-based first, LLM fallback.
        
        Preserves original RAG agent logic while fitting into BaseAgent interface.
        """
        if not user_input or not user_input.strip():
            return {
                "steps": [],
                "confidence": 0.0,
                "reasoning": "Empty input received",
                "needs_clarification": False,
                "error": "No input provided",
            }

        user_input = user_input.strip()

        # Check cache for identical requests
        cache_key = user_input.lower()
        if cache_key in self._plan_cache:
            cached = self._plan_cache[cache_key].copy()
            cached["from_cache"] = True
            return cached

        # Try rule-based parsing first (fast, reliable)
        plan = self._rule_based_parse(user_input)

        # If rule-based returns low confidence and we have LLM, use it
        if plan["confidence"] < 0.7 and self.ollama_service:
            try:
                llm_plan = await self._llm_parse(user_input, context)
                if llm_plan["confidence"] > plan["confidence"]:
                    plan = llm_plan
            except Exception as e:
                logger.warning(f"LLM parsing failed, using rule-based fallback: {e}")
                plan["llm_error"] = str(e)

        # Cache successful plans
        if plan["confidence"] > 0.5:
            self._plan_cache[cache_key] = plan.copy()

        logger.info(
            "plan_generated",
            user_input=user_input[:100],
            steps=len(plan["steps"]),
            confidence=plan["confidence"],
        )

        return plan

    def _rule_based_parse(self, user_input: str) -> Dict[str, Any]:
        """Parse common patterns with rules — no LLM needed."""
        text = user_input.lower().strip()
        steps = []
        confidence = 0.0
        reasoning = ""

        # ── Pattern: Open application ───────────────────────
        open_match = re.match(
            r"^open\s+(.+?)(?:\s+and\s+.*)?$", text
        )
        if open_match:
            app_name = open_match.group(1).strip()
            # Check if there's complexity (e.g., "and draft", "and send", etc.)
            has_complex_action = re.search(r"\s+and\s+(draft|compose|send|type|write|search|find|navigate)", text)
            
            if has_complex_action:
                # Multi-step request - let LLM handle it
                confidence = 0.45
                reasoning = f"Detected complex 'open + action' request: {app_name}"
                steps = []
            else:
                # Simple open command
                app_name = re.sub(r"\s+and\s+.*", "", app_name).strip()
                steps.append({
                    "action": "open_application",
                    "parameters": {"app_name": app_name},
                    "description": f"Open {app_name}",
                    "timeout": 10,
                    "retry_count": 1,
                })
                confidence = 0.95
                reasoning = f"Detected 'open' command for application: {app_name}"

        # ── Pattern: Open X and go to Y ─────────────────────
        open_goto_match = re.match(
            r"^open\s+(.+?)\s+and\s+(?:go\s+to|navigate\s+to|visit)\s+(.+)$", text
        )
        if open_goto_match:
            app_name = open_goto_match.group(1).strip()
            url_or_location = open_goto_match.group(2).strip()
            steps = [
                {
                    "action": "open_application",
                    "parameters": {"app_name": app_name},
                    "description": f"Open {app_name}",
                    "timeout": 10,
                    "retry_count": 1,
                },
                {
                    "action": "wait",
                    "parameters": {"seconds": 2},
                    "description": "Wait for application to load",
                    "timeout": 5,
                    "retry_count": 0,
                },
                {
                    "action": "type_text",
                    "parameters": {"text": url_or_location},
                    "description": f"Type {url_or_location}",
                    "timeout": 5,
                    "retry_count": 1,
                },
                {
                    "action": "press_key",
                    "parameters": {"key": "enter"},
                    "description": "Press Enter to navigate",
                    "timeout": 5,
                    "retry_count": 1,
                },
            ]
            confidence = 0.92
            reasoning = f"Detected 'open + navigate' pattern: {app_name} → {url_or_location}"

        # ── Pattern: Copy file/folder from X to Y ───────────
        copy_match = re.match(
            r"^copy\s+(?:the\s+)?(?:file|folder|directory)?\s*(.+?)\s+(?:from\s+(.+?)\s+)?(?:to|into|in)\s+(.+)$",
            text
        )
        
        # If complex copy pattern didn't match, try simple "copy X to Y"  
        if not copy_match:
            copy_match = re.match(r"^copy\s+(.+?)\s+to\s+(.+)$", text)
            if copy_match:
                source = copy_match.group(1).strip()
                destination = copy_match.group(2).strip()
                steps = [
                    {
                        "action": "copy_file",
                        "parameters": {"source": source, "destination": destination},
                        "description": f"Copy {source} to {destination}",
                        "timeout": 30,
                        "retry_count": 1,
                    },
                ]
                confidence = 0.90
                reasoning = f"Detected copy operation: {source} → {destination}"
        
        # Handle complex copy pattern (copy file from X to Y)
        if copy_match and "from" in text.lower():
            item = copy_match.group(1).strip()
            source_dir = copy_match.group(2).strip() if copy_match.lastindex >= 2 and copy_match.group(2) else ""
            dest = copy_match.group(3).strip() if copy_match.lastindex >= 3 else copy_match.group(copy_match.lastindex).strip()
            source_path = f"{source_dir}/{item}".replace("\\", "/") if source_dir else item
            steps = [
                {
                    "action": "copy_file",
                    "parameters": {"source": source_path, "destination": dest},
                    "description": f"Copy {source_path} to {dest}",
                    "timeout": 30,
                    "retry_count": 1,
                },
            ]
            confidence = 0.90
            reasoning = f"Detected copy operation: {source_path} → {dest}"

        # ── Pattern: Move file/folder ───────────────────────
        move_match = re.match(
            r"^move\s+(.+?)\s+to\s+(.+)$", text
        )
        if move_match and not steps:
            source = move_match.group(1).strip()
            dest = move_match.group(2).strip()
            steps = [
                {
                    "action": "move_file",
                    "parameters": {"source": source, "destination": dest},
                    "description": f"Move {source} to {dest}",
                    "timeout": 30,
                    "retry_count": 1,
                },
            ]
            confidence = 0.90
            reasoning = f"Detected move operation: {source} → {dest}"

        # ── Pattern: Take screenshot ────────────────────────
        if re.match(r"^(?:take\s+)?(?:a\s+)?screenshot", text) and not steps:
            steps = [
                {
                    "action": "take_screenshot",
                    "parameters": {},
                    "description": "Capture screenshot of current screen",
                    "timeout": 5,
                    "retry_count": 1,
                },
            ]
            confidence = 0.99
            reasoning = "Detected screenshot request"

        # ── Pattern: Create file ────────────────────────────
        create_match = re.match(
            r"^create\s+(?:a\s+)?(?:new\s+)?file\s+(?:named?\s+)?(.+?)(?:\s+(?:with|containing)\s+(?:content\s+)?(.+))?$",
            text
        )
        if create_match and not steps:
            filepath = create_match.group(1).strip().strip('"').strip("'")
            content = create_match.group(2).strip() if create_match.group(2) else ""
            steps = [
                {
                    "action": "create_file",
                    "parameters": {"filepath": filepath, "content": content},
                    "description": f"Create file: {filepath}",
                    "timeout": 5,
                    "retry_count": 0,
                },
            ]
            confidence = 0.93
            reasoning = f"Detected file creation: {filepath}"

        # ── Pattern: Delete file ────────────────────────────
        delete_match = re.match(
            r"^(?:delete|remove)\s+(?:the\s+)?(?:file|folder)?\s*(.+)$", text
        )
        if delete_match and not steps:
            filepath = delete_match.group(1).strip().strip('"').strip("'")
            steps = [
                {
                    "action": "delete_file",
                    "parameters": {"filepath": filepath},
                    "description": f"Delete: {filepath}",
                    "timeout": 10,
                    "retry_count": 0,
                },
            ]
            confidence = 0.90
            reasoning = f"Detected deletion: {filepath}"

        # ── Pattern: List directory contents ────────────────
        list_match = re.match(
            r"^(?:list|show|display)\s+(?:the\s+)?(?:contents?\s+of\s+|files?\s+in\s+|folders?\s+in\s+)?(.+)$",
            text
        )
        if list_match and not steps:
            path = list_match.group(1).strip().strip('"').strip("'")
            steps = [
                {
                    "action": "list_directory",
                    "parameters": {"path": path},
                    "description": f"List contents of: {path}",
                    "timeout": 10,
                    "retry_count": 0,
                },
            ]
            confidence = 0.88
            reasoning = f"Detected directory listing: {path}"

        # ── Pattern: Open folder in explorer ────────────────
        explore_match = re.match(
            r"^(?:open|browse|explore)\s+(?:the\s+)?(?:folder|directory|path)?\s*(.+?)(?:\s+in\s+explorer)?$",
            text
        )
        if explore_match and not steps:
            path = explore_match.group(1).strip().strip('"').strip("'")
            # Only match paths that look like drive letters or absolute paths
            if re.match(r"^[a-zA-Z]:[/\\]", path) or path.startswith("/") or path.startswith("\\"):
                steps = [
                    {
                        "action": "open_explorer",
                        "parameters": {"path": path},
                        "description": f"Open folder: {path}",
                        "timeout": 10,
                        "retry_count": 1,
                    },
                ]
                confidence = 0.90
                reasoning = f"Detected folder exploration: {path}"

        # ── Pattern: Close application ──────────────────────
        close_match = re.match(
            r"^(?:close|quit|exit|kill|stop)\s+(.+)$", text
        )
        if close_match and not steps:
            app = close_match.group(1).strip()
            steps = [
                {
                    "action": "close_application",
                    "parameters": {"process_name": app},
                    "description": f"Close {app}",
                    "timeout": 5,
                    "retry_count": 1,
                },
            ]
            confidence = 0.92
            reasoning = f"Detected close command: {app}"

        # ── Pattern: Check if app is running ────────────────
        running_match = re.match(
            r"^(?:is|check\s+if)\s+(.+?)\s+(?:running|open|active)", text
        )
        if running_match and not steps:
            process = running_match.group(1).strip()
            steps = [
                {
                    "action": "is_process_running",
                    "parameters": {"process_name": process},
                    "description": f"Check if {process} is running",
                    "timeout": 5,
                    "retry_count": 0,
                },
            ]
            confidence = 0.95
            reasoning = f"Detected process check: {process}"

        # ── Pattern: Type/Write text ────────────────────────
        type_match = re.match(
            r"^(?:type|write|enter)\s+['\"]?(.+?)['\"]?\s*$", text
        )
        if type_match and not steps:
            text_to_type = type_match.group(1).strip()
            steps = [
                {
                    "action": "type_text",
                    "parameters": {"text": text_to_type},
                    "description": f"Type: {text_to_type[:50]}",
                    "timeout": 10,
                    "retry_count": 1,
                },
            ]
            confidence = 0.88
            reasoning = f"Detected type command"

        # ── Pattern: Wait ───────────────────────────────────
        wait_match = re.match(r"^wait\s+(\d+(?:\.\d+)?)\s*(?:seconds?|s)?$", text)
        if wait_match and not steps:
            seconds = float(wait_match.group(1))
            steps = [
                {
                    "action": "wait",
                    "parameters": {"seconds": seconds},
                    "description": f"Wait {seconds} seconds",
                    "timeout": seconds + 5,
                    "retry_count": 0,
                },
            ]
            confidence = 0.99
            reasoning = f"Detected wait: {seconds}s"

        # If no pattern matched, low confidence
        if not steps:
            confidence = 0.3
            reasoning = f"No rule-based pattern matched for: {user_input[:100]}"

        return {
            "steps": steps,
            "confidence": confidence,
            "reasoning": reasoning,
            "needs_clarification": confidence < 0.7,
            "parser": "rule_based",
        }

    async def _llm_parse(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use LLM to parse complex requests into steps."""
        system_prompt = """You are JARVIS AI's planning engine. Convert user requests into structured execution plans.

Available actions:
- open_application: {app_name: str, args?: list}
- click: {x: int, y: int, button?: str}
- type_text: {text: str}
- press_key: {key: str}  (enter, tab, escape, etc.)
- hotkey: {keys: list}  (e.g., ["ctrl", "c"])
- take_screenshot: {}
- copy_file: {source: str, destination: str}
- copy_folder: {source: str, destination: str}
- move_file: {source: str, destination: str}
- create_file: {filepath: str, content?: str}
- delete_file: {filepath: str}
- list_directory: {path: str}
- open_explorer: {path: str}
- close_application: {process_name: str}
- is_process_running: {process_name: str}
- wait: {seconds: float}

Respond ONLY with JSON:
{
  "steps": [{"action": "...", "parameters": {...}, "description": "..."}],
  "confidence": 0.0-1.0,
  "reasoning": "..."
}"""

        prompt = f"User request: {user_input}"
        if context:
            prompt += f"\nContext: {json.dumps(context, default=str)}"

        response = await self.ollama_service.generate(
            prompt=prompt,
            system=system_prompt,
            temperature=0.3,
            max_tokens=1024,
        )

        # Try to parse JSON from response
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                plan = json.loads(json_match.group())
                plan.setdefault("steps", [])
                plan.setdefault("confidence", 0.7)
                plan.setdefault("reasoning", "LLM-generated plan")
                plan["parser"] = "llm"
                plan["needs_clarification"] = plan["confidence"] < 0.7
                return plan
        except json.JSONDecodeError:
            pass

        return {
            "steps": [],
            "confidence": 0.3,
            "reasoning": f"LLM response could not be parsed: {response[:200]}",
            "needs_clarification": True,
            "parser": "llm_failed",
        }
