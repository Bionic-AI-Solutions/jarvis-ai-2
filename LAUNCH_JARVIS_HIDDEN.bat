@echo off
REM Hidden launcher for JARVIS AI backend

cd /d "%~dp0"

REM Check if backend already running
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:9000/health' -TimeoutSec 1 -ErrorAction Stop; if ($response.StatusCode -eq 200) { exit 0 } } catch { }; exit 1"
if %errorlevel% equ 0 (
    REM Backend already running
    exit /b 0
)

REM Start backend in background
start "" /B python backend/run_server.py

REM Wait for backend to be ready (with retries)
powershell -Command "
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri 'http://localhost:9000/health' -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            exit 0
        }
    } catch { }
    Start-Sleep -Milliseconds 500
}
exit 1
"
