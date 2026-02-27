@echo off
REM ========================================
REM  JARVIS AI - Desktop Application Launcher
REM  This starts the backend, then launches the app
REM ========================================

cd /d "%~dp0"

echo.
echo ========================================
echo   JARVIS AI - Starting...
echo ========================================
echo.

REM Check if backend is already running
echo [1/3] Checking backend...
powershell -Command "try { $r = Invoke-WebRequest 'http://localhost:9000/health' -TimeoutSec 1 -ErrorAction Stop; if ($r.StatusCode -eq 200) { exit 0 } } catch { }; exit 1" >nul 2>&1

if %errorlevel% equ 0 (
    echo [✓] Backend already running
) else (
    echo [2/3] Starting backend server...
    start "" /B python backend/run_server.py
    echo Waiting for backend to be ready...
    
    powershell -Command "
    for (\$i = 0; \$i -lt 30; \$i++) {
        try {
            \$r = Invoke-WebRequest 'http://localhost:9000/health' -TimeoutSec 1 -ErrorAction Stop
            if (\$r.StatusCode -eq 200) {
                Write-Host '[✓] Backend ready'
                exit 0
            }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    Write-Host '[!] Backend timeout'
    exit 1
    "
)

echo [3/3] Launching JARVIS AI app...
echo.

REM Launch the desktop app
start "" JARVIS_AI.exe

echo.
echo ========================================
echo [✓] JARVIS AI is launching!
echo ========================================
echo.
