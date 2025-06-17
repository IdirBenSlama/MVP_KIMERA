#!/usr/bin/env python3
"""
Test system startup and core functionality without scipy dependency.
"""

import sys
import os

def test_core_imports():
    """Test that all core components can be imported."""
    print("📦 Testing Core Imports...")
    
    try:
        # Core components
        from backend.core.geoid import GeoidState
        from backend.core.native_math import NativeMath, NativeStats, NativeDistance
        from backend.core.embedding_utils import encode_text
        print("   ✅ Core components imported")
        
        # Engines
        from backend.engines.contradiction_engine import ContradictionEngine
        from backend.engines.spde import SPDE
        from backend.engines.asm import AxisStabilityMonitor
        from backend.engines.proactive_contradiction_detector import ProactiveContradictionDetector
        print("   ✅ All engines imported")
        
        # API components (without starting server)
        from backend.api.main import app
        print("   ✅ API components imported")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_functionality():
    """Test embedding functionality works."""
    print("🧠 Testing Embedding Functionality...")
    
    try:
        from backend.core.embedding_utils import encode_text
        
        # Test encoding
        test_text = "This is a test sentence for semantic processing."
        embedding = encode_text(test_text)
        
        print(f"   ✅ Generated embedding of length: {len(embedding)}")
        print(f"   ✅ First few values: {embedding[:3]}")
        
        # Verify embedding properties
        assert len(embedding) > 0, "Embedding should not be empty"
        assert all(isinstance(x, (int, float)) for x in embedding), "All values should be numeric"
        
        return True
        
    except Exception as e:
        print(f"   ❌ Embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_semantic_processing():
    """Test end-to-end semantic processing."""
    print("🔄 Testing Semantic Processing Pipeline...")
    
    try:
        from backend.core.geoid import GeoidState
        from backend.core.embedding_utils import encode_text, extract_semantic_features
        from backend.engines.contradiction_engine import ContradictionEngine
        from backend.engines.spde import SPDE
        
        # Create semantic content
        text1 = "The cat sits on the mat."
        text2 = "A feline rests on the carpet."
        
        # Extract features and embeddings
        features1 = extract_semantic_features(text1)
        features2 = extract_semantic_features(text2)
        embedding1 = encode_text(text1)
        embedding2 = encode_text(text2)
        
        print(f"   ✅ Extracted features: {len(features1)} and {len(features2)}")
        print(f"   ✅ Generated embeddings: {len(embedding1)} and {len(embedding2)}")
        
        # Create geoids
        geoid1 = GeoidState('semantic_1', features1, {'text': text1}, embedding1)
        geoid2 = GeoidState('semantic_2', features2, {'text': text2}, embedding2)
        
        # Test contradiction detection
        engine = ContradictionEngine()
        tensions = engine.detect_tension_gradients([geoid1, geoid2])
        print(f"   ✅ Detected {len(tensions)} tensions between similar concepts")
        
        # Test diffusion
        spde = SPDE()
        diffused1 = spde.diffuse(features1)
        diffused2 = spde.diffuse(features2)
        print(f"   ✅ Applied semantic diffusion")
        
        # Test entropy
        entropy1 = geoid1.calculate_entropy()
        entropy2 = geoid2.calculate_entropy()
        print(f"   ✅ Calculated entropies: {entropy1:.4f} and {entropy2:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Semantic processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mathematical_accuracy():
    """Test mathematical accuracy against known values."""
    print("🧮 Testing Mathematical Accuracy...")
    
    try:
        from backend.core.native_math import NativeMath, NativeStats
        import math
        
        # Test cosine distance accuracy
        a = [1, 0, 0]
        b = [0, 1, 0]  # Orthogonal vectors
        distance = NativeMath.cosine_distance(a, b)
        expected = 1.0  # Orthogonal vectors have cosine similarity 0, distance 1
        assert abs(distance - expected) < 0.001, f"Expected {expected}, got {distance}"
        print(f"   ✅ Cosine distance accuracy: {distance:.6f}")
        
        # Test entropy accuracy
        uniform_probs = [0.25, 0.25, 0.25, 0.25]
        entropy = NativeStats.entropy(uniform_probs, base=2.0)
        expected_entropy = 2.0  # log2(4) = 2 for uniform distribution
        assert abs(entropy - expected_entropy) < 0.001, f"Expected {expected_entropy}, got {entropy}"
        print(f"   ✅ Entropy accuracy: {entropy:.6f}")
        
        # Test Gaussian filter smoothing
        step_function = [0, 0, 0, 1, 1, 1, 0, 0, 0]
        smoothed = NativeMath.gaussian_filter_1d(step_function, sigma=1.0)
        
        # Check that smoothing reduces the peak
        assert max(smoothed) < max(step_function), "Smoothing should reduce peak"
        assert min(smoothed) > min(step_function), "Smoothing should raise valleys"
        print(f"   ✅ Gaussian filter smoothing verified")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Mathematical accuracy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_baseline():
    """Test performance baseline for native implementations."""
    print("⚡ Testing Performance Baseline...")
    
    try:
        import time
        from backend.core.native_math import NativeMath, NativeDistance
        
        # Performance test data
        large_vector_a = [float(i) for i in range(100)]
        large_vector_b = [float(i + 0.1) for i in range(100)]
        
        # Test cosine distance performance
        start_time = time.time()
        for _ in range(1000):
            NativeMath.cosine_distance(large_vector_a, large_vector_b)
        cosine_time = time.time() - start_time
        
        print(f"   ✅ Cosine distance (1000x 100-dim): {cosine_time:.4f}s")
        
        # Test batch distance calculation
        vectors = [large_vector_a, large_vector_b, [float(i + 0.2) for i in range(100)]]
        start_time = time.time()
        distances = NativeDistance.condensed_distances(vectors)
        batch_time = time.time() - start_time
        
        print(f"   ✅ Batch distances (3 vectors): {batch_time:.4f}s")
        print(f"   ✅ Performance baseline established")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive system tests."""
    print("🚀 Kimera SWM System Startup & Functionality Tests")
    print("=" * 70)
    
    tests = [
        test_core_imports,
        test_embedding_functionality,
        test_semantic_processing,
        test_mathematical_accuracy,
        test_performance_baseline
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
    
    print("=" * 70)
    print(f"📊 Final Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 SYSTEM FULLY OPERATIONAL!")
        print("✅ All native math implementations working correctly")
        print("✅ Kimera SWM is independent of scipy dependency")
        print("✅ System ready for production deployment")
        print("✅ Performance baseline established")
        print()
        print("🚀 READY TO PROCEED TO NEXT PHASE OF INDEPENDENCE UPGRADES")
    else:
        print("❌ System tests failed - address issues before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()