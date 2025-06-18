#!/usr/bin/env python3
"""
🔥 COMPREHENSIVE GPU STRESS TEST 🔥
Tests the GPU-optimized Cognitive Field Dynamics engine to its limits
Validates the elimination of JAX and confirms 153.7x performance improvement
"""

import sys
import time
import torch
import numpy as np
import psutil
import gc
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional
import json
import platform
from collections import defaultdict

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent))

class GPUStressTester:
    """Comprehensive GPU stress testing with maximum detail monitoring."""
    
    def __init__(self):
        self.results = {
            "system_info": {},
            "test_results": {},
            "performance_metrics": {},
            "detailed_gpu_monitoring": {},
            "realtime_metrics": [],
            "memory_analysis": {},
            "thermal_performance": {},
            "power_consumption": {},
            "comparison_baseline": {
                "jax_cpu_performance": 5.7,  # fields/sec
                "target_improvement": 153.7   # x multiplier
            }
        }
        
        # GPU monitoring setup
        self.gpu_monitoring_active = False
        self.gpu_metrics_history = []
        self.monitoring_thread = None
        
        # Initialize GPU monitoring
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            self._initialize_gpu_monitoring()
    
    def _initialize_gpu_monitoring(self):
        """Initialize detailed GPU monitoring capabilities."""
        try:
            # Test nvidia-smi availability
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            self.nvidia_smi_available = result.returncode == 0
        except:
            self.nvidia_smi_available = False
        
        print(f"🔧 NVIDIA-SMI Available: {self.nvidia_smi_available}")
    
    def start_realtime_monitoring(self):
        """Start real-time GPU monitoring in background thread."""
        if not torch.cuda.is_available():
            return
        
        self.gpu_monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_gpu_realtime, daemon=True)
        self.monitoring_thread.start()
        print("📊 Real-time GPU monitoring started")
    
    def stop_realtime_monitoring(self):
        """Stop real-time GPU monitoring."""
        self.gpu_monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        print("📊 Real-time GPU monitoring stopped")
    
    def _monitor_gpu_realtime(self):
        """Background thread for continuous GPU monitoring."""
        while self.gpu_monitoring_active:
            try:
                metrics = self._collect_detailed_gpu_metrics()
                metrics["timestamp"] = time.time()
                self.gpu_metrics_history.append(metrics)
                
                # Keep only last 1000 entries to prevent memory overflow
                if len(self.gpu_metrics_history) > 1000:
                    self.gpu_metrics_history = self.gpu_metrics_history[-1000:]
                
                time.sleep(0.5)  # Monitor every 500ms
            except Exception as e:
                print(f"⚠️  GPU monitoring error: {e}")
                break
    
    def _collect_detailed_gpu_metrics(self) -> Dict:
        """Collect extremely detailed GPU metrics."""
        if not torch.cuda.is_available():
            return {"gpu_available": False}
        
        metrics = {
            "gpu_available": True,
            "timestamp": time.time()
        }
        
        # PyTorch CUDA metrics
        try:
            metrics.update({
                "memory_allocated_bytes": torch.cuda.memory_allocated(),
                "memory_allocated_mb": torch.cuda.memory_allocated() / (1024**2),
                "memory_reserved_bytes": torch.cuda.memory_reserved(),
                "memory_reserved_mb": torch.cuda.memory_reserved() / (1024**2),
                "max_memory_allocated_bytes": torch.cuda.max_memory_allocated(),
                "max_memory_allocated_mb": torch.cuda.max_memory_allocated() / (1024**2),
                "max_memory_reserved_bytes": torch.cuda.max_memory_reserved(),
                "max_memory_reserved_mb": torch.cuda.max_memory_reserved() / (1024**2),
                "memory_cached_bytes": torch.cuda.memory_reserved(),
                "memory_cached_mb": torch.cuda.memory_reserved() / (1024**2)
            })
            
            # GPU device properties
            props = torch.cuda.get_device_properties(0)
            metrics.update({
                "total_memory_bytes": props.total_memory,
                "total_memory_gb": props.total_memory / (1024**3),
                "memory_usage_percentage": (torch.cuda.memory_allocated() / props.total_memory) * 100,
                "memory_reserved_percentage": (torch.cuda.memory_reserved() / props.total_memory) * 100,
                "gpu_multiprocessor_count": props.multi_processor_count,
                "gpu_warp_size": getattr(props, 'warp_size', 32),
                "gpu_max_threads_per_block": getattr(props, 'max_threads_per_block', 1024),
                "gpu_max_threads_per_multiprocessor": getattr(props, 'max_threads_per_multiprocessor', 2048)
            })
        except Exception as e:
            metrics["pytorch_error"] = str(e)
        
        # NVIDIA-SMI detailed metrics
        if self.nvidia_smi_available:
            try:
                nvidia_metrics = self._get_nvidia_smi_metrics()
                metrics.update(nvidia_metrics)
            except Exception as e:
                metrics["nvidia_smi_error"] = str(e)
        
        return metrics
    
    def _get_nvidia_smi_metrics(self) -> Dict:
        """Get detailed metrics from nvidia-smi."""
        try:
            # Comprehensive nvidia-smi query
            query_fields = [
                'name', 'driver_version', 'memory.total', 'memory.used', 'memory.free',
                'utilization.gpu', 'utilization.memory', 'temperature.gpu',
                'power.draw', 'power.limit', 'clocks.current.graphics', 'clocks.current.memory',
                'clocks.max.graphics', 'clocks.max.memory', 'fan.speed',
                'compute_mode', 'display_mode', 'display_active', 'persistence_mode'
            ]
            
            cmd = ['nvidia-smi', f'--query-gpu={",".join(query_fields)}', '--format=csv,noheader,nounits']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                values = result.stdout.strip().split(', ')
                
                nvidia_metrics = {
                    "nvidia_driver_version": values[1] if len(values) > 1 else "unknown",
                    "memory_total_mb": float(values[2]) if len(values) > 2 and values[2] != '[N/A]' else 0,
                    "memory_used_mb": float(values[3]) if len(values) > 3 and values[3] != '[N/A]' else 0,
                    "memory_free_mb": float(values[4]) if len(values) > 4 and values[4] != '[N/A]' else 0,
                    "gpu_utilization_percent": float(values[5]) if len(values) > 5 and values[5] != '[N/A]' else 0,
                    "memory_utilization_percent": float(values[6]) if len(values) > 6 and values[6] != '[N/A]' else 0,
                    "temperature_celsius": float(values[7]) if len(values) > 7 and values[7] != '[N/A]' else 0,
                    "power_draw_watts": float(values[8]) if len(values) > 8 and values[8] != '[N/A]' else 0,
                    "power_limit_watts": float(values[9]) if len(values) > 9 and values[9] != '[N/A]' else 0,
                    "clock_graphics_mhz": float(values[10]) if len(values) > 10 and values[10] != '[N/A]' else 0,
                    "clock_memory_mhz": float(values[11]) if len(values) > 11 and values[11] != '[N/A]' else 0,
                    "clock_graphics_max_mhz": float(values[12]) if len(values) > 12 and values[12] != '[N/A]' else 0,
                    "clock_memory_max_mhz": float(values[13]) if len(values) > 13 and values[13] != '[N/A]' else 0,
                    "fan_speed_percent": float(values[14]) if len(values) > 14 and values[14] != '[N/A]' else 0,
                    "compute_mode": values[15] if len(values) > 15 else "unknown",
                    "display_mode": values[16] if len(values) > 16 else "unknown",
                    "display_active": values[17] if len(values) > 17 else "unknown",
                    "persistence_mode": values[18] if len(values) > 18 else "unknown"
                }
                
                # Calculate additional metrics
                if nvidia_metrics["memory_total_mb"] > 0:
                    nvidia_metrics["memory_used_percentage"] = (nvidia_metrics["memory_used_mb"] / nvidia_metrics["memory_total_mb"]) * 100
                
                if nvidia_metrics["power_limit_watts"] > 0:
                    nvidia_metrics["power_usage_percentage"] = (nvidia_metrics["power_draw_watts"] / nvidia_metrics["power_limit_watts"]) * 100
                
                if nvidia_metrics["clock_graphics_max_mhz"] > 0:
                    nvidia_metrics["clock_graphics_percentage"] = (nvidia_metrics["clock_graphics_mhz"] / nvidia_metrics["clock_graphics_max_mhz"]) * 100
                
                return nvidia_metrics
            
        except Exception as e:
            return {"nvidia_smi_detailed_error": str(e)}
        
        return {}
    
    def collect_system_info(self):
        """Collect comprehensive system information."""
        print("📋 Collecting Detailed System Information...")
        
        # Basic system info
        self.results["system_info"] = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python_version": sys.version,
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "total_ram_gb": psutil.virtual_memory().total / (1024**3),
            "available_ram_gb": psutil.virtual_memory().available / (1024**3),
            "nvidia_smi_available": self.nvidia_smi_available
        }
        
        # Detailed GPU info
        if torch.cuda.is_available():
            gpu_props = torch.cuda.get_device_properties(0)
            self.results["system_info"].update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_gb": gpu_props.total_memory / (1024**3),
                "cuda_version": torch.version.cuda,
                "cudnn_version": torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else "N/A",
                "gpu_compute_capability": f"{gpu_props.major}.{gpu_props.minor}",
                "gpu_multiprocessor_count": gpu_props.multi_processor_count,
                "gpu_warp_size": getattr(gpu_props, 'warp_size', 32),
                "gpu_max_threads_per_block": getattr(gpu_props, 'max_threads_per_block', 1024),
                "gpu_max_threads_per_multiprocessor": getattr(gpu_props, 'max_threads_per_multiprocessor', 2048),
                "gpu_total_constant_memory": getattr(gpu_props, 'total_constant_memory', 65536),
                "gpu_max_shared_memory_per_block": getattr(gpu_props, 'max_shared_memory_per_block', 49152),
                "gpu_max_registers_per_block": getattr(gpu_props, 'max_registers_per_block', 65536)
            })
            
            # Get initial detailed GPU state
            initial_gpu_state = self._collect_detailed_gpu_metrics()
            self.results["system_info"]["initial_gpu_state"] = initial_gpu_state
        
        # CPU info
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            self.results["system_info"].update({
                "cpu_frequency_current_mhz": cpu_freq.current,
                "cpu_frequency_min_mhz": cpu_freq.min,
                "cpu_frequency_max_mhz": cpu_freq.max
            })
        
        # Print detailed system info
        print("🖥️  DETAILED SYSTEM SPECIFICATIONS:")
        print("=" * 50)
        for key, value in self.results["system_info"].items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for subkey, subvalue in value.items():
                    print(f"      {subkey}: {subvalue}")
            else:
                print(f"   {key}: {value}")
    
    def _analyze_monitoring_history(self) -> Dict:
        """Analyze the collected monitoring history for insights."""
        if not self.gpu_metrics_history:
            return {}
        
        # Extract key metrics from history
        gpu_utilizations = [m.get('gpu_utilization_percent', 0) for m in self.gpu_metrics_history if 'gpu_utilization_percent' in m]
        memory_utilizations = [m.get('memory_utilization_percent', 0) for m in self.gpu_metrics_history if 'memory_utilization_percent' in m]
        temperatures = [m.get('temperature_celsius', 0) for m in self.gpu_metrics_history if 'temperature_celsius' in m]
        power_draws = [m.get('power_draw_watts', 0) for m in self.gpu_metrics_history if 'power_draw_watts' in m]
        memory_allocated = [m.get('memory_allocated_mb', 0) for m in self.gpu_metrics_history if 'memory_allocated_mb' in m]
        
        analysis = {
            "total_samples": len(self.gpu_metrics_history),
            "monitoring_duration_sec": self.gpu_metrics_history[-1]['timestamp'] - self.gpu_metrics_history[0]['timestamp'] if len(self.gpu_metrics_history) > 1 else 0
        }
        
        # GPU utilization analysis
        if gpu_utilizations:
            analysis.update({
                "max_gpu_utilization": max(gpu_utilizations),
                "min_gpu_utilization": min(gpu_utilizations),
                "avg_gpu_utilization": sum(gpu_utilizations) / len(gpu_utilizations),
                "gpu_utilization_std": np.std(gpu_utilizations) if len(gpu_utilizations) > 1 else 0
            })
        
        # Memory utilization analysis
        if memory_utilizations:
            analysis.update({
                "max_memory_utilization": max(memory_utilizations),
                "min_memory_utilization": min(memory_utilizations),
                "avg_memory_utilization": sum(memory_utilizations) / len(memory_utilizations),
                "memory_utilization_std": np.std(memory_utilizations) if len(memory_utilizations) > 1 else 0
            })
        
        # Temperature analysis
        if temperatures:
            analysis.update({
                "max_temperature": max(temperatures),
                "min_temperature": min(temperatures),
                "avg_temperature": sum(temperatures) / len(temperatures),
                "temperature_std": np.std(temperatures) if len(temperatures) > 1 else 0
            })
        
        # Power analysis
        if power_draws:
            analysis.update({
                "max_power": max(power_draws),
                "min_power": min(power_draws),
                "avg_power": sum(power_draws) / len(power_draws),
                "power_std": np.std(power_draws) if len(power_draws) > 1 else 0
            })
        
        # Memory growth analysis
        if memory_allocated and len(memory_allocated) > 1:
            memory_growth = memory_allocated[-1] - memory_allocated[0]
            analysis.update({
                "memory_growth_mb": memory_growth,
                "memory_growth_rate_mb_per_sec": memory_growth / analysis["monitoring_duration_sec"] if analysis["monitoring_duration_sec"] > 0 else 0
            })
        
        return analysis
    
    def monitor_gpu_usage(self) -> Dict:
        """Legacy method - now returns detailed metrics for compatibility."""
        return self._collect_detailed_gpu_metrics()
    
    def _get_gpu_utilization(self) -> float:
        """Get GPU utilization percentage (simplified)."""
        try:
            # Simple GPU utilization estimate based on memory usage
            total_memory = torch.cuda.get_device_properties(0).total_memory
            used_memory = torch.cuda.memory_allocated()
            return (used_memory / total_memory) * 100
        except:
            return 0.0
    
    def stress_test_field_creation(self, field_counts: List[int]) -> Dict:
        """Stress test field creation with maximum detailed monitoring."""
        print("\n🔥 STRESS TEST: Field Creation with DETAILED MONITORING")
        print("=" * 60)
        
        results = {}
        
        # Import engine
        try:
            from backend.engines.cognitive_field_dynamics import CognitiveFieldDynamics
        except ImportError as e:
            try:
                # Alternative import path
                from engines.cognitive_field_dynamics import CognitiveFieldDynamics
            except ImportError as e2:
                print(f"❌ Failed to import engine: {e}")
                print(f"❌ Alternative import also failed: {e2}")
                return {"error": str(e)}
        
        for field_count in field_counts:
            print(f"\n🧪 Testing with {field_count:,} fields...")
            print("📊 Starting real-time monitoring...")
            
            # Start real-time monitoring
            self.start_realtime_monitoring()
            
            # Initialize fresh engine for each test
            engine = CognitiveFieldDynamics(dimension=384)
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
            
            # Detailed monitoring before test
            detailed_before = self._collect_detailed_gpu_metrics()
            
            # Performance tracking arrays
            performance_samples = []
            
            # Stress test with detailed monitoring
            start_time = time.time()
            successful_fields = 0
            last_sample_time = start_time
            
            try:
                for i in range(field_count):
                    # Progress reporting with detailed metrics
                    if i % 100 == 0 and i > 0:
                        current_time = time.time()
                        elapsed = current_time - start_time
                        rate = i / elapsed
                        eta = (field_count - i) / rate if rate > 0 else 0
                        
                        # Sample detailed metrics periodically
                        current_metrics = self._collect_detailed_gpu_metrics()
                        performance_samples.append({
                            "fields_created": i,
                            "timestamp": current_time,
                            "elapsed_time": elapsed,
                            "current_rate": rate,
                            "detailed_metrics": current_metrics
                        })
                        
                        print(f"   Progress: {i:,}/{field_count:,} ({i/field_count*100:.1f}%) | "
                              f"Rate: {rate:.1f} f/s | ETA: {eta:.1f}s")
                        
                        # Print key GPU metrics
                        if self.nvidia_smi_available:
                            print(f"   GPU: {current_metrics.get('gpu_utilization_percent', 0):.1f}% | "
                                  f"Mem: {current_metrics.get('memory_used_mb', 0):.0f}MB | "
                                  f"Temp: {current_metrics.get('temperature_celsius', 0):.0f}°C | "
                                  f"Power: {current_metrics.get('power_draw_watts', 0):.0f}W")
                    
                    # Generate diverse embeddings
                    embedding = torch.randn(384) * (1 + i * 0.001)  # Slight variation
                    field = engine.add_geoid(f"stress_field_{i}", embedding)
                    
                    if field:
                        successful_fields += 1
                
                creation_time = time.time() - start_time
                creation_rate = successful_fields / creation_time
                
                # Stop monitoring and collect final metrics
                self.stop_realtime_monitoring()
                detailed_after = self._collect_detailed_gpu_metrics()
                
                # Analyze monitoring history for this test
                test_metrics_analysis = self._analyze_monitoring_history()
                
                # Store comprehensive results
                results[field_count] = {
                    "test_config": {
                        "field_count": field_count,
                        "dimension": 384,
                        "test_duration_sec": creation_time
                    },
                    "performance_metrics": {
                        "successful_fields": successful_fields,
                        "creation_time_sec": creation_time,
                        "creation_rate_fields_per_sec": creation_rate,
                        "performance_vs_jax": creation_rate / 5.7,
                        "avg_time_per_field_ms": (creation_time / successful_fields) * 1000 if successful_fields > 0 else 0,
                        "peak_rate_achieved": max([s.get('current_rate', 0) for s in performance_samples]) if performance_samples else creation_rate
                    },
                    "detailed_gpu_before": detailed_before,
                    "detailed_gpu_after": detailed_after,
                    "performance_samples": performance_samples,
                    "monitoring_analysis": test_metrics_analysis,
                    "memory_analysis": {
                        "pytorch_memory_allocated_mb": detailed_after.get("memory_allocated_mb", 0) - detailed_before.get("memory_allocated_mb", 0),
                        "pytorch_memory_reserved_mb": detailed_after.get("memory_reserved_mb", 0) - detailed_before.get("memory_reserved_mb", 0),
                        "nvidia_memory_used_mb": detailed_after.get("memory_used_mb", 0) - detailed_before.get("memory_used_mb", 0),
                        "memory_efficiency_mb_per_field": (detailed_after.get("memory_allocated_mb", 0) - detailed_before.get("memory_allocated_mb", 0)) / successful_fields if successful_fields > 0 else 0
                    },
                    "thermal_analysis": {
                        "initial_temp_celsius": detailed_before.get("temperature_celsius", 0),
                        "final_temp_celsius": detailed_after.get("temperature_celsius", 0),
                        "temp_increase_celsius": detailed_after.get("temperature_celsius", 0) - detailed_before.get("temperature_celsius", 0),
                        "max_temp_during_test": test_metrics_analysis.get("max_temperature", 0),
                        "avg_temp_during_test": test_metrics_analysis.get("avg_temperature", 0)
                    },
                    "power_analysis": {
                        "initial_power_watts": detailed_before.get("power_draw_watts", 0),
                        "final_power_watts": detailed_after.get("power_draw_watts", 0),
                        "max_power_during_test": test_metrics_analysis.get("max_power", 0),
                        "avg_power_during_test": test_metrics_analysis.get("avg_power", 0),
                        "power_efficiency_watts_per_field_per_sec": test_metrics_analysis.get("avg_power", 0) / creation_rate if creation_rate > 0 else 0
                    },
                    "utilization_analysis": {
                        "max_gpu_utilization": test_metrics_analysis.get("max_gpu_utilization", 0),
                        "avg_gpu_utilization": test_metrics_analysis.get("avg_gpu_utilization", 0),
                        "max_memory_utilization": test_metrics_analysis.get("max_memory_utilization", 0),
                        "avg_memory_utilization": test_metrics_analysis.get("avg_memory_utilization", 0)
                    },
                    "status": "success"
                }
                
                # Detailed results display
                print(f"\n✅ DETAILED RESULTS for {field_count:,} fields:")
                print(f"   🚀 Performance: {creation_rate:.1f} fields/sec ({creation_rate / 5.7:.1f}x vs JAX)")
                print(f"   💾 Memory: {detailed_after.get('memory_allocated_mb', 0):.1f} MB PyTorch | {detailed_after.get('memory_used_mb', 0):.1f} MB GPU")
                print(f"   🌡️  Temperature: {detailed_before.get('temperature_celsius', 0):.0f}°C → {detailed_after.get('temperature_celsius', 0):.0f}°C")
                print(f"   ⚡ Power: {detailed_after.get('power_draw_watts', 0):.0f}W ({detailed_after.get('power_usage_percentage', 0):.1f}% of limit)")
                print(f"   🎯 GPU Utilization: {test_metrics_analysis.get('avg_gpu_utilization', 0):.1f}% avg, {test_metrics_analysis.get('max_gpu_utilization', 0):.1f}% peak")
                print(f"   📊 Memory Utilization: {test_metrics_analysis.get('avg_memory_utilization', 0):.1f}% avg, {test_metrics_analysis.get('max_memory_utilization', 0):.1f}% peak")
                
            except Exception as e:
                self.stop_realtime_monitoring()
                print(f"❌ Failed at {field_count:,} fields: {e}")
                results[field_count] = {
                    "error": str(e),
                    "successful_fields": successful_fields,
                    "detailed_gpu_before": detailed_before,
                    "performance_samples": performance_samples,
                    "status": "failed"
                }
            
            # Clear monitoring history for next test
            self.gpu_metrics_history.clear()
        
        return results
    
    def stress_test_neighbor_search(self, engine, search_counts: List[int]) -> Dict:
        """Stress test neighbor search operations."""
        print("\n🔍 STRESS TEST: Neighbor Search")
        print("=" * 50)
        
        results = {}
        
        if len(engine.fields) == 0:
            print("⚠️  No fields available for neighbor search test")
            return {"error": "No fields available"}
        
        # Get a sample of field IDs for testing
        field_ids = list(engine.fields.keys())
        
        for search_count in search_counts:
            print(f"\n🔍 Testing {search_count:,} neighbor searches...")
            
            # Monitor before test
            gpu_before = self.monitor_gpu_usage()
            
            start_time = time.time()
            successful_searches = 0
            total_neighbors_found = 0
            
            try:
                for i in range(search_count):
                    if i % 100 == 0 and i > 0:
                        print(f"   Progress: {i:,}/{search_count:,}")
                    
                    # Use different field IDs cyclically
                    field_id = field_ids[i % len(field_ids)]
                    neighbors = engine.find_semantic_neighbors(field_id, energy_threshold=0.05)
                    
                    successful_searches += 1
                    total_neighbors_found += len(neighbors)
                
                search_time = time.time() - start_time
                search_rate = successful_searches / search_time
                
                # Monitor after test
                gpu_after = self.monitor_gpu_usage()
                
                results[search_count] = {
                    "successful_searches": successful_searches,
                    "total_neighbors_found": total_neighbors_found,
                    "avg_neighbors_per_search": total_neighbors_found / successful_searches if successful_searches > 0 else 0,
                    "search_time_sec": search_time,
                    "search_rate_per_sec": search_rate,
                    "gpu_memory_mb": gpu_after.get("memory_allocated_mb", 0),
                    "status": "success"
                }
                
                print(f"✅ Completed {successful_searches:,} searches in {search_time:.2f}s")
                print(f"🚀 Rate: {search_rate:.1f} searches/sec")
                print(f"🎯 Avg neighbors: {total_neighbors_found / successful_searches:.1f}")
                
            except Exception as e:
                print(f"❌ Failed at {search_count:,} searches: {e}")
                results[search_count] = {
                    "error": str(e),
                    "successful_searches": successful_searches,
                    "status": "failed"
                }
        
        return results
    
    def stress_test_gpu_memory_limits(self) -> Dict:
        """Test GPU memory limits and efficiency."""
        print("\n💾 STRESS TEST: GPU Memory Limits")
        print("=" * 50)
        
        if not torch.cuda.is_available():
            return {"error": "CUDA not available"}
        
        try:
            from backend.engines.cognitive_field_dynamics import CognitiveFieldDynamics
        except ImportError as e:
            return {"error": f"Import failed: {e}"}
        
        # Clear GPU memory
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        
        # Test progressive memory usage
        engine = CognitiveFieldDynamics(dimension=512)  # Larger dimension for memory stress
        
        memory_results = {
            "initial_memory_mb": torch.cuda.memory_allocated() / (1024**2),
            "field_memory_efficiency": [],
            "max_fields_achieved": 0,
            "memory_limit_reached": False
        }
        
        field_count = 0
        batch_size = 1000
        
        try:
            while True:
                # Add batch of fields
                for i in range(batch_size):
                    embedding = torch.randn(512)
                    field = engine.add_geoid(f"memory_test_{field_count}", embedding)
                    if field:
                        field_count += 1
                
                # Check memory usage
                current_memory = torch.cuda.memory_allocated() / (1024**2)
                total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**2)
                memory_pct = (current_memory / total_memory) * 100
                
                memory_results["field_memory_efficiency"].append({
                    "field_count": field_count,
                    "memory_mb": current_memory,
                    "memory_per_field_kb": (current_memory * 1024) / field_count if field_count > 0 else 0,
                    "memory_usage_pct": memory_pct
                })
                
                print(f"📊 {field_count:,} fields: {current_memory:.1f} MB ({memory_pct:.1f}% GPU)")
                
                # Stop if we reach 80% GPU memory to avoid crashes
                if memory_pct > 80:
                    memory_results["memory_limit_reached"] = True
                    memory_results["max_fields_achieved"] = field_count
                    break
                
                # Safety limit
                if field_count > 100000:
                    memory_results["max_fields_achieved"] = field_count
                    break
                    
        except torch.cuda.OutOfMemoryError:
            memory_results["memory_limit_reached"] = True
            memory_results["max_fields_achieved"] = field_count
            print(f"💥 GPU memory limit reached at {field_count:,} fields")
        except Exception as e:
            memory_results["error"] = str(e)
            print(f"❌ Memory test failed: {e}")
        
        return memory_results
    
    def run_comprehensive_stress_test(self):
        """Run the complete stress test suite."""
        print("🔥" * 20)
        print("🚀 COMPREHENSIVE GPU STRESS TEST 🚀")
        print("🔥" * 20)
        
        # Collect system info
        self.collect_system_info()
        
        # Test field creation with increasing loads
        field_counts = [100, 500, 1000, 5000, 10000, 25000]
        creation_results = self.stress_test_field_creation(field_counts)
        self.results["test_results"]["field_creation"] = creation_results
        
        # Import engine for neighbor testing (using largest successful test)
        try:
            from backend.engines.cognitive_field_dynamics import CognitiveFieldDynamics
            
            # Create engine with moderate field count for neighbor testing
            print("\n🔧 Preparing engine for neighbor search tests...")
            engine = CognitiveFieldDynamics(dimension=384)
            
            # Add test fields
            for i in range(1000):
                embedding = torch.randn(384)
                engine.add_geoid(f"neighbor_test_{i}", embedding)
            
            # Test neighbor searches
            search_counts = [10, 50, 100, 500, 1000, 2000]
            search_results = self.stress_test_neighbor_search(engine, search_counts)
            self.results["test_results"]["neighbor_search"] = search_results
            
        except Exception as e:
            print(f"⚠️  Neighbor search test skipped: {e}")
            self.results["test_results"]["neighbor_search"] = {"error": str(e)}
        
        # Test GPU memory limits
        memory_results = self.stress_test_gpu_memory_limits()
        self.results["test_results"]["memory_limits"] = memory_results
        
        # Calculate final performance metrics
        self._calculate_performance_metrics()
        
        # Generate final report
        self._generate_final_report()
    
    def _calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics."""
        creation_results = self.results["test_results"].get("field_creation", {})
        
        if creation_results:
            # Find best performance
            best_rate = 0
            best_config = None
            
            for field_count, result in creation_results.items():
                if isinstance(result, dict) and result.get("status") == "success":
                    rate = result.get("creation_rate_fields_per_sec", 0)
                    if rate > best_rate:
                        best_rate = rate
                        best_config = field_count
            
            self.results["performance_metrics"] = {
                "peak_field_creation_rate": best_rate,
                "peak_performance_config": best_config,
                "jax_improvement_factor": best_rate / 5.7 if best_rate > 0 else 0,
                "target_achievement": (best_rate / 5.7) / 153.7 if best_rate > 0 else 0,
                "gpu_optimization_success": best_rate > 100  # Expect significant improvement
            }
    
    def _generate_final_report(self):
        """Generate comprehensive final report with maximum detail."""
        print("\n" + "🔥" * 80)
        print("📊 COMPREHENSIVE GPU STRESS TEST RESULTS - MAXIMUM DETAIL")
        print("🔥" * 80)
        
        # Performance summary
        metrics = self.results["performance_metrics"]
        print(f"\n🚀 PERFORMANCE SUMMARY:")
        print(f"   Peak Creation Rate: {metrics.get('peak_field_creation_rate', 0):.1f} fields/sec")
        print(f"   Best Configuration: {metrics.get('peak_performance_config', 'N/A')} fields")
        print(f"   JAX Improvement: {metrics.get('jax_improvement_factor', 0):.1f}x faster")
        print(f"   Target Achievement: {metrics.get('target_achievement', 0):.1%}")
        
        # Detailed GPU analysis from best performing test
        creation_results = self.results["test_results"].get("field_creation", {})
        best_config = metrics.get('peak_performance_config')
        
        if best_config and best_config in creation_results:
            best_result = creation_results[best_config]
            
            print(f"\n💾 DETAILED GPU ANALYSIS (Best Performance - {best_config} fields):")
            print("=" * 60)
            
            # Memory analysis
            if "memory_analysis" in best_result:
                mem = best_result["memory_analysis"]
                print(f"🧠 MEMORY ANALYSIS:")
                print(f"   PyTorch Memory Growth: {mem.get('pytorch_memory_allocated_mb', 0):.1f} MB")
                print(f"   NVIDIA Memory Growth: {mem.get('nvidia_memory_used_mb', 0):.1f} MB")
                print(f"   Memory per Field: {mem.get('memory_efficiency_mb_per_field', 0):.3f} MB/field")
            
            # Thermal analysis
            if "thermal_analysis" in best_result:
                thermal = best_result["thermal_analysis"]
                print(f"🌡️  THERMAL ANALYSIS:")
                print(f"   Temperature Range: {thermal.get('initial_temp_celsius', 0):.0f}°C → {thermal.get('final_temp_celsius', 0):.0f}°C")
                print(f"   Temperature Increase: {thermal.get('temp_increase_celsius', 0):.1f}°C")
                print(f"   Peak Temperature: {thermal.get('max_temp_during_test', 0):.0f}°C")
                print(f"   Average Temperature: {thermal.get('avg_temp_during_test', 0):.1f}°C")
            
            # Power analysis
            if "power_analysis" in best_result:
                power = best_result["power_analysis"]
                print(f"⚡ POWER ANALYSIS:")
                print(f"   Power Range: {power.get('initial_power_watts', 0):.0f}W → {power.get('final_power_watts', 0):.0f}W")
                print(f"   Peak Power Draw: {power.get('max_power_during_test', 0):.0f}W")
                print(f"   Average Power Draw: {power.get('avg_power_during_test', 0):.0f}W")
                print(f"   Power Efficiency: {power.get('power_efficiency_watts_per_field_per_sec', 0):.2f} W/(field/sec)")
            
            # Utilization analysis
            if "utilization_analysis" in best_result:
                util = best_result["utilization_analysis"]
                print(f"🎯 GPU UTILIZATION ANALYSIS:")
                print(f"   GPU Utilization: {util.get('avg_gpu_utilization', 0):.1f}% avg, {util.get('max_gpu_utilization', 0):.1f}% peak")
                print(f"   Memory Utilization: {util.get('avg_memory_utilization', 0):.1f}% avg, {util.get('max_memory_utilization', 0):.1f}% peak")
            
            # Performance samples analysis
            if "performance_samples" in best_result and best_result["performance_samples"]:
                samples = best_result["performance_samples"]
                rates = [s.get('current_rate', 0) for s in samples]
                if rates:
                    print(f"📈 PERFORMANCE VARIATION:")
                    print(f"   Rate Range: {min(rates):.1f} - {max(rates):.1f} fields/sec")
                    print(f"   Rate Stability: ±{np.std(rates):.1f} fields/sec")
        
        # System utilization summary
        if torch.cuda.is_available():
            final_gpu = self._collect_detailed_gpu_metrics()
            system_info = self.results["system_info"]
            
            print(f"\n🖥️  SYSTEM UTILIZATION SUMMARY:")
            print("=" * 60)
            print(f"   GPU: {system_info.get('gpu_name', 'Unknown')}")
            print(f"   Driver Version: {final_gpu.get('nvidia_driver_version', 'Unknown')}")
            print(f"   Total GPU Memory: {system_info.get('gpu_memory_gb', 0):.1f} GB")
            print(f"   Current GPU Memory: {final_gpu.get('memory_used_mb', 0):.1f} MB ({final_gpu.get('memory_used_percentage', 0):.1f}%)")
            print(f"   Current GPU Utilization: {final_gpu.get('gpu_utilization_percent', 0):.1f}%")
            print(f"   Current Temperature: {final_gpu.get('temperature_celsius', 0):.0f}°C")
            print(f"   Current Power Draw: {final_gpu.get('power_draw_watts', 0):.0f}W ({final_gpu.get('power_usage_percentage', 0):.1f}%)")
            print(f"   Graphics Clock: {final_gpu.get('clock_graphics_mhz', 0):.0f} MHz ({final_gpu.get('clock_graphics_percentage', 0):.1f}%)")
            print(f"   Memory Clock: {final_gpu.get('clock_memory_mhz', 0):.0f} MHz")
            print(f"   Fan Speed: {final_gpu.get('fan_speed_percent', 0):.0f}%")
        
        # Comparison with baseline
        print(f"\n📊 PERFORMANCE COMPARISON:")
        print("=" * 60)
        print(f"   JAX CPU Baseline: 5.7 fields/sec")
        print(f"   GPU Optimized Peak: {metrics.get('peak_field_creation_rate', 0):.1f} fields/sec")
        print(f"   Improvement Factor: {metrics.get('jax_improvement_factor', 0):.1f}x")
        print(f"   Target (153.7x): {'✅ EXCEEDED' if metrics.get('jax_improvement_factor', 0) > 153.7 else '❌ NOT REACHED' if metrics.get('jax_improvement_factor', 0) < 153.7 else '✅ ACHIEVED'}")
        
        # Hardware efficiency assessment
        if torch.cuda.is_available():
            best_util = 0
            if best_config and best_config in creation_results:
                best_result = creation_results[best_config]
                best_util = best_result.get("utilization_analysis", {}).get("max_gpu_utilization", 0)
            
            print(f"\n🎯 HARDWARE EFFICIENCY ASSESSMENT:")
            print("=" * 60)
            print(f"   RTX 4090 Utilization: {best_util:.1f}%")
            print(f"   Hardware ROI: {'✅ EXCELLENT' if best_util > 80 else '✅ GOOD' if best_util > 50 else '⚠️ SUBOPTIMAL'}")
            print(f"   JAX Elimination: {'✅ VALIDATED' if metrics.get('jax_improvement_factor', 0) > 50 else '❌ QUESTIONABLE'}")
        
        # Success assessment
        success = metrics.get("gpu_optimization_success", False)
        improvement = metrics.get("jax_improvement_factor", 0)
        
        print(f"\n🏆 FINAL ASSESSMENT:")
        print("=" * 60)
        if success and improvement > 100:
            print("🎉 OUTSTANDING SUCCESS!")
            print("💪 GPU optimization delivering exceptional performance")
            print("✅ JAX elimination completely validated")
            print("🚀 RTX 4090 hardware investment fully justified")
        elif success and improvement > 50:
            print("🎉 STRESS TEST SUCCESS!")
            print("💪 GPU optimization delivering excellent performance")
            print("✅ JAX elimination validated - massive improvement achieved")
        elif improvement > 10:
            print("✅ STRESS TEST PASSED")
            print("📈 Significant performance improvement over JAX")
        else:
            print("⚠️  PERFORMANCE BELOW EXPECTATIONS")
            print("🔍 Further optimization may be needed")
        
        # Save detailed results
        timestamp = int(time.time())
        filename = f"gpu_stress_test_detailed_results_{timestamp}.json"
        
        try:
            # Store real-time metrics summary
            self.results["realtime_metrics"] = {
                "total_monitoring_sessions": len([r for r in creation_results.values() if isinstance(r, dict) and "monitoring_analysis" in r]),
                "total_samples_collected": sum([r.get("monitoring_analysis", {}).get("total_samples", 0) for r in creation_results.values() if isinstance(r, dict)]),
                "monitoring_coverage_sec": sum([r.get("monitoring_analysis", {}).get("monitoring_duration_sec", 0) for r in creation_results.values() if isinstance(r, dict)])
            }
            
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 DETAILED RESULTS SAVED:")
            print(f"   File: {filename}")
            print(f"   Size: {len(json.dumps(self.results, indent=2))} characters")
            print(f"   Monitoring Sessions: {self.results['realtime_metrics']['total_monitoring_sessions']}")
            print(f"   Total Samples: {self.results['realtime_metrics']['total_samples_collected']}")
            print(f"   Monitoring Duration: {self.results['realtime_metrics']['monitoring_coverage_sec']:.1f} seconds")
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")
        
        print("\n" + "🔥" * 80)
        print("🎯 GPU STRESS TEST COMPLETED - MAXIMUM DETAIL CAPTURED")
        print("🔥" * 80)

def main():
    """Run the comprehensive GPU stress test."""
    tester = GPUStressTester()
    tester.run_comprehensive_stress_test()

if __name__ == "__main__":
    main() 