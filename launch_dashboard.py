#!/usr/bin/env python3
"""
KIMERA SWM Real-Time Dashboard Launcher
Opens the real-time dashboard in your default browser
"""

import webbrowser
import os
import sys
from pathlib import Path

def launch_dashboard():
    """Launch the KIMERA SWM real-time dashboard"""
    
    # Get the absolute path to the dashboard
    dashboard_path = Path(__file__).parent / "real_time_dashboard.html"
    
    if not dashboard_path.exists():
        print("❌ Dashboard file not found!")
        print(f"Expected location: {dashboard_path}")
        return False
    
    # Convert to file URL
    dashboard_url = f"file:///{dashboard_path.as_posix()}"
    
    print("🚀 Launching KIMERA SWM Real-Time Dashboard...")
    print(f"📊 Dashboard URL: {dashboard_url}")
    print("🔗 API Expected at: http://localhost:8001")
    print()
    print("✨ Features:")
    print("  • Real-time system metrics")
    print("  • Live vault status monitoring")
    print("  • Stability metrics tracking")
    print("  • Active geoids management")
    print("  • Contradiction processing")
    print("  • Activity logging")
    print("  • Auto-refresh every 5 seconds")
    print()
    
    try:
        # Open in default browser
        webbrowser.open(dashboard_url)
        print("✅ Dashboard opened in your default browser!")
        print()
        print("🔧 Troubleshooting:")
        print("  • Ensure KIMERA API is running on port 8001")
        print("  • Check browser console (F12) for any errors")
        print("  • Verify CORS is enabled on the API")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Failed to open dashboard: {e}")
        print(f"📋 Manual URL: {dashboard_url}")
        return False

if __name__ == "__main__":
    success = launch_dashboard()
    
    if not success:
        sys.exit(1)
    
    print("🎯 Dashboard is now running!")
    print("Press Ctrl+C to exit this script (dashboard will continue running)")
    
    try:
        # Keep script running to show it's active
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard launcher stopped (dashboard still running in browser)")