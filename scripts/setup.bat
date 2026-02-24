@echo off
:: JARVIS AI — Windows Installer Helper
:: Installs Python dependencies, Node dependencies, and verifies Ollama.

echo ============================================================
echo   JARVIS AI — Setup
echo ============================================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.12+ from python.org
    pause
    exit /b 1
)

:: Check Node
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Install Node 18+ from nodejs.org
    pause
    exit /b 1
)

:: Check Ollama
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama not found in PATH. Install from ollama.com
    echo            JARVIS will run but LLM features will be unavailable.
    echo.
)

echo.
echo [1/4] Setting up Python virtual environment...
cd /d "%~dp0..\backend"
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo.
echo [3/4] Installing Node dependencies...
cd /d "%~dp0..\frontend"
call npm install --silent

echo.
echo [4/4] Verifying Ollama model...
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    ollama list 2>nul | findstr /i "qwen2.5" >nul
    if %errorlevel% neq 0 (
        echo    Pulling default model qwen2.5:3b ...
        ollama pull qwen2.5:3b
    ) else (
        echo    qwen2.5 model found.
    )
) else (
    echo    Skipping — Ollama not installed.
)

echo.
echo ============================================================
echo   Setup complete!
echo.
echo   Start backend:  cd backend ^& venv\Scripts\activate ^& uvicorn app.main:app --port 9000
echo   Start frontend: cd frontend ^& npm run dev
echo ============================================================
pause
