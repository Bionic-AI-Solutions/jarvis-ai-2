# JARVIS AI - Quick Command Reference

## Test Commands (Use via Chat API)

```bash
# Vision Service Test
"Take a screenshot and tell me what you see"
→ Executes: screenshot → moondream analysis → response

# App Automation Tests
"Open notepad"           → ✓ Works
"Close notepad"          → ✓ Works  
"Open calculator"        → ✓ Works
"Open chrome"            → ✓ Works

# Browser Navigation Tests
"Open chrome and navigate to google.com"               → ✓ Works (3461ms)
"Open chrome and go to github.com"                     → ✓ Works (3480ms)
"Open chrome and visit google.com then search python" → ✓ Works (4000ms)

# Voice/Audio Tests (Framework ready)
[Not yet tested - piper_tts_service available]
[Whisper transcription framework ready]
```

## API Endpoints

### Create Chat Session
```
POST /api/chats
{
  "name": "My Chat",
  "description": "Optional description"
}
```

### Send Message & Get Response
```
POST /api/chats/{session_id}/messages
{
  "content": "Take a screenshot",
  "role": "user"
}

Response (after pipeline execution):
{
  "id": "msg-id",
  "session_id": "session-id",
  "role": "assistant",
  "content": "Done! Completed 1 step(s) in 181ms:\n  ✓ Capture screenshot...",
  "sequence": 2
}
```

### List Agents
```
GET /api/agents
→ Returns all 12 registered agents with capabilities
```

### Check Health
```
GET /api/health
→ Returns: ollama=true, database=true, agents_registered=12
```

## Workflow Examples

### Screenshot Analysis Workflow
```
User: "Take a screenshot and tell me what you see"
  ↓ RAG Agent: Generate plan [step: "capture_screenshot"]
  ↓ Safety Agent: Approved
  ↓ Execution Agent: pyautogui.screenshot() → saved to temp
  ↓ Observer Agent: Run moondream: "What's on screen?"
  ↓ Response: moondream analysis result
```

### App Automation Workflow
```
User: "Open chrome and navigate to google.com"
  ↓ RAG Agent: Detected "open + navigate" pattern
    Generated 4-step plan:
    1. open chrome
    2. wait 2 seconds
    3. type google.com
    4. press enter
  ↓ Safety Agent: Approved
  ↓ Execution Agent: subprocess.Popen("chrome") + pyautogui...
  ↓ Observer Agent: Verification (2 checks)
  ↓ Response: "Done! Completed 4 step(s) in 3461ms"
```

## Model Information

### Available Models (Ollama)
1. **moondream:latest** - Vision (1.0B, 3-bit quantized)
   - Used by: Observer Agent for screenshot analysis
   - Provider: Ollama (http://localhost:11434)

2. **qwen2.5:3b** - Reasoning (3.1B, Q4_K_M quantized)
   - Used by: RAG Agent, LLM fallback parsing
   - Provider: Ollama (http://localhost:11434)

3. **qwen2.5vl:7b** - Vision+Language (8.3B, optional)
   - Available for advanced analysis

4. **qwen3-vl:8b** - Vision+Language (8.8B, optional)
   - Available for advanced analysis

## Service Integration

### Vision Service
```python
from app.services.vision_service import VisionService
vision = VisionService()
result = await vision.analyze_screenshot("path/to/screenshot.png", "What is visible?")
# Returns: VisionResult(text, confidence, ui_changes, detections, verified)
```

### Piper TTS Service
```python
from app.services.piper_tts_service import PiperTTSService
tts = PiperTTSService()
result = await tts.synthesize("Hello world", voice="en_US-ryan-medium", output_path="output.wav")
# Returns: SynthesisResult(audio_bytes, text, duration_ms, model_used)
```

### Ollama Service
```python
from app.services.ollama_service import OllamaService
ollama = OllamaService()
response = await ollama.generate(
    prompt="Generate a plan for: open notepad",
    system="You are a planning agent",
    model="qwen2.5:3b"
)
models = await ollama.list_models()  # Returns all 4 available models
```

## Database

### SQLite Location
```
backend/data/jarvis.db
```

### Key Tables
- `chat_sessions` - Chat session metadata
- `chat_messages` - Chat message history
- `workflow_executions` - Execution logs
- `execution_logs` - Step-by-step execution details
- `context_snapshots` - Context for recovery
- `execution_patterns` - Learned workflows
- `application_registry` - Available apps

## Backend Server

### Start Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --log-level info
```

### Verify Services Running
```bash
# Check ollama (should return 4 models)
curl http://localhost:11434/api/tags

# Check JARVIS backend health
curl http://localhost:9000/api/health

# Check agents
curl http://localhost:9000/api/agents
```

## Troubleshooting

### Issue: "Unknown error" response
**Solutions**:
1. Check if app exists: "Open notepad" works, "Open gmail" doesn't (use Chrome + URL)
2. Check ollama: `curl localhost:11434/api/tags`
3. Check logs: Backend outputs agent pipeline details
4. Verify agent is running: `GET /api/agents`

### Issue: Screenshot takes too long
**Solution**: moondream analysis takes ~150ms - this is normal

### Issue: Browser navigation fails
**Solution**: Ensure Chrome is installed; use "Open chrome" first (agent auto-detects)

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Screenshot | 50-100ms | System call |
| moondream analysis | 120-170ms | Model inference |
| App launch | 800-1500ms | Windows startup |
| Single-step workflow | 170-500ms | Total pipeline |
| Multi-step workflow | 3-4s | Per step overhead |

## Next Features To Implement

- [ ] **TTS Output** - Speak responses via Piper
- [ ] **Voice Input** - Whisper transcription
- [ ] **Failure Recovery** - 6-level recovery system
- [ ] **Clarification UI** - Ask user when ambiguous
- [ ] **Frontend Display** - Real-time step progress
- [ ] **Workflow Learning** - Remember and reuse patterns

---

*JARVIS AI Development Guide - Sprint 2 Complete*
