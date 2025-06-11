#!/usr/bin/env python3
"""
KIMERA SWM Startup Script
"""
import uvicorn
import sys
import socket
from backend.api.main import app

def find_free_port(start_port=8001, max_port=8010):
    """Find a free port starting from start_port"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return None

if __name__ == "__main__":
    print("🚀 Starting KIMERA SWM API Server...")
    
    # Find a free port
    port = find_free_port()
    if port is None:
        print("❌ No free ports available between 8000-8010")
        sys.exit(1)
    
    print(f"📡 Server will start on http://localhost:{port}")
    print("📚 API Documentation available at:")
    print(f"   - Swagger UI: http://localhost:{port}/docs")
    print(f"   - ReDoc: http://localhost:{port}/redoc")
    print("\n🔧 Available endpoints:")
    print("   - POST /geoids - Create semantic geoids")
    print("   - POST /process/contradictions - Process contradictions")
    print("   - GET /system/status - System status")
    print("   - GET /system/stability - Stability metrics")
    print("\n⚡ Press Ctrl+C to stop the server\n")
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
