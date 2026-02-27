"""Piper TTS Service — Text-to-Speech via local Piper or Ollama.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 7
Role: Convert text responses to speech audio
Models: Piper (lightweight, local) or Ollama TTS models
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SynthesisResult:
    """Result of text-to-speech synthesis."""

    audio_bytes: bytes | None  # WAV audio data
    text: str  # Original text
    duration_ms: float = 0.0
    sample_rate: int = 22050
    model_used: str = "piper"
    error: str | None = None

    def save_to_file(self, path: str | Path) -> bool:
        """Save audio to WAV file."""
        if not self.audio_bytes:
            return False
        try:
            with open(path, "wb") as f:
                f.write(self.audio_bytes)
            return True
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False


class PiperTTSService:
    """Text-to-Speech using local Piper model or Ollama."""

    def __init__(self):
        self.settings = get_settings()
        self.piper_path = getattr(self.settings, 'piper_path', None) or self._find_piper()
        self.piper_available = self.piper_path is not None
        self.default_voice = "en_US-ryan-medium"
        self.sample_rate = 22050

    def _find_piper(self) -> str | None:
        """Try to locate Piper executable in common locations."""
        common_paths = [
            Path("C:/Program Files/Piper/piper.exe"),
            Path("C:/Program Files (x86)/Piper/piper.exe"),
            Path(Path.home() / ".local/bin/piper"),
            Path("/usr/bin/piper"),
            Path("/usr/local/bin/piper"),
        ]
        for path in common_paths:
            if path.exists():
                logger.info(f"Found Piper at: {path}")
                return str(path)
        return None

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        output_path: str | Path | None = None,
    ) -> SynthesisResult:
        """Synthesize text to speech.

        Args:
            text: Text to convert to speech
            voice: Voice name (default: "en_US-ryan-medium")
            output_path: Optional path to save WAV file

        Returns:
            SynthesisResult with audio bytes and metadata
        """
        start = time.perf_counter()
        voice = voice or self.default_voice

        if not text or not text.strip():
            return SynthesisResult(
                audio_bytes=None,
                text=text,
                error="Empty text",
                duration_ms=0,
            )

        # Try Piper first if available
        if self.piper_available:
            result = await self._synthesize_with_piper(text, voice, output_path)
            result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return result

        # Fallback: Try Ollama TTS models
        result = await self._synthesize_with_ollama(text, voice, output_path)
        result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return result

    async def _synthesize_with_piper(
        self,
        text: str,
        voice: str,
        output_path: str | Path | None,
    ) -> SynthesisResult:
        """Use local Piper binary for TTS."""
        if not self.piper_available:
            return SynthesisResult(
                audio_bytes=None,
                text=text,
                error="Piper not available",
            )

        try:
            # Create temp output file
            temp_output = Path("/tmp/piper_output.wav")
            if output_path:
                temp_output = Path(output_path)

            # Run piper command
            # piper --model en_US-ryan-medium --output_file /tmp/out.wav
            cmd = [
                str(self.piper_path),
                "--voice", voice,
                "--output-file", str(temp_output),
            ]

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate(input=text.encode("utf-8"))

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8") if stderr else "Unknown error"
                logger.warning(f"Piper TTS error: {error_msg}")
                return SynthesisResult(
                    audio_bytes=None,
                    text=text,
                    error=error_msg,
                    model_used="piper",
                )

            # Read output file
            if temp_output.exists():
                with open(temp_output, "rb") as f:
                    audio_bytes = f.read()
                return SynthesisResult(
                    audio_bytes=audio_bytes,
                    text=text,
                    model_used="piper",
                )
            else:
                return SynthesisResult(
                    audio_bytes=None,
                    text=text,
                    error="Output file not created",
                )

        except Exception as e:
            logger.error(f"Piper TTS execution failed: {e}")
            return SynthesisResult(
                audio_bytes=None,
                text=text,
                error=str(e),
                model_used="piper",
            )

    async def _synthesize_with_ollama(
        self,
        text: str,
        voice: str,
        output_path: str | Path | None,
    ) -> SynthesisResult:
        """Fallback: Use edge-tts (Microsoft Edge neural voices, free)."""
        try:
            import edge_tts
            import io
            
            # Map voice names to edge-tts voices
            edge_voice = "en-US-GuyNeural"  # Default male voice (JARVIS-like)
            voice_map = {
                "en_US-ryan-medium": "en-US-GuyNeural",
                "en_US-ryan-high": "en-US-ChristopherNeural",
                "en_US-ryan-low": "en-US-AndrewNeural",
                "en_US-kirsten-medium": "en-US-JennyNeural",
                "en_GB-bngl_male-medium": "en-GB-RyanNeural",
                "jarvis": "en-US-GuyNeural",
            }
            edge_voice = voice_map.get(voice, "en-US-GuyNeural")
            
            communicate = edge_tts.Communicate(text, edge_voice)
            
            # Collect audio bytes
            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
            
            if not audio_chunks:
                return SynthesisResult(
                    audio_bytes=None,
                    text=text,
                    error="edge-tts returned no audio",
                    model_used="edge-tts",
                )
            
            audio_bytes = b"".join(audio_chunks)
            
            # Save to file if path specified
            if output_path:
                with open(str(output_path), "wb") as f:
                    f.write(audio_bytes)
            
            logger.info(f"edge-tts synthesized {len(text)} chars → {len(audio_bytes)} bytes")
            return SynthesisResult(
                audio_bytes=audio_bytes,
                text=text,
                model_used="edge-tts",
                sample_rate=24000,  # edge-tts uses 24kHz
            )
        except ImportError:
            logger.warning("edge-tts not installed. Run: pip install edge-tts")
            return SynthesisResult(
                audio_bytes=None,
                text=text,
                error="TTS not available (Piper not installed, edge-tts not installed)",
                model_used="none",
            )
        except Exception as e:
            logger.error(f"edge-tts synthesis failed: {e}")
            return SynthesisResult(
                audio_bytes=None,
                text=text,
                error=f"edge-tts error: {str(e)}",
                model_used="edge-tts",
            )

    async def check_piper_available(self) -> dict[str, Any]:
        """Check if Piper is available and list available voices."""
        if not self.piper_available:
            return {
                "available": False,
                "path": None,
                "voices": [],
                "status": "not_found",
                "message": "Piper binary not found",
            }

        # Try to list voices
        voices = [
            "en_US-ryan-medium",  # Default
            "en_US-ryan-high",
            "en_US-ryan-low",
            "en_US-kirsten-medium",
            "en_GB-bngl_male-medium",
        ]

        return {
            "available": True,
            "path": str(self.piper_path),
            "voices": voices,
            "default_voice": self.default_voice,
            "status": "ready",
        }

    async def get_available_voices(self) -> list[str]:
        """Get list of available voices."""
        if not self.piper_available:
            return []
        return [
            "en_US-ryan-medium",
            "en_US-ryan-high",
            "en_US-ryan-low",
            "en_US-kirsten-medium",
            "en_GB-bngl_male-medium",
        ]


# Global instance
_piper_service: PiperTTSService | None = None


def get_piper_service() -> PiperTTSService:
    """Get or create global Piper TTS service instance."""
    global _piper_service
    if _piper_service is None:
        _piper_service = PiperTTSService()
    return _piper_service


piper_service = get_piper_service()
