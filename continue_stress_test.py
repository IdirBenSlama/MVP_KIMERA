#!/usr/bin/env python3
"""
Continue KIMERA SWM Stress Test from Cognitive Cycles
====================================================

This script continues the stress test from the cognitive cycles phase,
handling database constraint errors gracefully.
"""

import os
import sys
import time
import random
import statistics
from datetime import datetime
from typing import Dict, Any
import json
import uuid

# Set environment variables for testing
os.environ["LIGHTWEIGHT_EMBEDDING"] = "1"
os.environ["ENABLE_JOBS"] = "0"
os.environ["DATABASE_URL"] = f"sqlite:///./stress_test_{uuid.uuid4().hex[:8]}.db"

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api.main import app

class ContinuedStressTester:
    def __init__(self):
        self.client = TestClient(app)
        self.results = {}
        self.errors = []
        self.expected_errors = []
        
    def log_result(self, test_name: str, result: Dict[str, Any]):
        """Log test results"""
        self.results[test_name] = result
        print(f"✅ {test_name}")
        for key, value in result.items():
            print(f"   {key}: {value}")
        
    def is_expected_error(self, error_msg: str) -> bool:
        """Check if an error is expected under stress conditions"""
        expected_patterns = [
            "UNIQUE constraint failed",
            "database is locked", 
            "timeout",
            "connection refused",
            "not found"
        ]
        return any(pattern in error_msg.lower() for pattern in expected_patterns)

    def stress_test_cognitive_cycles_continued(self, num_cycles: int = 25):
        """Continue cognitive cycles stress test with robust error handling"""
        print(f"\n🔥 CONTINUING STRESS TEST: Running {num_cycles} cognitive cycles")
        print("   (Handling database constraint errors gracefully)")
        
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
                
                if response.status_code == 200:
                    success_count += 1
                    cycle_times.append(cycle_time)
                    print(f"   Cycle {i+1:2d}/{num_cycles}: ✅ {cycle_time:.3f}s")
                else:
                    error_msg = response.text if hasattr(response, 'text') else str(response.status_code)
                    if self.is_expected_error(error_msg):
                        expected_error_count += 1
                        print(f"   Cycle {i+1:2d}/{num_cycles}: ⚠️  Expected error (constraint)")
                    else:
                        error_count += 1
                        print(f"   Cycle {i+1:2d}/{num_cycles}: ❌ Unexpected error")
                        self.errors.append(f"cognitive_cycle_{i}: {error_msg}")
                        
            except Exception as e:
                error_msg = str(e)
                if self.is_expected_error(error_msg):
                    expected_error_count += 1
                    print(f"   Cycle {i+1:2d}/{num_cycles}: ⚠️  Expected exception")
                else:
                    error_count += 1
                    print(f"   Cycle {i+1:2d}/{num_cycles}: ❌ Unexpected exception")
                    self.errors.append(f"cognitive_cycle_{i}: {error_msg}")
                
            # Small delay to reduce database contention
            time.sleep(0.2)
        
        total_time = time.time() - start_time
        
        result = {
            "total_cycles": num_cycles,
            "successful": success_count,
            "failed": error_count,
            "expected_errors": expected_error_count,
            "total_time": round(total_time, 2),
            "avg_cycle_time": round(statistics.mean(cycle_times) if cycle_times else 0, 4),
            "max_cycle_time": round(max(cycle_times) if cycle_times else 0, 4),
            "success_rate": round((success_count / num_cycles) * 100, 2)
        }
        
        self.log_result("Cognitive Cycles Stress Test (Continued)", result)
        return result

    def stress_test_vault_operations(self, num_operations: int = 100):
        """Test vault operations under stress"""
        print(f"\n🔥 STRESS TEST: Vault operations ({num_operations} operations)")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        
        for i in range(num_operations):
            try:
                # Alternate between different vault operations
                if i % 3 == 0:
                    response = self.client.get(f"/vaults/vault_a?limit={random.randint(1, 5)}")
                elif i % 3 == 1:
                    response = self.client.get(f"/vaults/vault_b?limit={random.randint(1, 5)}")
                else:
                    response = self.client.post("/vaults/rebalance")
                
                if response.status_code == 200:
                    success_count += 1
                    if i % 20 == 0:
                        print(f"   Vault ops {i+1:3d}/{num_operations}: ✅")
                else:
                    error_count += 1
                    if i % 20 == 0:
                        print(f"   Vault ops {i+1:3d}/{num_operations}: ❌")
                
                time.sleep(0.05)  # Small delay
                
            except Exception as e:
                error_count += 1
                self.errors.append(f"vault_operation_{i}: {str(e)}")
        
        total_time = time.time() - start_time
        
        result = {
            "total_operations": num_operations,
            "successful": success_count,
            "failed": error_count,
            "total_time": round(total_time, 2),
            "operations_per_second": round(num_operations / total_time, 2),
            "success_rate": round((success_count / num_operations) * 100, 2)
        }
        
        self.log_result("Vault Operations Stress Test", result)
        return result

    def stress_test_system_queries(self, num_queries: int = 500):
        """Test system status queries under load"""
        print(f"\n🔥 STRESS TEST: System status queries ({num_queries} queries)")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        response_times = []
        
        for i in range(num_queries):
            try:
                req_start = time.time()
                response = self.client.get("/system/status")
                req_time = time.time() - req_start
                response_times.append(req_time)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
                
                if i % 100 == 0:
                    print(f"   Status queries {i+1:3d}/{num_queries}: {success_count} successful")
                
            except Exception as e:
                error_count += 1
                self.errors.append(f"status_query_{i}: {str(e)}")
        
        total_time = time.time() - start_time
        
        result = {
            "total_queries": num_queries,
            "successful": success_count,
            "failed": error_count,
            "total_time": round(total_time, 2),
            "queries_per_second": round(num_queries / total_time, 2),
            "avg_response_time": round(statistics.mean(response_times) if response_times else 0, 4),
            "success_rate": round((success_count / num_queries) * 100, 2)
        }
        
        self.log_result("System Status Queries Stress Test", result)
        return result

    def stress_test_mixed_load(self, duration_seconds: int = 90):
        """Run mixed load test for specified duration"""
        print(f"\n🔥 STRESS TEST: Mixed load test ({duration_seconds} seconds)")
        
        start_time = time.time()
        operations = 0
        successes = 0
        errors = 0
        
        operation_types = ["status", "vault_query", "geoid_create"]
        
        while time.time() - start_time < duration_seconds:
            try:
                operation = random.choice(operation_types)
                operations += 1
                
                if operation == "status":
                    response = self.client.get("/system/status")
                elif operation == "vault_query":
                    vault = random.choice(["vault_a", "vault_b"])
                    response = self.client.get(f"/vaults/{vault}?limit=3")
                elif operation == "geoid_create":
                    response = self.client.post("/geoids", json={
                        "semantic_features": {
                            f"feature_{random.randint(1,5)}": random.uniform(-1.0, 1.0)
                        },
                        "metadata": {"stress_test": True}
                    })
                
                if response.status_code in [200, 201]:
                    successes += 1
                else:
                    errors += 1
                
                # Progress update
                if operations % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = operations / elapsed
                    print(f"   Mixed load: {operations} ops, {rate:.1f} ops/s, {successes} successful")
                
                time.sleep(0.01)  # Small delay
                
            except Exception as e:
                errors += 1
                if len(self.errors) < 10:  # Limit error logging
                    self.errors.append(f"mixed_load: {str(e)}")
        
        total_time = time.time() - start_time
        
        result = {
            "duration": round(total_time, 2),
            "total_operations": operations,
            "successful": successes,
            "failed": errors,
            "operations_per_second": round(operations / total_time, 2),
            "success_rate": round((successes / operations) * 100, 2) if operations > 0 else 0
        }
        
        self.log_result("Mixed Load Stress Test", result)
        return result

    def run_continued_stress_tests(self):
        """Run the continued stress test suite"""
        print("🚀 KIMERA SWM CONTINUED STRESS TEST SUITE")
        print("=" * 60)
        print("Continuing from cognitive cycles phase...")
        print("=" * 60)
        
        test_start = time.time()
        
        # Run the stress tests
        self.stress_test_cognitive_cycles_continued(num_cycles=25)
        self.stress_test_vault_operations(num_operations=100)
        self.stress_test_system_queries(num_queries=300)
        self.stress_test_mixed_load(duration_seconds=60)
        
        total_test_time = time.time() - test_start
        
        # Generate final report
        print("\n" + "=" * 60)
        print("🎯 CONTINUED STRESS TEST RESULTS")
        print("=" * 60)
        
        total_operations = sum(
            result.get("total_operations", result.get("total_cycles", result.get("total_queries", 0)))
            for result in self.results.values()
        )
        total_successes = sum(result.get("successful", 0) for result in self.results.values())
        total_errors = sum(result.get("failed", 0) for result in self.results.values())
        
        print(f"\n📈 OVERALL SUMMARY:")
        print(f"   Total Operations: {total_operations}")
        print(f"   Successful: {total_successes}")
        print(f"   Failed: {total_errors}")
        print(f"   Overall Success Rate: {round((total_successes / total_operations) * 100, 2) if total_operations > 0 else 0}%")
        print(f"   Total Test Duration: {round(total_test_time, 2)} seconds")
        
        if self.errors:
            print(f"\n❌ ERRORS ENCOUNTERED ({len(self.errors)}):")
            for error in self.errors[:5]:
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more errors")
        
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
        
        # Overall assessment
        success_rate = (total_successes / total_operations) * 100 if total_operations > 0 else 0
        if success_rate >= 90:
            print("\n🎉 STRESS TEST PASSED! System performed excellently under load")
        elif success_rate >= 75:
            print("\n✅ STRESS TEST MOSTLY SUCCESSFUL! System handled load well")
        elif success_rate >= 50:
            print("\n⚠️  STRESS TEST PARTIAL SUCCESS! System showed some resilience")
        else:
            print("\n❌ STRESS TEST REVEALED ISSUES! System needs optimization")
        
        return self.results, self.errors

if __name__ == "__main__":
    print("Initializing Continued KIMERA Stress Tester...")
    tester = ContinuedStressTester()
    
    try:
        results, errors = tester.run_continued_stress_tests()
        
        # Save results
        with open("continued_stress_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "errors": errors
            }, f, indent=2)
        
        print(f"\n💾 Results saved to continued_stress_test_results.json")
        
    except KeyboardInterrupt:
        print("\n🛑 Stress test interrupted by user")
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
