@echo off
REM ================================================
REM  JARVIS AI - Windows Desktop Application
REM  Runs as a standalone Windows app
REM ================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Check if backend/frontend already running
tasklist /FI "WINDOWTITLE eq JARVIS*" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    REM Already running, just open the URL
    start http://localhost:3000
    exit /b 0
)

REM Start backend in background
echo Launching JARVIS AI...
start "" /B cmd /C "cd backend && python run_server.py >nul 2>&1"

REM Wait for backend
timeout /t 2 /nobreak

REM Start frontend in background  
start "" /B cmd /C "cd frontend && python serve.py >nul 2>&1"

REM Wait for frontend
timeout /t 2 /nobreak

REM Try to open with Chrome in App Mode (looks like native app, no browser UI)
where chrome >nul 2>&1
if %errorlevel% equ 0 (
    start chrome --app=http://localhost:3000 --new-window
    exit /b 0
)

REM Try Edge
where msedge >nul 2>&1
if %errorlevel% equ 0 (
    start msedge --app=http://localhost:3000
    exit /b 0
)

REM Fall back to default browser
start http://localhost:3000
