#!/usr/bin/env python3
"""
KIMERA SWM Crash Test Suite
===========================

This script pushes the KIMERA system to its absolute limits to find breaking points:
1. Massive concurrent load testing
2. Memory exhaustion testing
3. Database overload testing
4. Extreme cognitive cycle stress
5. Resource starvation scenarios
6. Cascading failure testing

The goal is to find the scale at which the system fails and understand failure modes.
"""

import os
import sys
import time
import threading
import concurrent.futures
import random
import string
import statistics
import psutil
import gc
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import uuid
import multiprocessing

# Set environment for maximum stress
os.environ["LIGHTWEIGHT_EMBEDDING"] = "1"
os.environ["ENABLE_JOBS"] = "0"
os.environ["DATABASE_URL"] = f"sqlite:///./crash_test_{uuid.uuid4().hex[:8]}.db"

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api.main import app

class KimeraCrashTester:
    def __init__(self):
        self.client = TestClient(app)
        self.results = {}
        self.failures = []
        self.system_metrics = []
        self.max_concurrent_threads = multiprocessing.cpu_count() * 4
        self.start_time = time.time()
        
    def log_system_metrics(self):
        """Log current system resource usage"""
        process = psutil.Process()
        metrics = {
            "timestamp": time.time() - self.start_time,
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": process.memory_info().rss / 1024 / 1024,
            "open_files": len(process.open_files()),
            "threads": process.num_threads()
        }
        self.system_metrics.append(metrics)
        return metrics
        
    def log_failure(self, test_name: str, failure_details: Dict[str, Any]):
        """Log system failure details"""
        failure = {
            "test": test_name,
            "timestamp": datetime.now().isoformat(),
            "details": failure_details,
            "system_metrics": self.log_system_metrics()
        }
        self.failures.append(failure)
        print(f"💥 FAILURE in {test_name}: {failure_details}")

    def crash_test_massive_geoid_creation(self, target_geoids: int = 10000, max_threads: int = 50):
        """Test massive geoid creation until failure"""
        print(f"\n💥 CRASH TEST: Massive geoid creation - targeting {target_geoids} geoids with {max_threads} threads")
        
        start_time = time.time()
        created_count = 0
        error_count = 0
        memory_errors = 0
        database_errors = 0
        
        def create_geoid_batch():
            nonlocal created_count, error_count, memory_errors, database_errors
            batch_created = 0
            batch_errors = 0
            
            for _ in range(100):  # Create 100 geoids per thread
                try:
                    # Generate complex geoid data
                    geoid_data = {
                        "semantic_features": {
                            f"feature_{i}": random.uniform(-1.0, 1.0) 
                            for i in range(random.randint(10, 50))  # More features = more memory
                        },
                        "symbolic_content": {
                            "type": "crash_test",
                            "complexity": random.randint(1, 100),
                            "data": ''.join(random.choices(string.ascii_letters, k=random.randint(100, 1000)))
                        },
                        "metadata": {
                            "crash_test_id": uuid.uuid4().hex,
                            "timestamp": datetime.now().isoformat(),
                            "thread_id": threading.current_thread().ident
                        }
                    }
                    
                    response = self.client.post("/geoids", json=geoid_data)
                    
                    if response.status_code == 200:
                        batch_created += 1
                    else:
                        batch_errors += 1
                        error_msg = response.text if hasattr(response, 'text') else str(response.status_code)
                        if "memory" in error_msg.lower():
                            memory_errors += 1
                        elif "database" in error_msg.lower() or "constraint" in error_msg.lower():
                            database_errors += 1
                            
                except MemoryError:
                    memory_errors += 1
                    batch_errors += 1
                    break  # Stop this thread on memory error
                except Exception as e:
                    batch_errors += 1
                    if "memory" in str(e).lower():
                        memory_errors += 1
                    elif "database" in str(e).lower():
                        database_errors += 1
            
            created_count += batch_created
            error_count += batch_errors
        
        # Launch massive concurrent load
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                # Submit batches until we reach target or system fails
                futures = []
                for batch in range(target_geoids // 100):
                    if batch % 10 == 0:
                        metrics = self.log_system_metrics()
                        print(f"   Batch {batch}: {created_count} created, {error_count} errors, "
                              f"Memory: {metrics['memory_percent']:.1f}%, CPU: {metrics['cpu_percent']:.1f}%")
                        
                        # Check for system stress indicators
                        if metrics['memory_percent'] > 90:
                            print("   ⚠️  High memory usage detected!")
                        if metrics['cpu_percent'] > 95:
                            print("   ⚠️  High CPU usage detected!")
                    
                    future = executor.submit(create_geoid_batch)
                    futures.append(future)
                    
                    # Small delay to prevent immediate system overload
                    time.sleep(0.01)
                
                # Wait for completion or timeout
                try:
                    concurrent.futures.wait(futures, timeout=300)  # 5 minute timeout
                except concurrent.futures.TimeoutError:
                    print("   ⏰ Timeout reached - cancelling remaining operations")
                    
        except Exception as e:
            self.log_failure("massive_geoid_creation", {
                "error": str(e),
                "created_count": created_count,
                "error_count": error_count
            })
        
        total_time = time.time() - start_time
        final_metrics = self.log_system_metrics()
        
        result = {
            "target_geoids": target_geoids,
            "created_successfully": created_count,
            "total_errors": error_count,
            "memory_errors": memory_errors,
            "database_errors": database_errors,
            "total_time": round(total_time, 2),
            "creation_rate": round(created_count / total_time, 2),
            "final_memory_usage": final_metrics['memory_percent'],
            "final_cpu_usage": final_metrics['cpu_percent'],
            "peak_threads": final_metrics['threads']
        }
        
        self.results["Massive Geoid Creation Crash Test"] = result
        print(f"✅ Crash test completed: {created_count}/{target_geoids} geoids created")
        return result

    def crash_test_cognitive_cycle_overload(self, max_cycles: int = 1000, concurrent_cycles: int = 20):
        """Test cognitive cycle system under extreme load"""
        print(f"\n💥 CRASH TEST: Cognitive cycle overload - {max_cycles} cycles with {concurrent_cycles} concurrent")
        
        start_time = time.time()
        completed_cycles = 0
        failed_cycles = 0
        timeout_cycles = 0
        
        def run_cycle_batch():
            nonlocal completed_cycles, failed_cycles, timeout_cycles
            batch_completed = 0
            batch_failed = 0
            
            for _ in range(50):  # 50 cycles per thread
                try:
                    cycle_start = time.time()
                    response = self.client.post("/system/cycle", timeout=10)  # 10 second timeout
                    cycle_time = time.time() - cycle_start
                    
                    if response.status_code == 200:
                        batch_completed += 1
                        if cycle_time > 5:  # Log slow cycles
                            print(f"   ⚠️  Slow cycle: {cycle_time:.2f}s")
                    else:
                        batch_failed += 1
                        
                except Exception as e:
                    batch_failed += 1
                    if "timeout" in str(e).lower():
                        timeout_cycles += 1
            
            completed_cycles += batch_completed
            failed_cycles += batch_failed
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_cycles) as executor:
                futures = []
                for batch in range(max_cycles // 50):
                    if batch % 5 == 0:
                        metrics = self.log_system_metrics()
                        print(f"   Cycle batch {batch}: {completed_cycles} completed, {failed_cycles} failed")
                    
                    future = executor.submit(run_cycle_batch)
                    futures.append(future)
                    time.sleep(0.1)  # Slight delay between batch submissions
                
                concurrent.futures.wait(futures, timeout=600)  # 10 minute timeout
                
        except Exception as e:
            self.log_failure("cognitive_cycle_overload", {
                "error": str(e),
                "completed_cycles": completed_cycles,
                "failed_cycles": failed_cycles
            })
        
        total_time = time.time() - start_time
        
        result = {
            "target_cycles": max_cycles,
            "completed_cycles": completed_cycles,
            "failed_cycles": failed_cycles,
            "timeout_cycles": timeout_cycles,
            "total_time": round(total_time, 2),
            "cycles_per_second": round(completed_cycles / total_time, 2),
            "success_rate": round((completed_cycles / (completed_cycles + failed_cycles)) * 100, 2) if (completed_cycles + failed_cycles) > 0 else 0
        }
        
        self.results["Cognitive Cycle Overload Crash Test"] = result
        print(f"✅ Cycle crash test completed: {completed_cycles} cycles completed")
        return result

    def crash_test_memory_exhaustion(self, duration_minutes: int = 5):
        """Test system behavior under memory exhaustion"""
        print(f"\n💥 CRASH TEST: Memory exhaustion test - {duration_minutes} minutes")
        
        start_time = time.time()
        operations = 0
        memory_errors = 0
        large_objects = []  # Keep references to prevent garbage collection
        
        while time.time() - start_time < duration_minutes * 60:
            try:
                # Create memory-intensive operations
                
                # 1. Large geoid with massive feature vectors
                large_features = {f"feature_{i}": random.uniform(-1.0, 1.0) for i in range(1000)}
                large_symbolic = {
                    "massive_data": ''.join(random.choices(string.ascii_letters, k=10000)),
                    "array_data": [random.random() for _ in range(1000)]
                }
                
                response = self.client.post("/geoids", json={
                    "semantic_features": large_features,
                    "symbolic_content": large_symbolic,
                    "metadata": {"memory_test": True}
                })
                
                # 2. Keep some large objects in memory
                if len(large_objects) < 100:
                    large_objects.append([random.random() for _ in range(10000)])
                
                # 3. Force multiple cognitive cycles
                self.client.post("/system/cycle")
                
                operations += 1
                
                # Monitor memory usage
                if operations % 10 == 0:
                    metrics = self.log_system_metrics()
                    print(f"   Memory test: {operations} ops, Memory: {metrics['memory_percent']:.1f}%")
                    
                    if metrics['memory_percent'] > 95:
                        print("   🚨 CRITICAL MEMORY USAGE!")
                        break
                
            except MemoryError:
                memory_errors += 1
                print(f"   💥 Memory error at operation {operations}")
                break
            except Exception as e:
                if "memory" in str(e).lower():
                    memory_errors += 1
                    print(f"   💥 Memory-related error: {str(e)[:100]}")
                    break
        
        # Force garbage collection
        gc.collect()
        
        total_time = time.time() - start_time
        final_metrics = self.log_system_metrics()
        
        result = {
            "duration_minutes": duration_minutes,
            "operations_completed": operations,
            "memory_errors": memory_errors,
            "total_time": round(total_time, 2),
            "final_memory_usage": final_metrics['memory_percent'],
            "peak_memory_objects": len(large_objects)
        }
        
        self.results["Memory Exhaustion Crash Test"] = result
        print(f"✅ Memory crash test completed: {operations} operations before limit")
        return result

    def crash_test_database_overload(self, concurrent_writers: int = 100, operations_per_writer: int = 100):
        """Test database under extreme concurrent load"""
        print(f"\n💥 CRASH TEST: Database overload - {concurrent_writers} writers, {operations_per_writer} ops each")
        
        start_time = time.time()
        successful_ops = 0
        failed_ops = 0
        constraint_errors = 0
        lock_errors = 0
        
        def database_stress_worker():
            nonlocal successful_ops, failed_ops, constraint_errors, lock_errors
            worker_success = 0
            worker_failed = 0
            
            for i in range(operations_per_writer):
                try:
                    # Mix of operations that stress the database
                    operation = random.choice(["create_geoid", "process_contradiction", "vault_query", "cycle"])
                    
                    if operation == "create_geoid":
                        response = self.client.post("/geoids", json={
                            "semantic_features": {"stress": random.random()},
                            "metadata": {"db_stress": True}
                        })
                    elif operation == "process_contradiction":
                        response = self.client.post("/process/contradictions", json={
                            "trigger_geoid_id": f"GEOID_{random.randint(1, 1000)}",
                            "search_limit": 5
                        })
                    elif operation == "vault_query":
                        vault = random.choice(["vault_a", "vault_b"])
                        response = self.client.get(f"/vaults/{vault}?limit=10")
                    elif operation == "cycle":
                        response = self.client.post("/system/cycle")
                    
                    if response.status_code in [200, 201]:
                        worker_success += 1
                    else:
                        worker_failed += 1
                        error_msg = response.text if hasattr(response, 'text') else ""
                        if "constraint" in error_msg.lower():
                            constraint_errors += 1
                        elif "lock" in error_msg.lower():
                            lock_errors += 1
                            
                except Exception as e:
                    worker_failed += 1
                    error_msg = str(e).lower()
                    if "constraint" in error_msg:
                        constraint_errors += 1
                    elif "lock" in error_msg or "database" in error_msg:
                        lock_errors += 1
            
            successful_ops += worker_success
            failed_ops += worker_failed
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_writers) as executor:
                futures = [executor.submit(database_stress_worker) for _ in range(concurrent_writers)]
                
                # Monitor progress
                start_monitor = time.time()
                while not all(f.done() for f in futures):
                    time.sleep(5)
                    elapsed = time.time() - start_monitor
                    print(f"   DB stress: {elapsed:.0f}s elapsed, {successful_ops} success, {failed_ops} failed")
                    
                    if elapsed > 300:  # 5 minute timeout
                        print("   ⏰ Database stress test timeout")
                        break
                
                concurrent.futures.wait(futures, timeout=60)
                
        except Exception as e:
            self.log_failure("database_overload", {
                "error": str(e),
                "successful_ops": successful_ops,
                "failed_ops": failed_ops
            })
        
        total_time = time.time() - start_time
        total_ops = successful_ops + failed_ops
        
        result = {
            "concurrent_writers": concurrent_writers,
            "target_operations": concurrent_writers * operations_per_writer,
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "constraint_errors": constraint_errors,
            "lock_errors": lock_errors,
            "total_time": round(total_time, 2),
            "operations_per_second": round(total_ops / total_time, 2) if total_time > 0 else 0,
            "success_rate": round((successful_ops / total_ops) * 100, 2) if total_ops > 0 else 0
        }
        
        self.results["Database Overload Crash Test"] = result
        print(f"✅ Database crash test completed: {successful_ops}/{total_ops} operations successful")
        return result

    def crash_test_cascading_failures(self):
        """Test system behavior under cascading failure scenarios"""
        print(f"\n💥 CRASH TEST: Cascading failure scenarios")
        
        failure_scenarios = []
        
        try:
            # Scenario 1: Overload then memory stress
            print("   Scenario 1: Overload + Memory Stress")
            self.crash_test_massive_geoid_creation(target_geoids=1000, max_threads=20)
            self.crash_test_memory_exhaustion(duration_minutes=2)
            
            # Scenario 2: Database stress + Cognitive overload
            print("   Scenario 2: Database + Cognitive Overload")
            self.crash_test_database_overload(concurrent_writers=50, operations_per_writer=50)
            self.crash_test_cognitive_cycle_overload(max_cycles=200, concurrent_cycles=10)
            
            # Check system status after each scenario
            try:
                status_response = self.client.get("/system/status")
                if status_response.status_code == 200:
                    print("   ✅ System still responsive after cascading tests")
                else:
                    failure_scenarios.append("System unresponsive after cascading tests")
            except Exception as e:
                failure_scenarios.append(f"System status check failed: {str(e)}")
                
        except Exception as e:
            failure_scenarios.append(f"Cascading test failure: {str(e)}")
        
        result = {
            "scenarios_tested": 2,
            "failure_scenarios": failure_scenarios,
            "system_survived": len(failure_scenarios) == 0
        }
        
        self.results["Cascading Failure Crash Test"] = result
        return result

    def run_comprehensive_crash_test(self):
        """Run the complete crash test suite"""
        print("💥 KIMERA SWM COMPREHENSIVE CRASH TEST SUITE")
        print("=" * 60)
        print("WARNING: This test will push the system to its breaking point!")
        print("=" * 60)
        
        test_start = time.time()
        initial_metrics = self.log_system_metrics()
        
        print(f"🔧 Initial System State:")
        print(f"   CPU: {initial_metrics['cpu_percent']:.1f}%")
        print(f"   Memory: {initial_metrics['memory_percent']:.1f}%")
        print(f"   Threads: {initial_metrics['threads']}")
        
        # Run crash tests in order of increasing severity
        try:
            self.crash_test_massive_geoid_creation(target_geoids=5000, max_threads=30)
            self.crash_test_cognitive_cycle_overload(max_cycles=500, concurrent_cycles=15)
            self.crash_test_database_overload(concurrent_writers=75, operations_per_writer=75)
            self.crash_test_memory_exhaustion(duration_minutes=3)
            self.crash_test_cascading_failures()
            
        except Exception as e:
            print(f"💥 CRITICAL SYSTEM FAILURE: {e}")
            self.log_failure("comprehensive_crash_test", {"critical_error": str(e)})
        
        total_test_time = time.time() - test_start
        final_metrics = self.log_system_metrics()
        
        # Generate crash test report
        print("\n" + "=" * 60)
        print("💥 CRASH TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            print(f"\n🔥 {test_name}:")
            for key, value in result.items():
                print(f"   {key}: {value}")
        
        print(f"\n📊 SYSTEM IMPACT ANALYSIS:")
        print(f"   Initial Memory: {initial_metrics['memory_percent']:.1f}%")
        print(f"   Final Memory: {final_metrics['memory_percent']:.1f}%")
        print(f"   Memory Delta: +{final_metrics['memory_percent'] - initial_metrics['memory_percent']:.1f}%")
        print(f"   Initial Threads: {initial_metrics['threads']}")
        print(f"   Final Threads: {final_metrics['threads']}")
        print(f"   Total Test Duration: {round(total_test_time, 2)} seconds")
        
        if self.failures:
            print(f"\n💥 SYSTEM FAILURES ({len(self.failures)}):")
            for failure in self.failures:
                print(f"   - {failure['test']}: {failure['details']}")
        
        # Final system health check
        try:
            final_status = self.client.get("/system/status", timeout=10)
            if final_status.status_code == 200:
                status_data = final_status.json()
                print(f"\n🏁 FINAL SYSTEM STATUS (System Survived!):")
                print(f"   Active Geoids: {status_data.get('active_geoids', 'N/A')}")
                print(f"   System Entropy: {status_data.get('system_entropy', 'N/A')}")
                print(f"   Vault A Scars: {status_data.get('vault_a_scars', 'N/A')}")
                print(f"   Vault B Scars: {status_data.get('vault_b_scars', 'N/A')}")
                system_survived = True
            else:
                print(f"\n💀 SYSTEM COMPROMISED: Status check returned {final_status.status_code}")
                system_survived = False
        except Exception as e:
            print(f"\n💀 SYSTEM UNRESPONSIVE: {e}")
            system_survived = False
        
        # Overall assessment
        if system_survived and len(self.failures) == 0:
            print("\n🎉 CRASH TEST VERDICT: SYSTEM EXTREMELY ROBUST!")
            print("   The system survived all crash test scenarios")
        elif system_survived and len(self.failures) < 3:
            print("\n✅ CRASH TEST VERDICT: SYSTEM ROBUST")
            print("   The system survived with minor failures")
        elif system_survived:
            print("\n⚠️  CRASH TEST VERDICT: SYSTEM MODERATELY ROBUST")
            print("   The system survived but showed significant stress")
        else:
            print("\n💥 CRASH TEST VERDICT: SYSTEM BREAKING POINT FOUND")
            print("   The system reached its operational limits")
        
        return self.results, self.failures, self.system_metrics

if __name__ == "__main__":
    print("Initializing KIMERA Crash Tester...")
    print("⚠️  WARNING: This will stress test the system to its limits!")
    
    tester = KimeraCrashTester()
    
    try:
        results, failures, metrics = tester.run_comprehensive_crash_test()
        
        # Save comprehensive results
        with open("crash_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "failures": failures,
                "system_metrics": metrics
            }, f, indent=2)
        
        print(f"\n💾 Crash test results saved to crash_test_results.json")
        
    except KeyboardInterrupt:
        print("\n🛑 Crash test interrupted by user")
    except Exception as e:
        print(f"\n💥 Critical crash test failure: {e}")
        import traceback
        traceback.print_exc()