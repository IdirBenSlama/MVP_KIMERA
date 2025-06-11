#!/usr/bin/env python3
"""
Test script for Kimera SWM Monitoring System

This script tests the core monitoring functionality to ensure everything works correctly.
"""

import sys
import os
import numpy as np
from datetime import datetime

# Add the backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.geoid import GeoidState
from backend.core.models import LinguisticGeoid
from backend.monitoring.entropy_monitor import EntropyMonitor
from backend.monitoring.semantic_metrics import SemanticMetricsCollector
from backend.monitoring.thermodynamic_analyzer import ThermodynamicAnalyzer
from backend.monitoring.system_observer import SystemObserver
from backend.monitoring.benchmarking_suite import benchmark_runner

def create_test_geoids(count=10):
    """Create test geoids for monitoring"""
    geoids = []
    for i in range(count):
        semantic_state = {
            f'feature_{j}': np.random.random() 
            for j in range(np.random.randint(3, 8))
        }
        
        geoid = GeoidState(
            geoid_id=f'test_geoid_{i}',
            semantic_state=semantic_state,
            symbolic_state={'type': 'test', 'index': i},
            metadata={'created': datetime.now().isoformat()}
        )
        geoids.append(geoid)
    
    return geoids

def create_test_linguistic_geoids(geoids):
    """Create test linguistic geoids"""
    linguistic_geoids = []
    
    for i, geoid in enumerate(geoids[:5]):  # Only first 5
        lg = LinguisticGeoid(
            primary_statement=f"Test statement for geoid {geoid.geoid_id}",
            confidence_score=np.random.uniform(0.6, 1.0),
            source_geoid_id=geoid.geoid_id,
            supporting_scars=[],
            potential_ambiguities=[f'ambiguity_{j}' for j in range(np.random.randint(0, 3))],
            explanation_lineage=f'test_lineage_{i}'
        )
        linguistic_geoids.append(lg)
    
    return linguistic_geoids

def test_entropy_monitor():
    """Test the entropy monitoring system"""
    print("🧪 Testing Entropy Monitor...")
    
    entropy_monitor = EntropyMonitor()
    geoids = create_test_geoids(20)
    
    vault_info = {
        'vault_a_scars': 15,
        'vault_b_scars': 12,
        'active_geoids': len(geoids)
    }
    
    # Set baseline
    entropy_monitor.set_baseline(geoids[:10])
    
    # Calculate entropy
    measurement = entropy_monitor.calculate_system_entropy(geoids, vault_info)
    
    print(f"  ✅ Shannon Entropy: {measurement.shannon_entropy:.4f}")
    print(f"  ✅ Thermodynamic Entropy: {measurement.thermodynamic_entropy:.4f}")
    print(f"  ✅ Relative Entropy: {measurement.relative_entropy:.4f}")
    print(f"  ✅ System Complexity: {measurement.system_complexity:.4f}")
    
    # Test trends
    for _ in range(5):
        measurement = entropy_monitor.calculate_system_entropy(geoids, vault_info)
    
    trends = entropy_monitor.get_entropy_trends(window_size=5)
    print(f"  ✅ Trend data points: {len(trends.get('shannon_entropy', []))}")
    
    # Test anomaly detection
    anomalies = entropy_monitor.detect_entropy_anomalies()
    print(f"  ✅ Anomalies detected: {len(anomalies)}")
    
    return True

def test_semantic_metrics():
    """Test the semantic metrics collection"""
    print("🧠 Testing Semantic Metrics Collector...")
    
    semantic_collector = SemanticMetricsCollector()
    geoids = create_test_geoids(15)
    linguistic_geoids = create_test_linguistic_geoids(geoids)
    
    # Collect metrics
    measurement = semantic_collector.collect_semantic_metrics(
        geoids, linguistic_geoids, 'analytical'
    )
    
    print(f"  ✅ Semantic Entropy: {measurement.semantic_entropy:.4f}")
    print(f"  ✅ Meaning Density: {measurement.meaning_density:.4f}")
    print(f"  ✅ Context Coherence: {measurement.context_coherence:.4f}")
    print(f"  ✅ Semantic Efficiency: {measurement.semantic_efficiency:.4f}")
    print(f"  ✅ Information Utility: {measurement.information_utility:.4f}")
    
    # Test trends
    for context in ['analytical', 'creative', 'balanced']:
        measurement = semantic_collector.collect_semantic_metrics(
            geoids, linguistic_geoids, context
        )
    
    trends = semantic_collector.get_semantic_trends(window_size=3)
    print(f"  ✅ Trend data points: {len(trends.get('semantic_entropy', []))}")
    
    # Test anomaly detection
    anomalies = semantic_collector.detect_semantic_anomalies()
    print(f"  ✅ Anomalies detected: {len(anomalies)}")
    
    return True

def test_thermodynamic_analyzer():
    """Test the thermodynamic analysis"""
    print("🔥 Testing Thermodynamic Analyzer...")
    
    thermodynamic_analyzer = ThermodynamicAnalyzer()
    geoids = create_test_geoids(25)
    
    vault_info = {
        'vault_a_scars': 20,
        'vault_b_scars': 18,
        'active_geoids': len(geoids)
    }
    
    # Analyze state
    state = thermodynamic_analyzer.analyze_thermodynamic_state(
        geoids, vault_info, 2.5  # system entropy
    )
    
    print(f"  ✅ Total Energy: {state.total_energy:.4f}")
    print(f"  ✅ Temperature: {state.temperature:.4f}")
    print(f"  ✅ Pressure: {state.pressure:.4f}")
    print(f"  ✅ Free Energy: {state.free_energy:.4f}")
    print(f"  ✅ Efficiency: {state.efficiency:.4f}")
    
    # Test multiple states for trends
    for _ in range(3):
        # Modify geoids slightly
        for geoid in geoids:
            for feature in geoid.semantic_state:
                geoid.semantic_state[feature] += np.random.normal(0, 0.05)
            geoid.__post_init__()
        
        state = thermodynamic_analyzer.analyze_thermodynamic_state(
            geoids, vault_info, 2.5
        )
    
    # Test efficiency calculation
    efficiency = thermodynamic_analyzer.calculate_thermodynamic_efficiency()
    print(f"  ✅ Efficiency metrics: {len(efficiency)} measures")
    
    # Test constraint checking
    violations = thermodynamic_analyzer.check_thermodynamic_constraints(state)
    print(f"  ✅ Constraint violations: {len(violations)}")
    
    return True

def test_system_observer():
    """Test the integrated system observer"""
    print("👁️ Testing System Observer...")
    
    system_observer = SystemObserver()
    geoids = create_test_geoids(30)
    linguistic_geoids = create_test_linguistic_geoids(geoids)
    
    vault_info = {
        'vault_a_scars': 25,
        'vault_b_scars': 22,
        'active_geoids': len(geoids)
    }
    
    # Test different observer contexts
    for context in ['analytical', 'operational', 'research', 'default']:
        system_observer.set_observer_context(context)
        snapshot = system_observer.observe_system(geoids, linguistic_geoids, vault_info)
        
        print(f"  ✅ {context.capitalize()} observation complete")
        print(f"    - Overall Health: {snapshot.system_health['overall_health']:.3f}")
        print(f"    - Shannon Entropy: {snapshot.entropy_measurement.shannon_entropy:.3f}")
        print(f"    - Semantic Efficiency: {snapshot.semantic_measurement.semantic_efficiency:.3f}")
    
    # Test summary generation
    summary = system_observer.get_system_summary()
    print(f"  ✅ System summary generated with {summary.get('observation_count', 0)} observations")
    
    # Test report generation
    for report_type in ['comprehensive', 'executive', 'technical']:
        report = system_observer.generate_report(report_type)
        print(f"  ✅ {report_type.capitalize()} report generated ({len(report)} chars)")
    
    return True

def test_benchmarking_suite():
    """Test the benchmarking system"""
    print("🧪 Testing Benchmarking Suite...")
    
    # Test individual benchmark functions
    try:
        # Test entropy estimator comparison
        result = benchmark_runner.run_test('entropy_estimator_comparison')
        print(f"  ✅ Entropy estimator test: {'PASSED' if result.success else 'FAILED'}")
        if result.success:
            print(f"    - Duration: {result.duration:.3f}s")
            print(f"    - Metrics: {len(result.metrics)} measures")
        
        # Test thermodynamic consistency
        result = benchmark_runner.run_test('thermodynamic_consistency')
        print(f"  ✅ Thermodynamic test: {'PASSED' if result.success else 'FAILED'}")
        if result.success:
            print(f"    - Duration: {result.duration:.3f}s")
            print(f"    - Energy conservation error: {result.metrics.get('energy_conservation_error', 'N/A')}")
        
        # Test semantic processing
        text_samples = [
            "This is a test of semantic processing capabilities",
            "Analyzing information content and meaning density",
            "Evaluating semantic thermodynamic principles"
        ]
        result = benchmark_runner.run_test('semantic_processing', {'text_samples': text_samples})
        print(f"  ✅ Semantic processing test: {'PASSED' if result.success else 'FAILED'}")
        if result.success:
            print(f"    - Duration: {result.duration:.3f}s")
            print(f"    - Throughput: {result.metrics.get('throughput', 'N/A'):.1f} texts/sec")
        
        # Test benchmark suite
        suite_results = benchmark_runner.run_suite('entropy_suite')
        passed = sum(1 for r in suite_results.values() if r.success)
        total = len(suite_results)
        print(f"  ✅ Entropy suite: {passed}/{total} tests passed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Benchmarking test failed: {e}")
        return False

def main():
    """Run all monitoring system tests"""
    print("🧠 Kimera SWM Monitoring System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Entropy Monitor", test_entropy_monitor),
        ("Semantic Metrics", test_semantic_metrics),
        ("Thermodynamic Analyzer", test_thermodynamic_analyzer),
        ("System Observer", test_system_observer),
        ("Benchmarking Suite", test_benchmarking_suite)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}")
            print("-" * len(test_name))
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The monitoring system is ready to use.")
        print("\nNext steps:")
        print("1. Start the API server: python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8001")
        print("2. Launch the monitoring dashboard: python launch_monitoring.py")
        print("3. Access the dashboard at: file:///path/to/monitoring_dashboard.html")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
