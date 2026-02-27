@echo off
REM ========================================
REM Build JARVIS AI Desktop Installer
REM Creates JARVIS-AI-Setup.exe (native desktop app)
REM ========================================

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [!] Administrator privileges required
    echo.
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %CD% ^& %~s0' -Verb RunAs"
    exit /b 1
)

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   JARVIS AI Desktop Installer Builder
echo ========================================
echo.

REM Check for Developer Mode (Windows 11/10)
powershell -Command "
$devModeRegPath = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock'
$devModeValue = Get-ItemProperty -Path $devModeRegPath -Name 'AllowDevelopmentWithoutDevLicense' -ErrorAction SilentlyContinue
if ($null -eq $devModeValue -or $devModeValue.AllowDevelopmentWithoutDevLicense -ne 1) {
    Write-Host '[WARNING] Developer Mode not enabled!'
    Write-Host ''
    Write-Host 'IMPORTANT: Windows Developer Mode is required to build the desktop app.'
    Write-Host ''
    Write-Host 'To enable:'
    Write-Host '  1. Windows 11: Settings → System → For developers → Enable Developer Mode'
    Write-Host '  2. Windows 10: Settings → Update & Security → For developers → Developer mode'
    Write-Host '  3. Restart your computer'
    Write-Host ''
    Write-Host 'Without Developer Mode, the build may fail with symbolic link errors.'
    Write-Host ''
}
"

REM Navigate to frontend directory
cd frontend

echo [1/3] Building React frontend with Vite...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed
    pause
    exit /b 1
)

echo [2/3] Building Electron app with electron-builder...
echo.
echo This will create:
echo   - JARVIS-AI-Setup.exe (installer with Start Menu shortcut)
echo   - JARVIS AI.exe (portable executable, no installation needed)
echo.

call npm run electron:build
if %errorlevel% neq 0 (
    echo [ERROR] Electron build failed
    echo.
    echo  If you see "symbolic link" errors, please:
    echo  1. Enable Windows Developer Mode (see above)
    echo  2. Restart your computer
    echo  3. Run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [✓] Build Complete!
echo ========================================
echo.
echo Desktop executables created in: dist\
echo.
echo Files created:
echo   - dist\JARVIS-AI-Setup.exe (Recommended - with installer)
echo   - dist\JARVIS AI.exe (Portable - run directly)
echo.
echo Next steps:
echo   1. Run dist\JARVIS-AI-Setup.exe (or dist\"JARVIS AI.exe" for portable)
echo   2. JARVIS AI will be installed as a native desktop application
echo   3. Click the desktop shortcut or Start button to launch
echo.
echo The app will:
echo   - Automatically start the backend server
echo   - Open as a native Electron desktop window (NOT a browser)
echo   - Display the chat interface
echo   - Work just like any other installed Windows application
