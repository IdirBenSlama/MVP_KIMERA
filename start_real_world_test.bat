@echo off
echo ========================================
echo KIMERA Real-World Test Suite Launcher
echo ========================================
echo.
echo This will start a comprehensive real-world test of KIMERA
echo across multiple domains: finance, weather, social dynamics,
echo scientific discovery, and crisis management.
echo.

REM Check if KIMERA is already running
echo Checking if KIMERA is running...
curl -s http://localhost:8001/system/status >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ KIMERA is already running
    goto :run_test
)

echo ⚠️  KIMERA is not running. Starting KIMERA first...
echo.
echo Starting KIMERA in a new window...
start "KIMERA SWM Server" cmd /c "python run_kimera.py"

echo Waiting for KIMERA to start up...
timeout /t 10 /nobreak >nul

REM Wait for KIMERA to be ready
:wait_loop
curl -s http://localhost:8001/system/status >nul 2>&1
if %errorlevel% neq 0 (
    echo Still waiting for KIMERA to start...
    timeout /t 5 /nobreak >nul
    goto :wait_loop
)

echo ✅ KIMERA is now running!
echo.

:run_test
echo ========================================
echo Starting Real-World Test Suite
echo ========================================
echo.
python run_real_world_test.py

echo.
echo ========================================
echo Test Complete
echo ========================================
echo.
echo Check the generated files:
echo - real_world_test_results_*.json (detailed results)
echo - real_world_test_*.log (execution log)
echo.
pause 