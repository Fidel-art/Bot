@echo off
echo ========================================
echo SMC Trading Bot - Web Dashboard Launcher
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
echo.

:: Install Python dependencies if needed
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing/updating Python dependencies...
pip install -q -r requirements.txt

echo.
echo [2/4] Starting FastAPI backend server...
echo.

:: Start backend in new window
start "SMC Bot API Server" cmd /k "cd backend && python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak >nul

echo.
echo [3/4] Checking frontend dependencies...
echo.

:: Install Node dependencies if needed
cd frontend
if not exist "node_modules" (
    echo Installing Node.js dependencies (this may take a few minutes)...
    call npm install
) else (
    echo Frontend dependencies already installed
)

echo.
echo [4/4] Starting React development server...
echo.

:: Start frontend in new window
start "SMC Bot Dashboard" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Dashboard is starting up!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:3000
echo.
echo Press any key to open dashboard in browser...
pause >nul

:: Wait a bit for servers to start
timeout /t 3 /nobreak >nul

:: Open browser
start http://localhost:3000

echo.
echo Dashboard opened in your default browser.
echo Keep this window open to keep servers running.
echo Press Ctrl+C to stop the servers.
echo.
pause
