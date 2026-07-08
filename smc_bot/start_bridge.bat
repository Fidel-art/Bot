@echo off
title MT5 Bridge Server
echo ==================================================
echo MT5 Bridge Server Launcher
echo ==================================================
echo.
echo This script starts the MT5 Bridge on the Windows host.
echo Required for Docker containers to communicate with MetaTrader 5.
echo.

:: Check prerequisites
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Set up Python virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate venv and install requirements
call venv\Scripts\activate
if exist mt5_bridge\requirements.txt (
    pip install -q -r mt5_bridge\requirements.txt
)

:: Kill any existing bridge process on port 8765
echo Checking for existing bridge processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8765 "') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Start the bridge
echo.
echo Starting MT5 Bridge on port 8765...
echo.
python -m uvicorn mt5_bridge.server:app --host 0.0.0.0 --port 8765 --log-level info

pause
