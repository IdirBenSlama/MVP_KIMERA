@echo off
REM KIMERA SWM Database Builder - Windows Batch Script
REM This script builds the complete KIMERA SWM database system

echo.
echo ========================================
echo KIMERA SWM Database Builder
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend\vault\database.py" (
    echo ❌ Please run this script from the KIMERA SWM root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo 🔍 Checking for Neo4j...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker not available. Neo4j setup will be skipped.
    set NEO4J_OPTION=
) else (
    echo ✅ Docker available. Checking for Neo4j container...
    docker ps | findstr neo4j >nul 2>&1
    if errorlevel 1 (
        echo 🚀 Starting Neo4j container...
        docker run -d --name kimera-neo4j ^
            -p 7687:7687 -p 7474:7474 ^
            -e NEO4J_AUTH=neo4j/kimera123 ^
            neo4j:5
        
        if errorlevel 1 (
            echo ⚠️  Failed to start Neo4j. Continuing without graph database.
            set NEO4J_OPTION=
        ) else (
            echo ✅ Neo4j container started successfully
            echo ⏳ Waiting for Neo4j to be ready...
            timeout /t 15 /nobreak >nul
            set NEO4J_URI=bolt://localhost:7687
            set NEO4J_USER=neo4j
            set NEO4J_PASS=kimera123
            set NEO4J_OPTION=--neo4j
        )
    ) else (
        echo ✅ Neo4j container already running
        set NEO4J_URI=bolt://localhost:7687
        set NEO4J_USER=neo4j
        set NEO4J_PASS=kimera123
        set NEO4J_OPTION=--neo4j
    )
)

echo.
echo 🏗️  Building KIMERA SWM Database...
echo.

REM Run the database builder
python build_database.py %NEO4J_OPTION% --enhanced --sample-data

if errorlevel 1 (
    echo.
    echo ❌ Database build failed!
    pause
    exit /b 1
)

echo.
echo 🎉 Database build completed successfully!
echo.
echo 📋 What was created:
echo   ✅ SQLite database with all tables
echo   ✅ Optimized database indexes
if defined NEO4J_OPTION (
    echo   ✅ Neo4j graph database with constraints
    echo   ✅ Sample data in both databases
    echo.
    echo 🌐 Neo4j Browser: http://localhost:7474
    echo    Username: neo4j
    echo    Password: kimera123
) else (
    echo   ⚠️  Neo4j not configured (Docker required)
)
echo.
echo 🚀 Next steps:
echo   1. Start KIMERA: python run_kimera.py
echo   2. Test API: curl http://localhost:8000/health
echo   3. Run tests: python -m pytest tests/
echo.

pause