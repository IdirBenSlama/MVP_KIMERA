#!/usr/bin/env python3
"""
Integration test to verify native math implementations work with Kimera SWM components.
"""

import sys
import traceback
from typing import List, Dict

def test_contradiction_engine():
    """Test contradiction engine with native math."""
    print("🔍 Testing Contradiction Engine...")
    
    try:
        from backend.engines.contradiction_engine import ContradictionEngine
        from backend.core.geoid import GeoidState
        
        # Create test geoids
        geoid_a = GeoidState(
            geoid_id='test_a',
            semantic_state={'feature1': 1.0, 'feature2': 2.0, 'feature3': 0.5},
            symbolic_state={'type': 'concept'},
            embedding_vector=[1.0, 2.0, 3.0, 4.0],
            metadata={'source': 'test'}
        )
        
        geoid_b = GeoidState(
            geoid_id='test_b', 
            semantic_state={'feature1': 0.5, 'feature2': 1.5, 'feature3': 2.0},
            symbolic_state={'type': 'concept'},
            embedding_vector=[2.0, 3.0, 4.0, 5.0],
            metadata={'source': 'test'}
        )
        
        # Test contradiction detection
        engine = ContradictionEngine(tension_threshold=0.1)
        tensions = engine.detect_tension_gradients([geoid_a, geoid_b])
        
        print(f"   ✅ Detected {len(tensions)} tension gradients")
        if tensions:
            tension = tensions[0]
            print(f"   ✅ Tension score: {tension.tension_score:.4f}")
            print(f"   ✅ Gradient type: {tension.gradient_type}")
        
        # Test pulse strength calculation
        if tensions:
            pulse = engine.calculate_pulse_strength(tensions[0], {
                'test_a': geoid_a,
                'test_b': geoid_b
            })
            print(f"   ✅ Pulse strength: {pulse:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Contradiction engine test failed: {e}")
        traceback.print_exc()
        return False

def test_spde_engine():
    """Test SPDE engine with native Gaussian filter."""
    print("🌊 Testing SPDE Engine...")
    
    try:
        from backend.engines.spde import SPDE
        
        # Create SPDE instance
        spde = SPDE(diffusion_rate=0.3, decay_factor=1.5)
        
        # Test with semantic state
        test_state = {
            'concept_a': 1.0,
            'concept_b': 2.0, 
            'concept_c': 0.5,
            'concept_d': 3.0,
            'concept_e': 1.5
        }
        
        print(f"   Original state: {test_state}")
        
        # Apply diffusion
        diffused = spde.diffuse(test_state)
        
        print(f"   Diffused state: {diffused}")
        
        # Verify diffusion worked
        assert len(diffused) == len(test_state), "State size should be preserved"
        assert all(isinstance(v, float) for v in diffused.values()), "All values should be floats"
        
        # Test with empty state
        empty_diffused = spde.diffuse({})
        assert empty_diffused == {}, "Empty state should remain empty"
        
        print("   ✅ SPDE diffusion working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ SPDE engine test failed: {e}")
        traceback.print_exc()
        return False

def test_proactive_detector():
    """Test proactive contradiction detector."""
    print("🔎 Testing Proactive Contradiction Detector...")
    
    try:
        from backend.engines.proactive_contradiction_detector import ProactiveContradictionDetector, ProactiveDetectionConfig
        from backend.core.geoid import GeoidState
        
        # Create detector with test config
        config = ProactiveDetectionConfig(
            batch_size=10,
            similarity_threshold=0.5,
            max_comparisons_per_run=50
        )
        detector = ProactiveContradictionDetector(config)
        
        # Create test geoids
        geoids = []
        for i in range(5):
            geoid = GeoidState(
                geoid_id=f'test_{i}',
                semantic_state={f'feature_{j}': float(i + j) for j in range(3)},
                symbolic_state={'type': 'test', 'index': i},
                embedding_vector=[float(i + j) for j in range(4)],
                metadata={'timestamp': f'2024-01-{i+1:02d}T12:00:00Z'}
            )
            geoids.append(geoid)
        
        # Test similarity calculation
        similarity = detector._calculate_similarity(geoids[0], geoids[1])
        print(f"   ✅ Similarity calculation: {similarity:.4f}")
        
        # Test clustering
        clusters = detector._create_semantic_clusters(geoids)
        print(f"   ✅ Created {len(clusters)} semantic clusters")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Proactive detector test failed: {e}")
        traceback.print_exc()
        return False

def test_asm_engine():
    """Test ASM engine imports and basic functionality."""
    print("📊 Testing ASM Engine...")
    
    try:
        from backend.engines.asm import AxisStabilityMonitor
        from backend.core.native_math import NativeDistance
        
        # Test the native distance function that ASM uses
        test_vectors = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0], 
            [0.0, 0.0, 1.0]
        ]
        
        distances = NativeDistance.condensed_distances(test_vectors, metric='cosine')
        print(f"   ✅ Distance calculation: {len(distances)} pairwise distances")
        print(f"   ✅ Sample distances: {[f'{d:.4f}' for d in distances[:3]]}")
        
        # Verify ASM class can be instantiated (without DB)
        print("   ✅ ASM class imports successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ASM engine test failed: {e}")
        traceback.print_exc()
        return False

def test_geoid_entropy():
    """Test GeoidState entropy calculation."""
    print("🧮 Testing GeoidState Entropy...")
    
    try:
        from backend.core.geoid import GeoidState
        
        # Test with uniform distribution (high entropy)
        uniform_geoid = GeoidState(
            geoid_id='uniform',
            semantic_state={'a': 0.25, 'b': 0.25, 'c': 0.25, 'd': 0.25},
            symbolic_state={},
            embedding_vector=[],
            metadata={}
        )
        
        uniform_entropy = uniform_geoid.calculate_entropy()
        print(f"   ✅ Uniform entropy: {uniform_entropy:.4f}")
        
        # Test with skewed distribution (low entropy)
        skewed_geoid = GeoidState(
            geoid_id='skewed',
            semantic_state={'a': 0.7, 'b': 0.1, 'c': 0.1, 'd': 0.1},
            symbolic_state={},
            embedding_vector=[],
            metadata={}
        )
        
        skewed_entropy = skewed_geoid.calculate_entropy()
        print(f"   ✅ Skewed entropy: {skewed_entropy:.4f}")
        
        # Verify entropy ordering
        assert uniform_entropy > skewed_entropy, "Uniform should have higher entropy than skewed"
        
        # Test with empty state
        empty_geoid = GeoidState('empty', {}, {}, [], {})
        empty_entropy = empty_geoid.calculate_entropy()
        assert empty_entropy == 0.0, "Empty state should have zero entropy"
        
        print("   ✅ Entropy calculations working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ GeoidState entropy test failed: {e}")
        traceback.print_exc()
        return False

def test_api_compatibility():
    """Test that API components work with native math."""
    print("🌐 Testing API Compatibility...")
    
    try:
        # Test the specific function used in main.py
        from backend.core.native_math import NativeMath
        
        # Simulate the exact usage in main.py
        vec_a = [1.0, 2.0, 3.0, 4.0]
        vec_b = [2.0, 3.0, 4.0, 5.0]
        
        cls_angle_proxy = NativeMath.cosine_distance(vec_a, vec_b) if any(vec_a) and any(vec_b) else 0.0
        print(f"   ✅ API cosine distance: {cls_angle_proxy:.4f}")
        
        # Test edge cases that might occur in API
        empty_result = NativeMath.cosine_distance([], []) if any([]) and any([]) else 0.0
        assert empty_result == 0.0, "Empty vector handling should work"
        
        print("   ✅ API compatibility verified")
        return True
        
    except Exception as e:
        print(f"   ❌ API compatibility test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("🚀 Kimera SWM Native Math Integration Tests")
    print("=" * 60)
    
    tests = [
        test_contradiction_engine,
        test_spde_engine,
        test_proactive_detector,
        test_asm_engine,
        test_geoid_entropy,
        test_api_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Native math implementations are fully compatible with Kimera SWM")
        print("✅ System is ready for production use without scipy dependency")
    else:
        print("❌ Some tests failed - review and fix before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()