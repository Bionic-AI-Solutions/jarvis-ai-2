"""JARVIS AI Backend - Error codes catalog.

Sprint 0 Deliverable: Comprehensive error codes mapped to HTTP status,
user-facing messages, and UX recovery actions.

Ranges:
  1XXX — Agent errors
  2XXX — Workflow / execution errors
  3XXX — Security / auth errors
  4XXX — System / infrastructure errors
  5XXX — Validation / input errors
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


@dataclass(frozen=True, slots=True)
class ErrorDefinition:
    """Immutable error definition used across the application."""

    code: str
    http_status: int
    message: str
    ux_action: str
    retry_allowed: bool
    category: str


class ErrorCode(str, Enum):
    """All error codes used by the JARVIS backend.

    Each value corresponds to a key in the ERROR_CATALOG dict.
    """

    # ── 1XXX: Agent Errors ──────────────────────────────────
    AGENT_NOT_FOUND = "AG_001"
    AGENT_TIMEOUT = "AG_002"
    AGENT_UNHEALTHY = "AG_003"
    AGENT_COMMUNICATION_FAILED = "AG_004"
    AGENT_INVALID_RESPONSE = "AG_005"
    AGENT_BUSY = "AG_006"
    AGENT_REGISTRATION_FAILED = "AG_007"

    # ── 2XXX: Workflow / Execution Errors ───────────────────
    WORKFLOW_NOT_FOUND = "WF_001"
    WORKFLOW_TIMEOUT = "WF_002"
    WORKFLOW_STEP_FAILED = "WF_003"
    WORKFLOW_CANCELLED = "WF_004"
    WORKFLOW_ALREADY_RUNNING = "WF_005"
    WORKFLOW_INVALID_STEPS = "WF_006"
    WORKFLOW_SAVE_FAILED = "WF_007"
    WORKFLOW_DUPLICATE_NAME = "WF_008"
    WORKFLOW_SAVE_INCOMPLETE = "WF_009"
    WORKFLOW_NOT_TEMPLATE = "WF_010"
    WORKFLOW_PAUSED = "WF_011"
    EXECUTION_NOT_FOUND = "EX_001"
    EXECUTION_ALREADY_COMPLETE = "EX_002"
    SCREENSHOT_CAPTURE_FAILED = "EX_003"
    RECOVERY_EXHAUSTED = "EX_004"
    STEP_VERIFICATION_FAILED = "EX_005"

    # ── 3XXX: Security / Auth Errors ────────────────────────
    AUTH_REQUIRED = "SEC_001"
    AUTH_INVALID_PASSPHRASE = "SEC_002"
    AUTH_LOCKED_OUT = "SEC_003"
    AUTH_SESSION_EXPIRED = "SEC_004"
    AUTH_INSUFFICIENT_PERMISSIONS = "SEC_005"
    AUTH_BRUTE_FORCE_DETECTED = "SEC_006"
    MODE_LOCKED = "SEC_007"
    AUDIT_INTEGRITY_FAILED = "SEC_008"
    SESSION_NOT_FOUND = "SEC_009"
    SESSION_ALREADY_REVOKED = "SEC_010"
    ENCRYPTION_FAILED = "SEC_011"
    DECRYPTION_FAILED = "SEC_012"
    PASSPHRASE_WEAK = "SEC_013"
    QUEUE_EMPTY = "SEC_014"

    # ── 4XXX: System / Infrastructure Errors ────────────────
    DB_CONNECTION_FAILED = "SYS_001"
    DB_QUERY_FAILED = "SYS_002"
    DB_MIGRATION_FAILED = "SYS_003"
    OLLAMA_UNAVAILABLE = "SYS_004"
    OLLAMA_MODEL_NOT_FOUND = "SYS_005"
    OLLAMA_INFERENCE_FAILED = "SYS_006"
    WEBSOCKET_CONNECTION_FAILED = "SYS_007"
    DISK_SPACE_LOW = "SYS_008"
    SCREENSHOT_STORAGE_FULL = "SYS_009"
    BACKUP_FAILED = "SYS_010"

    # ── 5XXX: Validation / Input Errors ─────────────────────
    VALIDATION_FAILED = "VAL_001"
    INVALID_SESSION_ID = "VAL_002"
    INVALID_WORKFLOW_ID = "VAL_003"
    MISSING_REQUIRED_FIELD = "VAL_004"
    INVALID_MODE = "VAL_005"
    INVALID_AUTH_METHOD = "VAL_006"
    INPUT_TOO_LONG = "VAL_007"
    INVALID_HOTKEY = "VAL_008"

    # ── General ─────────────────────────────────────────────
    INTERNAL_ERROR = "GEN_001"
    NOT_FOUND = "GEN_002"
    METHOD_NOT_ALLOWED = "GEN_003"

    # ── 6XXX: Learning Errors ───────────────────────────────
    PATTERN_NOT_FOUND = "LRN_001"
    SUGGESTION_ALREADY_HANDLED = "LRN_002"
    CONFIDENCE_OUT_OF_RANGE = "LRN_003"
    RATE_LIMITED = "GEN_004"
    SERVICE_UNAVAILABLE = "GEN_005"


# ── Error Catalog ───────────────────────────────────────────
# Maps each ErrorCode to its full definition.

ERROR_CATALOG: Dict[str, ErrorDefinition] = {
    # Agent errors
    ErrorCode.AGENT_NOT_FOUND: ErrorDefinition(
        code="AG_001", http_status=404,
        message="Requested agent is not registered",
        ux_action="notify", retry_allowed=False, category="agent",
    ),
    ErrorCode.AGENT_TIMEOUT: ErrorDefinition(
        code="AG_002", http_status=504,
        message="Agent did not respond within the timeout period",
        ux_action="suggest_retry", retry_allowed=True, category="agent",
    ),
    ErrorCode.AGENT_UNHEALTHY: ErrorDefinition(
        code="AG_003", http_status=503,
        message="Agent health check failed",
        ux_action="suggest_retry", retry_allowed=True, category="agent",
    ),
    ErrorCode.AGENT_COMMUNICATION_FAILED: ErrorDefinition(
        code="AG_004", http_status=502,
        message="Failed to communicate with agent",
        ux_action="suggest_retry", retry_allowed=True, category="agent",
    ),
    ErrorCode.AGENT_INVALID_RESPONSE: ErrorDefinition(
        code="AG_005", http_status=502,
        message="Agent returned an invalid response",
        ux_action="notify", retry_allowed=True, category="agent",
    ),
    ErrorCode.AGENT_BUSY: ErrorDefinition(
        code="AG_006", http_status=429,
        message="Agent is busy processing another request",
        ux_action="suggest_retry", retry_allowed=True, category="agent",
    ),
    ErrorCode.AGENT_REGISTRATION_FAILED: ErrorDefinition(
        code="AG_007", http_status=500,
        message="Failed to register agent in the registry",
        ux_action="notify", retry_allowed=False, category="agent",
    ),

    # Workflow / Execution errors
    ErrorCode.WORKFLOW_NOT_FOUND: ErrorDefinition(
        code="WF_001", http_status=404,
        message="Workflow not found",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.WORKFLOW_TIMEOUT: ErrorDefinition(
        code="WF_002", http_status=504,
        message="Workflow execution timed out",
        ux_action="suggest_retry", retry_allowed=True, category="workflow",
    ),
    ErrorCode.WORKFLOW_STEP_FAILED: ErrorDefinition(
        code="WF_003", http_status=500,
        message="A workflow step failed during execution",
        ux_action="suggest_retry", retry_allowed=True, category="workflow",
    ),
    ErrorCode.WORKFLOW_CANCELLED: ErrorDefinition(
        code="WF_004", http_status=200,
        message="Workflow was cancelled by the user",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.WORKFLOW_ALREADY_RUNNING: ErrorDefinition(
        code="WF_005", http_status=409,
        message="A workflow is already executing in this session",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.WORKFLOW_INVALID_STEPS: ErrorDefinition(
        code="WF_006", http_status=422,
        message="Workflow steps are invalid or malformed",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.WORKFLOW_SAVE_FAILED: ErrorDefinition(
        code="WF_007", http_status=500,
        message="Failed to save workflow",
        ux_action="suggest_retry", retry_allowed=True, category="workflow",
    ),
    ErrorCode.WORKFLOW_DUPLICATE_NAME: ErrorDefinition(
        code="WF_008", http_status=409,
        message="A workflow with this name already exists",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.WORKFLOW_SAVE_INCOMPLETE: ErrorDefinition(
        code="WF_009", http_status=400,
        message="Cannot save workflow from an incomplete execution",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.WORKFLOW_NOT_TEMPLATE: ErrorDefinition(
        code="WF_010", http_status=400,
        message="The specified workflow is not a template and cannot be cloned",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.WORKFLOW_PAUSED: ErrorDefinition(
        code="WF_011", http_status=409,
        message="Workflow execution is already paused",
        ux_action="notify", retry_allowed=False, category="workflow",
    ),
    ErrorCode.EXECUTION_NOT_FOUND: ErrorDefinition(
        code="EX_001", http_status=404,
        message="Execution record not found",
        ux_action="notify", retry_allowed=False, category="execution",
    ),
    ErrorCode.EXECUTION_ALREADY_COMPLETE: ErrorDefinition(
        code="EX_002", http_status=409,
        message="This execution has already completed",
        ux_action="notify", retry_allowed=False, category="execution",
    ),
    ErrorCode.SCREENSHOT_CAPTURE_FAILED: ErrorDefinition(
        code="EX_003", http_status=500,
        message="Failed to capture screenshot",
        ux_action="suggest_retry", retry_allowed=True, category="execution",
    ),
    ErrorCode.RECOVERY_EXHAUSTED: ErrorDefinition(
        code="EX_004", http_status=500,
        message="All recovery levels exhausted — action marked impossible",
        ux_action="notify", retry_allowed=False, category="execution",
    ),
    ErrorCode.STEP_VERIFICATION_FAILED: ErrorDefinition(
        code="EX_005", http_status=500,
        message="Step verification failed — visual check did not match",
        ux_action="suggest_retry", retry_allowed=True, category="execution",
    ),

    # Security errors
    ErrorCode.AUTH_REQUIRED: ErrorDefinition(
        code="SEC_001", http_status=401,
        message="Authentication is required",
        ux_action="prompt_auth", retry_allowed=False, category="security",
    ),
    ErrorCode.AUTH_INVALID_PASSPHRASE: ErrorDefinition(
        code="SEC_002", http_status=401,
        message="Incorrect passphrase",
        ux_action="prompt_auth", retry_allowed=True, category="security",
    ),
    ErrorCode.AUTH_LOCKED_OUT: ErrorDefinition(
        code="SEC_003", http_status=429,
        message="Too many failed attempts — locked out temporarily",
        ux_action="wait_and_retry", retry_allowed=True, category="security",
    ),
    ErrorCode.AUTH_SESSION_EXPIRED: ErrorDefinition(
        code="SEC_004", http_status=401,
        message="Session has expired — please re-authenticate",
        ux_action="prompt_auth", retry_allowed=False, category="security",
    ),
    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS: ErrorDefinition(
        code="SEC_005", http_status=403,
        message="You don't have permission to perform this action",
        ux_action="notify", retry_allowed=False, category="security",
    ),
    ErrorCode.AUTH_BRUTE_FORCE_DETECTED: ErrorDefinition(
        code="SEC_006", http_status=429,
        message="Brute-force attack detected — extended lockout applied",
        ux_action="wait_and_retry", retry_allowed=True, category="security",
    ),
    ErrorCode.MODE_LOCKED: ErrorDefinition(
        code="SEC_007", http_status=403,
        message="System is in locked mode — request queued",
        ux_action="prompt_auth", retry_allowed=False, category="security",
    ),
    ErrorCode.AUDIT_INTEGRITY_FAILED: ErrorDefinition(
        code="SEC_008", http_status=500,
        message="Audit log integrity check failed",
        ux_action="notify", retry_allowed=False, category="security",
    ),
    ErrorCode.SESSION_NOT_FOUND: ErrorDefinition(
        code="SEC_009", http_status=404,
        message="Session not found",
        ux_action="notify", retry_allowed=False, category="security",
    ),
    ErrorCode.SESSION_ALREADY_REVOKED: ErrorDefinition(
        code="SEC_010", http_status=400,
        message="Session has already been revoked",
        ux_action="notify", retry_allowed=False, category="security",
    ),
    ErrorCode.ENCRYPTION_FAILED: ErrorDefinition(
        code="SEC_011", http_status=500,
        message="Data encryption failed",
        ux_action="notify", retry_allowed=False, category="security",
    ),
    ErrorCode.DECRYPTION_FAILED: ErrorDefinition(
        code="SEC_012", http_status=500,
        message="Data decryption failed",
        ux_action="notify", retry_allowed=False, category="security",
    ),
    ErrorCode.PASSPHRASE_WEAK: ErrorDefinition(
        code="SEC_013", http_status=400,
        message="Passphrase does not meet strength requirements",
        ux_action="prompt_input", retry_allowed=True, category="security",
    ),
    ErrorCode.QUEUE_EMPTY: ErrorDefinition(
        code="SEC_014", http_status=200,
        message="No pending requests in queue",
        ux_action="notify", retry_allowed=False, category="security",
    ),

    # System errors
    ErrorCode.DB_CONNECTION_FAILED: ErrorDefinition(
        code="SYS_001", http_status=503,
        message="Database connection failed",
        ux_action="suggest_retry", retry_allowed=True, category="system",
    ),
    ErrorCode.DB_QUERY_FAILED: ErrorDefinition(
        code="SYS_002", http_status=500,
        message="Database query failed",
        ux_action="suggest_retry", retry_allowed=True, category="system",
    ),
    ErrorCode.DB_MIGRATION_FAILED: ErrorDefinition(
        code="SYS_003", http_status=500,
        message="Database migration failed",
        ux_action="notify", retry_allowed=False, category="system",
    ),
    ErrorCode.OLLAMA_UNAVAILABLE: ErrorDefinition(
        code="SYS_004", http_status=503,
        message="Ollama service is not available",
        ux_action="suggest_retry", retry_allowed=True, category="system",
    ),
    ErrorCode.OLLAMA_MODEL_NOT_FOUND: ErrorDefinition(
        code="SYS_005", http_status=404,
        message="Requested Ollama model is not installed",
        ux_action="notify", retry_allowed=False, category="system",
    ),
    ErrorCode.OLLAMA_INFERENCE_FAILED: ErrorDefinition(
        code="SYS_006", http_status=500,
        message="Ollama inference request failed",
        ux_action="suggest_retry", retry_allowed=True, category="system",
    ),
    ErrorCode.WEBSOCKET_CONNECTION_FAILED: ErrorDefinition(
        code="SYS_007", http_status=500,
        message="WebSocket connection failed",
        ux_action="suggest_retry", retry_allowed=True, category="system",
    ),
    ErrorCode.DISK_SPACE_LOW: ErrorDefinition(
        code="SYS_008", http_status=507,
        message="Low disk space — cleanup recommended",
        ux_action="notify", retry_allowed=False, category="system",
    ),
    ErrorCode.SCREENSHOT_STORAGE_FULL: ErrorDefinition(
        code="SYS_009", http_status=507,
        message="Screenshot storage limit reached",
        ux_action="notify", retry_allowed=False, category="system",
    ),
    ErrorCode.BACKUP_FAILED: ErrorDefinition(
        code="SYS_010", http_status=500,
        message="Backup operation failed",
        ux_action="suggest_retry", retry_allowed=True, category="system",
    ),

    # Validation errors
    ErrorCode.VALIDATION_FAILED: ErrorDefinition(
        code="VAL_001", http_status=422,
        message="Request validation failed",
        ux_action="notify", retry_allowed=False, category="validation",
    ),
    ErrorCode.INVALID_SESSION_ID: ErrorDefinition(
        code="VAL_002", http_status=422,
        message="Invalid session ID format",
        ux_action="notify", retry_allowed=False, category="validation",
    ),
    ErrorCode.INVALID_WORKFLOW_ID: ErrorDefinition(
        code="VAL_003", http_status=422,
        message="Invalid workflow ID format",
        ux_action="notify", retry_allowed=False, category="validation",
    ),
    ErrorCode.MISSING_REQUIRED_FIELD: ErrorDefinition(
        code="VAL_004", http_status=422,
        message="A required field is missing from the request",
        ux_action="notify", retry_allowed=False, category="validation",
    ),
    ErrorCode.INVALID_MODE: ErrorDefinition(
        code="VAL_005", http_status=422,
        message="Invalid operational mode specified",
        ux_action="notify", retry_allowed=False, category="validation",
    ),
    ErrorCode.INVALID_AUTH_METHOD: ErrorDefinition(
        code="VAL_006", http_status=422,
        message="Invalid authentication method",
        ux_action="notify", retry_allowed=False, category="validation",
    ),
    ErrorCode.INPUT_TOO_LONG: ErrorDefinition(
        code="VAL_007", http_status=422,
        message="Input exceeds maximum allowed length",
        ux_action="notify", retry_allowed=False, category="validation",
    ),
    ErrorCode.INVALID_HOTKEY: ErrorDefinition(
        code="VAL_008", http_status=422,
        message="Invalid hotkey binding",
        ux_action="notify", retry_allowed=False, category="validation",
    ),

    # General
    ErrorCode.INTERNAL_ERROR: ErrorDefinition(
        code="GEN_001", http_status=500,
        message="An unexpected internal error occurred",
        ux_action="suggest_retry", retry_allowed=True, category="general",
    ),
    ErrorCode.NOT_FOUND: ErrorDefinition(
        code="GEN_002", http_status=404,
        message="The requested resource was not found",
        ux_action="notify", retry_allowed=False, category="general",
    ),
    ErrorCode.METHOD_NOT_ALLOWED: ErrorDefinition(
        code="GEN_003", http_status=405,
        message="HTTP method not allowed for this endpoint",
        ux_action="notify", retry_allowed=False, category="general",
    ),
    ErrorCode.RATE_LIMITED: ErrorDefinition(
        code="GEN_004", http_status=429,
        message="Too many requests — please slow down",
        ux_action="wait_and_retry", retry_allowed=True, category="general",
    ),
    ErrorCode.SERVICE_UNAVAILABLE: ErrorDefinition(
        code="GEN_005", http_status=503,
        message="Backend service temporarily unavailable",
        ux_action="suggest_retry", retry_allowed=True, category="general",
    ),

    # Learning errors
    ErrorCode.PATTERN_NOT_FOUND: ErrorDefinition(
        code="LRN_001", http_status=404,
        message="Pattern not found",
        ux_action="notify", retry_allowed=False, category="learning",
    ),
    ErrorCode.SUGGESTION_ALREADY_HANDLED: ErrorDefinition(
        code="LRN_002", http_status=400,
        message="Suggestion has already been accepted or dismissed",
        ux_action="notify", retry_allowed=False, category="learning",
    ),
    ErrorCode.CONFIDENCE_OUT_OF_RANGE: ErrorDefinition(
        code="LRN_003", http_status=400,
        message="Confidence value must be between 0.0 and 1.0",
        ux_action="prompt_input", retry_allowed=True, category="learning",
    ),
}


def get_error(code: ErrorCode) -> ErrorDefinition:
    """Look up an error definition by its code enum."""
    return ERROR_CATALOG[code]


def error_response_body(
    code: ErrorCode,
    detail: Optional[str] = None,
) -> dict:
    """Build a standardised JSON error response payload.

    Format:
      {
        "error_code": "WF_002",
        "message": "Workflow execution timed out",
        "detail": "Step 4 exceeded 30 s timeout",
        "ux_action": "suggest_retry",
        "retry_allowed": true
      }
    """
    err = get_error(code)
    body: dict = {
        "error_code": err.code,
        "message": err.message,
        "ux_action": err.ux_action,
        "retry_allowed": err.retry_allowed,
    }
    if detail:
        body["detail"] = detail
    return body
