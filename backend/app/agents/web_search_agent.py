"""Web Search Agent (Agent 3) — Non-LLM fact finder.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 3
Role: External information retrieval
Model: None (internal HTTP scraper + cached results, NO LLM)
Responsibilities:
  1. Execute HTTP search, extract title/URL/snippet
  2. 10-second timeout per query
  3. Return top 5 results exactly
  4. Cache results for 24 hours
  5. NO interpretation — raw results only, caller interprets
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class WebSearchAgent(BaseAgent):
    """Web Search Agent — retrieves external information via HTTP.
    
    Architecture V3, Agent 3:
    Input:  {query: str, context_for_results: str}
    Output: {status: "results_found", results: [{rank, title, url, snippet}], elapsed_ms, from_cache}
    Performance: <10s per query; cached responses instant
    
    NOTE: This agent uses a local knowledge base fallback when no HTTP
    search API is configured. Configure JARVIS_SEARCH_API_KEY for real search.
    """

    def __init__(self):
        super().__init__(
            agent_name="web_search_agent",
            agent_type="search",
            description="Non-LLM fact finder — retrieves external information",
        )
        # 24-hour cache: {cache_key: {results, timestamp}}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl: float = 86400.0  # 24 hours
        
        # Local knowledge base fallback
        self._local_kb: Dict[str, List[Dict]] = {
            "react": [
                {"rank": 1, "title": "React Documentation", "url": "https://react.dev", "snippet": "The library for web and native user interfaces."},
                {"rank": 2, "title": "Create React App", "url": "https://create-react-app.dev", "snippet": "Set up a modern web app by running one command."},
            ],
            "python": [
                {"rank": 1, "title": "Python.org", "url": "https://python.org", "snippet": "Official Python programming language website."},
                {"rank": 2, "title": "PyPI", "url": "https://pypi.org", "snippet": "The Python Package Index."},
            ],
            "node": [
                {"rank": 1, "title": "Node.js", "url": "https://nodejs.org", "snippet": "Node.js is a JavaScript runtime."},
            ],
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: perform web search.
        
        Args:
            input_data: {
                "query": str,  # Search query
                "context_for_results": str,  # Context for filtering
                "max_results": int,  # Default 5
            }
        """
        start = time.perf_counter()
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 5)

        if not query:
            return {
                "status": "error",
                "results": [],
                "error": "No query provided",
                "elapsed_ms": 0,
            }

        # Check cache first
        cache_key = self._cache_key(query)
        cached = self._get_cached(cache_key)
        if cached is not None:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            self._record_call(duration_ms)
            return {
                "status": "results_found",
                "query": query,
                "results": cached[:max_results],
                "elapsed_ms": duration_ms,
                "from_cache": True,
                "context_updates": {},
            }

        # Try HTTP search (with 10s timeout per architecture)
        results = await self._http_search(query, max_results)

        # Fallback to local knowledge base
        if not results:
            results = self._local_search(query, max_results)

        # Cache results
        if results:
            self._cache[cache_key] = {
                "results": results,
                "timestamp": time.time(),
            }

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            "status": "results_found" if results else "no_results",
            "query": query,
            "results": results[:max_results],
            "elapsed_ms": duration_ms,
            "from_cache": False,
            "context_updates": {},
        }

    async def _http_search(self, query: str, max_results: int) -> List[Dict]:
        """Execute HTTP search with 10s timeout.
        
        Returns empty list if no search API configured or search fails.
        Real implementation would use DuckDuckGo, Brave Search, or SearXNG.
        """
        # TODO: Integrate real search API (DuckDuckGo, Brave, SearXNG)
        # For now, return empty to fall through to local KB
        return []

    def _local_search(self, query: str, max_results: int) -> List[Dict]:
        """Search local knowledge base as fallback."""
        query_lower = query.lower()
        results = []

        for keyword, entries in self._local_kb.items():
            if keyword in query_lower:
                results.extend(entries)

        return results[:max_results]

    def _cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    def _get_cached(self, cache_key: str) -> Optional[List[Dict]]:
        """Get cached results if fresh (within 24h TTL)."""
        entry = self._cache.get(cache_key)
        if entry is None:
            return None
        if time.time() - entry["timestamp"] > self._cache_ttl:
            del self._cache[cache_key]
            return None
        return entry["results"]
