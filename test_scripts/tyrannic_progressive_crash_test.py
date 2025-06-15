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

    def run_tyrannic_phase(self, num_threads: int, feature_count: int, depth: int, ops_per_thread: int = 10) -> Dict[str, Any]:
        print(f"\n🔥 Tyrannic Phase: {num_threads} threads, {feature_count} features, depth {depth}")
        total_ops = num_threads * ops_per_thread
        successes, failures, response_times = 0, 0, []
        start_metrics = self.log_system_metrics()
        start_time = time.time()

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
        return {
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
        print(f"💥 KIMERA SWM TYRANNIC PROGRESSIVE CRASH TEST ({test_mode})")
        print("=" * 70)
        if not self.test_gpu():
            return {"error": "GPU not available and CPU mode not allowed"}
        print("This test will progressively increase both concurrency and complexity.")
        print("=" * 70)
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
        if self.breaking_point:
            print(f"\n💀 Breaking Point: {self.breaking_point}")
        else:
            print("\n🎉 No breaking point found! System survived all phases.")
        print(f"\nTotal test duration: {time.time() - self.start_time:.1f} seconds")
        # Save results
        with open("tyrannic_progressive_crash_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
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
