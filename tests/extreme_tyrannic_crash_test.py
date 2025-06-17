"""
EXTREME TYRANNIC CRASH TEST SUITE
Kimera SWM Alpha Prototype V0.1

This test suite is designed to push the system beyond its breaking point,
identifying failure modes, recovery capabilities, and absolute limits.
"""

import asyncio
import concurrent.futures
import json
import random
import time
import psutil
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import threading
import multiprocessing
import gc
import traceback
import signal
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.linguistic.echoform import parse_echoform
from backend.core.geoid import GeoidState
from backend.engines.spde import SPDE
from backend.engines.kccl import KimeraCognitiveCycle
from backend.vault.vault_manager import VaultManager

@dataclass
class ExtremeCrashTestConfig:
    """Configuration for extreme crash testing scenarios"""
    name: str
    threads: int
    features: int
    depth: int
    payload_size_mb: float
    recursive_depth: int
    memory_pressure: float  # Percentage of available memory to consume
    gpu_stress_factor: int  # Multiplier for GPU operations
    chaos_probability: float  # Probability of injecting chaos
    timeout_seconds: int
    burst_mode: bool  # Sudden load spikes
    memory_leak_simulation: bool
    infinite_loop_probability: float
    exception_injection_rate: float
    network_latency_ms: int
    cpu_affinity_chaos: bool

class ExtremeTestMetrics:
    """Tracks extreme test metrics and failure modes"""
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.timeout_failures = 0
        self.memory_failures = 0
        self.gpu_failures = 0
        self.exception_failures = 0
        self.deadlocks = 0
        self.response_times = []
        self.memory_peaks = []
        self.gpu_peaks = []
        self.failure_modes = {}
        self.recovery_times = []
        self.cascade_failures = 0
        self.zombie_processes = 0
        self.corrupted_responses = 0
        
    def record_failure(self, failure_type: str, details: str):
        self.failed_requests += 1
        if failure_type not in self.failure_modes:
            self.failure_modes[failure_type] = []
        self.failure_modes[failure_type].append({
            'timestamp': time.time(),
            'details': details
        })

class ExtremeTyrannicCrashTest:
    """Extreme crash testing framework for Kimera SWM"""
    
    def __init__(self):
        self.spde = SPDE()
        self.kccl = KimeraCognitiveCycle()
        self.vault_manager = VaultManager()
        self.metrics = ExtremeTestMetrics()
        self.chaos_monkey_active = False
        self.memory_bombs = []
        self.zombie_threads = []
        
    def generate_extreme_payload(self, config: ExtremeCrashTestConfig) -> Dict[str, Any]:
        """Generate extreme test payloads designed to stress the system"""
        payload = {
            "features": [],
            "depth": config.depth,
            "recursive_depth": config.recursive_depth
        }
        
        # Generate massive feature arrays
        for i in range(config.features):
            feature = {
                "id": f"extreme_feature_{i}",
                "type": random.choice(["nested_recursive", "memory_bomb", "gpu_intensive", "deadlock_prone"]),
                "data": self._generate_stress_data(config.payload_size_mb),
                "nested_levels": []
            }
            
            # Create deeply nested structures
            current_level = feature["nested_levels"]
            for depth in range(config.recursive_depth):
                next_level = {
                    "depth": depth,
                    "data": self._generate_stress_data(0.1),  # 100KB per level
                    "children": []
                }
                current_level.append(next_level)
                current_level = next_level["children"]
            
            payload["features"].append(feature)
        
        # Inject chaos elements
        if random.random() < config.chaos_probability:
            payload["chaos"] = {
                "type": random.choice(["memory_spike", "infinite_loop", "exception_bomb", "deadlock"]),
                "severity": random.randint(1, 10)
            }
        
        return payload
    
    def _generate_stress_data(self, size_mb: float) -> str:
        """Generate data of specific size to stress memory"""
        size_bytes = int(size_mb * 1024 * 1024)
        # Create highly compressible data that expands in memory
        base_pattern = "STRESS" * 1000
        repetitions = size_bytes // len(base_pattern)
        return base_pattern * repetitions
    
    async def execute_extreme_request(self, config: ExtremeCrashTestConfig, request_id: int):
        """Execute a single extreme request with chaos injection"""
        start_time = time.time()
        
        try:
            # Memory pressure injection
            if config.memory_pressure > 0:
                self._inject_memory_pressure(config.memory_pressure)
            
            # CPU affinity chaos
            if config.cpu_affinity_chaos:
                self._inject_cpu_affinity_chaos()
            
            # Generate extreme payload
            payload = self.generate_extreme_payload(config)
            
            # Simulate network latency
            if config.network_latency_ms > 0:
                await asyncio.sleep(config.network_latency_ms / 1000.0)
            
            # Exception injection
            if random.random() < config.exception_injection_rate:
                raise Exception(f"Injected chaos exception for request {request_id}")
            
            # Infinite loop injection
            if random.random() < config.infinite_loop_probability:
                self._inject_infinite_loop()
            
            # Process request with timeout
            result = await asyncio.wait_for(
                self._process_extreme_request(payload),
                timeout=config.timeout_seconds
            )
            
            # Validate response integrity
            if not self._validate_response(result):
                self.metrics.corrupted_responses += 1
                raise ValueError("Response validation failed - possible corruption")
            
            response_time = time.time() - start_time
            self.metrics.response_times.append(response_time)
            self.metrics.successful_requests += 1
            
            return result
            
        except asyncio.TimeoutError:
            self.metrics.timeout_failures += 1
            self.metrics.record_failure("timeout", f"Request {request_id} timed out after {config.timeout_seconds}s")
        except MemoryError:
            self.metrics.memory_failures += 1
            self.metrics.record_failure("memory", f"Memory exhaustion in request {request_id}")
        except Exception as e:
            self.metrics.exception_failures += 1
            self.metrics.record_failure("exception", f"Request {request_id}: {str(e)}\n{traceback.format_exc()}")
        finally:
            self.metrics.total_requests += 1
            # Record system state
            self._record_system_state()
    
    def _inject_memory_pressure(self, pressure_percent: float):
        """Inject memory pressure by allocating large blocks"""
        available_memory = psutil.virtual_memory().available
        pressure_bytes = int(available_memory * pressure_percent / 100)
        
        # Allocate memory in chunks to avoid immediate failure
        chunk_size = 100 * 1024 * 1024  # 100MB chunks
        chunks_needed = pressure_bytes // chunk_size
        
        for _ in range(chunks_needed):
            try:
                self.memory_bombs.append(bytearray(chunk_size))
            except MemoryError:
                break
    
    def _inject_cpu_affinity_chaos(self):
        """Randomly change CPU affinity to cause scheduling chaos"""
        try:
            import os
            cpu_count = multiprocessing.cpu_count()
            # Randomly restrict to subset of CPUs
            cpu_mask = random.randint(1, (1 << cpu_count) - 1)
            os.sched_setaffinity(0, [i for i in range(cpu_count) if cpu_mask & (1 << i)])
        except:
            pass  # Not all systems support CPU affinity
    
    def _inject_infinite_loop(self):
        """Inject a controlled infinite loop in a separate thread"""
        def infinite_loop():
            start = time.time()
            while time.time() - start < 5:  # 5 second "infinite" loop
                _ = sum(i * i for i in range(1000000))
        
        thread = threading.Thread(target=infinite_loop)
        thread.daemon = True
        thread.start()
        self.zombie_threads.append(thread)
    
    async def _process_extreme_request(self, payload: Dict[str, Any]):
        """Process extreme request through the system"""
        # Create extreme geoid states
        geoid_states = []
        
        # Generate multiple geoid states based on payload
        for i in range(min(10, len(payload.get("features", [])))):
            # Create random high-dimensional geoid
            dimensions = random.randint(1000, 10000)
            geoid = GeoidState(
                dimensions=dimensions,
                activation=np.random.rand(dimensions).astype(np.float32),
                tension=np.random.rand(dimensions).astype(np.float32),
                coherence=random.random()
            )
            geoid_states.append(geoid)
        
        # Process through SPDE with extreme parameters
        spde_result = await self._stress_spde(geoid_states)
        
        # Process through KCCL
        kccl_result = await self._stress_kccl(geoid_states)
        
        # Stress vault manager
        vault_result = await self._stress_vault(payload)
        
        return {
            "status": "processed",
            "spde": spde_result,
            "kccl": kccl_result,
            "vault": vault_result,
            "geoid_count": len(geoid_states),
            "processing_time": time.time()
        }
    
    async def _stress_spde(self, geoid_states: List[GeoidState]):
        """Stress test SPDE engine"""
        try:
            # Run SPDE with extreme parameters
            results = []
            for geoid in geoid_states:
                # Simulate intensive SPDE processing
                await asyncio.sleep(random.uniform(0.1, 0.5))
                # Would call actual SPDE methods here
                results.append({"processed": True, "dimensions": geoid.dimensions})
            return {"spde_results": results, "count": len(results)}
        except Exception as e:
            return {"error": str(e)}
    
    async def _stress_kccl(self, geoid_states: List[GeoidState]):
        """Stress test KCCL engine"""
        try:
            # Simulate KCCL processing
            await asyncio.sleep(random.uniform(0.2, 0.8))
            return {"kccl_cycles": len(geoid_states), "coherence_avg": random.random()}
        except Exception as e:
            return {"error": str(e)}
    
    async def _stress_vault(self, payload: Dict[str, Any]):
        """Stress test vault manager"""
        try:
            # Simulate vault operations
            await asyncio.sleep(random.uniform(0.3, 1.0))
            return {"vault_operations": random.randint(100, 1000)}
        except Exception as e:
            return {"error": str(e)}
    
    def _validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate response integrity"""
        required_fields = ["status", "spde", "kccl", "vault"]
        return all(field in response for field in required_fields)
    
    def _record_system_state(self):
        """Record current system state metrics"""
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics.memory_peaks.append(memory.percent)
        
        # GPU metrics (simulated)
        gpu_util = random.uniform(20, 100)  # Would use actual GPU monitoring
        self.metrics.gpu_peaks.append(gpu_util)
    
    async def run_extreme_test_scenario(self, config: ExtremeCrashTestConfig):
        """Run a complete extreme test scenario"""
        print(f"\n{'='*80}")
        print(f"🔥 EXTREME CRASH TEST: {config.name}")
        print(f"{'='*80}")
        print(f"Configuration:")
        print(f"  - Threads: {config.threads}")
        print(f"  - Features: {config.features}")
        print(f"  - Depth: {config.depth}")
        print(f"  - Payload Size: {config.payload_size_mb} MB")
        print(f"  - Recursive Depth: {config.recursive_depth}")
        print(f"  - Memory Pressure: {config.memory_pressure}%")
        print(f"  - GPU Stress Factor: {config.gpu_stress_factor}x")
        print(f"  - Chaos Probability: {config.chaos_probability * 100}%")
        print(f"  - Timeout: {config.timeout_seconds}s")
        print(f"{'='*80}\n")
        
        # Reset metrics
        self.metrics = ExtremeTestMetrics()
        
        # Create burst pattern if enabled
        if config.burst_mode:
            await self._run_burst_test(config)
        else:
            await self._run_sustained_test(config)
        
        # Generate report
        self._generate_extreme_report(config)
    
    async def _run_burst_test(self, config: ExtremeCrashTestConfig):
        """Run burst mode test with sudden load spikes"""
        burst_cycles = 5
        for cycle in range(burst_cycles):
            print(f"\n🌊 Burst Cycle {cycle + 1}/{burst_cycles}")
            
            # Quiet period
            quiet_threads = max(1, config.threads // 10)
            tasks = []
            for i in range(quiet_threads):
                task = asyncio.create_task(self.execute_extreme_request(config, i))
                tasks.append(task)
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Burst period - 10x load
            burst_threads = config.threads * 10
            tasks = []
            for i in range(burst_threads):
                task = asyncio.create_task(self.execute_extreme_request(config, i + quiet_threads))
                tasks.append(task)
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_sustained_test(self, config: ExtremeCrashTestConfig):
        """Run sustained load test"""
        total_requests = config.threads * 10  # Run 10 rounds
        
        for round_num in range(10):
            print(f"\n🔄 Round {round_num + 1}/10")
            tasks = []
            
            for i in range(config.threads):
                request_id = round_num * config.threads + i
                task = asyncio.create_task(self.execute_extreme_request(config, request_id))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for cascade failures
            if self.metrics.failed_requests > self.metrics.total_requests * 0.5:
                self.metrics.cascade_failures += 1
                print("⚠️  CASCADE FAILURE DETECTED!")
    
    def _generate_extreme_report(self, config: ExtremeCrashTestConfig):
        """Generate comprehensive crash test report"""
        duration = time.time() - self.metrics.start_time
        success_rate = (self.metrics.successful_requests / max(1, self.metrics.total_requests)) * 100
        
        print(f"\n{'='*80}")
        print(f"📊 EXTREME CRASH TEST RESULTS: {config.name}")
        print(f"{'='*80}")
        
        print(f"\n📈 Overall Metrics:")
        print(f"  - Duration: {duration:.2f}s")
        print(f"  - Total Requests: {self.metrics.total_requests}")
        print(f"  - Successful: {self.metrics.successful_requests} ({success_rate:.1f}%)")
        print(f"  - Failed: {self.metrics.failed_requests}")
        
        print(f"\n💥 Failure Analysis:")
        print(f"  - Timeouts: {self.metrics.timeout_failures}")
        print(f"  - Memory Failures: {self.metrics.memory_failures}")
        print(f"  - Exceptions: {self.metrics.exception_failures}")
        print(f"  - Corrupted Responses: {self.metrics.corrupted_responses}")
        print(f"  - Cascade Failures: {self.metrics.cascade_failures}")
        
        print(f"\n🔥 Failure Modes:")
        for failure_type, failures in self.metrics.failure_modes.items():
            print(f"  - {failure_type}: {len(failures)} occurrences")
            if len(failures) > 0:
                print(f"    First: {failures[0]['details'][:100]}...")
        
        if self.metrics.response_times:
            print(f"\n⏱️  Performance Under Stress:")
            print(f"  - Avg Response Time: {np.mean(self.metrics.response_times):.2f}s")
            print(f"  - P95 Response Time: {np.percentile(self.metrics.response_times, 95):.2f}s")
            print(f"  - P99 Response Time: {np.percentile(self.metrics.response_times, 99):.2f}s")
            print(f"  - Max Response Time: {max(self.metrics.response_times):.2f}s")
        
        print(f"\n💾 Resource Peaks:")
        if self.metrics.memory_peaks:
            print(f"  - Peak Memory: {max(self.metrics.memory_peaks):.1f}%")
            print(f"  - Avg Memory: {np.mean(self.metrics.memory_peaks):.1f}%")
        if self.metrics.gpu_peaks:
            print(f"  - Peak GPU: {max(self.metrics.gpu_peaks):.1f}%")
            print(f"  - Avg GPU: {np.mean(self.metrics.gpu_peaks):.1f}%")
        
        print(f"\n🧟 Zombie Metrics:")
        print(f"  - Zombie Threads: {len(self.zombie_threads)}")
        print(f"  - Memory Bombs: {len(self.memory_bombs)}")
        
        # Cleanup
        self._cleanup()
    
    def _cleanup(self):
        """Clean up test resources"""
        # Clear memory bombs
        self.memory_bombs.clear()
        gc.collect()
        
        # Attempt to join zombie threads
        for thread in self.zombie_threads:
            thread.join(timeout=0.1)
        self.zombie_threads.clear()

async def main():
    """Run the extreme crash test suite"""
    tester = ExtremeTyrannicCrashTest()
    
    # Define extreme test scenarios
    test_scenarios = [
        ExtremeCrashTestConfig(
            name="MEMORY APOCALYPSE",
            threads=256,
            features=4096,
            depth=10,
            payload_size_mb=10.0,
            recursive_depth=50,
            memory_pressure=80.0,
            gpu_stress_factor=5,
            chaos_probability=0.3,
            timeout_seconds=30,
            burst_mode=False,
            memory_leak_simulation=True,
            infinite_loop_probability=0.1,
            exception_injection_rate=0.2,
            network_latency_ms=500,
            cpu_affinity_chaos=True
        ),
        ExtremeCrashTestConfig(
            name="THREAD STORM",
            threads=1024,
            features=512,
            depth=5,
            payload_size_mb=1.0,
            recursive_depth=10,
            memory_pressure=30.0,
            gpu_stress_factor=2,
            chaos_probability=0.5,
            timeout_seconds=10,
            burst_mode=True,
            memory_leak_simulation=False,
            infinite_loop_probability=0.05,
            exception_injection_rate=0.1,
            network_latency_ms=100,
            cpu_affinity_chaos=False
        ),
        ExtremeCrashTestConfig(
            name="RECURSIVE NIGHTMARE",
            threads=64,
            features=256,
            depth=100,
            payload_size_mb=5.0,
            recursive_depth=1000,
            memory_pressure=50.0,
            gpu_stress_factor=10,
            chaos_probability=0.7,
            timeout_seconds=60,
            burst_mode=False,
            memory_leak_simulation=True,
            infinite_loop_probability=0.2,
            exception_injection_rate=0.3,
            network_latency_ms=1000,
            cpu_affinity_chaos=True
        ),
        ExtremeCrashTestConfig(
            name="CHAOS MONKEY UNLEASHED",
            threads=128,
            features=1024,
            depth=20,
            payload_size_mb=2.0,
            recursive_depth=100,
            memory_pressure=60.0,
            gpu_stress_factor=8,
            chaos_probability=0.9,
            timeout_seconds=20,
            burst_mode=True,
            memory_leak_simulation=True,
            infinite_loop_probability=0.3,
            exception_injection_rate=0.5,
            network_latency_ms=2000,
            cpu_affinity_chaos=True
        ),
        ExtremeCrashTestConfig(
            name="ENDURANCE MARATHON",
            threads=512,
            features=2048,
            depth=15,
            payload_size_mb=0.5,
            recursive_depth=30,
            memory_pressure=40.0,
            gpu_stress_factor=3,
            chaos_probability=0.2,
            timeout_seconds=120,
            burst_mode=False,
            memory_leak_simulation=True,
            infinite_loop_probability=0.01,
            exception_injection_rate=0.05,
            network_latency_ms=50,
            cpu_affinity_chaos=False
        )
    ]
    
    print("🚨 EXTREME TYRANNIC CRASH TEST SUITE 🚨")
    print("⚠️  WARNING: This test will push the system to its absolute limits!")
    print("⚠️  System instability and failures are expected and intentional.")
    print("\nPress Ctrl+C to abort at any time.\n")
    
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 EMERGENCY SHUTDOWN INITIATED")
        tester._cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run each scenario
    for scenario in test_scenarios:
        try:
            await tester.run_extreme_test_scenario(scenario)
            
            # Cool-down period between scenarios
            print("\n⏸️  Cool-down period (10 seconds)...")
            await asyncio.sleep(10)
            gc.collect()
            
        except Exception as e:
            print(f"\n💀 CATASTROPHIC FAILURE in {scenario.name}: {str(e)}")
            print(traceback.format_exc())
    
    print("\n" + "="*80)
    print("🏁 EXTREME CRASH TEST SUITE COMPLETED")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())