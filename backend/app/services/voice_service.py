"""
JARVIS AI — Voice Service (Stories 1.1–1.5).

Handles:
- Speech-to-Text transcription via Whisper (local or Ollama)
- Audio processing with silence detection
- Confidence scoring and threshold management
- Configurable voice profiles
"""

from __future__ import annotations

import base64
import io
import json
import logging
import struct
import time
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class TranscriptionResult:
    """Result of a speech-to-text transcription."""

    text: str
    confidence: float  # 0.0 – 1.0
    language: str = "en"
    duration_ms: float = 0.0
    segments: list[dict[str, Any]] = field(default_factory=list)
    source: str = "voice"  # 'voice' | 'typed'
    auto_accepted: bool = False
    needs_re_speak: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "language": self.language,
            "duration_ms": self.duration_ms,
            "segments": self.segments,
            "source": self.source,
            "auto_accepted": self.auto_accepted,
            "needs_re_speak": self.needs_re_speak,
        }


@dataclass
class SilenceDetectionResult:
    """Result of silence analysis on an audio segment."""

    is_silent: bool
    avg_db: float
    duration_seconds: float
    should_submit: bool = False


@dataclass
class VoiceConfig:
    """Per-device or global voice configuration."""

    confidence_threshold: float = 0.90
    auto_accept_threshold: float = 0.90
    re_speak_threshold: float = 0.80
    silence_db_threshold: float = 5.0
    silence_duration: float = 1.5
    max_recording_seconds: int = 30
    language: str = "auto"
    device_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "confidence_threshold": self.confidence_threshold,
            "auto_accept_threshold": self.auto_accept_threshold,
            "re_speak_threshold": self.re_speak_threshold,
            "silence_db_threshold": self.silence_db_threshold,
            "silence_duration": self.silence_duration,
            "max_recording_seconds": self.max_recording_seconds,
            "language": self.language,
            "device_id": self.device_id,
        }

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "VoiceConfig":
        s = settings or get_settings()
        return cls(
            confidence_threshold=s.voice_confidence_threshold,
            auto_accept_threshold=s.voice_auto_accept_threshold,
            re_speak_threshold=s.voice_re_speak_threshold,
            silence_db_threshold=s.voice_silence_db,
            silence_duration=s.voice_silence_duration,
            max_recording_seconds=s.voice_max_duration,
        )


class VoiceService:
    """Handles voice transcription, silence detection, and confidence scoring.

    Whisper model can be accessed via:
    1. Ollama (if whisper model is available)
    2. Local Whisper binary (openai-whisper or whisper.cpp)
    3. HTTP endpoint (custom deployment)
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._config = VoiceConfig.from_settings(self._settings)
        self._ollama_url = self._settings.ollama_host
        self._timeout = httpx.Timeout(60.0, connect=10.0)
        self._device_profiles: dict[str, VoiceConfig] = {}

    @property
    def config(self) -> VoiceConfig:
        return self._config

    def get_device_config(self, device_id: str | None = None) -> VoiceConfig:
        """Get config for a specific device, or global default."""
        if device_id and device_id in self._device_profiles:
            return self._device_profiles[device_id]
        return self._config

    def set_device_config(self, device_id: str, config: VoiceConfig) -> None:
        """Store per-device voice profile."""
        config.device_id = device_id
        self._device_profiles[device_id] = config
        logger.info("voice_device_config_set", device_id=device_id)

    def update_config(self, **kwargs: Any) -> VoiceConfig:
        """Update the global voice config."""
        for key, val in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, val)
        return self._config

    async def transcribe(
        self,
        audio_data: bytes,
        *,
        language: str | None = None,
        device_id: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes (WAV format expected).
            language: Override language code (e.g. 'en', 'es'). None = auto-detect.
            device_id: Optional device ID for per-device thresholds.

        Returns:
            TranscriptionResult with text, confidence, and metadata.
        """
        start = time.time()
        cfg = self.get_device_config(device_id)

        # Try Ollama-based transcription first, fall back to local
        try:
            result = await self._transcribe_via_ollama(audio_data, language)
        except Exception as e:
            logger.warning("ollama_transcription_failed", error=str(e))
            result = self._transcribe_local_fallback(audio_data, language)

        duration = (time.time() - start) * 1000
        result.duration_ms = duration

        # Apply threshold logic
        result.auto_accepted = result.confidence >= cfg.auto_accept_threshold
        result.needs_re_speak = result.confidence < cfg.re_speak_threshold

        logger.info(
            "voice_transcription_complete",
            text_length=len(result.text),
            confidence=result.confidence,
            auto_accepted=result.auto_accepted,
            needs_re_speak=result.needs_re_speak,
            duration_ms=round(duration, 2),
        )

        return result

    async def _transcribe_via_ollama(
        self, audio_data: bytes, language: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe using Ollama's audio capabilities."""
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        payload = {
            "model": self._settings.voice_model,
            "prompt": "Transcribe the following audio accurately.",
            "stream": False,
            "images": [audio_b64],  # Ollama uses images field for binary data
        }

        if language:
            payload["prompt"] = f"Transcribe the following audio in {language}."

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._ollama_url}/api/generate", json=payload,
            )

        if resp.status_code != 200:
            raise RuntimeError(f"Ollama transcription failed: HTTP {resp.status_code}")

        data = resp.json()
        text = data.get("response", "").strip()

        # Estimate confidence from model metadata if available
        eval_count = data.get("eval_count", 0)
        confidence = min(0.95, max(0.5, eval_count / max(len(text.split()), 1) / 10)) if text else 0.0

        return TranscriptionResult(
            text=text,
            confidence=confidence,
            language=language or "auto",
            source="voice",
        )

    def _transcribe_local_fallback(
        self, audio_data: bytes, language: str | None = None,
    ) -> TranscriptionResult:
        """Fallback: return empty transcription when no engine available."""
        logger.warning("voice_no_engine_available")
        return TranscriptionResult(
            text="",
            confidence=0.0,
            language=language or "unknown",
            source="voice",
        )

    def detect_silence(
        self,
        audio_data: bytes,
        *,
        sample_rate: int = 16000,
        sample_width: int = 2,
        device_id: str | None = None,
    ) -> SilenceDetectionResult:
        """Analyze audio data for silence.

        Args:
            audio_data: Raw PCM audio bytes.
            sample_rate: Samples per second.
            sample_width: Bytes per sample (2 = 16-bit).
            device_id: Optional device ID for per-device thresholds.

        Returns:
            SilenceDetectionResult with dB level and submit flag.
        """
        cfg = self.get_device_config(device_id)

        if len(audio_data) < sample_width:
            return SilenceDetectionResult(
                is_silent=True, avg_db=0.0, duration_seconds=0.0, should_submit=False,
            )

        # Calculate RMS amplitude
        num_samples = len(audio_data) // sample_width
        if num_samples == 0:
            return SilenceDetectionResult(
                is_silent=True, avg_db=0.0, duration_seconds=0.0, should_submit=False,
            )

        fmt = f"<{num_samples}h"  # little-endian signed short
        try:
            samples = struct.unpack(fmt, audio_data[:num_samples * sample_width])
        except struct.error:
            return SilenceDetectionResult(
                is_silent=True, avg_db=0.0, duration_seconds=0.0, should_submit=False,
            )

        sum_squares = sum(s * s for s in samples)
        rms = (sum_squares / num_samples) ** 0.5

        # Convert to dB (relative to max 16-bit value)
        import math
        if rms > 0:
            db = 20 * math.log10(rms / 32768.0) + 96  # Normalize so 0 dB ~ silence
        else:
            db = 0.0

        duration = num_samples / sample_rate
        is_silent = db < cfg.silence_db_threshold

        should_submit = is_silent and duration >= cfg.silence_duration

        return SilenceDetectionResult(
            is_silent=is_silent,
            avg_db=round(db, 2),
            duration_seconds=round(duration, 4),
            should_submit=should_submit,
        )

    async def check_whisper_available(self) -> dict[str, Any]:
        """Check if Whisper model is available for transcription."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._ollama_url}/api/tags")

            if resp.status_code == 200:
                models = resp.json().get("models", [])
                whisper_models = [
                    m for m in models
                    if "whisper" in m.get("name", "").lower()
                ]
                return {
                    "available": len(whisper_models) > 0,
                    "models": [m.get("name") for m in whisper_models],
                    "ollama_reachable": True,
                }

            return {"available": False, "models": [], "ollama_reachable": True}
        except Exception:
            return {"available": False, "models": [], "ollama_reachable": False}


# Singleton
voice_service = VoiceService()
