#!/bin/bash
# KIMERA SWM Database Builder - Unix/Linux Shell Script
# This script builds the complete KIMERA SWM database system

set -e  # Exit on any error

echo ""
echo "========================================"
echo "KIMERA SWM Database Builder"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python not found. Please install Python 3.8+ and add it to PATH."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Using Python: $($PYTHON_CMD --version)"

# Check if we're in the right directory
if [ ! -f "backend/vault/database.py" ]; then
    echo "❌ Please run this script from the KIMERA SWM root directory."
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✅ Running from correct directory"

# Check for Docker and Neo4j
NEO4J_OPTION=""
if command -v docker &> /dev/null; then
    echo "✅ Docker available. Checking for Neo4j container..."
    
    if docker ps | grep -q neo4j; then
        echo "✅ Neo4j container already running"
        export NEO4J_URI="bolt://localhost:7687"
        export NEO4J_USER="neo4j"
        export NEO4J_PASS="kimera123"
        NEO4J_OPTION="--neo4j"
    else
        echo "🚀 Starting Neo4j container..."
        if docker run -d --name kimera-neo4j \
            -p 7687:7687 -p 7474:7474 \
            -e NEO4J_AUTH=neo4j/kimera123 \
            neo4j:5; then
            
            echo "✅ Neo4j container started successfully"
            echo "⏳ Waiting for Neo4j to be ready..."
            sleep 15
            
            export NEO4J_URI="bolt://localhost:7687"
            export NEO4J_USER="neo4j"
            export NEO4J_PASS="kimera123"
            NEO4J_OPTION="--neo4j"
        else
            echo "⚠️  Failed to start Neo4j. Continuing without graph database."
        fi
    fi
else
    echo "⚠️  Docker not available. Neo4j setup will be skipped."
fi

echo ""
echo "🏗️  Building KIMERA SWM Database..."
echo ""

# Run the database builder
$PYTHON_CMD build_database.py $NEO4J_OPTION --enhanced --sample-data

echo ""
echo "🎉 Database build completed successfully!"
echo ""
echo "📋 What was created:"
echo "  ✅ SQLite database with all tables"
echo "  ✅ Optimized database indexes"

if [ -n "$NEO4J_OPTION" ]; then
    echo "  ✅ Neo4j graph database with constraints"
    echo "  ✅ Sample data in both databases"
    echo ""
    echo "🌐 Neo4j Browser: http://localhost:7474"
    echo "   Username: neo4j"
    echo "   Password: kimera123"
else
    echo "  ⚠️  Neo4j not configured (Docker required)"
fi

echo ""
echo "🚀 Next steps:"
echo "  1. Start KIMERA: python run_kimera.py"
echo "  2. Test API: curl http://localhost:8000/health"
echo "  3. Run tests: python -m pytest tests/"
echo ""

# Make the script executable
chmod +x "$0" 2>/dev/null || true