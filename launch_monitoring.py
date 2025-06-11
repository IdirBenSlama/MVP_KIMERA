#!/usr/bin/env python3
"""
Launch script for Kimera SWM Monitoring Dashboard

This script starts the monitoring dashboard and optionally the API server.
"""

import os
import sys
import webbrowser
import subprocess
import time
import argparse
from pathlib import Path

def check_api_running(host="localhost", port=8001):
    """Check if the API server is running"""
    try:
        import requests
        response = requests.get(f"http://{host}:{port}/system/status", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server"""
    print("Starting Kimera SWM API server...")
    try:
        # Try to start the API server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ], cwd=Path(__file__).parent)
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        if check_api_running():
            print("✅ API server started successfully on http://localhost:8001")
            return process
        else:
            print("❌ Failed to start API server")
            return None
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def open_dashboard():
    """Open the monitoring dashboard in the default browser"""
    dashboard_path = Path(__file__).parent / "monitoring_dashboard.html"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return False
    
    try:
        # Convert to file URL
        file_url = dashboard_path.as_uri()
        webbrowser.open(file_url)
        print(f"✅ Monitoring dashboard opened: {file_url}")
        return True
    except Exception as e:
        print(f"❌ Error opening dashboard: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Launch Kimera SWM Monitoring Dashboard")
    parser.add_argument("--no-api", action="store_true", 
                       help="Don't start the API server (assume it's already running)")
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't open the browser automatically")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check if API is running")
    
    args = parser.parse_args()
    
    print("🧠 Kimera SWM Monitoring Dashboard Launcher")
    print("=" * 50)
    
    # Check if API is already running
    if check_api_running():
        print("✅ API server is already running on http://localhost:8001")
        api_process = None
    elif args.check_only:
        print("❌ API server is not running")
        return 1
    elif args.no_api:
        print("⚠️  API server not running, but --no-api flag set")
        print("   Make sure to start the API server manually:")
        print("   python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8001 --reload")
        api_process = None
    else:
        api_process = start_api_server()
        if not api_process:
            print("❌ Failed to start API server. Exiting.")
            return 1
    
    if args.check_only:
        return 0
    
    # Open the dashboard
    if not args.no_browser:
        if open_dashboard():
            print("\n🎉 Monitoring dashboard is ready!")
            print("\nFeatures available:")
            print("  ��� Real-time system metrics")
            print("  📈 Entropy and thermodynamic trends")
            print("  🧠 Semantic analysis")
            print("  🚨 Alert monitoring")
            print("  🧪 Benchmark testing")
            print("\nAPI endpoints available at: http://localhost:8001/docs")
        else:
            print("❌ Failed to open dashboard")
            return 1
    else:
        dashboard_path = Path(__file__).parent / "monitoring_dashboard.html"
        print(f"📊 Dashboard available at: {dashboard_path.as_uri()}")
    
    # Keep the script running if we started the API server
    if api_process:
        try:
            print("\n⌨️  Press Ctrl+C to stop the API server and exit")
            api_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping API server...")
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()
            print("✅ API server stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
