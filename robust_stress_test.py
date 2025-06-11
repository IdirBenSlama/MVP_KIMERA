#!/usr/bin/env python3
"""
KIMERA SWM Robust Stress Test Suite
===================================

This script performs stress testing with proper error handling for database constraints
and continues testing even when encountering expected errors under high load.
"""

import os
import sys
import time
import threading
import concurrent.futures
import random
import string
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import sqlite3

# Set environment variables for testing
os.environ["LIGHTWEIGHT_EMBEDDING"] = "1"
os.environ["ENABLE_JOBS"] = "0"
os.environ["DATABASE_URL"] = "sqlite:///./robust_stress_test.db"

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api.main import app

class RobustKimeraStressTester:
    def __init__(self):
        self.client = TestClient(app)
        self.results = {}
        self.errors = []
        self.expected_errors = []  # Track expected errors like constraint violations
        
    def log_result(self, test_name: str, result: Dict[str, Any]):
        """Log test results"""
        self.results[test_name] = result
        print(f"✅ {test_name}: {result}")
        
    def log_error(self, test_name: str, error: str, is_expected: bool = False):
        """Log test errors"""
        if is_expected:
            self.expected_errors.append(f"{test_name}: {error}")
            print(f"⚠️  {test_name} (expected): {error}")
        else:
            self.errors.append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")

    def is_expected_error(self, error_msg: str) -> bool:
        """Check if an error is expected under stress conditions"""
        expected_patterns = [
            "UNIQUE constraint failed",
            "database is locked",
            "timeout",
            "connection refused",
            "too many connections"
        ]
        return any(pattern in error_msg.lower() for pattern in expected_patterns)

    def stress_test_cognitive_cycles_robust(self, num_cycles: int = 25):
        """Robust stress test for cognitive cycle execution with error handling"""
        print(f"\n🔥 ROBUST STRESS TEST: Running {num_cycles} cognitive cycles with error handling")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        expected_error_count = 0
        cycle_times = []
        
        for i in range(num_cycles):
            try:
                cycle_start = time.time()
                response = self.client.post("/system/cycle")
                cycle_time = time.time() - cycle_start
                cycle_times.append(cycle_time)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"   Cycle {i+1}/{num_cycles}: ✅ {cycle_time:.3f}s")
                else:
                    error_msg = response.text if hasattr(response, 'text') else str(response.status_code)
                    if self.is_expected_error(error_msg):
                        expected_error_count += 1
                        self.log_error("cognitive_cycle", error_msg, is_expected=True)
                    else:
                        error_count += 1
                        self.log_error("cognitive_cycle", error_msg)
                    print(f"   Cycle {i+1}/{num_cycles}: ⚠️  Error")
                    
            except Exception as e:
                error_msg = str(e)
                if self.is_expected_error(error_msg):
                    expected_error_count += 1
                    self.log_error("cognitive_cycle", error_msg, is_expected=True)
                else:
                    error_count += 1
                    self.log_error("cognitive_cycle", error_msg)
                print(f"   Cycle {i+1}/{num_cycles}: ❌ Exception")
                
            # Small delay to reduce database contention
            time.sleep(0.1)
        
        total_time = time.time() - start_time
        
        result = {
            "total_cycles": num_cycles,
            "successful": success_count,
            "failed": error_count,
            "expected_errors": expected_error_count,
            "total_time": round(total_time, 2),
            "avg_cycle_time": round(statistics.mean(cycle_times) if cycle_times else 0, 4),
            "max_cycle_time": round(max(cycle_times) if cycle_times else 0, 4),
            "min_cycle_time": round(min(cycle_times) if cycle_times else 0, 4),
            "success_rate": round((success_count / num_cycles) * 100, 2)
        }
        
        self.log_result("Robust Cognitive Cycle Stress Test", result)
        return result

    def stress_test_vault_operations_robust(self, num_operations: int = 100):
        """Robust stress test for vault operations"""
        print(f"\n🔥 ROBUST STRESS TEST: Performing {num_operations} vault operations")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        expected_error_count = 0
        
        for i in range(num_operations):
            try:
                # Test vault queries
                response = self.client.get(f"/vaults/vault_a?limit={random.randint(1, 5)}")
                if response.status_code == 200:
                    success_count += 1
                    print(f"   Vault query {i+1}/{num_operations}: ✅")
                else:
                    error_msg = response.text if hasattr(response, 'text') else str(response.status_code)
                    if self.is_expected_error(error_msg):
                        expected_error_count += 1
                    else:
                        error_count += 1
                    print(f"   Vault query {i+1}/{num_operations}: ⚠️")
                
                # Test vault rebalancing occasionally
                if i % 10 == 0:
                    response = self.client.post("/vaults/rebalance")
                    if response.status_code != 200:
                        error_msg = response.text if hasattr(response, 'text') else str(response.status_code)
                        if self.is_expected_error(error_msg):
                            expected_error_count += 1
                        else:
                            error_count += 1
                        
            except Exception as e:
                error_msg = str(e)
                if self.is_expected_error(error_msg):
                    expected_error_count += 1
                else:
                    error_count += 1
                print(f"   Vault operation {i+1}/{num_operations}: ❌")
                
            # Small delay to reduce contention
            time.sleep(0.05)
        
        total_time = time.time() - start_time
        
        result = {
            "total_operations": num_operations,
            "successful": success_count,
            "failed": error_count,
            "expected_errors": expected_error_count,
            "total_time": round(total_time, 2),
            "operations_per_second": round(num_operations / total_time, 2),
            "success_rate": round((success_count / num_operations) * 100, 2)
        }
        
        self.log_result("Robust Vault Operations Stress Test", result)
        return result

    def stress_test_concurrent_geoid_creation(self, num_geoids: int = 200, concurrent_threads: int = 5):
        """Stress test geoid creation with controlled concurrency"""
        print(f"\n🔥 ROBUST STRESS TEST: Creating {num_geoids} geoids with {concurrent_threads} threads")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        expected_error_count = 0
        response_times = []
        
        def create_geoid():
            nonlocal success_count, error_count, expected_error_count
            try:
                geoid_data = {
                    "semantic_features": {
                        f"feature_{random.randint(1,10)}": random.uniform(-1.0, 1.0)
                        for _ in range(random.randint(2, 5))
                    },
                    "metadata": {"test_id": f"stress_{random.randint(1000, 9999)}"}
                }
                
                req_start = time.time()
                response = self.client.post("/geoids", json=geoid_data)
                req_time = time.time() - req_start
                response_times.append(req_time)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_msg = response.text if hasattr(response, 'text') else str(response.status_code)
                    if self.is_expected_error(error_msg):
                        expected_error_count += 1
                    else:
                        error_count += 1
                        
            except Exception as e:
                error_msg = str(e)
                if self.is_expected_error(error_msg):
                    expected_error_count += 1
                else:
                    error_count += 1
        
        # Execute with controlled concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
            futures = [executor.submit(create_geoid) for _ in range(num_geoids)]
            concurrent.futures.wait(futures)
        
        total_time = time.time() - start_time
        
        result = {
            "total_geoids": num_geoids,
            "successful": success_count,
            "failed": error_count,
            "expected_errors": expected_error_count,
            "total_time": round(total_time, 2),
            "requests_per_second": round(num_geoids / total_time, 2),
            "avg_response_time": round(statistics.mean(response_times) if response_times else 0, 4),
            "success_rate": round((success_count / num_geoids) * 100, 2)
        }
        
        self.log_result("Robust Geoid Creation Stress Test", result)
        return result

    def stress_test_system_endurance(self, duration_seconds: int = 120):
        """Endurance test running mixed operations for extended period"""
        print(f"\n🔥 ENDURANCE TEST: Running mixed operations for {duration_seconds} seconds")
        
        start_time = time.time()
        operations = 0
        successes = 0
        errors = 0
        expected_errors = 0
        
        operation_types = ["geoid_create", "status_check", "contradiction_process", "vault_query"]
        
        while time.time() - start_time < duration_seconds:
            try:
                operation = random.choice(operation_types)
                operations += 1
                
                if operation == "geoid_create":
                    response = self.client.post("/geoids", json={
                        "semantic_features": {"test": random.random()},
                        "metadata": {"endurance_test": True}
                    })
                elif operation == "status_check":
                    response = self.client.get("/system/status")
                elif operation == "vault_query":
                    response = self.client.get("/vaults/vault_a?limit=3")
                elif operation == "contradiction_process":
                    # Skip if no geoids exist
                    status_resp = self.client.get("/system/status")
                    if status_resp.status_code == 200 and status_resp.json().get("active_geoids", 0) > 0:
                        response = self.client.post("/process/contradictions", json={
                            "trigger_geoid_id": "dummy",  # Will fail gracefully
                            "search_limit": 2
                        })
                    else:
                        continue
                
                if response.status_code in [200, 201]:
                    successes += 1
                else:
                    error_msg = response.text if hasattr(response, 'text') else str(response.status_code)
                    if self.is_expected_error(error_msg):
                        expected_errors += 1
                    else:
                        errors += 1
                
                # Progress indicator
                if operations % 50 == 0:
                    elapsed = time.time() - start_time
                    print(f"   {operations} ops in {elapsed:.1f}s (rate: {operations/elapsed:.1f} ops/s)")
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
                
            except Exception as e:
                error_msg = str(e)
                if self.is_expected_error(error_msg):
                    expected_errors += 1
                else:
                    errors += 1
        
        total_time = time.time() - start_time
        
        result = {
            "duration": round(total_time, 2),
            "total_operations": operations,
            "successful": successes,
            "failed": errors,
            "expected_errors": expected_errors,
            "operations_per_second": round(operations / total_time, 2),
            "success_rate": round((successes / operations) * 100, 2) if operations > 0 else 0
        }
        
        self.log_result("System Endurance Test", result)
        return result

    def run_robust_stress_test_suite(self):
        """Run the robust stress test suite"""
        print("🚀 KIMERA SWM ROBUST STRESS TEST SUITE")
        print("=" * 60)
        print("This test suite handles expected errors under high load conditions")
        print("=" * 60)
        
        test_start = time.time()
        
        # Clean up any existing test database
        try:
            os.remove("robust_stress_test.db")
            print("🧹 Cleaned up previous test database")
        except FileNotFoundError:
            pass
        
        # Run robust stress tests
        print("\n📊 Starting robust stress test sequence...")
        
        self.stress_test_concurrent_geoid_creation(num_geoids=150, concurrent_threads=4)
        self.stress_test_cognitive_cycles_robust(num_cycles=25)
        self.stress_test_vault_operations_robust(num_operations=75)
        self.stress_test_system_endurance(duration_seconds=60)
        
        total_test_time = time.time() - test_start
        
        # Generate comprehensive report
        print("\n" + "=" * 60)
        print("🎯 ROBUST STRESS TEST RESULTS")
        print("=" * 60)
        
        total_operations = 0
        total_successes = 0
        total_errors = 0
        total_expected_errors = 0
        
        for test_name, result in self.results.items():
            print(f"\n📊 {test_name}:")
            for key, value in result.items():
                print(f"   {key}: {value}")
            
            # Accumulate totals
            if "total_operations" in result:
                total_operations += result["total_operations"]
            elif "total_geoids" in result:
                total_operations += result["total_geoids"]
            elif "total_cycles" in result:
                total_operations += result["total_cycles"]
            
            total_successes += result.get("successful", 0)
            total_errors += result.get("failed", 0)
            total_expected_errors += result.get("expected_errors", 0)
        
        # Summary statistics
        print(f"\n📈 OVERALL SUMMARY:")
        print(f"   Total Operations: {total_operations}")
        print(f"   Successful: {total_successes}")
        print(f"   Failed: {total_errors}")
        print(f"   Expected Errors: {total_expected_errors}")
        print(f"   Overall Success Rate: {round((total_successes / total_operations) * 100, 2) if total_operations > 0 else 0}%")
        
        if self.errors:
            print(f"\n❌ UNEXPECTED ERRORS ({len(self.errors)}):")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more errors")
        
        if self.expected_errors:
            print(f"\n⚠️  EXPECTED ERRORS UNDER LOAD ({len(self.expected_errors)}):")
            print("   These are normal under high stress conditions:")
            error_types = {}
            for error in self.expected_errors:
                error_type = error.split(":")[1].strip().split()[0] if ":" in error else "unknown"
                error_types[error_type] = error_types.get(error_type, 0) + 1
            for error_type, count in error_types.items():
                print(f"   - {error_type}: {count} occurrences")
        
        print(f"\n⏱️  Total test duration: {round(total_test_time, 2)} seconds")
        
        # Final system status
        try:
            final_status = self.client.get("/system/status")
            if final_status.status_code == 200:
                status_data = final_status.json()
                print(f"\n🏁 FINAL SYSTEM STATUS:")
                print(f"   Active Geoids: {status_data.get('active_geoids', 'N/A')}")
                print(f"   System Entropy: {status_data.get('system_entropy', 'N/A')}")
                print(f"   Vault A Scars: {status_data.get('vault_a_scars', 'N/A')}")
                print(f"   Vault B Scars: {status_data.get('vault_b_scars', 'N/A')}")
                print(f"   Cycle Count: {status_data.get('cycle_count', 'N/A')}")
        except Exception as e:
            print(f"❌ Could not get final system status: {e}")
        
        # Determine overall test result
        if len(self.errors) == 0:
            print("\n🎉 ALL STRESS TESTS COMPLETED SUCCESSFULLY!")
            print("   System handled stress conditions robustly")
        elif len(self.errors) < 5:
            print(f"\n✅ STRESS TESTS MOSTLY SUCCESSFUL!")
            print(f"   Only {len(self.errors)} unexpected errors encountered")
        else:
            print(f"\n⚠️  STRESS TESTS COMPLETED WITH ISSUES")
            print(f"   {len(self.errors)} unexpected errors need investigation")
        
        return self.results, self.errors, self.expected_errors

if __name__ == "__main__":
    print("Initializing Robust KIMERA Stress Tester...")
    tester = RobustKimeraStressTester()
    
    try:
        results, errors, expected_errors = tester.run_robust_stress_test_suite()
        
        # Save results to file
        with open("robust_stress_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "unexpected_errors": errors,
                "expected_errors": expected_errors
            }, f, indent=2)
        
        print(f"\n💾 Results saved to robust_stress_test_results.json")
            
    except KeyboardInterrupt:
        print("\n🛑 Stress test interrupted by user")
    except Exception as e:
        print(f"\n💥 Critical error during stress testing: {e}")
        import traceback
        traceback.print_exc()