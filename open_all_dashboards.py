#!/usr/bin/env python3
"""
Open all KIMERA SWM dashboards
"""

import webbrowser
import os
from pathlib import Path

def open_dashboards():
    """Open all available KIMERA dashboards"""
    
    base_path = Path(__file__).parent
    
    dashboards = [
        {
            "name": "Original React Dashboard",
            "file": "dashboard/index.html",
            "description": "Main original dashboard with React components"
        },
        {
            "name": "Simple Styled Dashboard", 
            "file": "dashboard/simple_dashboard.html",
            "description": "Beautiful styled dashboard with auto-refresh"
        },
        {
            "name": "Real-Time Enhanced Dashboard",
            "file": "real_time_dashboard.html", 
            "description": "Most comprehensive with detailed metrics"
        },
        {
            "name": "Dashboard Guide",
            "file": "dashboard_guide.html",
            "description": "Complete explanation of what everything means"
        },
        {
            "name": "Quick Reference",
            "file": "dashboard_cheatsheet.html",
            "description": "Quick reference card to keep open"
        }
    ]
    
    print("🚀 Opening KIMERA SWM Dashboards...")
    print("=" * 50)
    
    for i, dashboard in enumerate(dashboards, 1):
        file_path = base_path / dashboard["file"]
        
        if file_path.exists():
            file_url = f"file:///{file_path.as_posix()}"
            print(f"{i}. {dashboard['name']}")
            print(f"   📄 {dashboard['description']}")
            print(f"   🔗 {file_url}")
            
            try:
                webbrowser.open(file_url)
                print(f"   ✅ Opened successfully")
            except Exception as e:
                print(f"   ❌ Failed to open: {e}")
        else:
            print(f"{i}. {dashboard['name']} - ❌ File not found: {file_path}")
        
        print()
    
    print("🎯 All dashboards opened!")
    print("\n📋 Dashboard Comparison:")
    print("• React Dashboard (index.html) - Original, component-based")
    print("• Simple Dashboard - Clean, styled, auto-refresh") 
    print("• Real-Time Dashboard - Most features, comprehensive")
    print("• Guide & Cheatsheet - Help understanding the data")
    
    print(f"\n🔗 API should be running on: http://localhost:8001")
    print("🔧 If dashboards show connection errors, restart the API server")

if __name__ == "__main__":
    open_dashboards()
