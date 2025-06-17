@echo off
echo Installing KIMERA SWM Requirements...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo Python found. Installing requirements...
echo.

REM Install requirements
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some requirements
    echo This might be due to:
    echo - Missing system dependencies
    echo - Network connectivity issues
    echo - Incompatible Python version
    echo.
    echo Trying to install core dependencies only...
    pip install fastapi uvicorn pydantic sqlalchemy numpy torch transformers
)

echo.
echo Installation complete!
echo You can now run Kimera with: python run_kimera.py
pause