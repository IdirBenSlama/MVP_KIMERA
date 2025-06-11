#!/usr/bin/env python3
"""
Open KIMERA SWM Dashboard in Browser
"""
import webbrowser
import os
import time

def open_dashboard():
    # Get the absolute path to the test dashboard
    dashboard_path = os.path.abspath("test_dashboard.html")
    dashboard_url = f"file:///{dashboard_path.replace(os.sep, '/')}"
    
    print("🚀 Opening KIMERA SWM Dashboard...")
    print(f"📊 Dashboard URL: {dashboard_url}")
    print(f"🔗 API Server: http://localhost:8001")
    print("\n✅ The dashboard should open in your default browser")
    print("📈 It will show real-time metrics from your KIMERA SWM system")
    
    # Open in browser
    webbrowser.open(dashboard_url)
    
    print("\n🔧 Dashboard Features:")
    print("   - Real-time system metrics")
    print("   - Connection status indicator") 
    print("   - Create test geoids")
    print("   - Run cognitive cycles")
    print("   - Search existing geoids")
    print("   - Auto-refresh every 10 seconds")

if __name__ == "__main__":
    open_dashboard()