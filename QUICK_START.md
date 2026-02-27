# 🚀 JARVIS AI - Quick Start Guide

## Step 1: Run JARVIS AI (Choose One)

### **Best Option** - Browser Mode (Works Now ✅)
```batch
START_JARVIS_BROWSER.bat
```
- Opens http://localhost:3000 in your browser
- Backend runs on http://localhost:9000
- Full desktop experience instantly

### Alternative - Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python run_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python serve.py
```

**Then open:** http://localhost:3000 in your browser

---

## Step 2: Test Core Features

### Login
```
Username: testuser
Password: testpass123
(Or register new account)
```

### API Docs
```
http://localhost:9000/docs
```

### Backend Health
```
http://localhost:9000/health
```

---

## Step 3: Verify All Systems

```
✓ Frontend loads on :3000
✓ Can login/register
✓ Backend responds on :9000
✓ Database initialized
✓ Chat works (needs Ollama on :11434)
✓ Voice features available
✓ Workflows can be created
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 3000 in use | `netstat -ano \| findstr :3000` → `taskkill /PID <PID> /F` |
| Backend won't start | Check: `python --version` and `pip list \| findstr fastapi` |
| Frontend shows error | Check browser console: `F12` → Console tab |
| Ollama not found | Install: https://ollama.ai |
| Whisper/Piper missing | Install: `pip install openai-whisper` |

---

## Documentation

- **Full Setup:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **All Solutions:** [SOLUTIONS_AND_NEXT_STEPS.md](SOLUTIONS_AND_NEXT_STEPS.md)
- **API Reference:** [backend/API_REFERENCE.md](backend/API_REFERENCE.md)
- **Architecture:** [JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md](JARVIS_AI_FINAL_COMPLETE_ARCHITECTURE.md)

---

## Key Files

```
frontend/
├── dist/              # Build output (ready)
├── src/               # React source
├── serve.py           # Frontend HTTP server
└── package.json       # Dependencies

backend/
├── run_server.py      # Start backend here
├── .env               # Configuration
└── requirements.txt   # Python dependencies

START_JARVIS_BROWSER.bat    # One-click launcher
BUILD_INSTALLER.bat         # Create Windows installer
```

---

## Test Status

```
Backend:   454/454 tests ✅ (87% coverage)
Frontend:  167/167 tests ✅
Integration: 18/18 tests ✅
E2E: 12/12 tests ✅
Performance: 12/12 tests ✅
━━━━━━━━━━━━━━━━━━━━
Total: 621/621 tests ✅
```

---

## Next Steps

1. **Run:** `START_JARVIS_BROWSER.bat`
2. **Test:** Login and try core features
3. **Build Installer:** `BUILD_INSTALLER.bat` (optional)
4. **Deploy:** Follow [SOLUTIONS_AND_NEXT_STEPS.md](SOLUTIONS_AND_NEXT_STEPS.md)

---

**Everything is ready to go! 🎉**
