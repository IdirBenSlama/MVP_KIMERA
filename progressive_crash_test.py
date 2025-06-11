#!/usr/bin/env python3
"""
KIMERA SWM Progressive Crash Test
=================================

This test progressively increases load until we find the breaking point.
It starts small and gradually ramps up to avoid immediate system overload.
"""

import os
import sys
import time
import threading
import concurrent.futures
import random
import requests
import json
from datetime import datetime

# Lightweight test environment
os.environ["LIGHTWEIGHT_EMBEDDING"] = "1"
os.environ["ENABLE_JOBS"] = "0"

class ProgressiveCrashTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.results = []
        self.breaking_point = None
        
    def test_system_health(self):
        """Quick system health check"""
        try:
            response = requests.get(f"{self.base_url}/system/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def progressive_load_test(self, start_threads=1, max_threads=100, step=5, operations_per_thread=50):
        """Progressively increase load until system breaks"""
        print(f"🔥 PROGRESSIVE CRASH TEST: {start_threads} to {max_threads} threads")
        print("=" * 60)
        
        current_threads = start_threads
        
        while current_threads <= max_threads:
            print(f"\n📊 Testing with {current_threads} concurrent threads...")
            
            # Test current load level
            success_count = 0
            error_count = 0
            start_time = time.time()
            
            def worker():
                nonlocal success_count, error_count
                worker_success = 0
                worker_errors = 0
                
                for i in range(operations_per_thread):
                    try:
                        # Mix of operations
                        operation = random.choice(["geoid", "status", "cycle"])
                        
                        if operation == "geoid":
                            response = requests.post(f"{self.base_url}/geoids", 
                                json={"semantic_features": {"test": random.random()}},
                                timeout=10)
                        elif operation == "status":
                            response = requests.get(f"{self.base_url}/system/status", timeout=10)
                        elif operation == "cycle":
                            response = requests.post(f"{self.base_url}/system/cycle", timeout=15)
                        
                        if response.status_code in [200, 201]:
                            worker_success += 1
                        else:
                            worker_errors += 1
                            
                    except requests.exceptions.Timeout:
                        worker_errors += 1
                        print(f"   ⏰ Timeout in thread with {current_threads} concurrent")
                    except requests.exceptions.ConnectionError:
                        worker_errors += 1
                        print(f"   🔌 Connection error with {current_threads} concurrent")
                    except Exception as e:
                        worker_errors += 1
                        print(f"   ❌ Error: {str(e)[:50]}")
                
                success_count += worker_success
                error_count += worker_errors
            
            # Run the load test
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=current_threads) as executor:
                    futures = [executor.submit(worker) for _ in range(current_threads)]
                    
                    # Wait with timeout
                    try:
                        concurrent.futures.wait(futures, timeout=120)  # 2 minute timeout
                    except concurrent.futures.TimeoutError:
                        print(f"   ⏰ TIMEOUT at {current_threads} threads!")
                        error_count += len([f for f in futures if not f.done()])
                
            except Exception as e:
                print(f"   💥 EXECUTOR FAILURE at {current_threads} threads: {e}")
                error_count += current_threads * operations_per_thread
            
            total_time = time.time() - start_time
            total_operations = success_count + error_count
            success_rate = (success_count / total_operations * 100) if total_operations > 0 else 0
            
            result = {
                "threads": current_threads,
                "operations": total_operations,
                "successful": success_count,
                "failed": error_count,
                "success_rate": round(success_rate, 2),
                "duration": round(total_time, 2),
                "ops_per_second": round(total_operations / total_time, 2) if total_time > 0 else 0
            }
            
            self.results.append(result)
            
            print(f"   Results: {success_count}/{total_operations} successful ({success_rate:.1f}%)")
            print(f"   Duration: {total_time:.2f}s, Rate: {result['ops_per_second']:.1f} ops/s")
            
            # Check if system is still healthy
            if not self.test_system_health():
                print(f"   💀 SYSTEM UNRESPONSIVE at {current_threads} threads!")
                self.breaking_point = current_threads
                break
            
            # Check if we've hit a performance cliff
            if success_rate < 50:
                print(f"   📉 PERFORMANCE CLIFF at {current_threads} threads (success rate: {success_rate:.1f}%)")
                self.breaking_point = current_threads
                break
            
            # Check if errors are increasing rapidly
            if error_count > success_count:
                print(f"   ⚠️  HIGH ERROR RATE at {current_threads} threads")
                if current_threads > start_threads * 2:  # Only break if we've made some progress
                    self.breaking_point = current_threads
                    break
            
            current_threads += step
            
            # Brief pause between tests
            time.sleep(2)
        
        return self.results, self.breaking_point

    def memory_pressure_test(self, duration_seconds=60):
        """Test system under memory pressure"""
        print(f"\n🧠 MEMORY PRESSURE TEST: {duration_seconds} seconds")
        
        start_time = time.time()
        operations = 0
        errors = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                # Create large geoids to consume memory
                large_features = {f"feature_{i}": random.random() for i in range(100)}
                large_metadata = {
                    "large_data": "x" * 1000,  # 1KB string
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(f"{self.base_url}/geoids", 
                    json={
                        "semantic_features": large_features,
                        "metadata": large_metadata
                    }, timeout=10)
                
                if response.status_code in [200, 201]:
                    operations += 1
                else:
                    errors += 1
                
                # Trigger cognitive cycle occasionally
                if operations % 10 == 0:
                    requests.post(f"{self.base_url}/system/cycle", timeout=15)
                
                if operations % 50 == 0:
                    elapsed = time.time() - start_time
                    print(f"   Memory test: {operations} ops in {elapsed:.1f}s, {errors} errors")
                
            except Exception as e:
                errors += 1
                if "memory" in str(e).lower():
                    print(f"   💾 Memory error detected: {str(e)[:50]}")
                    break
        
        total_time = time.time() - start_time
        
        result = {
            "duration": round(total_time, 2),
            "operations": operations,
            "errors": errors,
            "ops_per_second": round(operations / total_time, 2)
        }
        
        print(f"   Memory test completed: {operations} operations, {errors} errors")
        return result

    def rapid_fire_test(self, requests_per_second=100, duration_seconds=30):
        """Test system with rapid-fire requests"""
        print(f"\n⚡ RAPID FIRE TEST: {requests_per_second} req/s for {duration_seconds}s")
        
        start_time = time.time()
        operations = 0
        errors = 0
        delay = 1.0 / requests_per_second
        
        while time.time() - start_time < duration_seconds:
            try:
                response = requests.get(f"{self.base_url}/system/status", timeout=5)
                if response.status_code == 200:
                    operations += 1
                else:
                    errors += 1
                
                time.sleep(delay)
                
            except Exception as e:
                errors += 1
                if operations % 100 == 0:
                    print(f"   Rapid fire: {operations} ops, {errors} errors")
        
        total_time = time.time() - start_time
        actual_rate = operations / total_time
        
        result = {
            "target_rate": requests_per_second,
            "actual_rate": round(actual_rate, 2),
            "operations": operations,
            "errors": errors,
            "duration": round(total_time, 2)
        }
        
        print(f"   Rapid fire completed: {actual_rate:.1f} actual req/s")
        return result

    def run_progressive_crash_test(self):
        """Run the complete progressive crash test"""
        print("🚀 KIMERA SWM PROGRESSIVE CRASH TEST")
        print("Finding the system's breaking point...")
        print("=" * 60)
        
        # Initial health check
        if not self.test_system_health():
            print("❌ System is not responding - cannot run crash test")
            return
        
        print("✅ Initial system health check passed")
        
        # Progressive load test
        load_results, breaking_point = self.progressive_load_test(
            start_threads=1, max_threads=50, step=3, operations_per_thread=20
        )
        
        # Memory pressure test (if system survived)
        if self.test_system_health():
            memory_result = self.memory_pressure_test(duration_seconds=45)
        else:
            memory_result = {"error": "System unresponsive"}
        
        # Rapid fire test (if system survived)
        if self.test_system_health():
            rapid_result = self.rapid_fire_test(requests_per_second=50, duration_seconds=20)
        else:
            rapid_result = {"error": "System unresponsive"}
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 PROGRESSIVE CRASH TEST RESULTS")
        print("=" * 60)
        
        print(f"\n🔥 Load Test Results:")
        for result in load_results:
            print(f"   {result['threads']:2d} threads: {result['success_rate']:5.1f}% success, "
                  f"{result['ops_per_second']:6.1f} ops/s")
        
        if breaking_point:
            print(f"\n💥 BREAKING POINT FOUND: {breaking_point} concurrent threads")
        else:
            print(f"\n🎉 NO BREAKING POINT FOUND: System handled up to {load_results[-1]['threads']} threads")
        
        print(f"\n🧠 Memory Pressure Test: {memory_result}")
        print(f"\n⚡ Rapid Fire Test: {rapid_result}")
        
        # Final health check
        if self.test_system_health():
            print(f"\n✅ SYSTEM SURVIVED: Still responsive after all tests")
            
            # Get final status
            try:
                response = requests.get(f"{self.base_url}/system/status")
                if response.status_code == 200:
                    status = response.json()
                    print(f"   Active Geoids: {status.get('active_geoids', 'N/A')}")
                    print(f"   System Entropy: {status.get('system_entropy', 'N/A')}")
            except:
                pass
        else:
            print(f"\n💀 SYSTEM COMPROMISED: Unresponsive after crash test")
        
        # Save results
        results = {
            "timestamp": datetime.now().isoformat(),
            "breaking_point": breaking_point,
            "load_test_results": load_results,
            "memory_test": memory_result,
            "rapid_fire_test": rapid_result,
            "system_survived": self.test_system_health()
        }
        
        with open("progressive_crash_results.json", "w") as f:
            json.dump(results, indent=2, fp=f)
        
        print(f"\n💾 Results saved to progressive_crash_results.json")
        
        return results

if __name__ == "__main__":
    tester = ProgressiveCrashTester()
    
    try:
        results = tester.run_progressive_crash_test()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
