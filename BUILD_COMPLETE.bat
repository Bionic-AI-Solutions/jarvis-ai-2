@echo off
REM Complete build workflow for JARVIS AI Desktop App
REM 1. Build backend exe with PyInstaller
REM 2. Build frontend
REM 3. Package with electron-builder

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ========================================
echo   JARVIS AI - Complete Build Process
echo ========================================
echo.

REM Step 1: Build backend .exe
echo [Step 1/3] Building backend with PyInstaller...
echo.
call BUILD_BACKEND_EXE.bat
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Backend build failed. Aborting.
    pause
    exit /b 1
)

echo.
echo [Step 2/3] Building Electron desktop app...
echo.

cd frontend
call npm run electron:build

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [✓] BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Desktop app created in: dist\
    echo.
    echo Files:
    echo   - dist\win-unpacked\JARVIS AI.exe (portable)
    echo   - dist\JARVIS-AI-Setup.exe (installer, if enabled)
    echo.
    echo Next: Double-click the .exe to launch!
    echo.
) else (
    echo.
    echo [ERROR] Electron build failed
    echo.
)

cd ..
pause
