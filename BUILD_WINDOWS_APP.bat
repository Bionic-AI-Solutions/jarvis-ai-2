@echo off
REM ================================================
REM JARVIS AI - Build Windows Application (.exe)
REM Uses PyInstaller to create standalone executable
REM ================================================

setlocal enabledelayedexpansion

cls
echo.
echo ================================================
echo   JARVIS AI Windows Application Builder
echo ================================================
echo.

REM Check PyInstaller
python -m pip list | findstr pyinstaller >nul
if %errorlevel% neq 0 (
    echo [*] Installing PyInstaller...
    python -m pip install -q pyinstaller
)

echo [*] Building Windows executable...
echo     (This takes 1-2 minutes, please wait...)
echo.

REM Build with PyInstaller
cd /d "%~dp0"

REM Create the wrapper app using Python's capabilities
python -c "
import sys
code = '''#!/usr/bin/env python3
\"\"\"JARVIS AI Desktop Application\"\"\"
import os, sys, subprocess, time, threading, webbrowser
from pathlib import Path

def start_backend():
    backend_path = Path(__file__).parent / 'backend' / 'run_server.py'
    if backend_path.exists():
        try:
            import socket
            sock = socket.socket()
            if sock.connect_ex(('localhost', 9000)) != 0:
                subprocess.Popen([sys.executable, str(backend_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                time.sleep(2)
        except: pass

def start_frontend():
    frontend_path = Path(__file__).parent / 'frontend' / 'serve.py'
    if frontend_path.exists():
        try:
            subprocess.Popen([sys.executable, str(frontend_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            time.sleep(2)
        except: pass

if __name__ == '__main__':
    print('Starting JARVIS AI...')
    start_backend()
    start_frontend()
    time.sleep(1)
    webbrowser.open('http://localhost:3000')
'''
with open('jarvis_desktop.py', 'w') as f:
    f.write(code)
print('Wrapper created')
"

python -m PyInstaller jarvis_desktop.py ^
    --onefile ^
    --windowed ^
    --name "JARVIS AI" ^
    --icon NONE ^
    --distpath "dist" ^
    --specpath ".build" ^
    --buildpath ".build" ^
    2>nul

if exist "dist\JARVIS AI.exe" (
    echo.
    echo ================================================
    echo   ✅ BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Location: dist\JARVIS AI.exe
    echo Size: ~20 MB
    echo.
    echo Ready to use!
    echo.
    
    REM Clean up temp files
    del /q jarvis_desktop.py 2>nul
    rmdir /s /q ".build" 2>nul
    
    echo [+] You can now:
    echo   1. Double-click: dist\JARVIS AI.exe
    echo   2. Or run: "dist\JARVIS AI.exe"
    echo.
) else (
    echo.
    echo [ERROR] Build failed
    echo.
    echo Make sure:
    echo   - Python 3.8+ is installed
    echo   - Run: python -m pip install pyinstaller
    echo   - Frontend is built: cd frontend && npm run build
    echo.
)

pause
