"""
Benchmarking Suite for Kimera SWM

Implements comprehensive benchmarking capabilities following the computational tools
specification. Provides standardized tests and comparisons for entropy measures,
semantic processing, and thermodynamic analysis.
"""

import numpy as np
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
import traceback

from ..core.geoid import GeoidState
from ..core.models import LinguisticGeoid
from .entropy_monitor import EntropyMonitor, EntropyEstimator
from .semantic_metrics import SemanticMetricsCollector, SemanticAnalyzer
from .thermodynamic_analyzer import ThermodynamicAnalyzer, ThermodynamicCalculator
from .system_observer import SystemObserver


@dataclass
class BenchmarkResult:
    """Container for benchmark test results"""
    test_name: str
    timestamp: datetime
    duration: float
    success: bool
    metrics: Dict[str, float]
    parameters: Dict[str, Any]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSuite:
    """Configuration for a benchmark suite"""
    name: str
    description: str
    tests: List[str]
    parameters: Dict[str, Any]
    expected_results: Dict[str, Dict[str, float]]
    tolerance: float = 0.1


class StandardBenchmarks:
    """
    Standard benchmark tests for entropy and thermodynamic calculations
    Following the computational tools specification
    """
    
    @staticmethod
    def entropy_estimator_comparison(sample_sizes: List[int] = [100, 500, 1000, 5000]) -> Dict[str, Any]:
        """
        Compare different entropy estimators as recommended in the specification
        Tests MLE, Miller-Madow, and Chao-Shen estimators
        """
        results = {}
        
        # Generate known distribution for testing
        true_probs = np.array([0.5, 0.3, 0.15, 0.05])  # Known distribution
        true_entropy = EntropyEstimator.shannon_entropy_mle(true_probs)
        
        for sample_size in sample_sizes:
            # Generate samples from known distribution
            samples = np.random.choice(len(true_probs), size=sample_size, p=true_probs)
            counts = np.bincount(samples, minlength=len(true_probs))
            observed_probs = counts / sample_size
            
            # Test different estimators
            mle_entropy = EntropyEstimator.shannon_entropy_mle(observed_probs)
            mm_entropy = EntropyEstimator.miller_madow_entropy(observed_probs, sample_size)
            cs_entropy = EntropyEstimator.chao_shen_entropy(counts)
            
            results[f'sample_size_{sample_size}'] = {
                'true_entropy': true_entropy,
                'mle_entropy': mle_entropy,
                'miller_madow_entropy': mm_entropy,
                'chao_shen_entropy': cs_entropy,
                'mle_error': abs(mle_entropy - true_entropy),
                'mm_error': abs(mm_entropy - true_entropy),
                'cs_error': abs(cs_entropy - true_entropy)
            }
        
        return results
    
    @staticmethod
    def thermodynamic_consistency_test(geoid_count: int = 100) -> Dict[str, Any]:
        """
        Test thermodynamic consistency (energy conservation, entropy increase)
        """
        # Generate test geoids
        geoids = []
        for i in range(geoid_count):
            semantic_state = {
                f'feature_{j}': np.random.random() for j in range(np.random.randint(3, 8))
            }
            geoids.append(GeoidState(
                geoid_id=f'test_geoid_{i}',
                semantic_state=semantic_state
            ))
        
        # Calculate initial state
        initial_energy = ThermodynamicCalculator.calculate_semantic_energy(geoids)
        initial_entropy = sum(geoid.calculate_entropy() for geoid in geoids)
        initial_temp = ThermodynamicCalculator.calculate_semantic_temperature(geoids)
        
        # Simulate transformation (add noise to semantic states)
        for geoid in geoids:
            for feature in geoid.semantic_state:
                geoid.semantic_state[feature] += np.random.normal(0, 0.1)
            geoid.__post_init__()  # Renormalize
        
        # Calculate final state
        final_energy = ThermodynamicCalculator.calculate_semantic_energy(geoids)
        final_entropy = sum(geoid.calculate_entropy() for geoid in geoids)
        final_temp = ThermodynamicCalculator.calculate_semantic_temperature(geoids)
        
        # Calculate work and heat
        work, heat = ThermodynamicCalculator.calculate_work_and_heat(
            initial_energy, final_energy, initial_entropy, final_entropy, initial_temp
        )
        
        return {
            'initial_energy': initial_energy,
            'final_energy': final_energy,
            'energy_change': final_energy - initial_energy,
            'initial_entropy': initial_entropy,
            'final_entropy': final_entropy,
            'entropy_change': final_entropy - initial_entropy,
            'work_done': work,
            'heat_dissipated': heat,
            'energy_conservation_error': abs((final_energy - initial_energy) - (work - heat)),
            'entropy_increase': final_entropy >= initial_entropy,
            'temperature_change': final_temp - initial_temp
        }
    
    @staticmethod
    def semantic_processing_benchmark(text_samples: List[str]) -> Dict[str, Any]:
        """
        Benchmark semantic processing capabilities
        """
        results = {}
        
        # Create test linguistic geoids
        linguistic_geoids = []
        for i, text in enumerate(text_samples):
            lg = LinguisticGeoid(
                primary_statement=text,
                confidence_score=np.random.uniform(0.5, 1.0),
                source_geoid_id=f'test_geoid_{i}',
                supporting_scars=[],
                potential_ambiguities=[f'ambiguity_{j}' for j in range(np.random.randint(0, 3))],
                explanation_lineage=f'test_lineage_{i}'
            )
            linguistic_geoids.append(lg)
        
        # Test semantic analysis
        start_time = time.time()
        semantic_entropy = SemanticAnalyzer.calculate_semantic_entropy(linguistic_geoids)
        processing_time = time.time() - start_time
        
        # Test meaning density
        all_text = ' '.join(text_samples)
        semantic_keywords = {'test', 'semantic', 'analysis', 'processing', 'information'}
        meaning_density = SemanticAnalyzer.measure_meaning_density(all_text, semantic_keywords)
        
        # Test syntax-to-semantics ratio
        avg_ratio = np.mean([
            SemanticAnalyzer.calculate_syntax_to_semantics_ratio(lg.primary_statement, lg.confidence_score)
            for lg in linguistic_geoids
        ])
        
        results = {
            'semantic_entropy': semantic_entropy,
            'meaning_density': meaning_density,
            'avg_syntax_semantics_ratio': avg_ratio,
            'processing_time': processing_time,
            'throughput': len(text_samples) / processing_time if processing_time > 0 else 0,
            'avg_confidence': np.mean([lg.confidence_score for lg in linguistic_geoids]),
            'total_ambiguities': sum(len(lg.potential_ambiguities) for lg in linguistic_geoids)
        }
        
        return results


class BenchmarkRunner:
    """
    Comprehensive benchmark runner for Kimera SWM monitoring system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results_history: List[BenchmarkResult] = []
        self.benchmark_suites: Dict[str, BenchmarkSuite] = {}
        self.test_registry: Dict[str, Callable] = {}
        
        # Initialize standard benchmarks
        self._register_standard_benchmarks()
        self._initialize_benchmark_suites()
    
    def _register_standard_benchmarks(self):
        """Register standard benchmark tests"""
        self.test_registry.update({
            'entropy_estimator_comparison': StandardBenchmarks.entropy_estimator_comparison,
            'thermodynamic_consistency': StandardBenchmarks.thermodynamic_consistency_test,
            'semantic_processing': StandardBenchmarks.semantic_processing_benchmark
        })
    
    def _initialize_benchmark_suites(self):
        """Initialize predefined benchmark suites"""
        
        # Entropy benchmarking suite
        self.benchmark_suites['entropy_suite'] = BenchmarkSuite(
            name='Entropy Benchmarking Suite',
            description='Comprehensive entropy calculation and estimation benchmarks',
            tests=['entropy_estimator_comparison', 'thermodynamic_consistency'],
            parameters={
                'sample_sizes': [100, 500, 1000],
                'geoid_count': 100,
                'tolerance': 0.1
            },
            expected_results={
                'entropy_estimator_comparison': {
                    'cs_error_improvement': 0.8,  # Chao-Shen should be better than MLE
                    'mm_error_improvement': 0.9   # Miller-Madow should improve over MLE
                },
                'thermodynamic_consistency': {
                    'energy_conservation_error': 0.1,
                    'entropy_increase': 1.0  # Should always increase
                }
            }
        )
        
        # Semantic processing suite
        self.benchmark_suites['semantic_suite'] = BenchmarkSuite(
            name='Semantic Processing Suite',
            description='Semantic analysis and processing benchmarks',
            tests=['semantic_processing'],
            parameters={
                'text_samples': [
                    'This is a test of semantic processing capabilities',
                    'Analyzing information content and meaning density',
                    'Evaluating semantic thermodynamic principles'
                ]
            },
            expected_results={
                'semantic_processing': {
                    'min_throughput': 10.0,  # texts per second
                    'max_processing_time': 1.0  # seconds
                }
            }
        )
    
    def run_test(self, test_name: str, parameters: Optional[Dict[str, Any]] = None) -> BenchmarkResult:
        """Run a single benchmark test"""
        if test_name not in self.test_registry:
            raise ValueError(f"Unknown test: {test_name}")
        
        test_function = self.test_registry[test_name]
        start_time = datetime.now()
        
        try:
            # Run the test
            if parameters:
                if test_name == 'semantic_processing':
                    metrics = test_function(parameters.get('text_samples', []))
                elif test_name == 'entropy_estimator_comparison':
                    metrics = test_function(parameters.get('sample_sizes', [100, 500, 1000]))
                elif test_name == 'thermodynamic_consistency':
                    metrics = test_function(parameters.get('geoid_count', 100))
                else:
                    metrics = test_function(**parameters)
            else:
                metrics = test_function()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = BenchmarkResult(
                test_name=test_name,
                timestamp=start_time,
                duration=duration,
                success=True,
                metrics=metrics,
                parameters=parameters or {},
                metadata={
                    'test_function': test_function.__name__,
                    'execution_time': duration
                }
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Benchmark test {test_name} failed: {e}")
            
            result = BenchmarkResult(
                test_name=test_name,
                timestamp=start_time,
                duration=duration,
                success=False,
                metrics={},
                parameters=parameters or {},
                error_message=str(e),
                metadata={
                    'error_traceback': traceback.format_exc(),
                    'execution_time': duration
                }
            )
        
        self.results_history.append(result)
        return result
    
    def run_suite(self, suite_name: str) -> Dict[str, BenchmarkResult]:
        """Run a complete benchmark suite"""
        if suite_name not in self.benchmark_suites:
            raise ValueError(f"Unknown benchmark suite: {suite_name}")
        
        suite = self.benchmark_suites[suite_name]
        results = {}
        
        self.logger.info(f"Running benchmark suite: {suite.name}")
        
        for test_name in suite.tests:
            self.logger.info(f"Running test: {test_name}")
            
            # Use suite parameters if available
            test_params = suite.parameters.copy()
            result = self.run_test(test_name, test_params)
            results[test_name] = result
            
            if not result.success:
                self.logger.warning(f"Test {test_name} failed: {result.error_message}")
        
        return results
    
    def export_results(self, format: str = 'json') -> Any:
        """Export benchmark results"""
        if format == 'json':
            return {
                'export_timestamp': datetime.now().isoformat(),
                'total_results': len(self.results_history),
                'benchmark_suites': {
                    name: {
                        'name': suite.name,
                        'description': suite.description,
                        'tests': suite.tests,
                        'parameters': suite.parameters
                    } for name, suite in self.benchmark_suites.items()
                },
                'results': [
                    {
                        'test_name': r.test_name,
                        'timestamp': r.timestamp.isoformat(),
                        'duration': r.duration,
                        'success': r.success,
                        'metrics': r.metrics,
                        'parameters': r.parameters,
                        'error_message': r.error_message,
                        'metadata': r.metadata
                    }
                    for r in self.results_history
                ]
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global benchmark runner instance
benchmark_runner = BenchmarkRunner()