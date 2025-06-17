#!/usr/bin/env python3
"""
Tyrannic Progressive Crash Test for Kimera SWM (GPU-Optimized)

- Progressively increases both horizontal (concurrency) and vertical (data complexity) load.
- Alternates between wide and deep stress patterns.
- Monitors GPU utilization, memory, and latency at each stage.
- Aborts if system falls back to CPU or GPU is not detected.
- Designed to push the system to its absolute limits.
"""
import os
import sys
import time
import threading
import concurrent.futures
import random
import string
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
import psutil
import logging
import argparse
import asyncio
import numpy as np

try:
    import torch
    GPU_AVAILABLE = torch.cuda.is_available()
    TORCH_VERSION = torch.__version__
except ImportError:
    GPU_AVAILABLE = False
    TORCH_VERSION = "Not installed"

# Try to import GPU monitoring
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

# Force GPU usage if possible
os.environ["KIMERA_FORCE_GPU"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["LIGHTWEIGHT_EMBEDDING"] = "0"
os.environ["ENABLE_JOBS"] = "0"
os.environ["DATABASE_URL"] = f"sqlite:///./tyrannic_crash_test_{uuid.uuid4().hex[:8]}.db"

# ----------------- Logging Setup -----------------
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logger = logging.getLogger("tyrannic_crash_test")  # Global logger for the test harness
# BasicConfig will be configured from main() based on CLI args.

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api.main import app

# Import innovation modules
try:
    import sys
    import os
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from innovations.quantum_batch_processor import (
        process_geoids_quantum, 
        QuantumBatchProcessor,
        get_quantum_metrics
    )
    from innovations.predictive_load_balancer import (
        PredictiveLoadBalancer,
        ResourceState,
        WorkloadRequest,
        register_resource,
        update_resource_state,
        submit_workload,
        get_load_balancing_decision,
        start_optimization_loop,
        stop_optimization_loop,
        get_system_metrics as get_balancer_metrics
    )
    INNOVATIONS_AVAILABLE = True
    logger.info("Innovation modules loaded successfully!")
except ImportError as e:
    logger.warning(f"Innovation modules not available: {e}")
    INNOVATIONS_AVAILABLE = False

# Import core modules for GeoidState
try:
    from backend.core.geoid import GeoidState
    GEOID_AVAILABLE = True
    logger.info("GeoidState loaded successfully!")
except ImportError:
    logger.warning("GeoidState not available, will use mock")
    GEOID_AVAILABLE = False
    
    # Mock GeoidState for testing
    class GeoidState:
        def __init__(self, semantic_state, symbolic_state, metadata=None):
            self.semantic_state = semantic_state
            self.symbolic_state = symbolic_state
            self.metadata = metadata or {}
            self.embedding_vector = None
            
        def calculate_entropy(self):
            return random.random()

class TyrannicCrashTester:
    def __init__(self, allow_cpu=False):
        self.client = TestClient(app)
        self.results = []
        self.breaking_point = None
        self.system_survived = True
        self.start_time = time.time()
        self.gpu_available = GPU_AVAILABLE
        self.gpu_device = torch.cuda.get_device_name(0) if self.gpu_available else None
        self.gpu_stats = []
        self.allow_cpu = allow_cpu
        
        # Innovation modules with optimized settings
        self.use_innovations = INNOVATIONS_AVAILABLE
        self.quantum_processor = QuantumBatchProcessor(
            max_batch_size=256,  # Larger batches
            entanglement_threshold=0.0,  # Skip entanglement calculations
            use_embeddings=False  # Disable embeddings for speed
        ) if INNOVATIONS_AVAILABLE else None
        self.predictive_balancer = PredictiveLoadBalancer() if INNOVATIONS_AVAILABLE else None
        
        # Performance feedback for adaptive optimization
        self.performance_history = []
        
        # Initialize predictive load balancer
        if self.use_innovations:
            self._initialize_load_balancer()

    def log_system_metrics(self) -> Dict[str, float]:
        process = psutil.Process()
        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": process.memory_info().rss / 1024 / 1024,
            "threads": process.num_threads(),
            "gpu_util": None,
            "gpu_mem": None,
            "gpu_temp": None
        }
        
        if self.gpu_available and PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util_rates = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                
                metrics["gpu_util"] = util_rates.gpu
                metrics["gpu_mem"] = mem_info.used / 1024 / 1024  # MB
                metrics["gpu_temp"] = temp
                self.gpu_stats.append({"time": time.time() - self.start_time, **metrics})
            except Exception as e:
                logger.debug(f"GPU monitoring error: {e}")
                metrics["gpu_util"] = -1
                metrics["gpu_mem"] = -1
                metrics["gpu_temp"] = -1
        elif self.gpu_available:
            # GPU available but no monitoring
            metrics["gpu_util"] = "N/A"
            metrics["gpu_mem"] = "N/A"
            metrics["gpu_temp"] = "N/A"
            
        return metrics
    
    def _initialize_load_balancer(self):
        """Initialize predictive load balancer with system resources"""
        if not self.predictive_balancer:
            return
            
        # Register CPU resources
        cpu_count = psutil.cpu_count()
        for i in range(cpu_count):
            resource = ResourceState(
                resource_id=f"cpu_{i}",
                resource_type="cpu",
                utilization=0.0,
                capacity=100.0,
                temperature=50.0,
                power_consumption=50.0,
                latency=0.1,
                throughput=100.0,
                error_rate=0.0
            )
            register_resource(resource)
        
        # Register GPU resources
        if self.gpu_available:
            resource = ResourceState(
                resource_id="gpu_0",
                resource_type="gpu",
                utilization=0.0,
                capacity=1000.0,  # GPU has 10x capacity
                temperature=50.0,
                power_consumption=200.0,
                latency=0.01,  # Lower latency
                throughput=1000.0,  # Higher throughput
                error_rate=0.0
            )
            register_resource(resource)
        
        # Start optimization loop
        start_optimization_loop()
        logger.info("Initialized predictive load balancer")

    def create_complex_geoid(self, feature_count: int, depth: int) -> Dict[str, Any]:
        """Create a geoid with high feature count and nested symbolic content."""
        semantic_features = {f"feature_{i}": random.uniform(-1.0, 1.0) for i in range(feature_count)}
        symbolic_content = self._generate_nested_symbolic(depth)
        return {
            "semantic_features": semantic_features,
            "symbolic_content": symbolic_content,
            "metadata": {
                "test_id": uuid.uuid4().hex,
                "timestamp": datetime.now().isoformat(),
                "depth": depth,
                "feature_count": feature_count
            }
        }

    def _generate_nested_symbolic(self, depth: int) -> Any:
        if depth <= 0:
            return ''.join(random.choices(string.ascii_letters, k=32))
        return {
            f"level_{depth}": self._generate_nested_symbolic(depth - 1),
            f"data_{depth}": ''.join(random.choices(string.ascii_letters, k=32))
        }
    
    async def _run_quantum_phase(self, num_threads: int, feature_count: int, depth: int, ops_per_thread: int) -> Dict[str, Any]:
        """Run phase using quantum batch processor"""
        print("   🌌 Using Quantum Batch Processing")
        
        total_ops = num_threads * ops_per_thread
        start_metrics = self.log_system_metrics()
        start_time = time.time()
        
        print(f"   📊 Creating {total_ops} geoids...")
        
        # Collect all geoids for quantum batch processing
        all_geoids = []
        for _ in range(total_ops):
            # Create GeoidState objects
            semantic_state = {f"feature_{i}": random.uniform(-1.0, 1.0) for i in range(feature_count)}
            symbolic_state = self._generate_nested_symbolic(depth)
            metadata = {
                "test_id": uuid.uuid4().hex,
                "timestamp": datetime.now().isoformat(),
                "depth": depth,
                "feature_count": feature_count
            }
            
            geoid = GeoidState(
                geoid_id=uuid.uuid4().hex,
                semantic_state=semantic_state,
                symbolic_state=symbolic_state,
                metadata=metadata
            )
            all_geoids.append(geoid)
        
        # Process in quantum batches
        batch_size = min(128, total_ops)  # Optimal quantum batch size
        successes, failures = 0, 0
        response_times = []
        
        print(f"   🔄 Processing in batches of {batch_size}...")
        
        for i in range(0, len(all_geoids), batch_size):
            batch = all_geoids[i:i + batch_size]
            print(f"   ⚛️ Processing batch {i//batch_size + 1}/{(len(all_geoids) + batch_size - 1)//batch_size} ({len(batch)} geoids)...")
            
            try:
                # Quantum batch processing with timeout
                t0 = time.time()
                quantum_result = await asyncio.wait_for(
                    process_geoids_quantum(batch),
                    timeout=60.0  # 60 second timeout for embedding initialization
                )
                processing_time = time.time() - t0
                print(f"   ✅ Batch processed in {processing_time:.2f}s")
                
                # Process results
                for processed_geoid in quantum_result.processed_geoids:
                    # Convert back to payload format
                    payload = {
                        "semantic_features": processed_geoid.semantic_state,
                        "symbolic_content": processed_geoid.symbolic_state,
                        "metadata": processed_geoid.metadata
                    }
                    
                    # Submit to API
                    try:
                        resp = self.client.post("/geoids", json=payload, timeout=60)
                        if resp.status_code == 200:
                            successes += 1
                        else:
                            failures += 1
                    except Exception:
                        failures += 1
                
                response_times.extend([processing_time / len(batch)] * len(batch))
                
                # Log quantum metrics
                if quantum_result.entanglement_preserved:
                    print(f"   ⚛️ Quantum entanglement preserved (coherence: {quantum_result.coherence_score:.2f})")
                
            except asyncio.TimeoutError:
                print(f"   ⏱️ Batch processing timed out after 30s")
                logger.error("Quantum processing timeout")
                failures += len(batch)
                response_times.extend([30.0] * len(batch))
            except Exception as e:
                print(f"   ❌ Batch processing error: {e}")
                logger.error(f"Quantum processing error: {e}")
                failures += len(batch)
                response_times.extend([1.0] * len(batch))  # Default response time
        
        duration = time.time() - start_time
        end_metrics = self.log_system_metrics()
        avg_resp = sum(response_times) / len(response_times) if response_times else 0
        ops_per_sec = total_ops / duration if duration > 0 else 0
        
        # Get quantum metrics
        quantum_metrics = get_quantum_metrics()
        
        result = {
            "threads": num_threads,
            "feature_count": feature_count,
            "depth": depth,
            "operations": total_ops,
            "successes": successes,
            "failures": failures,
            "success_rate": (successes / total_ops) * 100 if total_ops else 0,
            "duration": duration,
            "ops_per_sec": ops_per_sec,
            "avg_response_time": avg_resp,
            "start_metrics": start_metrics,
            "end_metrics": end_metrics,
            "quantum_metrics": quantum_metrics
        }
        
        # Store performance feedback
        self._store_performance_feedback(result)
        
        return result
    
    def _update_resource_states(self, metrics: Dict[str, Any]):
        """Update resource states in predictive load balancer"""
        if not self.use_innovations:
            return
        
        # Update CPU resources
        cpu_count = psutil.cpu_count()
        cpu_percent_per_core = psutil.cpu_percent(percpu=True)
        
        for i in range(cpu_count):
            utilization = cpu_percent_per_core[i] / 100.0 if i < len(cpu_percent_per_core) else 0.0
            
            resource = ResourceState(
                resource_id=f"cpu_{i}",
                resource_type="cpu",
                utilization=utilization,
                capacity=100.0,
                temperature=50.0 + utilization * 30.0,  # Estimate temperature
                power_consumption=50.0 + utilization * 50.0,
                latency=0.1 * (1.0 + utilization),
                throughput=100.0 * (1.0 - utilization * 0.5),
                error_rate=0.0 if utilization < 0.9 else 0.01
            )
            update_resource_state(resource)
        
        # Update GPU resource
        if self.gpu_available and metrics.get("gpu_util") is not None:
            gpu_util = metrics["gpu_util"] / 100.0 if isinstance(metrics["gpu_util"], (int, float)) else 0.0
            gpu_mem = metrics.get("gpu_mem", 0.0)
            gpu_temp = metrics.get("gpu_temp", 50.0)
            
            resource = ResourceState(
                resource_id="gpu_0",
                resource_type="gpu",
                utilization=gpu_util,
                capacity=1000.0,
                temperature=float(gpu_temp),
                power_consumption=200.0 + gpu_util * 200.0,
                latency=0.01 * (1.0 + gpu_util * 0.5),
                throughput=1000.0 * (1.0 - gpu_util * 0.3),
                error_rate=0.0 if gpu_util < 0.95 else 0.02
            )
            update_resource_state(resource)
    
    def _store_performance_feedback(self, result: Dict[str, Any]):
        """Store performance feedback for adaptive optimization"""
        feedback = {
            "timestamp": time.time(),
            "ops_per_sec": result["ops_per_sec"],
            "avg_response_time": result["avg_response_time"],
            "success_rate": result["success_rate"],
            "resource_utilization": {
                "cpu": result["end_metrics"]["cpu_percent"],
                "memory": result["end_metrics"]["memory_percent"],
                "gpu": result["end_metrics"].get("gpu_util", 0)
            }
        }
        
        self.performance_history.append(feedback)
        
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

    def run_tyrannic_phase(self, num_threads: int, feature_count: int, depth: int, ops_per_thread: int = 10) -> Dict[str, Any]:
        print(f"\n🔥 Tyrannic Phase: {num_threads} threads, {feature_count} features, depth {depth}")
        total_ops = num_threads * ops_per_thread
        successes, failures, response_times = 0, 0, []
        start_metrics = self.log_system_metrics()
        start_time = time.time()
        
        # Update resource states for predictive load balancer
        if self.use_innovations:
            self._update_resource_states(start_metrics)
            
            # Submit workload request
            workload = WorkloadRequest(
                request_id=f"phase_{num_threads}_{feature_count}_{depth}",
                complexity_score=feature_count / 2048.0,  # Normalize to 0-1
                resource_requirements={"gpu": 0.8, "cpu": 0.2} if self.gpu_available else {"cpu": 1.0},
                priority=depth,  # Higher depth = higher priority
                estimated_duration=ops_per_thread * 0.1
            )
            submit_workload(workload)
            
            # Get load balancing decision
            decision = get_load_balancing_decision(workload)
            logger.info(f"Load balancing decision: {decision.reasoning}")
            
            # Adjust thread count based on decision
            if decision.confidence_score < 0.5:
                num_threads = max(1, int(num_threads * 0.7))  # Reduce threads if low confidence
                print(f"   ⚡ Adjusted threads to {num_threads} based on predictive analysis")
        
        # Only use innovations for larger workloads where overhead is worth it
        min_ops_for_innovations = 40  # Lowered threshold with optimizations
        
        if self.use_innovations and self.quantum_processor and total_ops >= min_ops_for_innovations:
            # Use quantum batch processing
            print(f"   🚀 Workload large enough ({total_ops} ops) - using innovations")
            return asyncio.run(self._run_quantum_phase(num_threads, feature_count, depth, ops_per_thread))
        
        # For small workloads or when innovations are disabled, use standard processing
        if self.use_innovations and total_ops < min_ops_for_innovations:
            print(f"   ⚡ Workload too small ({total_ops} ops) - skipping innovations for efficiency")
        
        # Original implementation
        def worker():
            nonlocal successes, failures, response_times
            for _ in range(ops_per_thread):
                payload = self.create_complex_geoid(feature_count, depth)
                t0 = time.time()
                try:
                    resp = self.client.post("/geoids", json=payload, timeout=60)
                    dt = time.time() - t0
                    response_times.append(dt)
                    if resp.status_code == 200:
                        successes += 1
                    else:
                        failures += 1
                except Exception:
                    failures += 1
                    response_times.append(time.time() - t0)
                time.sleep(0.01)

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=300)
        duration = time.time() - start_time
        end_metrics = self.log_system_metrics()
        avg_resp = sum(response_times) / len(response_times) if response_times else 0
        ops_per_sec = total_ops / duration if duration > 0 else 0
        
        result = {
            "threads": num_threads,
            "feature_count": feature_count,
            "depth": depth,
            "operations": total_ops,
            "successes": successes,
            "failures": failures,
            "success_rate": (successes / total_ops) * 100 if total_ops else 0,
            "duration": duration,
            "ops_per_sec": ops_per_sec,
            "avg_response_time": avg_resp,
            "start_metrics": start_metrics,
            "end_metrics": end_metrics
        }
        
        # Store performance feedback
        if self.use_innovations:
            self._store_performance_feedback(result)
        
        return result

    def test_gpu(self):
        print("\n🔍 GPU Detection and Setup:")
        print(f"   PyTorch version: {TORCH_VERSION}")
        print(f"   CUDA available: {self.gpu_available}")
        
        if not self.gpu_available:
            print("💥 GPU/CUDA not available!")
            print("   Your system has an RTX 4090, but PyTorch can't access CUDA.")
            print("   Current PyTorch version appears to be CPU-only.")
            print("\n🔧 To enable GPU support:")
            print("   1. Install CUDA-enabled PyTorch:")
            print("      pip uninstall torch torchvision")
            print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
            print("   2. Install GPU monitoring:")
            print("      pip install nvidia-ml-py")
            print("   3. Restart the test")
            
            if self.allow_cpu:
                print("\n⚠️ Continuing with CPU mode (performance will be severely limited)")
                logger.warning("GPU not available, running on CPU with --allow-cpu flag")
                return True
            else:
                print("\n   Use --allow-cpu to run on CPU anyway (not recommended)")
                logger.error("GPU not available and --allow-cpu not specified")
                self.system_survived = False
                return False
                
        print(f"✅ GPU detected: {self.gpu_device}")
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                print(f"   GPU Memory: {mem_info.total / 1024**3:.1f} GB total, {mem_info.free / 1024**3:.1f} GB free")
            except Exception:
                print("   GPU memory info unavailable")
        else:
            print("   Install nvidia-ml-py for detailed GPU monitoring")
            
        logger.info(f"GPU detected: {self.gpu_device}")
        return True

    def run_tyrannic_progressive_test(self):
        test_mode = "CPU" if not self.gpu_available else "GPU"
        innovations_mode = " + INNOVATIONS" if self.use_innovations else ""
        print(f"💥 KIMERA SWM TYRANNIC PROGRESSIVE CRASH TEST ({test_mode}{innovations_mode})")
        print("=" * 70)
        if not self.test_gpu():
            return {"error": "GPU not available and CPU mode not allowed"}
        print("This test will progressively increase both concurrency and complexity.")
        if self.use_innovations:
            print("🚀 Innovation modules enabled: Quantum Batch Processing + Predictive Load Balancing")
        print("=" * 70)
        
        try:
            phases = [
                # (threads, features, depth)
                (2, 32, 2),
                (4, 64, 3),
                (8, 128, 4),
                (16, 256, 5),
                (32, 512, 6),
                (64, 1024, 7),
                (128, 2048, 8),
            ]
            for threads, features, depth in phases:
                result = self.run_tyrannic_phase(threads, features, depth)
                self.results.append(result)
                print(f"   {result['threads']} threads, {result['feature_count']} features, depth {result['depth']}: "
                      f"{result['success_rate']:.1f}% success, {result['ops_per_sec']:.2f} ops/s, "
                      f"{result['avg_response_time']:.2f}s avg resp, Mem: {result['end_metrics']['memory_percent']:.1f}%, "
                      f"GPU: {result['end_metrics']['gpu_util']}% util, {result['end_metrics']['gpu_mem']}MB")
                if result['success_rate'] < 50 or result['end_metrics']['memory_percent'] > 95:
                    print(f"   💀 Breaking point reached at {threads} threads, {features} features, depth {depth}")
                    self.breaking_point = (threads, features, depth)
                    self.system_survived = False
                    break
                time.sleep(2)
        finally:
            # Clean up innovation modules
            if self.use_innovations:
                stop_optimization_loop()
                logger.info("Stopped predictive load balancer optimization loop")
        
        self.generate_report()
        return self.results

    def generate_report(self):
        print("\n" + "=" * 70)
        print("📋 TYRANNIC PROGRESSIVE CRASH TEST REPORT")
        print("=" * 70)
        for r in self.results:
            status = "✅" if r['success_rate'] >= 90 else "⚠️" if r['success_rate'] >= 50 else "❌"
            print(f"{status} {r['threads']:3d} threads, {r['feature_count']:5d} features, depth {r['depth']}: "
                  f"{r['success_rate']:5.1f}% success, {r['ops_per_sec']:6.2f} ops/s, "
                  f"{r['avg_response_time']:5.2f}s avg resp, Mem: {r['end_metrics']['memory_percent']:5.1f}%, "
                  f"GPU: {r['end_metrics']['gpu_util']}% util, {r['end_metrics']['gpu_mem']}MB")
            
            # Show quantum metrics if available
            if 'quantum_metrics' in r:
                qm = r['quantum_metrics']
                print(f"     ⚛️ Quantum: {qm.get('total_superpositions', 0)} superpositions, "
                      f"{qm.get('successful_entanglements', 0)} entanglements, "
                      f"speedup: {qm.get('quantum_speedup_factor', 1.0):.2f}x")
        
        if self.breaking_point:
            print(f"\n💀 Breaking Point: {self.breaking_point}")
        else:
            print("\n🎉 No breaking point found! System survived all phases.")
        
        # Show innovation metrics if available
        if self.use_innovations:
            print("\n🚀 INNOVATION METRICS:")
            
            # Quantum processor metrics
            if self.quantum_processor:
                quantum_metrics = get_quantum_metrics()
                print(f"   Quantum Processor:")
                print(f"     - Total Superpositions: {quantum_metrics['total_superpositions']}")
                print(f"     - Successful Entanglements: {quantum_metrics['successful_entanglements']}")
                print(f"     - Coherence Violations: {quantum_metrics['coherence_violations']}")
                print(f"     - Quantum Speedup Factor: {quantum_metrics['quantum_speedup_factor']:.2f}x")
            
            # Predictive load balancer metrics
            if self.predictive_balancer:
                balancer_metrics = get_balancer_metrics()
                print(f"   Predictive Load Balancer:")
                print(f"     - Total Resources: {balancer_metrics['total_resources']}")
                print(f"     - Active Workloads: {balancer_metrics['active_workloads']}")
                print(f"     - Avg Utilization: {balancer_metrics['avg_utilization']:.1%}")
                print(f"     - Avg Efficiency: {balancer_metrics['avg_efficiency']:.1%}")
                print(f"     - Prediction Accuracy: {balancer_metrics['prediction_accuracy']:.1%}")
                if balancer_metrics['is_chaotic']:
                    print(f"     - ⚠️ CHAOS DETECTED! Strength: {balancer_metrics['chaos_strength']:.2f}")
                print(f"     - Lyapunov Exponent: {balancer_metrics['lyapunov_exponent']:.3f}")
        
        print(f"\nTotal test duration: {time.time() - self.start_time:.1f} seconds")
        
        # Save results
        results_data = {
            "results": self.results,
            "breaking_point": self.breaking_point,
            "system_survived": self.system_survived,
            "innovations_used": self.use_innovations,
            "test_duration": time.time() - self.start_time
        }
        
        if self.use_innovations:
            results_data["quantum_metrics"] = get_quantum_metrics() if self.quantum_processor else None
            results_data["balancer_metrics"] = get_balancer_metrics() if self.predictive_balancer else None
            results_data["performance_history"] = self.performance_history
        
        with open("tyrannic_progressive_crash_results.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        if self.gpu_stats:
            with open("tyrannic_gpu_stats.json", "w") as f:
                json.dump(self.gpu_stats, f, indent=2)
        
        print("\n💾 Results saved to tyrannic_progressive_crash_results.json and tyrannic_gpu_stats.json")

def parse_args():
    """Parse command-line arguments for logging level and other options."""
    parser = argparse.ArgumentParser(description="Run Tyrannic Progressive Crash Test")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity level",
    )
    parser.add_argument(
        "--allow-cpu",
        action="store_true",
        help="Allow running the test on CPU if GPU is not available (not recommended)",
    )
    parser.add_argument(
        "--install-gpu-deps",
        action="store_true",
        help="Install GPU dependencies (CUDA PyTorch and nvidia-ml-py)",
    )
    return parser.parse_args()


def install_gpu_dependencies():
    """Install GPU dependencies for CUDA support."""
    import subprocess
    import sys
    
    print("🔧 Installing GPU dependencies...")
    try:
        # Uninstall CPU-only PyTorch
        print("   Uninstalling CPU-only PyTorch...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision"], check=True)
        
        # Install CUDA-enabled PyTorch
        print("   Installing CUDA-enabled PyTorch...")
        # Try CUDA 12.4 first, then 11.8 as fallback
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "torch", "torchvision", 
                "--index-url", "https://download.pytorch.org/whl/cu124"
            ], check=True)
        except subprocess.CalledProcessError:
            print("   CUDA 12.4 not available, trying CUDA 11.8...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "torch", "torchvision", 
                "--index-url", "https://download.pytorch.org/whl/cu118"
            ], check=True)
        
        # Install GPU monitoring
        print("   Installing nvidia-ml-py...")
        subprocess.run([sys.executable, "-m", "pip", "install", "nvidia-ml-py"], check=True)
        
        print("✅ GPU dependencies installed successfully!")
        print("   Please restart the test to use GPU acceleration.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install GPU dependencies: {e}")
        return False


def main():
    args = parse_args()
    # Configure root logger once at runtime based on CLI
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format=LOG_FORMAT)

    # Handle GPU dependency installation
    if args.install_gpu_deps:
        if install_gpu_dependencies():
            sys.exit(0)
        else:
            sys.exit(1)

    logger.info("Initializing Tyrannic Progressive Crash Tester…")
    logger.warning("⚠️  This will push the system to its absolute limits (GPU required)!")

    tester = TyrannicCrashTester(allow_cpu=args.allow_cpu)
    try:
        tester.run_tyrannic_progressive_test()
    except KeyboardInterrupt:
        logger.warning("🛑 Test interrupted by user")
    except Exception as e:
        logger.exception("💥 Critical test failure: %s", e)


if __name__ == "__main__":
    main()
