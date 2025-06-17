#!/usr/bin/env python3
"""
Test Phase 4 in isolation to see why it hangs in the full test
"""
import os
import sys
import time
import uuid

sys.path.insert(0, os.path.abspath("."))

# Disable innovations to isolate the issue
os.environ["DATABASE_URL"] = f"sqlite:///./phase4_test_{uuid.uuid4().hex[:8]}.db"

from test_scripts.tyrannic_progressive_crash_test import TyrannicCrashTester

def main():
    print("=== TESTING PHASE 4 IN ISOLATION ===\n")
    
    # Create tester without innovations
    tester = TyrannicCrashTester(allow_cpu=False)
    
    # Disable innovations to test core functionality
    tester.use_innovations = False
    
    print("Testing Phase 4 parameters: 16 threads, 256 features, depth 5")
    print("Expected: 160 total operations (16 × 10)\n")
    
    start_time = time.time()
    
    # Run only Phase 4
    result = tester.run_tyrannic_phase(
        num_threads=16,
        feature_count=256,
        depth=5,
        ops_per_thread=10
    )
    
    duration = time.time() - start_time
    
    print(f"\n=== RESULTS ===")
    print(f"Total duration: {duration:.1f}s")
    print(f"Success rate: {result['success_rate']:.1f}%")
    print(f"Operations/sec: {result['ops_per_sec']:.2f}")
    print(f"Avg response time: {result['avg_response_time']:.2f}s")
    
    if result['success_rate'] < 100:
        print(f"\n⚠️ Failures detected: {result['failures']}/{result['operations']}")
    
    # Try with fewer operations per thread
    if duration > 60:
        print("\n\nTesting with reduced operations (5 per thread)...")
        result2 = tester.run_tyrannic_phase(
            num_threads=16,
            feature_count=256,
            depth=5,
            ops_per_thread=5
        )
        print(f"Success rate: {result2['success_rate']:.1f}%")
        print(f"Operations/sec: {result2['ops_per_sec']:.2f}")

if __name__ == "__main__":
    main()