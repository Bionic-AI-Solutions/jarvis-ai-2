@echo off
REM JARVIS AI - Diagnostic & Launch Tool

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ========================================
echo   JARVIS AI - Diagnostic Check
echo ========================================
echo.

REM Test 1: Check if backend is running
echo [Test 1] Checking if backend is running on port 9000...
powershell -Command "
try {
    \$r = Invoke-WebRequest 'http://127.0.0.1:9000/health' -TimeoutSec 2 -ErrorAction Stop
    if (\$r.StatusCode -eq 200) {
        Write-Host '[PASS] Backend is running'
        exit 0
    }
} catch { }
Write-Host '[FAIL] Backend is NOT running'
exit 1
" >nul 2>&1

if %errorlevel% equ 0 (
    set "BACKEND_RUNNING=YES"
    echo Status: PASS - Backend is running
) else (
    set "BACKEND_RUNNING=NO"
    echo Status: FAIL - Backend not running
)

echo.

REM Test 2: Check if JARVIS_AI.exe exists
echo [Test 2] Checking for JARVIS_AI.exe...
if exist "JARVIS_AI.exe" (
    echo Status: PASS - JARVIS_AI.exe found
    set "APP_EXISTS=YES"
) else (
    echo Status: FAIL - JARVIS_AI.exe not found
    set "APP_EXISTS=NO"
)

echo.
echo ========================================
echo.

REM Diagnostic summary
if "%BACKEND_RUNNING%"=="YES" and "%APP_EXISTS%"=="YES" (
    echo [Ready] All components present. Would you like to:
    echo.
    echo   [1] Start JARVIS AI (backend already running)
    echo   [2] Run diagnostics (detailed debug)
    echo   [3] Cancel
    echo.
    
    set /p CHOICE="Enter choice (1-3): "
    
    if "!CHOICE!"=="1" (
        echo.
        echo Starting JARVIS AI application...
        start "" JARVIS_AI.exe
        echo [Done] App launched in new window
        goto :end
    ) else if "!CHOICE!"=="2" (
        goto :diagnostics
    ) else (
        echo Cancelled.
        goto :end
    )
) else if "%BACKEND_RUNNING%"=="NO" and "%APP_EXISTS%"=="YES" (
    echo [Ready] Backend needs to be started. Starting now...
    echo.
    
    echo Attempting to start backend server...
    start "JARVIS Backend" /wait cmd /c "cd /d "%~dp0" && cd backend && python run_server.py"
    
    echo.
    echo Backend exited. Launching app...
    start "" JARVIS_AI.exe
    goto :end
) else (
    echo [ERROR] Missing required files:
    if "%APP_EXISTS%"=="NO" echo   - JARVIS_AI.exe not found
    echo.
    echo Please rebuild with: npm run electron:build
    goto :end
)

:diagnostics
echo.
echo ========================================
echo   Detailed Diagnostics
echo ========================================
echo.

echo [1] Backend Health Check:
powershell -Command "
try {
    \$r = Invoke-WebRequest 'http://127.0.0.1:9000/health' -TimeoutSec 2 -ErrorAction Stop
    Write-Host '[OK] Status: ' \$r.StatusCode
    Write-Host '[OK] Response: ' \$r.Content
} catch {
    Write-Host '[ERROR] Cannot reach backend'
    Write-Host '[ERROR] Details: ' \$_.Exception.Message
}
"

echo.
echo [2] JARVIS_AI.exe Properties:
if exist "JARVIS_AI.exe" (
    powershell -Command "
    \$file = Get-Item 'JARVIS_AI.exe'
    Write-Host 'File: ' \$file.Name
    Write-Host 'Size: ' ([math]::Round(\$file.Length/1MB, 2)) 'MB'
    Write-Host 'Modified: ' \$file.LastWriteTime
    "
) else (
    echo [ERROR] File not found
)

echo.
echo [3] Backend Process Check:
tasklist | find /i "python" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python process running
) else (
    echo [WARN] No Python process found
)

echo.
goto :end

:end
echo.
echo Press any key to close...
pause >nul
