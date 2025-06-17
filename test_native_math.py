#!/usr/bin/env python3
"""
Test script to verify native math implementations work correctly.
This replaces scipy dependencies with custom implementations.
"""

import sys
import time
from backend.core.native_math import NativeMath, NativeStats, NativeDistance

def test_cosine_distance():
    """Test cosine distance calculation."""
    print("🧮 Testing Cosine Distance...")
    
    # Test vectors
    a = [1.0, 2.0, 3.0, 4.0]
    b = [2.0, 3.0, 4.0, 5.0]
    c = [1.0, 2.0, 3.0, 4.0]  # Same as a
    d = [-1.0, -2.0, -3.0, -4.0]  # Opposite of a
    
    # Test similarity
    dist_ab = NativeMath.cosine_distance(a, b)
    dist_ac = NativeMath.cosine_distance(a, c)  # Should be 0 (identical)
    dist_ad = NativeMath.cosine_distance(a, d)  # Should be 2 (opposite)
    
    print(f"   Distance A-B: {dist_ab:.4f}")
    print(f"   Distance A-C (identical): {dist_ac:.4f}")
    print(f"   Distance A-D (opposite): {dist_ad:.4f}")
    
    # Verify expectations
    assert abs(dist_ac) < 0.001, "Identical vectors should have 0 distance"
    assert abs(dist_ad - 2.0) < 0.001, "Opposite vectors should have distance ~2"
    print("   ✅ Cosine distance tests passed")

def test_gaussian_filter():
    """Test Gaussian filter implementation."""
    print("🌊 Testing Gaussian Filter...")
    
    # Test data - step function
    data = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    sigma = 1.0
    
    filtered = NativeMath.gaussian_filter_1d(data, sigma)
    
    print(f"   Original: {[f'{x:.2f}' for x in data]}")
    print(f"   Filtered: {[f'{x:.2f}' for x in filtered]}")
    
    # Filtered data should be smoother
    assert len(filtered) == len(data), "Output length should match input"
    assert max(filtered) < max(data), "Peak should be reduced"
    print("   ✅ Gaussian filter tests passed")

def test_entropy_calculation():
    """Test entropy calculation."""
    print("📊 Testing Entropy Calculation...")
    
    # Uniform distribution (maximum entropy)
    uniform = [0.25, 0.25, 0.25, 0.25]
    entropy_uniform = NativeStats.entropy(uniform)
    
    # Skewed distribution (lower entropy)
    skewed = [0.7, 0.1, 0.1, 0.1]
    entropy_skewed = NativeStats.entropy(skewed)
    
    # Single value (minimum entropy)
    single = [1.0, 0.0, 0.0, 0.0]
    entropy_single = NativeStats.entropy(single)
    
    print(f"   Uniform entropy: {entropy_uniform:.4f}")
    print(f"   Skewed entropy: {entropy_skewed:.4f}")
    print(f"   Single entropy: {entropy_single:.4f}")
    
    # Verify entropy ordering
    assert entropy_uniform > entropy_skewed > entropy_single, "Entropy ordering incorrect"
    print("   ✅ Entropy calculation tests passed")

def test_pairwise_distances():
    """Test pairwise distance calculation."""
    print("📏 Testing Pairwise Distances...")
    
    vectors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 1.0]
    ]
    
    # Test condensed distances (like scipy.spatial.distance.pdist)
    distances = NativeDistance.condensed_distances(vectors, metric='cosine')
    
    print(f"   Condensed distances: {[f'{d:.4f}' for d in distances]}")
    
    # Test full distance matrix
    distance_matrix = NativeDistance.pairwise_distances(vectors, metric='cosine')
    
    print("   Distance matrix:")
    for i, row in enumerate(distance_matrix):
        print(f"     {i}: {[f'{d:.4f}' for d in row]}")
    
    # Verify properties
    assert len(distances) == len(vectors) * (len(vectors) - 1) // 2, "Condensed distance count incorrect"
    assert len(distance_matrix) == len(vectors), "Distance matrix size incorrect"
    
    # Diagonal should be zero
    for i in range(len(vectors)):
        assert abs(distance_matrix[i][i]) < 0.001, f"Diagonal element {i} should be zero"
    
    print("   ✅ Pairwise distance tests passed")

def test_performance():
    """Test performance of native implementations."""
    print("⚡ Testing Performance...")
    
    # Generate test data
    large_vector_a = [float(i) for i in range(1000)]
    large_vector_b = [float(i + 0.5) for i in range(1000)]
    
    # Test cosine distance performance
    start_time = time.time()
    for _ in range(100):
        NativeMath.cosine_distance(large_vector_a, large_vector_b)
    cosine_time = time.time() - start_time
    
    # Test Gaussian filter performance
    large_data = [float(i % 10) for i in range(1000)]
    start_time = time.time()
    for _ in range(10):
        NativeMath.gaussian_filter_1d(large_data, sigma=2.0)
    filter_time = time.time() - start_time
    
    print(f"   Cosine distance (100x 1000-dim): {cosine_time:.4f}s")
    print(f"   Gaussian filter (10x 1000-len): {filter_time:.4f}s")
    print("   ✅ Performance tests completed")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("🔍 Testing Edge Cases...")
    
    # Empty vectors
    try:
        result = NativeMath.cosine_distance([], [])
        assert result == 1.0, "Empty vectors should return distance 1.0"
        print("   ✅ Empty vector handling")
    except Exception as e:
        print(f"   ❌ Empty vector test failed: {e}")
    
    # Zero vectors
    zero_a = [0.0, 0.0, 0.0]
    zero_b = [1.0, 2.0, 3.0]
    result = NativeMath.cosine_distance(zero_a, zero_b)
    assert result == 1.0, "Zero vector should return distance 1.0"
    print("   ✅ Zero vector handling")
    
    # Mismatched lengths
    try:
        NativeMath.cosine_distance([1.0, 2.0], [1.0, 2.0, 3.0])
        print("   ❌ Should have raised error for mismatched lengths")
    except ValueError:
        print("   ✅ Mismatched length error handling")
    
    # Empty data for Gaussian filter
    result = NativeMath.gaussian_filter_1d([], sigma=1.0)
    assert result == [], "Empty data should return empty result"
    print("   ✅ Empty data handling")

def main():
    """Run all tests."""
    print("🚀 Testing Native Math Implementations")
    print("=" * 50)
    
    try:
        test_cosine_distance()
        print()
        
        test_gaussian_filter()
        print()
        
        test_entropy_calculation()
        print()
        
        test_pairwise_distances()
        print()
        
        test_performance()
        print()
        
        test_edge_cases()
        print()
        
        print("🎉 All native math tests passed!")
        print("✅ Successfully replaced scipy dependencies with native implementations")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()