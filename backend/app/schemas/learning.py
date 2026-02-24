"""Learning schemas — request/response models for pattern learning endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Pattern schemas ─────────────────────────────────────────

class PatternResponse(BaseModel):
    """Single execution pattern."""

    id: str
    pattern_hash: str
    intent: str
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    frequency: int = 1
    success_rate: float = 1.0
    confidence: float = 0.0
    suggested: bool = False
    accepted: bool = False
    last_seen: datetime

    model_config = {"from_attributes": True}


class PatternListResponse(BaseModel):
    """List of execution patterns."""

    patterns: List[PatternResponse]
    total: int


class PatternRecordRequest(BaseModel):
    """Record a new execution for pattern learning."""

    intent: str = Field(..., min_length=1, description="User intent")
    steps: List[Dict[str, Any]] = Field(..., description="List of step dicts with agent/action")
    success: bool = True


# ── Suggestion schemas ──────────────────────────────────────

class SuggestionResponse(BaseModel):
    """Suggestion action result."""

    id: str
    pattern_id: str
    suggestion_type: str = "workflow"
    accepted: bool = False
    dismissed: bool = False
    timestamp: datetime

    model_config = {"from_attributes": True}


class SuggestionListResponse(BaseModel):
    """List of suggested patterns."""

    suggestions: List[PatternResponse]


# ── Confidence schemas ──────────────────────────────────────

class ConfidenceUpdateRequest(BaseModel):
    """Request to update a confidence threshold."""

    context: str = Field(..., description="Domain context: voice, agent, workflow, pattern")
    old_value: float = Field(..., ge=0.0, le=1.0)
    new_value: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., min_length=1)


class ConfidenceAutoAdjustRequest(BaseModel):
    """Request for auto-adjusting confidence."""

    context: str = Field(..., description="Domain context")
    current_value: float = Field(..., ge=0.0, le=1.0)
    user_accepted: bool


class ConfidenceHistoryResponse(BaseModel):
    """Single confidence history entry."""

    id: str
    context: str
    old_value: float
    new_value: float
    reason: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class ConfidenceHistoryListResponse(BaseModel):
    """List of confidence history entries."""

    entries: List[ConfidenceHistoryResponse]
    total: int


class ConfidenceCurrentResponse(BaseModel):
    """Current confidence threshold for a context."""

    context: str
    value: Optional[float] = None


class PassphraseStrengthRequest(BaseModel):
    """Request to check passphrase strength."""

    passphrase: str = Field(..., min_length=1)


class PassphraseStrengthResponse(BaseModel):
    """Passphrase strength evaluation result."""

    strong: bool
    score: int = Field(..., ge=0, le=4)
    feedback: List[str] = Field(default_factory=list)


class EncryptRequest(BaseModel):
    """Request to encrypt data."""

    plaintext: str
    passphrase: str = Field(..., min_length=8)


class DecryptRequest(BaseModel):
    """Request to decrypt data."""

    encrypted: str
    passphrase: str = Field(..., min_length=8)


class EncryptResponse(BaseModel):
    """Encryption result."""

    encrypted: str


class DecryptResponse(BaseModel):
    """Decryption result."""

    plaintext: str
