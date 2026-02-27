@echo off
REM ============================================
REM  JARVIS AI - Browser Launcher
REM  Simple way to start JARVIS AI
REM ============================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ========================================
echo   JARVIS AI - Starting...
echo ========================================
echo.

REM Check if backend is already running on port 9000
echo [1/3] Checking backend server on port 9000...
powershell -Command "
try {
    \$r = Invoke-WebRequest 'http://127.0.0.1:9000/health' -TimeoutSec 1 -ErrorAction Stop
    if (\$r.StatusCode -eq 200) {
        Write-Host '[OK] Backend already running'
        exit 0
    }
} catch { }
Write-Host '[Starting] Backend needs to be started'
exit 1
" >nul 2>&1

if %errorlevel% neq 0 (
    echo [2/3] Starting backend server...
    echo.
    start "JARVIS AI Backend" cmd /k "cd backend && python run_server.py"
    echo Backend window opened. Waiting for server to be ready...
    
    powershell -Command "
    Write-Host 'Waiting for backend to respond...'
    for (\$i = 0; \$i -lt 15; \$i++) {
        try {
            \$r = Invoke-WebRequest 'http://127.0.0.1:9000/health' -TimeoutSec 1 -ErrorAction Stop
            if (\$r.StatusCode -eq 200) {
                Write-Host '[OK] Backend ready!'
                exit 0
            }
        } catch { }
        Write-Host -NoNewline '.'
        Start-Sleep -Seconds 1
    }
    Write-Host '[!] Timeout waiting for backend'
    exit 1
    "
) else (
    echo [2/3] Backend already running
)

echo.
echo [3/3] Opening JARVIS AI in browser...
echo.

REM Open browser to the backend
timeout /t 1 /nobreak >nul
start http://127.0.0.1:9000/

echo.
echo ========================================
echo [OK] JARVIS AI is running!
echo ========================================
echo.
echo Backend URL: http://127.0.0.1:9000/
echo.
echo Keep the backend console window open.
echo.
pause

