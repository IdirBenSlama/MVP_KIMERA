#!/usr/bin/env python3
"""
KIMERA SWM Startup Script
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env file

import uvicorn
import sys
import socket
import os
from pathlib import Path

# Add the current directory to Python path so we can import backend
sys.path.insert(0, str(Path(__file__).parent))

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
    print("🔧 Using upgraded BGE-M3 embedding model (1024 dimensions)")
    
    # Find a free port
    port = find_free_port()
    if port is None:
        print("❌ No free ports available between 8001-8010")
        sys.exit(1)
    
    # Save the port to a file for the test script to use
    with open(".port.tmp", "w") as f:
        f.write(str(port))
    
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
            "backend.api.main:app", 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)