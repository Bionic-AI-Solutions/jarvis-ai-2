"""Ollama service — interface to the local Ollama LLM.

Used for NLU (intent parsing), plan generation, and conversational responses.
Models path: configured via JARVIS_OLLAMA_MODELS_PATH (default F:/models).
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from app.config import Settings, get_settings
from app.core.errors import ErrorCode
from app.core.exceptions import JarvisError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class OllamaService:
    """Client for the Ollama REST API.

    Provides both blocking (generate) and streaming (generate_stream) interfaces.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._base_url = self._settings.ollama_host
        self._model = self._settings.ollama_model
        self._timeout = httpx.Timeout(120.0, connect=10.0)

    # ── Public API ──────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """Generate a completion (non-streaming).

        Returns the full generated text.
        """
        model = model or self._model
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self._base_url}/api/generate", json=payload)

            if resp.status_code != 200:
                raise JarvisError(
                    ErrorCode.OLLAMA_INFERENCE_FAILED,
                    detail=f"Ollama returned HTTP {resp.status_code}: {resp.text[:200]}",
                )

            data = resp.json()
            return data.get("response", "")

        except httpx.ConnectError:
            raise JarvisError(ErrorCode.OLLAMA_UNAVAILABLE, detail="Cannot connect to Ollama")
        except httpx.TimeoutException:
            raise JarvisError(ErrorCode.OLLAMA_INFERENCE_FAILED, detail="Ollama request timed out")

    async def generate_stream(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> AsyncIterator[str]:
        """Generate a streaming completion — yields text chunks."""
        model = model or self._model
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream("POST", f"{self._base_url}/api/generate", json=payload) as resp:
                    if resp.status_code != 200:
                        raise JarvisError(
                            ErrorCode.OLLAMA_INFERENCE_FAILED,
                            detail=f"Ollama streaming returned HTTP {resp.status_code}",
                        )
                    import json
                    async for line in resp.aiter_lines():
                        if line.strip():
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            if token:
                                yield token
                            if chunk.get("done", False):
                                break

        except httpx.ConnectError:
            raise JarvisError(ErrorCode.OLLAMA_UNAVAILABLE, detail="Cannot connect to Ollama")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """Ollama chat completion API.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts.
        """
        model = model or self._model
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self._base_url}/api/chat", json=payload)

            if resp.status_code != 200:
                raise JarvisError(
                    ErrorCode.OLLAMA_INFERENCE_FAILED,
                    detail=f"Ollama chat returned HTTP {resp.status_code}",
                )

            data = resp.json()
            return data.get("message", {}).get("content", "")

        except httpx.ConnectError:
            raise JarvisError(ErrorCode.OLLAMA_UNAVAILABLE, detail="Cannot connect to Ollama")
        except httpx.TimeoutException:
            raise JarvisError(ErrorCode.OLLAMA_INFERENCE_FAILED, detail="Ollama chat request timed out")

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Ollama models."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self._base_url}/api/tags")

            if resp.status_code != 200:
                return []

            data = resp.json()
            return data.get("models", [])

        except Exception:
            return []

    async def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base_url}/api/version")
                return resp.status_code == 200
        except Exception:
            return False
