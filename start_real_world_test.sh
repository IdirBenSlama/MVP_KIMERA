#!/bin/bash

echo "========================================"
echo "KIMERA Real-World Test Suite Launcher"
echo "========================================"
echo
echo "This will start a comprehensive real-world test of KIMERA"
echo "across multiple domains: finance, weather, social dynamics,"
echo "scientific discovery, and crisis management."
echo

# Check if KIMERA is already running
echo "Checking if KIMERA is running..."
if curl -s http://localhost:8001/system/status >/dev/null 2>&1; then
    echo "✅ KIMERA is already running"
else
    echo "⚠️  KIMERA is not running. Starting KIMERA first..."
    echo
    echo "Starting KIMERA in the background..."
    
    # Start KIMERA in background
    python run_kimera.py &
    KIMERA_PID=$!
    
    echo "KIMERA started with PID: $KIMERA_PID"
    echo "Waiting for KIMERA to start up..."
    sleep 10
    
    # Wait for KIMERA to be ready
    while ! curl -s http://localhost:8001/system/status >/dev/null 2>&1; do
        echo "Still waiting for KIMERA to start..."
        sleep 5
    done
    
    echo "✅ KIMERA is now running!"
    echo
fi

echo "========================================"
echo "Starting Real-World Test Suite"
echo "========================================"
echo

# Run the test suite
python run_real_world_test.py

echo
echo "========================================"
echo "Test Complete"
echo "========================================"
echo
echo "Check the generated files:"
echo "- real_world_test_results_*.json (detailed results)"
echo "- real_world_test_*.log (execution log)"
echo

# If we started KIMERA, ask if user wants to stop it
if [ ! -z "$KIMERA_PID" ]; then
    echo
    read -p "Stop KIMERA server? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping KIMERA server..."
        kill $KIMERA_PID
        echo "KIMERA server stopped."
    else
        echo "KIMERA server is still running (PID: $KIMERA_PID)"
        echo "You can stop it manually with: kill $KIMERA_PID"
    fi
fi 