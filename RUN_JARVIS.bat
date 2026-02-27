@echo off
REM JARVIS AI Desktop Application Launcher
REM Starts backend server and launches Electron app

setlocal enabledelayedexpansion

echo ========================================
echo   JARVIS AI Desktop - Starting Up...
echo ========================================
echo.

REM Check if backend server is running
echo [*] Checking backend server...
netstat -ano | findstr 9000 >nul
if %errorlevel% equ 0 (
    echo [+] Backend already running on port 9000
) else (
    echo [+] Starting backend server...
    cd backend
    python -m pip install -q -r requirements.txt 2>nul
    start "" python run_server.py
    echo [+] Backend server started (localhost:9000)
    cd ..
    timeout /t 2 /nobreak
)

echo.
echo [*] Launching JARVIS AI Desktop...
echo.

REM Launch Electron app
cd frontend\dist
start "" "JARVIS AI Portable.exe"

echo [+] JARVIS AI is now running!
echo.
echo To stop the backend server, use Ctrl+C in the backend terminal
echo.
