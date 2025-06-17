@echo off
title KIMERA SWM - Semantic Working Memory System
color 0A

echo.
echo ========================================
echo    KIMERA SWM - Alpha Prototype v0.1
echo    Semantic Working Memory System
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check if requirements are installed by trying to import key modules
echo Checking dependencies...
python -c "import fastapi, uvicorn, torch, transformers" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found. Installing requirements...
    echo This may take several minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo WARNING: Some packages failed to install.
        echo Installing core dependencies only...
        pip install fastapi uvicorn pydantic sqlalchemy numpy
    )
)

echo.
echo Dependencies check complete.
echo.

REM Create necessary directories
if not exist "static\images" mkdir "static\images"
if not exist "test_databases" mkdir "test_databases"

echo Starting KIMERA SWM...
echo.
echo The system will be available at:
echo - Main API: http://localhost:8001 (or next available port)
echo - Documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the system
echo.

REM Run Kimera
python run_kimera.py

echo.
echo KIMERA SWM has stopped.
pause