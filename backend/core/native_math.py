"""
Native mathematical implementations to reduce external dependencies.
High-performance, dependency-free implementations of common mathematical operations.
"""

from __future__ import annotations
import math
from typing import List, Union, Optional, Tuple
import numpy as np


class NativeMath:
    """Native mathematical operations without external dependencies."""
    
    @staticmethod
    def cosine_distance(a: List[float], b: List[float]) -> float:
        """
        Calculate cosine distance between two vectors.
        Replaces scipy.spatial.distance.cosine
        
        Returns: 1 - cosine_similarity (distance, not similarity)
        """
        if len(a) != len(b):
            raise ValueError("Vectors must have the same length")
        
        if len(a) == 0 or len(b) == 0:
            return 1.0
        
        # Calculate dot product
        dot_product = sum(x * y for x, y in zip(a, b))
        
        # Calculate magnitudes
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))
        
        # Handle zero vectors
        if magnitude_a == 0.0 or magnitude_b == 0.0:
            return 1.0
        
        # Calculate cosine similarity
        cosine_similarity = dot_product / (magnitude_a * magnitude_b)
        
        # Clamp to [-1, 1] to handle floating point errors
        cosine_similarity = max(-1.0, min(1.0, cosine_similarity))
        
        # Return cosine distance (1 - similarity)
        return 1.0 - cosine_similarity
    
    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        Returns: cosine similarity (not distance)
        """
        return 1.0 - NativeMath.cosine_distance(a, b)
    
    @staticmethod
    def euclidean_distance(a: List[float], b: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        if len(a) != len(b):
            raise ValueError("Vectors must have the same length")
        
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    
    @staticmethod
    def manhattan_distance(a: List[float], b: List[float]) -> float:
        """Calculate Manhattan (L1) distance between two vectors."""
        if len(a) != len(b):
            raise ValueError("Vectors must have the same length")
        
        return sum(abs(x - y) for x, y in zip(a, b))
    
    @staticmethod
    def dot_product(a: List[float], b: List[float]) -> float:
        """Calculate dot product of two vectors."""
        if len(a) != len(b):
            raise ValueError("Vectors must have the same length")
        
        return sum(x * y for x, y in zip(a, b))
    
    @staticmethod
    def vector_magnitude(vector: List[float]) -> float:
        """Calculate the magnitude (L2 norm) of a vector."""
        return math.sqrt(sum(x * x for x in vector))
    
    @staticmethod
    def normalize_vector(vector: List[float]) -> List[float]:
        """Normalize a vector to unit length."""
        magnitude = NativeMath.vector_magnitude(vector)
        if magnitude == 0.0:
            return vector.copy()
        return [x / magnitude for x in vector]
    
    @staticmethod
    def gaussian_filter_1d(data: List[float], sigma: float) -> List[float]:
        """
        Apply 1D Gaussian filter to data.
        Replaces scipy.ndimage.gaussian_filter1d
        """
        if not data:
            return []
        
        if sigma <= 0:
            return data.copy()
        
        # Calculate kernel size (6 sigma covers 99.7% of the distribution)
        kernel_size = max(3, int(6 * sigma))
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Generate Gaussian kernel
        kernel = NativeMath._gaussian_kernel_1d(kernel_size, sigma)
        
        # Apply convolution with padding
        return NativeMath._convolve_1d(data, kernel)
    
    @staticmethod
    def _gaussian_kernel_1d(size: int, sigma: float) -> List[float]:
        """Generate 1D Gaussian kernel."""
        kernel = []
        center = size // 2
        
        for i in range(size):
            x = i - center
            value = math.exp(-(x * x) / (2 * sigma * sigma))
            kernel.append(value)
        
        # Normalize kernel
        total = sum(kernel)
        return [k / total for k in kernel]
    
    @staticmethod
    def _convolve_1d(data: List[float], kernel: List[float]) -> List[float]:
        """Apply 1D convolution with reflection padding."""
        if not data or not kernel:
            return data.copy()
        
        result = []
        kernel_size = len(kernel)
        kernel_center = kernel_size // 2
        
        for i in range(len(data)):
            value = 0.0
            
            for j in range(kernel_size):
                data_index = i + j - kernel_center
                
                # Reflection padding
                if data_index < 0:
                    data_index = -data_index
                elif data_index >= len(data):
                    data_index = 2 * len(data) - data_index - 2
                
                # Clamp to valid range
                data_index = max(0, min(len(data) - 1, data_index))
                
                value += data[data_index] * kernel[j]
            
            result.append(value)
        
        return result


class NativeStats:
    """Native statistical functions to replace scipy.stats."""
    
    @staticmethod
    def mean(data: List[float]) -> float:
        """Calculate arithmetic mean."""
        if not data:
            return 0.0
        return sum(data) / len(data)
    
    @staticmethod
    def variance(data: List[float], ddof: int = 0) -> float:
        """Calculate variance with optional degrees of freedom correction."""
        if len(data) <= ddof:
            return 0.0
        
        mean_val = NativeStats.mean(data)
        squared_diffs = [(x - mean_val) ** 2 for x in data]
        return sum(squared_diffs) / (len(data) - ddof)
    
    @staticmethod
    def std(data: List[float], ddof: int = 0) -> float:
        """Calculate standard deviation."""
        return math.sqrt(NativeStats.variance(data, ddof))
    
    @staticmethod
    def entropy(probabilities: List[float], base: float = 2.0) -> float:
        """
        Calculate Shannon entropy.
        
        Args:
            probabilities: List of probability values (should sum to 1.0)
            base: Logarithm base (2 for bits, e for nats)
        
        Returns:
            Shannon entropy
        """
        if not probabilities:
            return 0.0
        
        # Filter out zero probabilities
        non_zero_probs = [p for p in probabilities if p > 0]
        
        if not non_zero_probs:
            return 0.0
        
        if base == 2.0:
            log_func = math.log2
        elif base == math.e:
            log_func = math.log
        else:
            log_func = lambda x: math.log(x) / math.log(base)
        
        return -sum(p * log_func(p) for p in non_zero_probs)
    
    @staticmethod
    def normalize_probabilities(values: List[float]) -> List[float]:
        """Normalize values to form a probability distribution."""
        if not values:
            return []
        
        total = sum(values)
        if total <= 0:
            # Return uniform distribution
            uniform_prob = 1.0 / len(values)
            return [uniform_prob] * len(values)
        
        return [v / total for v in values]
    
    @staticmethod
    def correlation(x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        mean_x = NativeStats.mean(x)
        mean_y = NativeStats.mean(y)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        
        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    @staticmethod
    def percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        if percentile <= 0:
            return sorted_data[0]
        if percentile >= 100:
            return sorted_data[-1]
        
        index = (percentile / 100.0) * (n - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, n - 1)
        
        if lower_index == upper_index:
            return sorted_data[lower_index]
        
        # Linear interpolation
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight


class NativeDistance:
    """Native distance and similarity metrics."""
    
    @staticmethod
    def pairwise_distances(vectors: List[List[float]], metric: str = 'cosine') -> List[List[float]]:
        """
        Calculate pairwise distances between vectors.
        Replaces scipy.spatial.distance.pdist functionality.
        
        Args:
            vectors: List of vectors
            metric: Distance metric ('cosine', 'euclidean', 'manhattan')
        
        Returns:
            Square distance matrix
        """
        n = len(vectors)
        distances = [[0.0] * n for _ in range(n)]
        
        distance_func = {
            'cosine': NativeMath.cosine_distance,
            'euclidean': NativeMath.euclidean_distance,
            'manhattan': NativeMath.manhattan_distance
        }.get(metric, NativeMath.cosine_distance)
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = distance_func(vectors[i], vectors[j])
                distances[i][j] = dist
                distances[j][i] = dist
        
        return distances
    
    @staticmethod
    def condensed_distances(vectors: List[List[float]], metric: str = 'cosine') -> List[float]:
        """
        Calculate condensed distance matrix (upper triangle only).
        Compatible with scipy.spatial.distance.pdist output format.
        """
        if not vectors:
            return []
        
        n = len(vectors)
        distances = []
        
        distance_func = {
            'cosine': NativeMath.cosine_distance,
            'euclidean': NativeMath.euclidean_distance,
            'manhattan': NativeMath.manhattan_distance
        }.get(metric, NativeMath.cosine_distance)
        
        for i in range(n):
            for j in range(i + 1, n):
                try:
                    # Ensure vectors are properly formatted
                    vec_a = vectors[i]
                    vec_b = vectors[j]
                    if vec_a is None or vec_b is None:
                        continue
                    # Convert to list if numpy array or other format
                    if hasattr(vec_a, 'tolist'):
                        vec_a = vec_a.tolist()
                    if hasattr(vec_b, 'tolist'):
                        vec_b = vec_b.tolist()
                    distances.append(distance_func(vec_a, vec_b))
                except Exception as e:
                    # Skip problematic vector pairs
                    continue
        
        return distances


# Convenience functions for backward compatibility
def cosine_distance(a: List[float], b: List[float]) -> float:
    """Backward compatible cosine distance function."""
    return NativeMath.cosine_distance(a, b)

def gaussian_filter1d(data: List[float], sigma: float) -> List[float]:
    """Backward compatible Gaussian filter function."""
    return NativeMath.gaussian_filter_1d(data, sigma)

def entropy(probabilities: List[float], base: float = 2.0) -> float:
    """Backward compatible entropy function."""
    return NativeStats.entropy(probabilities, base)

def pdist(vectors: List[List[float]], metric: str = 'cosine') -> List[float]:
    """Backward compatible pairwise distance function."""
    return NativeDistance.condensed_distances(vectors, metric)