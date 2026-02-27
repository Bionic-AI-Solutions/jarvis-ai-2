# JARVIS AI - Desktop App Setup

## Issue Encountered
The electron-builder couldn't create the native desktop application due to Windows permission restrictions when creating symbolic links.

## Quick Workaround (Temporary)

**For immediate testing:**
- Double-click `JARVIS_AI.vbs` to launch JARVIS AI
- This will silently start the backend and open in your browser
- **Note:** This is NOT a native desktop app (opens in default browser), just a workaround

## Permanent Solution - Enable Developer Mode OnWindows

To build a true native desktop application (native window, no browser), enable Developer Mode on Windows:

### For Windows 11:
1. Open **Settings** → **System** → **For developers**
2. Toggle **Developer Mode** to **ON**
3. Click **Yes** when prompted to install developer features
4. Wait for installation to complete (~30 seconds)
5. Restart your computer

### For Windows 10:
1. Open **Settings** → **Update & Security** → **For developers**
2. Select **Developer mode**
3. Click **Yes** when prompted
4. Wait for installation
5. Restart your computer

## After Enabling Developer Mode

Once Developer Mode is enabled, run the build again:

```bash
cd "e:\Bionic AI\Jarvis AI 3"
.\BUILD_INSTALLER.bat
```

This will create:
- `frontend\dist\JARVIS AI.exe` (portable, can run directly)
- `frontend\dist\JARVIS-AI-Setup.exe` (installer, creates Start Menu shortcut)

## Expected Result

After enabling Developer Mode and building:
1. Double-click `JARVIS-AI-Setup.exe` or `JARVIS AI.exe`
2. JARVIS AI opens as a **native desktop application**
3. Backend automatically starts in background
4. No command windows visible
5. Works just like installing Chrome

## Why This Is Needed

Windows requires special permissions to create symbolic links (used by the code signing tools). Developer Mode grants these permissions without needing admin for every action.

## Additional Notes

- Backend: `http://localhost:9000` (FastAPI, 12 agents operational)
- Voice/TTS: Requires Ollama (`https://ollama.ai`) running with models downloaded
- Models: qwen2.5:3b, moondream, whisper-medium, piper

## Current Files

- `JARVIS_AI.vbs` - Quick launcher (opens in browser)
- `LAUNCH_JARVIS_HIDDEN.bat` - Backend launcher
- `BUILD_INSTALLER.bat` - Build desktop app (requires Developer Mode)
