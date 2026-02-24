# JARVIS AI — API Reference

## Base URL

```
http://localhost:9000
```

## Authentication

JARVIS uses a local passphrase + JWT token flow. Set a passphrase, then verify to obtain a session token. Include the JWT in the `Authorization: Bearer <token>` header for protected endpoints.

---

## Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | System health check (DB, Ollama, disk, memory) |

### `GET /health`

**Response 200:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 123.45,
  "database": "ok",
  "ollama": "unavailable",
  "disk_usage_percent": 42.1,
  "memory_usage_percent": 55.3
}
```

---

## Authentication (`/api/auth`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/passphrase` | Set or reset the master passphrase |
| `POST` | `/api/auth/verify` | Verify passphrase and obtain JWT |
| `GET` | `/api/auth/status` | Check auth status |
| `POST` | `/api/auth/lock` | Lock the interface |
| `POST` | `/api/auth/unlock` | Unlock with passphrase |
| `POST` | `/api/auth/passphrase/strength` | Check passphrase strength |
| `POST` | `/api/auth/auto-lock-timeout` | Set auto-lock timeout (0–1440 min) |

### `POST /api/auth/passphrase`

**Request:**
```json
{ "passphrase": "MySecure123" }
```
- `passphrase` — **required**, `min_length: 8`

**Response 200:**
```json
{ "message": "Passphrase set successfully" }
```

### `POST /api/auth/verify`

**Request:**
```json
{ "passphrase": "MySecure123" }
```

**Response 200:**
```json
{
  "verified": true,
  "token": "eyJhbGciOi...",
  "jti": "abc-123-uuid"
}
```

### `POST /api/auth/auto-lock-timeout`

**Request:**
```json
{ "minutes": 15 }
```
- `minutes` — **required**, `0 ≤ value ≤ 1440` (0 = disabled)

---

## Chat Sessions (`/api/chats`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/chats` | List all chat sessions |
| `POST` | `/api/chats` | Create a new chat session |
| `GET` | `/api/chats/{session_id}` | Get session details |
| `PUT` | `/api/chats/{session_id}` | Update session (title, mode) |
| `DELETE` | `/api/chats/{session_id}` | Delete a session |
| `GET` | `/api/chats/{session_id}/messages` | List messages in a session |
| `POST` | `/api/chats/{session_id}/messages` | Send a message |

### `POST /api/chats`

**Request:**
```json
{
  "title": "New Chat",
  "mode": "auto"
}
```
- `title` — optional, default `"New Chat"`, `max_length: 255`
- `mode` — optional, default `"auto"`, enum: `auto | supervised | locked`

### `POST /api/chats/{session_id}/messages`

**Request:**
```json
{
  "content": "Hello Jarvis!",
  "role": "user"
}
```
- `content` — **required**, `1 ≤ length ≤ 10,000`
- `role` — optional, default `"user"`, enum: `user | assistant | system`

---

## Workflows (`/api/workflows`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/workflows` | List all workflows |
| `POST` | `/api/workflows` | Create a workflow |
| `GET` | `/api/workflows/{id}` | Get workflow details |
| `PUT` | `/api/workflows/{id}` | Update a workflow |
| `DELETE` | `/api/workflows/{id}` | Delete a workflow |
| `GET` | `/api/workflows/{id}/revisions` | List revision history |
| `POST` | `/api/workflows/{id}/clone` | Clone a workflow |
| `POST` | `/api/workflows/{id}/execute` | Execute a workflow |
| `POST` | `/api/workflows/{id}/export` | Export a workflow |
| `GET` | `/api/workflows/templates` | List built-in templates |
| `POST` | `/api/workflows/templates/seed` | Seed default templates |
| `POST` | `/api/workflows/search` | Search workflows by name |
| `POST` | `/api/workflows/save-from-execution` | Save from execution log |

### `POST /api/workflows`

**Request:**
```json
{
  "name": "My Workflow",
  "description": "Optional description",
  "steps": [{"action": "open_app", "target": "notepad"}],
  "trigger_type": "manual"
}
```
- `name` — **required**, `1 ≤ length ≤ 255`
- `trigger_type` — optional, enum: `manual | hotkey | schedule | event`

### `POST /api/workflows/{id}/clone`

**Request:**
```json
{ "new_name": "My Clone" }
```
- `new_name` — **required**, `1 ≤ length ≤ 255`

### `POST /api/workflows/{id}/export`

**Request:**
```json
{ "format": "json" }
```
- `format` — optional, default `"json"`, enum: `json | csv`

### `POST /api/workflows/search`

**Request:**
```json
{ "query": "deploy" }
```

---

## Executions (`/api/executions`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/executions` | List executions |
| `POST` | `/api/executions` | Create an execution |
| `GET` | `/api/executions/{id}` | Get execution details |
| `POST` | `/api/executions/{id}/cancel` | Cancel a running execution |
| `GET` | `/api/executions/{id}/logs` | Get execution logs |
| `POST` | `/api/executions/{id}/pause` | Pause execution |
| `POST` | `/api/executions/{id}/resume` | Resume execution |
| `GET` | `/api/executions/{id}/pause-status` | Check pause state |
| `GET` | `/api/executions/{id}/context-snapshots` | List context snapshots |
| `GET` | `/api/executions/{id}/context-snapshots/{sid}` | Get specific snapshot |
| `POST` | `/api/executions/{id}/context-snapshots/{sid}/suggestions` | Get recovery suggestions |

---

## Settings (`/api/settings`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/settings` | Get all settings |
| `PUT` | `/api/settings` | Update a setting |
| `GET` | `/api/settings/mode` | Get current operation mode |
| `POST` | `/api/settings/mode` | Set operation mode |

### `PUT /api/settings`

**Request:**
```json
{ "key": "theme", "value": "dark" }
```
- `key` — **required**, `max_length: 100`
- `value` — **required**, string

### `POST /api/settings/mode`

**Request:**
```json
{ "mode": "supervised" }
```
- `mode` — **required**, enum: `auto | supervised | locked`

---

## Agents (`/api/agents`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/agents` | List registered agents |
| `POST` | `/api/agents` | Register an agent |
| `DELETE` | `/api/agents/{agent_name}` | Unregister an agent |
| `POST` | `/api/agents/health-check` | Health check all agents |
| `POST` | `/api/agents/{agent_name}/health-check` | Health check one agent |

### `POST /api/agents`

**Request:**
```json
{
  "name": "browser-agent",
  "host": "localhost",
  "port": 9100,
  "capabilities": ["web_browse", "screenshot"]
}
```

---

## Audit (`/api/audit`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/audit` | List audit entries |
| `GET` | `/api/audit/verify` | Verify hash-chain integrity |

### `GET /api/audit/verify`

**Response 200:**
```json
{
  "valid": true,
  "entries_checked": 42,
  "first_broken_id": null,
  "message": "Chain intact"
}
```

---

## Sessions (`/api/sessions`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/sessions` | List active JWT sessions |
| `DELETE` | `/api/sessions/{session_id}` | Revoke a session |
| `POST` | `/api/sessions/revoke-all` | Revoke all active sessions |

---

## Queue (`/api/queue`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/queue` | List pending queue items |
| `POST` | `/api/queue/drain` | Drain all pending items |
| `POST` | `/api/queue/{item_id}/reject` | Reject a queue item |
| `POST` | `/api/queue/clear-expired` | Clear expired items |

---

## Learning Engine (`/api/learning`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/learning/patterns` | Record an execution pattern |
| `GET` | `/api/learning/patterns` | List learned patterns |
| `GET` | `/api/learning/suggestions` | Get pattern-based suggestions |
| `POST` | `/api/learning/suggestions/{id}/accept` | Accept a suggestion |
| `POST` | `/api/learning/suggestions/{id}/dismiss` | Dismiss a suggestion |
| `POST` | `/api/learning/confidence` | Manual confidence update |
| `POST` | `/api/learning/confidence/auto-adjust` | Auto-adjust confidence |
| `GET` | `/api/learning/confidence/{context}` | Get threshold for context |
| `GET` | `/api/learning/confidence` | Get global confidence history |
| `POST` | `/api/learning/encrypt` | Encrypt plaintext |
| `POST` | `/api/learning/decrypt` | Decrypt ciphertext |

### `POST /api/learning/patterns`

**Request:**
```json
{
  "intent": "open browser and search",
  "steps": [
    {"action": "open_app", "target": "chrome"},
    {"action": "type_text", "target": "search bar", "value": "query"}
  ]
}
```
- `intent` — **required**, `min_length: 1`
- `steps` — **required**, list of step dicts

### `POST /api/learning/confidence`

**Request:**
```json
{
  "context": "workflow_execution",
  "old_value": 0.7,
  "new_value": 0.85,
  "reason": "User confirmed accuracy"
}
```
- `old_value`, `new_value` — `0.0 ≤ value ≤ 1.0`

### `POST /api/learning/confidence/auto-adjust`

**Request:**
```json
{
  "context": "click_detection",
  "current_value": 0.75,
  "user_accepted": true
}
```

### `POST /api/learning/encrypt`

**Request:**
```json
{
  "plaintext": "sensitive data",
  "passphrase": "MySecure123"
}
```
- `passphrase` — **required**, `min_length: 8`

**Response 200:**
```json
{ "encrypted": "gAAAAA..." }
```

### `POST /api/learning/decrypt`

**Request:**
```json
{
  "encrypted": "gAAAAA...",
  "passphrase": "MySecure123"
}
```

---

## Voice (`/api/voice`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/voice/transcribe` | Transcribe base64 audio |
| `POST` | `/api/voice/transcribe/upload` | Transcribe uploaded file |
| `POST` | `/api/voice/silence` | Detect silence in audio |
| `GET` | `/api/voice/config` | Get voice configuration |
| `PUT` | `/api/voice/config` | Update voice configuration |
| `GET` | `/api/voice/status` | Get voice service status |

### `PUT /api/voice/config`

**Request:**
```json
{
  "confidence_threshold": 0.7,
  "silence_duration": 2.0,
  "max_recording_seconds": 30
}
```
- `confidence_threshold` — `0.0 ≤ value ≤ 1.0`
- `silence_duration` — `0.5 ≤ value ≤ 10.0`
- `max_recording_seconds` — `5 ≤ value ≤ 120`

---

## WebSocket (`/ws`)

Real-time bidirectional communication for live execution updates.

| Path | Description |
|------|-------------|
| `ws://localhost:9000/ws` | WebSocket connection |

**Inbound message types:** `subscribe`, `chat_message`, `ping`
**Outbound message types:** `execution_update`, `step_result`, `error`, `pong`

---

## Error Responses

All errors follow a structured format:

```json
{
  "error_code": "WF_001",
  "message": "Workflow not found",
  "detail": "No workflow with id abc-123",
  "ux_action": "show_error",
  "retry_allowed": false
}
```

### Error Code Prefixes

| Prefix | Category |
|--------|----------|
| `AG_` | Agent errors (001–007) |
| `WF_` | Workflow errors (001–011) |
| `EX_` | Execution errors (001–005) |
| `SEC_` | Security errors (001–014) |
| `SYS_` | System errors (001–010) |
| `VAL_` | Validation errors (001–008) |
| `GEN_` | General errors (001–005) |
| `LRN_` | Learning errors (001–003) |

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `400` | Bad request / business logic error |
| `401` | Authentication required or failed |
| `403` | Forbidden / insufficient permissions |
| `404` | Resource not found |
| `405` | Method not allowed |
| `409` | Conflict (duplicate, already running) |
| `422` | Validation error |
| `429` | Rate limited / locked out |
| `500` | Internal server error |
| `503` | Service unavailable |
| `504` | Timeout (agent/workflow) |
| `507` | Insufficient storage |

---

## Interactive Docs

When running in debug mode, interactive API documentation is available at:

- **Swagger UI:** `http://localhost:9000/docs`
- **ReDoc:** `http://localhost:9000/redoc`
