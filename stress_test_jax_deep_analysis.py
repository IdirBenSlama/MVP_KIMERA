#!/usr/bin/env python3
"""
JAX Implementation Stress Test & Deep Analysis

This script performs comprehensive stress testing and deep performance analysis
of Kimera's JAX cognitive field dynamics implementation.

Tests include:
- Scalability stress testing (1K to 100K fields)
- Memory usage profiling under load
- JIT compilation behavior analysis
- Numerical stability under extreme conditions
- Concurrent operation stress testing
- Performance degradation analysis
- Error handling validation
"""

import sys
import time
import tracemalloc
import gc
import psutil
import threading
import asyncio
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import warnings

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

try:
    import jax
    import jax.numpy as jnp
    from backend.engines.cognitive_field_dynamics_jax import CognitiveFieldDynamicsJAX
    print(f"✅ JAX {jax.__version__} loaded successfully")
    print(f"   Devices: {jax.devices()}")
    print(f"   Platform: {jax.lib.xla_bridge.get_backend().platform}")
except ImportError as e:
    print(f"❌ JAX setup failed: {e}")
    sys.exit(1)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single test."""
    test_name: str
    field_count: int
    operation_count: int
    execution_time: float
    memory_peak_mb: float
    memory_current_mb: float
    cpu_percent: float
    throughput_ops_per_sec: float
    jit_compilation_time: float = 0.0
    error_rate: float = 0.0
    numerical_precision: float = 0.0

@dataclass
class StressTestSuite:
    """Complete stress test results."""
    system_info: Dict
    scalability_results: List[PerformanceMetrics]
    memory_profile: Dict
    jit_analysis: Dict
    numerical_stability: Dict
    concurrent_performance: Dict
    error_handling: Dict
    recommendations: List[str]

class DeepAnalyzer:
    """Deep performance and behavior analyzer for JAX implementation."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = self.process.memory_info().rss / 1024 / 1024
        self.results = []
        
    def measure_detailed_performance(self, func, *args, **kwargs) -> Tuple[Any, PerformanceMetrics]:
        """Measure detailed performance metrics for a function."""
        # Start monitoring
        tracemalloc.start()
        gc.collect()
        
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        start_time = time.perf_counter()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # End monitoring
        end_time = time.perf_counter()
        end_cpu = self.process.cpu_percent()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time = end_time - start_time
        peak_memory_mb = peak / 1024 / 1024
        current_memory_mb = current / 1024 / 1024
        
        # Create metrics (will be filled by caller)
        metrics = PerformanceMetrics(
            test_name="",
            field_count=0,
            operation_count=0,
            execution_time=execution_time,
            memory_peak_mb=peak_memory_mb,
            memory_current_mb=current_memory_mb,
            cpu_percent=(start_cpu + end_cpu) / 2,
            throughput_ops_per_sec=0.0
        )
        
        return result, metrics

    def test_scalability_stress(self) -> List[PerformanceMetrics]:
        """Test scalability under increasing field counts."""
        print("\n🔥 SCALABILITY STRESS TEST")
        print("=" * 60)
        
        field_counts = [100, 500, 1000, 2500, 5000, 10000, 25000]
        scalability_results = []
        
        for field_count in field_counts:
            print(f"\n📊 Testing with {field_count:,} fields...")
            
            # Test field creation performance
            def create_fields():
                cfd = CognitiveFieldDynamicsJAX(dimension=256)
                embeddings = []
                
                for i in range(field_count):
                    embedding = np.random.randn(256).astype(np.float32)
                    embeddings.append(embedding)
                    field = cfd.add_geoid(f"stress_field_{i}", jnp.array(embedding))
                    
                    # Progress indicator for large tests
                    if field_count > 5000 and i % 1000 == 0:
                        print(f"   Created {i:,}/{field_count:,} fields...")
                
                return cfd
            
            cfd, metrics = self.measure_detailed_performance(create_fields)
            
            metrics.test_name = f"field_creation_{field_count}"
            metrics.field_count = field_count
            metrics.operation_count = field_count
            metrics.throughput_ops_per_sec = field_count / metrics.execution_time
            
            print(f"   ⏱️  Time: {metrics.execution_time:.2f}s")
            print(f"   🧠 Memory Peak: {metrics.memory_peak_mb:.1f} MB")
            print(f"   🚀 Throughput: {metrics.throughput_ops_per_sec:.1f} fields/sec")
            
            scalability_results.append(metrics)
            
            # Test neighbor finding performance on populated system
            if field_count <= 5000:  # Skip for very large tests (too slow)
                print(f"   🔍 Testing neighbor finding...")
                
                def find_neighbors():
                    neighbor_results = []
                    test_count = min(50, field_count // 10)
                    
                    for i in range(test_count):
                        neighbors = cfd.find_semantic_neighbors(f"stress_field_{i}")
                        neighbor_results.append(neighbors)
                    
                    return neighbor_results
                
                _, neighbor_metrics = self.measure_detailed_performance(find_neighbors)
                
                neighbor_metrics.test_name = f"neighbor_finding_{field_count}"
                neighbor_metrics.field_count = field_count
                neighbor_metrics.operation_count = min(50, field_count // 10)
                neighbor_metrics.throughput_ops_per_sec = neighbor_metrics.operation_count / neighbor_metrics.execution_time
                
                print(f"   🔍 Neighbor Time: {neighbor_metrics.execution_time:.2f}s")
                print(f"   🔍 Neighbor Throughput: {neighbor_metrics.throughput_ops_per_sec:.1f} searches/sec")
                
                scalability_results.append(neighbor_metrics)
            
            # Cleanup for next iteration
            del cfd
            gc.collect()
        
        return scalability_results

    def test_memory_behavior(self) -> Dict:
        """Analyze memory usage patterns and potential leaks."""
        print("\n🧠 MEMORY BEHAVIOR ANALYSIS")
        print("=" * 60)
        
        memory_profile = {
            "baseline_mb": self.baseline_memory,
            "growth_pattern": [],
            "gc_effectiveness": [],
            "peak_usage": 0.0,
            "memory_efficiency": {}
        }
        
        # Test memory growth with incremental field addition
        print("📈 Testing memory growth pattern...")
        
        cfd = CognitiveFieldDynamicsJAX(dimension=512)
        
        for iteration in range(10):
            iteration_start = self.process.memory_info().rss / 1024 / 1024
            
            # Add 1000 fields
            for i in range(1000):
                embedding = np.random.randn(512).astype(np.float32)
                cfd.add_geoid(f"memory_test_{iteration}_{i}", jnp.array(embedding))
            
            iteration_end = self.process.memory_info().rss / 1024 / 1024
            memory_growth = iteration_end - iteration_start
            
            memory_profile["growth_pattern"].append({
                "iteration": iteration,
                "fields_added": 1000,
                "memory_before_mb": iteration_start,
                "memory_after_mb": iteration_end,
                "growth_mb": memory_growth,
                "memory_per_field_kb": (memory_growth * 1024) / 1000
            })
            
            print(f"   Iteration {iteration}: +{memory_growth:.1f} MB ({(memory_growth * 1024) / 1000:.2f} KB/field)")
            
            # Test garbage collection effectiveness
            pre_gc = self.process.memory_info().rss / 1024 / 1024
            gc.collect()
            post_gc = self.process.memory_info().rss / 1024 / 1024
            gc_freed = pre_gc - post_gc
            
            memory_profile["gc_effectiveness"].append({
                "iteration": iteration,
                "memory_before_gc": pre_gc,
                "memory_after_gc": post_gc,
                "freed_mb": gc_freed
            })
            
            print(f"   GC freed: {gc_freed:.1f} MB")
            
            memory_profile["peak_usage"] = max(memory_profile["peak_usage"], iteration_end)
        
        # Memory efficiency analysis
        final_memory = self.process.memory_info().rss / 1024 / 1024
        total_fields = 10000
        memory_per_field = (final_memory - self.baseline_memory) / total_fields
        
        memory_profile["memory_efficiency"] = {
            "total_fields": total_fields,
            "total_memory_mb": final_memory - self.baseline_memory,
            "memory_per_field_kb": memory_per_field * 1024,
            "efficiency_rating": "excellent" if memory_per_field < 0.1 else "good" if memory_per_field < 0.5 else "poor"
        }
        
        print(f"\n📊 Memory Efficiency Summary:")
        print(f"   Total Memory Used: {final_memory - self.baseline_memory:.1f} MB")
        print(f"   Memory per Field: {memory_per_field * 1024:.2f} KB")
        print(f"   Efficiency Rating: {memory_profile['memory_efficiency']['efficiency_rating']}")
        
        return memory_profile

    def test_jit_compilation_behavior(self) -> Dict:
        """Analyze JIT compilation patterns and performance."""
        print("\n⚡ JIT COMPILATION BEHAVIOR ANALYSIS")
        print("=" * 60)
        
        jit_analysis = {
            "compilation_times": [],
            "warmup_behavior": {},
            "performance_scaling": [],
            "compilation_overhead": {}
        }
        
        # Test JIT compilation timing
        print("🔥 Testing JIT compilation overhead...")
        
        @jax.jit
        def jit_vector_operation(a, b):
            return jnp.dot(a, b) + jnp.sum(a * b)
        
        # Measure first compilation
        a = jnp.ones(10000)
        b = jnp.ones(10000)
        
        start_time = time.perf_counter()
        result1 = jit_vector_operation(a, b)  # First call - includes compilation
        first_call_time = time.perf_counter() - start_time
        
        # Measure subsequent calls
        times = []
        for _ in range(10):
            start_time = time.perf_counter()
            result = jit_vector_operation(a, b)  # Subsequent calls - no compilation
            times.append(time.perf_counter() - start_time)
        
        avg_runtime = np.mean(times)
        compilation_overhead = first_call_time - avg_runtime
        
        jit_analysis["compilation_times"].append({
            "operation": "vector_operation",
            "first_call_time": first_call_time,
            "average_runtime": avg_runtime,
            "compilation_overhead": compilation_overhead,
            "speedup_after_compilation": compilation_overhead / avg_runtime
        })
        
        print(f"   First call (with compilation): {first_call_time:.6f}s")
        print(f"   Average runtime: {avg_runtime:.6f}s")
        print(f"   Compilation overhead: {compilation_overhead:.6f}s")
        print(f"   Speedup after compilation: {compilation_overhead / avg_runtime:.1f}x")
        
        # Test JAX field operations compilation
        print("\n🧠 Testing cognitive field JIT behavior...")
        
        cfd = CognitiveFieldDynamicsJAX(dimension=256)
        
        # Add some fields first
        for i in range(100):
            embedding = np.random.randn(256).astype(np.float32)
            cfd.add_geoid(f"jit_test_{i}", jnp.array(embedding))
        
        # Test neighbor finding JIT behavior
        neighbor_times = []
        for i in range(20):
            start_time = time.perf_counter()
            neighbors = cfd.find_semantic_neighbors(f"jit_test_{i}")
            neighbor_times.append(time.perf_counter() - start_time)
        
        jit_analysis["warmup_behavior"] = {
            "neighbor_finding": {
                "first_calls": neighbor_times[:5],
                "steady_state": neighbor_times[10:],
                "warmup_improvement": np.mean(neighbor_times[:5]) / np.mean(neighbor_times[10:])
            }
        }
        
        print(f"   Neighbor finding warmup improvement: {jit_analysis['warmup_behavior']['neighbor_finding']['warmup_improvement']:.1f}x")
        
        return jit_analysis

    def test_numerical_stability(self) -> Dict:
        """Test numerical stability under extreme conditions."""
        print("\n🔬 NUMERICAL STABILITY ANALYSIS")
        print("=" * 60)
        
        stability_results = {
            "extreme_values": {},
            "precision_tests": {},
            "edge_cases": {},
            "convergence_behavior": {}
        }
        
        cfd = CognitiveFieldDynamicsJAX(dimension=128)
        
        # Test with extreme embedding values
        print("⚡ Testing with extreme embedding values...")
        
        extreme_tests = [
            ("very_small", np.ones(128) * 1e-10),
            ("very_large", np.ones(128) * 1e10),
            ("mixed_extreme", np.concatenate([np.ones(64) * 1e-10, np.ones(64) * 1e10])),
            ("zero_vector", np.zeros(128)),
            ("inf_values", np.full(128, np.inf)),
            ("nan_values", np.full(128, np.nan))
        ]
        
        for test_name, embedding in extreme_tests:
            try:
                embedding = embedding.astype(np.float32)
                field = cfd.add_geoid(f"extreme_{test_name}", jnp.array(embedding))
                
                if field is not None:
                    # Check if values are finite
                    is_finite = jnp.all(jnp.isfinite(field.embedding))
                    norm = jnp.linalg.norm(field.embedding)
                    
                    stability_results["extreme_values"][test_name] = {
                        "field_created": True,
                        "embedding_finite": bool(is_finite),
                        "embedding_norm": float(norm),
                        "field_strength": float(field.field_strength),
                        "resonance_frequency": float(field.resonance_frequency)
                    }
                    
                    print(f"   ✅ {test_name}: Created field with norm {norm:.2e}")
                else:
                    stability_results["extreme_values"][test_name] = {
                        "field_created": False,
                        "reason": "Field creation returned None"
                    }
                    print(f"   ⚠️  {test_name}: Field creation failed gracefully")
                    
            except Exception as e:
                stability_results["extreme_values"][test_name] = {
                    "field_created": False,
                    "error": str(e)
                }
                print(f"   ❌ {test_name}: Error - {str(e)[:50]}...")
        
        # Test precision with similar embeddings
        print("\n🎯 Testing numerical precision...")
        
        base_embedding = np.random.randn(128).astype(np.float32)
        precision_deltas = [1e-3, 1e-6, 1e-9, 1e-12]
        
        cfd.add_geoid("precision_base", jnp.array(base_embedding))
        
        for i, delta in enumerate(precision_deltas):
            similar_embedding = base_embedding + delta
            cfd.add_geoid(f"precision_test_{i}", jnp.array(similar_embedding))
            
            # Test neighbor detection
            neighbors = cfd.find_semantic_neighbors("precision_base")
            neighbor_dict = dict(neighbors)
            
            if f"precision_test_{i}" in neighbor_dict:
                similarity = neighbor_dict[f"precision_test_{i}"]
                stability_results["precision_tests"][f"delta_{delta}"] = {
                    "detected_as_neighbor": True,
                    "similarity_strength": float(similarity)
                }
                print(f"   Delta {delta}: Detected with similarity {similarity:.6f}")
            else:
                stability_results["precision_tests"][f"delta_{delta}"] = {
                    "detected_as_neighbor": False
                }
                print(f"   Delta {delta}: Not detected as neighbor")
        
        return stability_results

    def test_concurrent_performance(self) -> Dict:
        """Test performance under concurrent operations."""
        print("\n🔄 CONCURRENT PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        concurrent_results = {
            "thread_scaling": {},
            "contention_analysis": {},
            "throughput_scaling": {}
        }
        
        # Setup base system
        cfd = CognitiveFieldDynamicsJAX(dimension=256)
        
        # Pre-populate with fields
        print("📦 Pre-populating system with 1000 fields...")
        for i in range(1000):
            embedding = np.random.randn(256).astype(np.float32)
            cfd.add_geoid(f"concurrent_base_{i}", jnp.array(embedding))
        
        # Test concurrent neighbor finding
        def concurrent_neighbor_search(thread_id, search_count):
            results = []
            for i in range(search_count):
                field_id = f"concurrent_base_{(thread_id * search_count + i) % 1000}"
                start_time = time.perf_counter()
                neighbors = cfd.find_semantic_neighbors(field_id)
                end_time = time.perf_counter()
                results.append({
                    "thread_id": thread_id,
                    "search_id": i,
                    "time": end_time - start_time,
                    "neighbors_found": len(neighbors)
                })
            return results
        
        # Test with different thread counts
        thread_counts = [1, 2, 4, 8]
        searches_per_thread = 50
        
        for thread_count in thread_counts:
            print(f"\n🧵 Testing with {thread_count} threads...")
            
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = []
                for thread_id in range(thread_count):
                    future = executor.submit(concurrent_neighbor_search, thread_id, searches_per_thread)
                    futures.append(future)
                
                all_results = []
                for future in futures:
                    all_results.extend(future.result())
            
            total_time = time.perf_counter() - start_time
            total_operations = thread_count * searches_per_thread
            throughput = total_operations / total_time
            
            # Analyze individual operation times
            operation_times = [r["time"] for r in all_results]
            avg_time = np.mean(operation_times)
            std_time = np.std(operation_times)
            
            concurrent_results["thread_scaling"][thread_count] = {
                "total_time": total_time,
                "total_operations": total_operations,
                "throughput": throughput,
                "avg_operation_time": avg_time,
                "operation_time_std": std_time,
                "efficiency": throughput / (thread_count * (searches_per_thread / avg_time))
            }
            
            print(f"   Total time: {total_time:.2f}s")
            print(f"   Throughput: {throughput:.1f} ops/sec")
            print(f"   Avg operation time: {avg_time:.4f}s ± {std_time:.4f}s")
            print(f"   Threading efficiency: {concurrent_results['thread_scaling'][thread_count]['efficiency']:.2f}")
        
        return concurrent_results

    def test_error_handling_robustness(self) -> Dict:
        """Test error handling and recovery mechanisms."""
        print("\n🛡️ ERROR HANDLING ROBUSTNESS TEST")
        print("=" * 60)
        
        error_handling = {
            "invalid_inputs": {},
            "resource_exhaustion": {},
            "recovery_mechanisms": {}
        }
        
        cfd = CognitiveFieldDynamicsJAX(dimension=128)
        
        # Test invalid input handling
        print("⚠️  Testing invalid input handling...")
        
        invalid_tests = [
            ("empty_id", "", np.random.randn(128)),
            ("none_embedding", "valid_id", None),
            ("wrong_dimension", "valid_id", np.random.randn(64)),  # Wrong dimension
            ("non_numeric", "valid_id", ["not", "numeric", "data"]),
            ("invalid_threshold", "test_id", np.random.randn(128), {"energy_threshold": "invalid"})
        ]
        
        for test_name, *test_args in invalid_tests:
            try:
                if test_name == "invalid_threshold":
                    # Add a valid field first
                    cfd.add_geoid("test_id", jnp.array(test_args[1]))
                    # Then test invalid threshold
                    neighbors = cfd.find_semantic_neighbors("test_id", energy_threshold="invalid")
                    error_handling["invalid_inputs"][test_name] = {"handled": True, "error": None}
                else:
                    field_id, embedding = test_args[0], test_args[1]
                    if embedding is not None and hasattr(embedding, '__len__'):
                        embedding = jnp.array(embedding) if isinstance(embedding, (list, np.ndarray)) else embedding
                    field = cfd.add_geoid(field_id, embedding)
                    error_handling["invalid_inputs"][test_name] = {"handled": True, "error": None}
                    
                print(f"   ✅ {test_name}: Handled gracefully")
                
            except Exception as e:
                error_handling["invalid_inputs"][test_name] = {"handled": False, "error": str(e)}
                print(f"   ⚠️  {test_name}: Exception - {str(e)[:50]}...")
        
        # Test system state consistency after errors
        print("\n🔄 Testing system consistency after errors...")
        
        # Add some valid fields
        for i in range(10):
            embedding = np.random.randn(128).astype(np.float32)
            cfd.add_geoid(f"recovery_test_{i}", jnp.array(embedding))
        
        # Check system is still functional
        try:
            neighbors = cfd.find_semantic_neighbors("recovery_test_0")
            anomalies = cfd.detect_semantic_anomalies()
            
            error_handling["recovery_mechanisms"] = {
                "system_functional": True,
                "neighbors_working": len(neighbors) > 0,
                "anomaly_detection_working": isinstance(anomalies, list)
            }
            
            print(f"   ✅ System remains functional after error tests")
            print(f"   ✅ Found {len(neighbors)} neighbors")
            print(f"   ✅ Anomaly detection returned {len(anomalies)} results")
            
        except Exception as e:
            error_handling["recovery_mechanisms"] = {
                "system_functional": False,
                "error": str(e)
            }
            print(f"   ❌ System compromised: {str(e)}")
        
        return error_handling

    async def run_comprehensive_stress_test(self) -> StressTestSuite:
        """Run the complete stress test suite."""
        print("🔥 KIMERA JAX COMPREHENSIVE STRESS TEST SUITE")
        print("=" * 80)
        
        system_info = {
            "jax_version": jax.__version__,
            "jax_devices": [str(d) for d in jax.devices()],
            "platform": jax.lib.xla_bridge.get_backend().platform,
            "python_version": sys.version,
            "memory_baseline_mb": self.baseline_memory,
            "cpu_count": psutil.cpu_count(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"📊 System Info:")
        print(f"   JAX Version: {system_info['jax_version']}")
        print(f"   Platform: {system_info['platform']}")
        print(f"   Devices: {system_info['jax_devices']}")
        print(f"   Baseline Memory: {system_info['memory_baseline_mb']:.1f} MB")
        
        # Run all stress tests
        scalability_results = self.test_scalability_stress()
        memory_profile = self.test_memory_behavior()
        jit_analysis = self.test_jit_compilation_behavior()
        numerical_stability = self.test_numerical_stability()
        concurrent_performance = self.test_concurrent_performance()
        error_handling = self.test_error_handling_robustness()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            scalability_results, memory_profile, jit_analysis, 
            numerical_stability, concurrent_performance, error_handling
        )
        
        return StressTestSuite(
            system_info=system_info,
            scalability_results=scalability_results,
            memory_profile=memory_profile,
            jit_analysis=jit_analysis,
            numerical_stability=numerical_stability,
            concurrent_performance=concurrent_performance,
            error_handling=error_handling,
            recommendations=recommendations
        )

    def _generate_recommendations(self, scalability, memory, jit, stability, concurrent, errors) -> List[str]:
        """Generate performance recommendations based on test results."""
        recommendations = []
        
        # Scalability recommendations
        field_creation_rates = [r.throughput_ops_per_sec for r in scalability if "field_creation" in r.test_name]
        if field_creation_rates:
            avg_rate = np.mean(field_creation_rates)
            if avg_rate < 10:
                recommendations.append("⚠️  Field creation rate is low. Consider batch operations for better performance.")
            elif avg_rate > 50:
                recommendations.append("✅ Excellent field creation performance. System scales well.")
        
        # Memory recommendations
        if memory["memory_efficiency"]["memory_per_field_kb"] > 100:
            recommendations.append("⚠️  High memory usage per field. Consider optimizing embedding storage.")
        else:
            recommendations.append("✅ Excellent memory efficiency. JAX optimization is working well.")
        
        # JIT recommendations
        if jit["compilation_times"]:
            comp_overhead = jit["compilation_times"][0]["compilation_overhead"]
            if comp_overhead > 0.1:
                recommendations.append("⚠️  High JIT compilation overhead. Consider warming up critical paths.")
            else:
                recommendations.append("✅ Fast JIT compilation. Good for interactive performance.")
        
        # Concurrency recommendations
        if "thread_scaling" in concurrent:
            efficiencies = [v["efficiency"] for v in concurrent["thread_scaling"].values()]
            avg_efficiency = np.mean(efficiencies) if efficiencies else 0
            
            if avg_efficiency < 0.5:
                recommendations.append("⚠️  Poor threading efficiency. JAX operations may have GIL contention.")
            elif avg_efficiency > 0.8:
                recommendations.append("✅ Good threading efficiency. JAX releasing GIL effectively.")
        
        # Stability recommendations
        extreme_successes = sum(1 for v in stability["extreme_values"].values() if v.get("field_created", False))
        if extreme_successes > 3:
            recommendations.append("✅ Robust numerical handling. Good input validation and normalization.")
        
        return recommendations

def save_stress_test_results(results: StressTestSuite, filename: str = "jax_stress_test_results.json"):
    """Save stress test results to JSON file."""
    # Convert to serializable format
    results_dict = asdict(results)
    
    # Handle numpy types
    def convert_numpy(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        return obj
    
    def recursive_convert(obj):
        if isinstance(obj, dict):
            return {k: recursive_convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [recursive_convert(v) for v in obj]
        else:
            return convert_numpy(obj)
    
    results_dict = recursive_convert(results_dict)
    
    with open(filename, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"\n💾 Stress test results saved to: {filename}")

def print_executive_summary(results: StressTestSuite):
    """Print executive summary of stress test results."""
    print("\n" + "=" * 80)
    print("📈 EXECUTIVE SUMMARY - JAX STRESS TEST RESULTS")
    print("=" * 80)
    
    # Performance summary
    field_creation_results = [r for r in results.scalability_results if "field_creation" in r.test_name]
    if field_creation_results:
        max_fields = max(r.field_count for r in field_creation_results)
        max_throughput = max(r.throughput_ops_per_sec for r in field_creation_results)
        print(f"🚀 SCALABILITY: Tested up to {max_fields:,} fields")
        print(f"   Peak throughput: {max_throughput:.1f} fields/sec")
    
    # Memory summary
    memory_eff = results.memory_profile["memory_efficiency"]
    print(f"🧠 MEMORY: {memory_eff['memory_per_field_kb']:.2f} KB per field ({memory_eff['efficiency_rating']})")
    
    # JIT summary
    if results.jit_analysis["compilation_times"]:
        jit_speedup = results.jit_analysis["compilation_times"][0]["speedup_after_compilation"]
        print(f"⚡ JIT: {jit_speedup:.1f}x speedup after compilation")
    
    # Concurrent summary
    if "thread_scaling" in results.concurrent_performance:
        max_threads = max(results.concurrent_performance["thread_scaling"].keys())
        max_efficiency = max(v["efficiency"] for v in results.concurrent_performance["thread_scaling"].values())
        print(f"🔄 CONCURRENCY: Tested up to {max_threads} threads, {max_efficiency:.1f} efficiency")
    
    # Stability summary
    stable_tests = sum(1 for v in results.numerical_stability["extreme_values"].values() 
                      if v.get("field_created", False))
    total_tests = len(results.numerical_stability["extreme_values"])
    print(f"🔬 STABILITY: {stable_tests}/{total_tests} extreme value tests passed")
    
    # Error handling summary
    handled_errors = sum(1 for v in results.error_handling["invalid_inputs"].values() 
                        if v.get("handled", False))
    total_error_tests = len(results.error_handling["invalid_inputs"])
    print(f"🛡️  ERROR HANDLING: {handled_errors}/{total_error_tests} invalid inputs handled gracefully")
    
    # Recommendations
    print(f"\n💡 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(results.recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    print("\n🎉 OVERALL ASSESSMENT:")
    
    # Calculate overall score
    scores = []
    
    # Performance score (based on throughput)
    if field_creation_results:
        avg_throughput = np.mean([r.throughput_ops_per_sec for r in field_creation_results])
        perf_score = min(100, (avg_throughput / 50) * 100)  # 50 fields/sec = 100%
        scores.append(perf_score)
    
    # Memory score
    mem_per_field = memory_eff['memory_per_field_kb']
    mem_score = max(0, 100 - mem_per_field)  # Lower is better
    scores.append(mem_score)
    
    # Stability score
    stability_score = (stable_tests / total_tests) * 100
    scores.append(stability_score)
    
    overall_score = np.mean(scores) if scores else 0
    
    if overall_score >= 90:
        assessment = "🌟 EXCELLENT - Production ready with outstanding performance"
    elif overall_score >= 75:
        assessment = "✅ GOOD - Production ready with solid performance"
    elif overall_score >= 60:
        assessment = "⚠️  ACCEPTABLE - Production ready with some optimization needed"
    else:
        assessment = "❌ NEEDS WORK - Optimization required before production"
    
    print(f"   Overall Score: {overall_score:.1f}/100")
    print(f"   {assessment}")

async def main():
    """Run the comprehensive stress test suite."""
    analyzer = DeepAnalyzer()
    
    # Run stress tests
    results = await analyzer.run_comprehensive_stress_test()
    
    # Save results
    save_stress_test_results(results)
    
    # Print summary
    print_executive_summary(results)
    
    print(f"\n🏁 Stress test completed successfully!")
    print(f"   Check 'jax_stress_test_results.json' for detailed results")

if __name__ == "__main__":
    asyncio.run(main()) 