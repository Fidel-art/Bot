@echo off
title SMC Trading Bot — Full System Launcher
echo ==================================================
echo SMC Trading Bot — Full System Launcher
echo ==================================================
echo.
echo Architecture:
echo   Docker (Linux containers): Frontend + Backend + Database + Bot
echo   Windows Host:              MT5 Bridge + MT5 Terminal
echo.

:: Check prerequisites
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Setting up Python environment...
echo.
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -q -r backend\requirements.txt 2>nul
pip install -q -r mt5_bridge\requirements.txt

:: Kill any existing bridge process
taskkill /f /im uvicorn.exe >nul 2>&1

echo.
echo [2/5] Starting MT5 Bridge on Windows host...
echo.
start "MT5 Bridge" cmd /k "cd /d %~dp0 && title MT5 Bridge && call venv\Scripts\activate && python -m uvicorn mt5_bridge.server:app --host 0.0.0.0 --port 8765 --log-level info"
timeout /t 4 /nobreak >nul

echo.
echo [3/5] Building and starting Docker containers...
echo.
docker-compose build --parallel
docker-compose up -d

echo.
echo [4/5] Waiting for services to be ready...
echo.
timeout /t 8 /nobreak >nul

echo.
echo [5/5] Checking service health...
echo.

:: Check backend health
docker exec smc_bot_backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/api/system/health').read().decode())" 2>nul && (
    echo [OK] Backend API is healthy
) || (
    echo [..] Backend API starting up...
)

:: Check MT5 bridge
python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8765/health'); print(r.read().decode())" 2>nul && (
    echo [OK] MT5 Bridge is running
) || (
    echo [..] MT5 Bridge starting up...
)

echo.
echo ==================================================
echo All services launched!
echo ==================================================
echo.
echo   Frontend:     http://localhost:3000
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   MT5 Bridge:   http://localhost:8765/health
echo.
echo   Docker containers running:
docker-compose ps --services --filter "status=running" 2>nul
echo.
echo Press any key to open dashboard in browser...
pause >nul
start http://localhost:3000
echo.
echo Dashboard opened. Close this window to stop?^)
echo To manually stop: docker-compose down
echo.
pause
