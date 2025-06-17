#!/usr/bin/env python3
"""
Run the tyrannic test without innovations
"""
import os
import sys

# Disable innovations
os.environ["DISABLE_INNOVATIONS"] = "1"

# Import and run the test
sys.path.insert(0, os.path.abspath("."))
from test_scripts.tyrannic_progressive_crash_test import main

if __name__ == "__main__":
    # Modify sys.argv to ensure we don't load innovations
    original_file = sys.modules['__main__'].__file__
    sys.modules['__main__'].__file__ = __file__
    
    # Temporarily rename the innovations directory to prevent imports
    innovations_path = "innovations"
    temp_path = "innovations_disabled"
    
    if os.path.exists(innovations_path):
        os.rename(innovations_path, temp_path)
    
    try:
        main()
    finally:
        # Restore the innovations directory
        if os.path.exists(temp_path):
            os.rename(temp_path, innovations_path)