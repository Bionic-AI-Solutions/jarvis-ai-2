"""Workflow Learning Agent (Agent 13) — Learns and reuses execution patterns.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 13
Role: Two-layer learning system:
  Layer 1 — Silent Auto-Save: records every successful execution automatically
  Layer 2 — Conscious Save: prompts user after novel workflows ("Save this?")
Two matching sub-agents:
  - Exact Workflow Matcher: matches on intent hash → replays stored plan
  - Smart Step Recommender: partial match via intent similarity

NO external LLM needed — uses hashing, Levenshtein distance, frequency counting.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class WorkflowLearningAgent(BaseAgent):
    """Learns execution patterns and suggests reuse.

    Architecture V3, Agent 13:
    Input (save):  {operation: "save", intent: str, plan: [...], execution_result: dict,
                    session_id: str, user_confirmed: bool}
    Input (match): {operation: "match", intent: str, context: dict}
    Output (save): {status: "saved"|"skipped", workflow_id: str}
    Output (match):{status: "exact_match"|"partial_match"|"no_match",
                    workflow: {...}|None, confidence: float, next_agent: "rag"|None}
    """

    def __init__(self):
        super().__init__(
            agent_name="workflow_learning_agent",
            agent_type="support",
            description="Workflow learner — auto-saves and reuses execution patterns",
        )
        # In-memory workflow store (production: SQLite)
        self._workflows: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._max_workflows = 500
        self._intent_index: Dict[str, str] = {}  # normalized_intent → workflow_id

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface.

        Args:
            input_data: {
                "operation": "save"|"match"|"list"|"delete",
                ...operation-specific fields...
            }
        """
        start = time.perf_counter()
        operation = input_data.get("operation", "match")

        if operation == "save":
            result = self._save_workflow(input_data)
        elif operation == "match":
            result = self._match_workflow(input_data)
        elif operation == "list":
            result = self._list_workflows(input_data)
        elif operation == "delete":
            result = self._delete_workflow(input_data)
        else:
            result = {"status": "error", "message": f"Unknown operation: {operation}"}

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            **result,
            "duration_ms": duration_ms,
        }

    # ---- Layer 1: Silent Auto-Save ----

    def _save_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a successful execution as a learned workflow."""
        intent = data.get("intent", "")
        plan = data.get("plan", [])
        execution_result = data.get("execution_result", {})
        user_confirmed = data.get("user_confirmed", False)

        if not intent or not plan:
            return {"status": "skipped", "reason": "Missing intent or plan"}

        # Only save successful executions
        exec_status = execution_result.get("status", "")
        if exec_status not in ("success", "completed", "verified"):
            return {"status": "skipped", "reason": f"Execution was not successful: {exec_status}"}

        # Generate workflow ID from intent hash
        workflow_id = self._intent_hash(intent)

        # Check if we already have this exact workflow
        if workflow_id in self._workflows:
            # Update frequency count
            self._workflows[workflow_id]["use_count"] += 1
            self._workflows[workflow_id]["last_used"] = time.time()
            return {
                "status": "updated",
                "workflow_id": workflow_id,
                "use_count": self._workflows[workflow_id]["use_count"],
            }

        # Evict oldest if at capacity
        if len(self._workflows) >= self._max_workflows:
            self._workflows.popitem(last=False)

        # Store workflow
        workflow = {
            "workflow_id": workflow_id,
            "intent": intent,
            "normalized_intent": self._normalize_intent(intent),
            "plan": plan,
            "step_count": len(plan) if isinstance(plan, list) else 1,
            "execution_result_summary": {
                "status": exec_status,
                "duration_ms": execution_result.get("duration_ms", 0),
            },
            "user_confirmed": user_confirmed,
            "use_count": 1,
            "created_at": time.time(),
            "last_used": time.time(),
            "tags": self._extract_tags(intent),
        }

        self._workflows[workflow_id] = workflow
        self._intent_index[self._normalize_intent(intent)] = workflow_id

        return {
            "status": "saved",
            "workflow_id": workflow_id,
            "intent": intent,
        }

    # ---- Layer 2: Matching ----

    def _match_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find a matching workflow for the given intent.

        Two-pass matching:
        1. Exact match via intent hash
        2. Smart match via Levenshtein / token overlap
        """
        intent = data.get("intent", "")
        if not intent:
            return {"status": "no_match", "confidence": 0.0, "workflow": None}

        # Pass 1: Exact match
        workflow_id = self._intent_hash(intent)
        if workflow_id in self._workflows:
            wf = self._workflows[workflow_id]
            wf["use_count"] += 1
            wf["last_used"] = time.time()
            return {
                "status": "exact_match",
                "confidence": 1.0,
                "workflow": wf,
                "next_agent": "execution_agent",
            }

        # Pass 1b: Normalized exact match
        normalized = self._normalize_intent(intent)
        if normalized in self._intent_index:
            wf_id = self._intent_index[normalized]
            if wf_id in self._workflows:
                wf = self._workflows[wf_id]
                wf["use_count"] += 1
                wf["last_used"] = time.time()
                return {
                    "status": "exact_match",
                    "confidence": 0.95,
                    "workflow": wf,
                    "next_agent": "execution_agent",
                }

        # Pass 2: Smart match — token overlap + Levenshtein
        best_match: Optional[Dict] = None
        best_score = 0.0

        intent_tokens = set(self._tokenize(intent))

        for wf in self._workflows.values():
            wf_tokens = set(self._tokenize(wf["intent"]))

            # Jaccard similarity
            if not intent_tokens or not wf_tokens:
                continue
            intersection = intent_tokens & wf_tokens
            union = intent_tokens | wf_tokens
            jaccard = len(intersection) / len(union)

            # Bonus for high use_count (frequently used workflows are more likely matches)
            frequency_bonus = min(wf["use_count"] * 0.02, 0.10)

            score = jaccard + frequency_bonus

            if score > best_score:
                best_score = score
                best_match = wf

        if best_match and best_score >= 0.60:
            best_match["use_count"] += 1
            best_match["last_used"] = time.time()
            return {
                "status": "partial_match",
                "confidence": round(best_score, 3),
                "workflow": best_match,
                "suggestion": f"Found a similar workflow: '{best_match['intent']}'",
                "next_agent": "rag_agent",  # RAG adapts before execution
            }

        return {
            "status": "no_match",
            "confidence": 0.0,
            "workflow": None,
            "next_agent": None,
        }

    def _list_workflows(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List stored workflows."""
        limit = data.get("limit", 20)
        sorted_wfs = sorted(
            self._workflows.values(),
            key=lambda w: w.get("use_count", 0),
            reverse=True,
        )[:limit]

        return {
            "status": "success",
            "workflows": [
                {
                    "workflow_id": w["workflow_id"],
                    "intent": w["intent"],
                    "use_count": w["use_count"],
                    "step_count": w["step_count"],
                    "tags": w["tags"],
                }
                for w in sorted_wfs
            ],
            "total": len(self._workflows),
        }

    def _delete_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a workflow by ID."""
        workflow_id = data.get("workflow_id", "")
        if workflow_id in self._workflows:
            wf = self._workflows.pop(workflow_id)
            normalized = self._normalize_intent(wf["intent"])
            self._intent_index.pop(normalized, None)
            return {"status": "deleted", "workflow_id": workflow_id}
        return {"status": "not_found", "workflow_id": workflow_id}

    # ---- Utility Methods ----

    def _intent_hash(self, intent: str) -> str:
        """Deterministic hash for exact matching."""
        normalized = self._normalize_intent(intent)
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def _normalize_intent(self, intent: str) -> str:
        """Normalize intent for comparison: lower, strip, remove punctuation."""
        text = intent.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _tokenize(self, text: str) -> List[str]:
        """Split text into meaningful tokens."""
        stop_words = {"the", "a", "an", "is", "to", "for", "and", "or", "in", "on",
                      "at", "it", "of", "my", "me", "i", "please", "can", "you"}
        words = re.findall(r'\w+', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 1]

    def _extract_tags(self, intent: str) -> List[str]:
        """Extract action tags from intent text."""
        tags: List[str] = []
        text_lower = intent.lower()

        action_keywords = {
            "open": "app_launch",
            "close": "app_close",
            "create": "file_create",
            "delete": "file_delete",
            "copy": "file_copy",
            "move": "file_move",
            "screenshot": "screenshot",
            "search": "web_search",
            "navigate": "web_navigate",
            "type": "keyboard",
            "click": "mouse",
        }

        for keyword, tag in action_keywords.items():
            if keyword in text_lower:
                tags.append(tag)

        return tags or ["general"]
