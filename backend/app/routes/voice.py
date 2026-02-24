"""Voice routes — transcription, config, and status endpoints.

Stories 1.1–1.5: Voice activation, Whisper STT, pause/resume,
silence detection, confidence thresholds.
"""

from __future__ import annotations

import base64
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.services.voice_service import voice_service, VoiceConfig

router = APIRouter(prefix="/api/voice", tags=["voice"])


# ── Request / Response Schemas ──────────────────────────

class TranscribeRequest(BaseModel):
    """Audio transcription request (base64-encoded audio)."""
    audio_b64: str = Field(..., description="Base64-encoded audio data (WAV)")
    language: str | None = Field(None, description="Language code override")
    device_id: str | None = Field(None, description="Device ID for per-device config")


class TranscribeResponse(BaseModel):
    text: str
    confidence: float
    language: str
    duration_ms: float
    auto_accepted: bool
    needs_re_speak: bool
    source: str = "voice"


class VoiceConfigRequest(BaseModel):
    confidence_threshold: float | None = Field(None, ge=0.0, le=1.0)
    auto_accept_threshold: float | None = Field(None, ge=0.0, le=1.0)
    re_speak_threshold: float | None = Field(None, ge=0.0, le=1.0)
    silence_db_threshold: float | None = Field(None, ge=0.0)
    silence_duration: float | None = Field(None, ge=0.5, le=10.0)
    max_recording_seconds: int | None = Field(None, ge=5, le=120)
    language: str | None = None
    device_id: str | None = None


class SilenceRequest(BaseModel):
    """Audio data for silence analysis."""
    audio_b64: str = Field(..., description="Base64-encoded raw PCM audio")
    sample_rate: int = Field(16000, ge=8000, le=48000)
    sample_width: int = Field(2, ge=1, le=4)
    device_id: str | None = None


class SilenceResponse(BaseModel):
    is_silent: bool
    avg_db: float
    duration_seconds: float
    should_submit: bool


# ── Endpoints ───────────────────────────────────────────

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(req: TranscribeRequest) -> TranscribeResponse:
    """Transcribe audio data to text using Whisper."""
    try:
        audio_bytes = base64.b64decode(req.audio_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data")

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio data")

    result = await voice_service.transcribe(
        audio_bytes,
        language=req.language,
        device_id=req.device_id,
    )
    return TranscribeResponse(**result.to_dict())


@router.post("/transcribe/upload", response_model=TranscribeResponse)
async def transcribe_upload(
    file: UploadFile = File(...),
    language: str | None = None,
    device_id: str | None = None,
) -> TranscribeResponse:
    """Transcribe an uploaded audio file."""
    audio_bytes = await file.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    result = await voice_service.transcribe(
        audio_bytes,
        language=language,
        device_id=device_id,
    )
    return TranscribeResponse(**result.to_dict())


@router.post("/silence", response_model=SilenceResponse)
async def detect_silence(req: SilenceRequest) -> SilenceResponse:
    """Analyze audio for silence detection."""
    try:
        audio_bytes = base64.b64decode(req.audio_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data")

    result = voice_service.detect_silence(
        audio_bytes,
        sample_rate=req.sample_rate,
        sample_width=req.sample_width,
        device_id=req.device_id,
    )
    return SilenceResponse(
        is_silent=result.is_silent,
        avg_db=result.avg_db,
        duration_seconds=result.duration_seconds,
        should_submit=result.should_submit,
    )


@router.get("/config")
async def get_voice_config(device_id: str | None = None) -> dict[str, Any]:
    """Get the current voice configuration."""
    cfg = voice_service.get_device_config(device_id)
    return cfg.to_dict()


@router.put("/config")
async def update_voice_config(req: VoiceConfigRequest) -> dict[str, Any]:
    """Update voice configuration (global or per-device)."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None and k != "device_id"}

    if req.device_id:
        # Per-device config
        existing = voice_service.get_device_config(req.device_id)
        for k, v in updates.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
        voice_service.set_device_config(req.device_id, existing)
        return existing.to_dict()
    else:
        # Global config
        cfg = voice_service.update_config(**updates)
        return cfg.to_dict()


@router.get("/status")
async def voice_status() -> dict[str, Any]:
    """Check voice service status and Whisper availability."""
    whisper_info = await voice_service.check_whisper_available()
    return {
        "service": "operational",
        "config": voice_service.config.to_dict(),
        "whisper": whisper_info,
    }
