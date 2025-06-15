#!/usr/bin/env python3
"""
Safe Boundary Crash Test for Kimera SWM
Tests system limits with built-in safety mechanisms to prevent hardware damage
"""

import asyncio
import json
import logging
import os
import psutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import signal
import sys

try:
    import torch
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    from fastapi.testclient import TestClient
    from backend.api.main import app
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("safe_boundary_test")

class SafetyMonitor:
    """Monitors system resources and enforces safety limits"""
    
    def __init__(self):
        self.max_gpu_temp = 85.0  # °C - Safe threshold for RTX 4090
        self.max_gpu_memory = 0.90  # 90% of GPU memory
        self.max_cpu_temp = 80.0  # °C
        self.max_system_memory = 0.85  # 85% of system memory
        self.max_cpu_usage = 90.0  # 90% CPU usage
        self.emergency_stop = False
        self.monitoring = False
        self.stats = {
            "max_gpu_temp": 0.0,
            "max_gpu_memory": 0.0,
            "max_cpu_usage": 0.0,
            "max_system_memory": 0.0,
            "safety_violations": 0,
            "emergency_stops": 0
        }
    
    def start_monitoring(self):
        """Start safety monitoring in background thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        log.info("🛡️ Safety monitoring started")
    
    def stop_monitoring(self):
        """Stop safety monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2.0)
        log.info("🛡️ Safety monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_safety_limits()
                time.sleep(1.0)  # Check every second
            except Exception as e:
                log.error(f"Safety monitoring error: {e}")
    
    def _check_safety_limits(self):
        """Check all safety limits and trigger emergency stop if needed"""
        violations = []
        
        # Check GPU temperature and memory
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Primary GPU
                    temp = gpu.temperature
                    memory_util = gpu.memoryUtil
                    
                    self.stats["max_gpu_temp"] = max(self.stats["max_gpu_temp"], temp)
                    self.stats["max_gpu_memory"] = max(self.stats["max_gpu_memory"], memory_util)
                    
                    if temp > self.max_gpu_temp:
                        violations.append(f"GPU temperature: {temp}°C > {self.max_gpu_temp}°C")
                    
                    if memory_util > self.max_gpu_memory:
                        violations.append(f"GPU memory: {memory_util:.1%} > {self.max_gpu_memory:.1%}")
            except Exception as e:
                log.warning(f"GPU monitoring error: {e}")
        
        # Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=0.1)
        self.stats["max_cpu_usage"] = max(self.stats["max_cpu_usage"], cpu_usage)
        if cpu_usage > self.max_cpu_usage:
            violations.append(f"CPU usage: {cpu_usage:.1f}% > {self.max_cpu_usage}%")
        
        # Check system memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent / 100.0
        self.stats["max_system_memory"] = max(self.stats["max_system_memory"], memory_percent)
        if memory_percent > self.max_system_memory:
            violations.append(f"System memory: {memory_percent:.1%} > {self.max_system_memory:.1%}")
        
        # Check CPU temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current and entry.current > self.max_cpu_temp:
                            violations.append(f"CPU temperature: {entry.current}°C > {self.max_cpu_temp}°C")
        except (AttributeError, OSError):
            pass  # Temperature sensors not available on Windows
        
        # Trigger emergency stop if violations detected
        if violations:
            self.stats["safety_violations"] += len(violations)
            log.warning(f"⚠️ Safety violations detected: {'; '.join(violations)}")
            
            # Emergency stop on critical violations
            critical_violations = [v for v in violations if "temperature" in v.lower()]
            if critical_violations:
                self.emergency_stop = True
                self.stats["emergency_stops"] += 1
                log.error(f"🚨 EMERGENCY STOP triggered: {'; '.join(critical_violations)}")
    
    def is_safe_to_continue(self) -> bool:
        """Check if it's safe to continue testing"""
        return not self.emergency_stop
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        stats = self.stats.copy()
        
        # Add current readings
        stats["current_cpu_usage"] = psutil.cpu_percent()
        stats["current_memory_usage"] = psutil.virtual_memory().percent / 100.0
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    stats["current_gpu_temp"] = gpu.temperature
                    stats["current_gpu_memory"] = gpu.memoryUtil
                    stats["gpu_name"] = gpu.name
            except:
                pass
        
        return stats


class SafeBoundaryTester:
    """Safe boundary testing with progressive load increase"""
    
    def __init__(self):
        self.safety_monitor = SafetyMonitor()
        self.client = TestClient(app) if API_AVAILABLE else None
        self.results = {
            "test_start": datetime.now().isoformat(),
            "phases": [],
            "safety_stats": {},
            "final_status": "unknown"
        }
        self.test_running = False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            log.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.test_running = False
            self.safety_monitor.emergency_stop = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def generate_test_payload(self, complexity: int, feature_count: int) -> Dict[str, Any]:
        """Generate test payload with specified complexity"""
        # Create semantic features
        semantic_features = {}
        for i in range(feature_count):
            semantic_features[f"feature_{i}"] = float(i % 100) / 100.0
        
        # Create nested symbolic content based on complexity
        symbolic_content = {"type": "test_geoid", "complexity": complexity}
        for level in range(complexity):
            symbolic_content[f"level_{level}"] = {
                f"data_{j}": f"complex_value_{level}_{j}" 
                for j in range(min(10, complexity))
            }
        
        return {
            "semantic_features": semantic_features,
            "symbolic_content": symbolic_content,
            "metadata": {
                "test_id": str(uuid.uuid4()),
                "complexity": complexity,
                "feature_count": feature_count,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def run_test_batch(self, thread_count: int, requests_per_thread: int, 
                      complexity: int, feature_count: int) -> Dict[str, Any]:
        """Run a batch of tests with specified parameters"""
        if not self.client:
            return {"error": "API client not available"}
        
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        response_times = []
        errors = []
        
        def make_request():
            try:
                payload = self.generate_test_payload(complexity, feature_count)
                request_start = time.time()
                response = self.client.post("/geoids", json=payload)
                request_time = time.time() - request_start
                
                if response.status_code == 200:
                    return {"success": True, "time": request_time}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}", "time": request_time}
            except Exception as e:
                return {"success": False, "error": str(e), "time": 0}
        
        # Execute requests in parallel
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for thread_id in range(thread_count):
                for req_id in range(requests_per_thread):
                    if not self.safety_monitor.is_safe_to_continue() or not self.test_running:
                        break
                    futures.append(executor.submit(make_request))
                
                if not self.safety_monitor.is_safe_to_continue() or not self.test_running:
                    break
            
            # Collect results
            for future in as_completed(futures):
                if not self.safety_monitor.is_safe_to_continue() or not self.test_running:
                    break
                
                try:
                    result = future.result(timeout=30.0)
                    if result["success"]:
                        successful_requests += 1
                        response_times.append(result["time"])
                    else:
                        failed_requests += 1
                        errors.append(result["error"])
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        return {
            "thread_count": thread_count,
            "requests_per_thread": requests_per_thread,
            "complexity": complexity,
            "feature_count": feature_count,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / max(total_requests, 1),
            "total_time": total_time,
            "avg_response_time": sum(response_times) / max(len(response_times), 1),
            "throughput": successful_requests / max(total_time, 0.001),
            "errors": errors[:10],  # Keep only first 10 errors
            "safety_stats": self.safety_monitor.get_current_stats()
        }
    
    def run_progressive_test(self):
        """Run progressive boundary test with safety monitoring"""
        log.info("🚀 Starting Safe Boundary Test for Kimera SWM")
        
        if not self.client:
            log.error("❌ API client not available - cannot run test")
            return
        
        self.setup_signal_handlers()
        self.safety_monitor.start_monitoring()
        self.test_running = True
        
        # Progressive test phases - conservative start, gradual increase
        test_phases = [
            {"threads": 2, "requests": 10, "complexity": 2, "features": 32},
            {"threads": 4, "requests": 15, "complexity": 3, "features": 64},
            {"threads": 6, "requests": 20, "complexity": 4, "features": 96},
            {"threads": 8, "requests": 25, "complexity": 5, "features": 128},
            {"threads": 12, "requests": 30, "complexity": 6, "features": 192},
            {"threads": 16, "requests": 35, "complexity": 7, "features": 256},
            {"threads": 20, "requests": 40, "complexity": 8, "features": 320},
            {"threads": 24, "requests": 45, "complexity": 9, "features": 384},
            {"threads": 28, "requests": 50, "complexity": 10, "features": 448},
            {"threads": 32, "requests": 55, "complexity": 11, "features": 512},
        ]
        
        try:
            for phase_num, phase in enumerate(test_phases, 1):
                if not self.safety_monitor.is_safe_to_continue() or not self.test_running:
                    log.warning("🛑 Test stopped due to safety concerns or user interrupt")
                    break
                
                log.info(f"🔥 Phase {phase_num}: {phase['threads']} threads, "
                        f"{phase['requests']} req/thread, complexity {phase['complexity']}, "
                        f"{phase['features']} features")
                
                # Run the test phase
                phase_result = self.run_test_batch(
                    phase["threads"], phase["requests"], 
                    phase["complexity"], phase["features"]
                )
                
                self.results["phases"].append({
                    "phase": phase_num,
                    "config": phase,
                    "results": phase_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Log phase results
                success_rate = phase_result["success_rate"] * 100
                throughput = phase_result["throughput"]
                avg_time = phase_result["avg_response_time"] * 1000  # ms
                
                log.info(f"   Phase {phase_num} Results: {success_rate:.1f}% success, "
                        f"{throughput:.1f} ops/s, {avg_time:.1f}ms avg response")
                
                # Check if performance is degrading significantly
                if success_rate < 80.0:
                    log.warning(f"⚠️ Success rate dropped to {success_rate:.1f}% - approaching limits")
                
                if success_rate < 50.0:
                    log.error("🛑 Success rate below 50% - stopping test for safety")
                    break
                
                # Brief cooldown between phases
                if self.test_running:
                    time.sleep(2.0)
        
        except Exception as e:
            log.error(f"Test execution error: {e}")
            self.results["final_status"] = f"error: {e}"
        
        finally:
            self.test_running = False
            self.safety_monitor.stop_monitoring()
            self.results["safety_stats"] = self.safety_monitor.get_current_stats()
            self.results["test_end"] = datetime.now().isoformat()
            
            # Determine final status
            if self.safety_monitor.emergency_stop:
                self.results["final_status"] = "emergency_stop"
            elif len(self.results["phases"]) == len(test_phases):
                self.results["final_status"] = "completed"
            else:
                self.results["final_status"] = "partial_completion"
            
            self.save_results()
            self.print_summary()
    
    def save_results(self):
        """Save test results to file"""
        timestamp = int(time.time())
        filename = f"safe_boundary_test_results_{timestamp}.json"
        filepath = Path("test_results") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        log.info(f"📊 Results saved to {filepath}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 SAFE BOUNDARY TEST SUMMARY")
        print("="*80)
        
        total_phases = len(self.results["phases"])
        if total_phases == 0:
            print("❌ No phases completed")
            return
        
        # Overall statistics
        total_requests = sum(p["results"]["total_requests"] for p in self.results["phases"])
        total_successful = sum(p["results"]["successful_requests"] for p in self.results["phases"])
        overall_success_rate = (total_successful / max(total_requests, 1)) * 100
        
        print(f"📈 Phases Completed: {total_phases}")
        print(f"📊 Total Requests: {total_requests}")
        print(f"✅ Successful Requests: {total_successful}")
        print(f"📉 Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"🏁 Final Status: {self.results['final_status']}")
        
        # Peak performance
        if self.results["phases"]:
            peak_phase = max(self.results["phases"], key=lambda p: p["results"]["throughput"])
            peak_throughput = peak_phase["results"]["throughput"]
            peak_phase_num = peak_phase["phase"]
            
            print(f"🚀 Peak Throughput: {peak_throughput:.1f} ops/s (Phase {peak_phase_num})")
        
        # Safety statistics
        safety_stats = self.results["safety_stats"]
        print(f"\n🛡️ SAFETY STATISTICS:")
        print(f"   Max GPU Temperature: {safety_stats.get('max_gpu_temp', 'N/A')}°C")
        print(f"   Max GPU Memory: {safety_stats.get('max_gpu_memory', 0)*100:.1f}%")
        print(f"   Max CPU Usage: {safety_stats.get('max_cpu_usage', 0):.1f}%")
        print(f"   Max System Memory: {safety_stats.get('max_system_memory', 0)*100:.1f}%")
        print(f"   Safety Violations: {safety_stats.get('safety_violations', 0)}")
        print(f"   Emergency Stops: {safety_stats.get('emergency_stops', 0)}")
        
        print("\n" + "="*80)
        print("🎉 Safe boundary testing completed!")
        print("="*80)


def main():
    """Main entry point"""
    if not API_AVAILABLE:
        print("❌ FastAPI test client not available. Please install required dependencies.")
        return
    
    tester = SafeBoundaryTester()
    tester.run_progressive_test()


if __name__ == "__main__":
    main()