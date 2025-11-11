@echo off
REM FPL Assistant Quick Start Script for Windows

echo 🚀 FPL Assistant - Quick Start
echo ================================
echo.

REM Check Python and Node
echo 📋 Checking dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 14+
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i

echo ✅ %PYTHON_VERSION%
echo ✅ %NODE_VERSION%
echo.

REM Setup Backend
echo 📦 Setting up Backend...
cd backend

if not exist "venv" (
    echo    Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo    Installing Python dependencies...
pip install -q -r requirements.txt

if not exist ".env" (
    echo    Creating .env file...
    copy .env.example .env
)

echo ✅ Backend ready!
echo.

REM Setup Frontend
cd ..\frontend

echo 📦 Setting up Frontend...
if not exist "node_modules" (
    echo    Installing npm dependencies...
    call npm install --silent --no-progress
)

echo ✅ Frontend ready!
echo.

REM Summary
cd ..
echo 🎉 Setup complete!
echo.
echo 📚 To get started:
echo.
echo    Command Prompt 1 - Backend:
echo      cd backend
echo      venv\Scripts\activate.bat
echo      python run.py
echo.
echo    Command Prompt 2 - Frontend:
echo      cd frontend
echo      npm start
echo.
echo    Then open: http://localhost:3000
echo.
echo 📖 For more info, see SETUP_AND_USAGE.md
echo.
pause
