@echo off
REM Build backend as standalone .exe using PyInstaller

cd /d "%~dp0"

echo.
echo ========================================
echo   Building Backend with PyInstaller
echo ========================================
echo.

cd backend

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/3] Installing PyInstaller...
    python -m pip install pyinstaller -q
)

echo [2/3] Building backend executable...
python -m PyInstaller ^
    --onefile ^
    --name run_server ^
    --distpath ..\frontend\dist\resources ^
    --specpath build_spec ^
    --hidden-import=uvicorn ^
    --hidden-import=fastapi ^
    --hidden-import=sqlalchemy ^
    --hidden-import=pydantic ^
    --console ^
    run_server.py

if %errorlevel% equ 0 (
    echo [3/3] Success!
    echo.
    echo Backend executable created at:
    echo   frontend\dist\resources\run_server.exe
    echo.
    echo Now run: npm run electron:build
    echo.
) else (
    echo [ERROR] PyInstaller build failed
    echo.
    echo Troubleshooting:
    echo - Ensure all dependencies are installed
    echo - Run: pip install -r requirements.txt
    echo.
)

cd ..
pause
