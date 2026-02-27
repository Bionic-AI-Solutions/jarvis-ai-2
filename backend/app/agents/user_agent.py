"""User Agent (Agent 9) — Voice + text I/O bridge.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 9
Role: Handle all user-facing I/O (voice input via Whisper, text output via Piper TTS,
      text chat). Routes user input to the orchestrator after CMA context enrichment.
Model: qwen2.5:3b for intent pre-processing
External: Whisper STT, Piper TTS
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class UserAgent(BaseAgent):
    """User Agent — bridges user input (voice/text) with the agent mesh.

    Architecture V3, Agent 9:
    Input:  {message: str, input_mode: "text"|"voice", audio_data: bytes|None,
             session_id: str}
    Output: {status: "processed", user_input: str, input_mode: str,
             transcription_confidence: float|None, enriched_context: dict,
             next_agent: "rag_agent"}
    """

    def __init__(self, ollama_service=None, voice_service=None):
        super().__init__(
            agent_name="user_agent",
            agent_type="support",
            description="User Agent — voice/text I/O bridge and input router",
        )
        self.ollama_service = ollama_service
        self.voice_service = voice_service
        self._session_history: Dict[str, list] = {}  # session_id → recent messages

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: process user input and route to agent mesh.

        Args:
            input_data: {
                "message": str,           # text message (if text mode)
                "input_mode": "text"|"voice",
                "audio_data": bytes|None, # raw audio (if voice mode)
                "session_id": str,
                "context": dict,
            }
        """
        start = time.perf_counter()
        input_mode = input_data.get("input_mode", "text")
        session_id = input_data.get("session_id", "default")
        context = input_data.get("context", {})

        user_text: str = ""
        transcription_confidence: Optional[float] = None

        if input_mode == "voice":
            audio_data = input_data.get("audio_data")
            if audio_data:
                stt_result = await self._transcribe_voice(audio_data)
                user_text = stt_result.get("text", "")
                transcription_confidence = stt_result.get("confidence", 0.0)

                # Architecture V3: voice confidence must be >0.90
                if transcription_confidence < 0.90:
                    duration_ms = round((time.perf_counter() - start) * 1000, 2)
                    self._record_call(duration_ms)
                    return {
                        "status": "low_confidence",
                        "message": "I didn't catch that clearly. Could you please repeat?",
                        "transcription_confidence": transcription_confidence,
                        "input_mode": "voice",
                        "next_agent": None,
                        "duration_ms": duration_ms,
                    }
            else:
                # No audio data provided
                user_text = input_data.get("message", "")
        else:
            user_text = input_data.get("message", "")

        if not user_text.strip():
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            self._record_call(duration_ms)
            return {
                "status": "empty_input",
                "message": "No input received. Please type or speak your request.",
                "next_agent": None,
                "duration_ms": duration_ms,
            }

        # Track session history
        history = self._session_history.setdefault(session_id, [])
        history.append({"text": user_text, "mode": input_mode, "timestamp": time.time()})
        if len(history) > 20:
            history.pop(0)

        # Detect intent category (quick pre-classification)
        intent_hint = self._quick_classify(user_text)

        # Build enriched context
        enriched_context = {
            **context,
            "user_input": user_text,
            "input_mode": input_mode,
            "transcription_confidence": transcription_confidence,
            "intent_hint": intent_hint,
            "session_history_length": len(history),
        }

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            "status": "processed",
            "user_input": user_text,
            "input_mode": input_mode,
            "transcription_confidence": transcription_confidence,
            "intent_hint": intent_hint,
            "enriched_context": enriched_context,
            "next_agent": "rag_agent",
            "duration_ms": duration_ms,
        }

    async def _transcribe_voice(self, audio_data: bytes) -> Dict[str, Any]:
        """Transcribe voice input using Whisper STT service.

        Returns:
            {"text": str, "confidence": float, "language": str}
        """
        if self.voice_service:
            try:
                result = await self.voice_service.transcribe(audio_data)
                return {
                    "text": result.get("text", ""),
                    "confidence": result.get("confidence", 0.0),
                    "language": result.get("language", "en"),
                }
            except Exception as e:
                logger.warning(f"Whisper transcription failed: {e}")

        return {"text": "", "confidence": 0.0, "language": "en"}

    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech audio from text using Piper TTS.

        Returns audio bytes or None if TTS unavailable.
        """
        if self.voice_service:
            try:
                audio = await self.voice_service.synthesize(text)
                return audio
            except Exception as e:
                logger.warning(f"Piper TTS failed: {e}")
        return None

    def _quick_classify(self, text: str) -> str:
        """Quick rule-based intent classification (no LLM).

        Returns a category hint to speed up RAG routing.
        """
        text_lower = text.lower().strip()

        # Conversational / greeting
        greetings = ["hello", "hi", "hey", "good morning", "good evening", "how are you",
                      "what can you do", "help", "who are you"]
        if any(text_lower.startswith(g) or text_lower == g for g in greetings):
            return "conversational"

        # System commands
        system_kw = ["open", "close", "launch", "start", "run", "execute", "kill",
                      "stop", "restart"]
        if any(text_lower.startswith(kw) for kw in system_kw):
            return "system_command"

        # File operations
        file_kw = ["create file", "delete file", "move file", "copy file", "rename",
                    "make folder", "create folder", "mkdir"]
        if any(kw in text_lower for kw in file_kw):
            return "file_operation"

        # Web / search
        web_kw = ["search", "google", "browse", "navigate to", "go to", "open url",
                   "website"]
        if any(kw in text_lower for kw in web_kw):
            return "web_operation"

        # Screenshot / vision
        if "screenshot" in text_lower or "screen" in text_lower:
            return "screenshot"

        # Default
        return "general"
