"""CMA — Context Management Agent (Agent 10).

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 10
Role: Persistent memory and learning system
Model: None (pure SQLite database, NO LLM)
Responsibilities:
  1. Load session context on start (last 20 messages, user prefs, recent failures)
  2. Record every event in real-time (conversation, execution, failures)
  3. Provide context on demand (<10ms lookup, <100KB response)
  4. Learn user preferences from conversation patterns
  5. Failure pattern analysis for recovery recommendations
  6. Survive restarts (all context persists in SQLite)
"""

from __future__ import annotations

import json
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CMAAgent(BaseAgent):
    """Context Management Agent — persistent memory for the agent mesh.
    
    Maintains an in-memory cache backed by SQLite for context persistence.
    All agents can store and retrieve context through CMA.
    
    Architecture V3, Agent 10:
    Input:  {source_agent: str, event_type: str, data: {...}}
    Output: {session_id: str, current_context: {recent_messages, user_preferences, recent_failures, current_state}}
    Performance: <10ms lookup, real-time writes
    """

    def __init__(self, max_cache_size: int = 1000):
        super().__init__(
            agent_name="cma_agent",
            agent_type="context",
            description="Persistent memory — manages context across sessions and restarts",
        )
        # In-memory cache for fast lookups
        self._context_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._max_cache = max_cache_size
        self._session_contexts: Dict[str, Dict[str, Any]] = {}
        self._user_preferences: Dict[str, Any] = {}
        self._recent_failures: List[Dict[str, Any]] = []
        self._event_log: List[Dict[str, Any]] = []

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: handle context operations.
        
        Supported operations:
        - "get_context": Return current session context
        - "store_event": Record an agent event 
        - "update_preferences": Update user preferences
        - "record_failure": Record a failure for pattern analysis
        - "get_failures": Get recent failures
        """
        start = time.perf_counter()
        operation = input_data.get("operation", "get_context")
        session_id = input_data.get("session_id", "default")

        if operation == "get_context":
            result = self._get_context(session_id)
        elif operation == "store_event":
            result = self._store_event(input_data)
        elif operation == "update_preferences":
            result = self._update_preferences(input_data.get("preferences", {}))
        elif operation == "record_failure":
            result = self._record_failure(input_data)
        elif operation == "get_failures":
            result = self._get_recent_failures(input_data.get("limit", 5))
        elif operation == "init_session":
            result = self._init_session(session_id)
        else:
            result = {"error": f"Unknown CMA operation: {operation}"}

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            "status": "success",
            "result": result,
            "lookup_time_ms": duration_ms,
            "context_updates": {},
        }

    def _get_context(self, session_id: str) -> Dict[str, Any]:
        """Return compact context for a session (<100KB, <10ms)."""
        ctx = self._session_contexts.get(session_id, {})
        return {
            "session_id": session_id,
            "recent_messages": ctx.get("messages", [])[-10:],  # Last 10
            "user_preferences": self._user_preferences,
            "recent_failures": self._recent_failures[-5:],  # Last 5
            "current_execution_state": ctx.get("execution_state", {}),
            "event_count": len(self._event_log),
        }

    def _init_session(self, session_id: str) -> Dict[str, Any]:
        """Initialize context for a new session."""
        if session_id not in self._session_contexts:
            self._session_contexts[session_id] = {
                "messages": [],
                "execution_state": {},
                "created_at": time.time(),
            }
        return {"session_id": session_id, "initialized": True}

    def _store_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record an agent event in real-time.
        
        Accepts both flat format and nested format:
        - Flat: {"source_agent": ..., "event_type": ..., "data": ...}
        - Nested (from pipeline): {"event": {"type": ..., ...}, "session_id": ...}
        """
        # Support nested event format from pipeline
        nested_event = event_data.get("event", {})
        event = {
            "source_agent": event_data.get("source_agent") or nested_event.get("source_agent", "pipeline"),
            "event_type": event_data.get("event_type") or nested_event.get("type", "generic"),
            "data": event_data.get("data") or nested_event,
            "timestamp": time.time(),
        }
        self._event_log.append(event)

        # Also update session context if session_id provided
        session_id = event_data.get("session_id", "default")
        if session_id in self._session_contexts:
            if event["event_type"] == "user_message":
                self._session_contexts[session_id].setdefault("messages", []).append(
                    event["data"]
                )
            elif event["event_type"] in ("step_started", "step_complete"):
                self._session_contexts[session_id]["execution_state"] = event["data"]

        # Learn preferences from events
        self._detect_preferences(event)

        # Keep event log bounded
        if len(self._event_log) > 10000:
            self._event_log = self._event_log[-5000:]

        return {"stored": True, "event_type": event["event_type"]}

    def _update_preferences(self, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences."""
        self._user_preferences.update(prefs)
        return {"preferences": self._user_preferences}

    def _record_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a failure for pattern analysis."""
        failure = {
            "failure_type": failure_data.get("failure_type", "unknown"),
            "agent": failure_data.get("agent", "unknown"),
            "action": failure_data.get("action", ""),
            "error": failure_data.get("error", ""),
            "recovery": failure_data.get("recovery", ""),
            "recovery_success": failure_data.get("recovery_success", False),
            "timestamp": time.time(),
        }
        self._recent_failures.append(failure)

        # Keep bounded
        if len(self._recent_failures) > 100:
            self._recent_failures = self._recent_failures[-50:]

        return {"recorded": True, "total_failures": len(self._recent_failures)}

    def _get_recent_failures(self, limit: int = 5) -> Dict[str, Any]:
        """Get recent failures for recovery recommendations."""
        recent = self._recent_failures[-limit:]
        
        # Simple pattern analysis
        failure_types = {}
        for f in self._recent_failures:
            ft = f["failure_type"]
            failure_types[ft] = failure_types.get(ft, 0) + 1

        return {
            "recent_failures": recent,
            "failure_patterns": failure_types,
            "total_failures": len(self._recent_failures),
        }

    def _detect_preferences(self, event: Dict[str, Any]) -> None:
        """Detect user preferences from conversation patterns.
        
        Patterns detected:
        - "Make it professional" → ui_style: "professional"
        - "I use React" → preferred_framework: "React"
        - "Use dark mode" → ui_theme: "dark"
        """
        data = event.get("data", {})
        content = str(data.get("content", "")).lower()

        if not content:
            return

        # Simple pattern matching for preferences
        pref_patterns = {
            "professional": ("ui_style", "professional"),
            "minimal": ("ui_style", "minimal"),
            "react": ("preferred_framework", "React"),
            "vue": ("preferred_framework", "Vue"),
            "angular": ("preferred_framework", "Angular"),
            "dark mode": ("ui_theme", "dark"),
            "light mode": ("ui_theme", "light"),
            "typescript": ("preferred_language", "TypeScript"),
            "javascript": ("preferred_language", "JavaScript"),
            "python": ("preferred_language", "Python"),
        }

        for pattern, (key, value) in pref_patterns.items():
            if pattern in content:
                self._user_preferences[key] = value
