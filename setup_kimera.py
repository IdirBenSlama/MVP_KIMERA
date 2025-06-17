#!/usr/bin/env python3
"""
KIMERA SWM Setup Script
Checks dependencies and sets up the environment
"""
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install requirements from requirements.txt"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print("🔄 Trying to install core dependencies...")
        
        # Try installing core dependencies only
        core_deps = [
            "fastapi>=0.115.12",
            "uvicorn[standard]>=0.34.3", 
            "pydantic>=2.11.5",
            "sqlalchemy>=2.0.41",
            "numpy>=1.24.0",
            "torch>=2.0.0",
            "transformers>=4.44.2"
        ]
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + core_deps)
            print("✅ Core dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install core dependencies")
            return False

def check_dependencies():
    """Check if key dependencies are available"""
    required_modules = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "sqlalchemy",
        "numpy"
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing.append(module)
    
    return len(missing) == 0

def create_directories():
    """Create necessary directories"""
    dirs = [
        "static/images",
        "test_databases",
        "logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")

def main():
    print("🚀 KIMERA SWM Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if dependencies are already installed
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n📦 Installing missing dependencies...")
        if not install_requirements():
            print("\n❌ Setup failed. Please install dependencies manually:")
            print("pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ All dependencies are available")
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    print("\n✅ Setup complete!")
    print("\nYou can now run KIMERA with:")
    print("  python run_kimera.py")
    print("\nOr use the batch file:")
    print("  start_kimera.bat")

if __name__ == "__main__":
    main()