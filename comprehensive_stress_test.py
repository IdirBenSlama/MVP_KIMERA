#!/usr/bin/env python3
"""
KIMERA SWM Comprehensive Stress Test Suite
==========================================

This script performs extensive stress testing on the KIMERA system including:
1. Load testing with concurrent requests
2. Memory stress testing
3. Thermodynamic engine stress testing
4. Contradiction processing under load
5. Vault system resilience testing
6. Cognitive cycle performance testing
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

# Set environment variables for testing
os.environ["LIGHTWEIGHT_EMBEDDING"] = "1"
os.environ["ENABLE_JOBS"] = "0"
os.environ["DATABASE_URL"] = "sqlite:///./stress_test.db"

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api.main import app
from backend.core.geoid import GeoidState
from backend.vault.vault_manager import VaultManager
from backend.engines.contradiction_engine import ContradictionEngine

class KimeraStressTester:
    def __init__(self):
        self.client = TestClient(app)
        self.vault_manager = VaultManager()
        self.contradiction_engine = ContradictionEngine()
        self.results = {}
        self.errors = []
        
    def log_result(self, test_name: str, result: Dict[str, Any]):
        """Log test results"""
        self.results[test_name] = result
        print(f"✅ {test_name}: {result}")
        
    def log_error(self, test_name: str, error: str):
        """Log test errors"""
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")

    def generate_random_geoid_data(self) -> Dict[str, Any]:
        """Generate random geoid data for testing"""
        features = {}
        for i in range(random.randint(3, 10)):
            feature_name = ''.join(random.choices(string.ascii_lowercase, k=8))
            features[feature_name] = random.uniform(-1.0, 1.0)
        
        return {
            "semantic_features": features,
            "symbolic_content": {
                "type": random.choice(["concept", "entity", "relation"]),
                "category": random.choice(["abstract", "concrete", "temporal"])
            },
            "metadata": {
                "test_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "timestamp": datetime.now().isoformat()
            }
        }

    def stress_test_geoid_creation(self, num_geoids: int = 500, concurrent_threads: int = 10):
        """Stress test geoid creation with concurrent requests"""
        print(f"\n🔥 STRESS TEST: Creating {num_geoids} geoids with {concurrent_threads} concurrent threads")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        response_times = []
        
        def create_geoid():
            nonlocal success_count, error_count
            try:
                geoid_data = self.generate_random_geoid_data()
                req_start = time.time()
                response = self.client.post("/geoids", json=geoid_data)
                req_time = time.time() - req_start
                response_times.append(req_time)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                self.log_error("geoid_creation", str(e))
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
            futures = [executor.submit(create_geoid) for _ in range(num_geoids)]
            concurrent.futures.wait(futures)
        
        total_time = time.time() - start_time
        
        result = {
            "total_geoids": num_geoids,
            "successful": success_count,
            "failed": error_count,
            "total_time": round(total_time, 2),
            "requests_per_second": round(num_geoids / total_time, 2),
            "avg_response_time": round(statistics.mean(response_times) if response_times else 0, 4),
            "max_response_time": round(max(response_times) if response_times else 0, 4),
            "min_response_time": round(min(response_times) if response_times else 0, 4)
        }
        
        self.log_result("Geoid Creation Stress Test", result)
        return result

    def stress_test_contradiction_processing(self, num_tests: int = 100):
        """Stress test contradiction processing"""
        print(f"\n🔥 STRESS TEST: Processing {num_tests} contradiction scenarios")
        
        # First create some geoids to work with
        geoid_ids = []
        for i in range(20):
            geoid_data = self.generate_random_geoid_data()
            response = self.client.post("/geoids", json=geoid_data)
            if response.status_code == 200:
                geoid_ids.append(response.json()["geoid_id"])
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        contradictions_found = 0
        scars_created = 0
        
        for i in range(num_tests):
            try:
                trigger_id = random.choice(geoid_ids)
                response = self.client.post("/process/contradictions", json={
                    "trigger_geoid_id": trigger_id,
                    "search_limit": random.randint(3, 10)
                })
                
                if response.status_code == 200:
                    success_count += 1
                    result = response.json()
                    contradictions_found += result.get("contradictions_detected", 0)
                    scars_created += result.get("scars_created", 0)
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                self.log_error("contradiction_processing", str(e))
        
        total_time = time.time() - start_time
        
        result = {
            "total_tests": num_tests,
            "successful": success_count,
            "failed": error_count,
            "total_time": round(total_time, 2),
            "contradictions_found": contradictions_found,
            "scars_created": scars_created,
            "avg_time_per_test": round(total_time / num_tests, 4)
        }
        
        self.log_result("Contradiction Processing Stress Test", result)
        return result

    def stress_test_cognitive_cycles(self, num_cycles: int = 50):
        """Stress test cognitive cycle execution"""
        print(f"\n🔥 STRESS TEST: Running {num_cycles} cognitive cycles")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        cycle_times = []
        
        for i in range(num_cycles):
            try:
                cycle_start = time.time()
                response = self.client.post("/system/cycle")
                cycle_time = time.time() - cycle_start
                cycle_times.append(cycle_time)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                self.log_error("cognitive_cycle", str(e))
        
        total_time = time.time() - start_time
        
        result = {
            "total_cycles": num_cycles,
            "successful": success_count,
            "failed": error_count,
            "total_time": round(total_time, 2),
            "avg_cycle_time": round(statistics.mean(cycle_times) if cycle_times else 0, 4),
            "max_cycle_time": round(max(cycle_times) if cycle_times else 0, 4),
            "min_cycle_time": round(min(cycle_times) if cycle_times else 0, 4)
        }
        
        self.log_result("Cognitive Cycle Stress Test", result)
        return result

    def stress_test_vault_operations(self, num_operations: int = 200):
        """Stress test vault operations"""
        print(f"\n🔥 STRESS TEST: Performing {num_operations} vault operations")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        
        for i in range(num_operations):
            try:
                # Test vault queries
                response = self.client.get(f"/vaults/vault_a?limit={random.randint(1, 10)}")
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
                
                # Test vault rebalancing occasionally
                if i % 20 == 0:
                    response = self.client.post("/vaults/rebalance")
                    if response.status_code != 200:
                        error_count += 1
                        
            except Exception as e:
                error_count += 1
                self.log_error("vault_operations", str(e))
        
        total_time = time.time() - start_time
        
        result = {
            "total_operations": num_operations,
            "successful": success_count,
            "failed": error_count,
            "total_time": round(total_time, 2),
            "operations_per_second": round(num_operations / total_time, 2)
        }
        
        self.log_result("Vault Operations Stress Test", result)
        return result

    def stress_test_system_status_queries(self, num_queries: int = 1000, concurrent_threads: int = 20):
        """Stress test system status queries with high concurrency"""
        print(f"\n🔥 STRESS TEST: {num_queries} system status queries with {concurrent_threads} threads")
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        response_times = []
        
        def query_status():
            nonlocal success_count, error_count
            try:
                req_start = time.time()
                response = self.client.get("/system/status")
                req_time = time.time() - req_start
                response_times.append(req_time)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
            futures = [executor.submit(query_status) for _ in range(num_queries)]
            concurrent.futures.wait(futures)
        
        total_time = time.time() - start_time
        
        result = {
            "total_queries": num_queries,
            "successful": success_count,
            "failed": error_count,
            "total_time": round(total_time, 2),
            "queries_per_second": round(num_queries / total_time, 2),
            "avg_response_time": round(statistics.mean(response_times) if response_times else 0, 4),
            "max_response_time": round(max(response_times) if response_times else 0, 4)
        }
        
        self.log_result("System Status Query Stress Test", result)
        return result

    def memory_stress_test(self, duration_seconds: int = 60):
        """Run memory stress test for specified duration"""
        print(f"\n🔥 MEMORY STRESS TEST: Running for {duration_seconds} seconds")
        
        start_time = time.time()
        operations = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                # Create and process geoids rapidly
                geoid_data = self.generate_random_geoid_data()
                response = self.client.post("/geoids", json=geoid_data)
                
                if response.status_code == 200:
                    geoid_id = response.json()["geoid_id"]
                    # Immediately process contradictions
                    self.client.post("/process/contradictions", json={
                        "trigger_geoid_id": geoid_id,
                        "search_limit": 3
                    })
                
                operations += 1
                
                # Occasional system queries
                if operations % 10 == 0:
                    self.client.get("/system/status")
                    
            except Exception as e:
                self.log_error("memory_stress", str(e))
        
        total_time = time.time() - start_time
        
        result = {
            "duration": round(total_time, 2),
            "total_operations": operations,
            "operations_per_second": round(operations / total_time, 2)
        }
        
        self.log_result("Memory Stress Test", result)
        return result

    def run_comprehensive_stress_test(self):
        """Run all stress tests"""
        print("🚀 KIMERA SWM COMPREHENSIVE STRESS TEST SUITE")
        print("=" * 60)
        
        test_start = time.time()
        
        # Run individual stress tests
        self.stress_test_geoid_creation(num_geoids=300, concurrent_threads=8)
        self.stress_test_contradiction_processing(num_tests=50)
        self.stress_test_cognitive_cycles(num_cycles=25)
        self.stress_test_vault_operations(num_operations=100)
        self.stress_test_system_status_queries(num_queries=500, concurrent_threads=15)
        self.memory_stress_test(duration_seconds=30)
        
        total_test_time = time.time() - test_start
        
        # Generate final report
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE STRESS TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            print(f"\n📊 {test_name}:")
            for key, value in result.items():
                print(f"   {key}: {value}")
        
        if self.errors:
            print(f"\n❌ ERRORS ENCOUNTERED ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
        
        print(f"\n⏱️  Total test duration: {round(total_test_time, 2)} seconds")
        print(f"🔥 Total errors: {len(self.errors)}")
        
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
        
        return self.results, self.errors

if __name__ == "__main__":
    print("Initializing KIMERA Stress Tester...")
    tester = KimeraStressTester()
    
    try:
        results, errors = tester.run_comprehensive_stress_test()
        
        # Save results to file
        with open("stress_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "errors": errors
            }, f, indent=2)
        
        print(f"\n💾 Results saved to stress_test_results.json")
        
        if len(errors) == 0:
            print("🎉 ALL STRESS TESTS COMPLETED SUCCESSFULLY!")
        else:
            print(f"⚠️  Stress tests completed with {len(errors)} errors")
            
    except KeyboardInterrupt:
        print("\n🛑 Stress test interrupted by user")
    except Exception as e:
        print(f"\n💥 Critical error during stress testing: {e}")