#!/usr/bin/env python3
"""
KIMERA Real Market Case Study Launcher
Simplified launcher for the comprehensive market analysis case study
"""

import asyncio
import sys
import os
from pathlib import Path
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['aiohttp', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_kimera_api():
    """Check if KIMERA API is running"""
    try:
        import requests
        response = requests.get("http://localhost:8001/system/status", timeout=5)
        if response.status_code == 200:
            print("✅ KIMERA API is running")
            return True
        else:
            print(f"⚠️  KIMERA API responded with status {response.status_code}")
            return False
    except ImportError:
        print("⚠️  Cannot check KIMERA API (requests not installed)")
        return True  # Assume it's running
    except Exception as e:
        print(f"❌ KIMERA API not accessible: {e}")
        print("💡 Make sure to run 'python run_kimera.py' first")
        return False

def print_banner():
    """Print case study banner"""
    print("=" * 70)
    print("🧠 KIMERA SWM REAL MARKET CASE STUDY")
    print("=" * 70)
    print("📊 Real-time financial market contradiction detection")
    print("🔑 Using Alpha Vantage API: X5GCHUJSY20536ID")
    print("🎯 Analyzing: AAPL, GOOGL, MSFT, NVDA, AMD, TSLA, META, AMZN, NFLX, INTC")
    print("=" * 70)
    print()

def print_pre_run_info():
    """Print information before running the case study"""
    print("📋 CASE STUDY OVERVIEW:")
    print("   • Collect real market data from Alpha Vantage")
    print("   • Analyze cross-asset correlations")
    print("   • Detect 5 types of market contradictions:")
    print("     - Sector divergence (tech stocks moving opposite directions)")
    print("     - Volume-price mismatches (high volume, low price movement)")
    print("     - Technical indicator divergences (RSI vs price contradictions)")
    print("     - Correlation breakdowns (historically correlated assets diverging)")
    print("     - Cross-asset anomalies (market-wide volatility spikes)")
    print("   • Send significant contradictions to KIMERA for processing")
    print("   • Generate comprehensive analysis report")
    print()
    print("⏱️  Expected runtime: 5-10 minutes (due to API rate limits)")
    print("📁 Results will be saved to: real_market_case_study_results_[timestamp].json")
    print()

async def run_case_study():
    """Run the actual case study"""
    try:
        # Import and run the case study
        from real_market_case_study import run_real_market_case_study
        await run_real_market_case_study()
        return True
    except ImportError as e:
        print(f"❌ Cannot import case study module: {e}")
        return False
    except Exception as e:
        print(f"❌ Case study execution failed: {e}")
        return False

def main():
    """Main launcher function"""
    print_banner()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return 1
    
    print("✅ All dependencies are installed")
    
    # Check KIMERA API
    print("\n🔍 Checking KIMERA API connection...")
    kimera_running = check_kimera_api()
    
    if not kimera_running:
        print("\n⚠️  KIMERA API is not running. The case study will still collect and analyze")
        print("   market data, but won't be able to send contradictions to KIMERA.")
        print("\n💡 To enable full KIMERA integration:")
        print("   1. Open a new terminal")
        print("   2. Run: python run_kimera.py")
        print("   3. Wait for 'Server will start on http://localhost:XXXX'")
        print("   4. Re-run this case study")
        
        response = input("\n❓ Continue without KIMERA integration? (y/N): ").strip().lower()
        if response != 'y':
            print("👋 Exiting. Start KIMERA API first for full integration.")
            return 0
    
    print_pre_run_info()
    
    # Confirm execution
    response = input("🚀 Ready to start the case study? (Y/n): ").strip().lower()
    if response == 'n':
        print("👋 Case study cancelled.")
        return 0
    
    print("\n🎬 Starting case study execution...")
    print("📊 This will take several minutes due to API rate limiting...")
    print("📝 Watch the logs for real-time progress updates")
    print("-" * 70)
    
    # Run the case study
    try:
        success = asyncio.run(run_case_study())
        
        if success:
            print("\n" + "=" * 70)
            print("🎉 CASE STUDY COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print("📁 Check the generated JSON file for detailed results")
            print("📊 Review the console output above for key findings")
            print("🧠 If KIMERA was running, check the dashboard for new geoids")
            print("\n💡 Next steps:")
            print("   • Analyze the generated report")
            print("   • Review detected contradictions")
            print("   • Explore KIMERA dashboard for semantic insights")
            return 0
        else:
            print("\n❌ Case study execution failed. Check the logs above for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Case study interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print("\n🎯 Case study launcher completed successfully!")
    else:
        print("\n💥 Case study launcher failed!")
    
    sys.exit(exit_code)