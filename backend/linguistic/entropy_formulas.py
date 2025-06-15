"""
Entropy Formulas for Linguistic Analysis

This module implements various entropy-based formulas for analyzing
linguistic and semantic patterns, including predictability indices
and complexity measures.
"""

import numpy as np
from typing import List, Union, Dict
import math


def calculate_predictability_index(data: List[Union[float, int]], m: int, r: float) -> float:
    """
    Calculate a predictability index based on pattern matching.
    
    This function implements a simplified version of sample entropy concepts
    to measure the predictability of a time series. Higher values indicate
    more predictable patterns.
    
    Args:
        data: Time series data as a list of numbers
        m: Pattern length for matching
        r: Tolerance for matching (relative to data standard deviation)
        
    Returns:
        Predictability index (0 = unpredictable, >1 = predictable patterns)
    """
    if not data or len(data) <= m:
        return 0.0
    
    n = len(data)
    
    # Convert to numpy array for easier manipulation
    data_array = np.array(data)
    
    # Count pattern matches at length m
    matches_m = 0
    matches_m_plus_1 = 0
    
    for i in range(n - m):
        template_m = data_array[i:i + m]
        template_m_plus_1 = data_array[i:i + m + 1] if i + m + 1 <= n else None
        
        for j in range(i + 1, n - m):
            candidate_m = data_array[j:j + m]
            
            # Check if patterns match within tolerance
            if _patterns_match(template_m, candidate_m, r):
                matches_m += 1
                
                # Check m+1 length pattern if possible
                if template_m_plus_1 is not None and j + m + 1 <= n:
                    candidate_m_plus_1 = data_array[j:j + m + 1]
                    if _patterns_match(template_m_plus_1, candidate_m_plus_1, r):
                        matches_m_plus_1 += 1
    
    # Calculate predictability index
    if matches_m == 0:
        return 0.0
    
    # Simple ratio-based index
    # Higher ratio indicates more predictable patterns
    predictability_ratio = matches_m_plus_1 / matches_m if matches_m > 0 else 0.0
    
    # Scale to make interpretation easier
    # Values > 1 indicate predictable patterns
    # Values < 1 indicate less predictable patterns
    return predictability_ratio


def _patterns_match(pattern1: np.ndarray, pattern2: np.ndarray, tolerance: float) -> bool:
    """
    Check if two patterns match within a given tolerance.
    
    Args:
        pattern1: First pattern
        pattern2: Second pattern
        tolerance: Maximum allowed difference
        
    Returns:
        True if patterns match within tolerance
    """
    if len(pattern1) != len(pattern2):
        return False
    
    # Calculate maximum absolute difference
    max_diff = np.max(np.abs(pattern1 - pattern2))
    
    return max_diff <= tolerance


def calculate_sample_entropy(data: List[Union[float, int]], m: int = 2, r: float = None) -> float:
    """
    Calculate sample entropy of a time series.
    
    Sample entropy is a measure of complexity/regularity in time-series data.
    Lower values indicate more regular, predictable data.
    
    Args:
        data: Time series data
        m: Pattern length
        r: Tolerance for matching (defaults to 0.2 * std(data))
        
    Returns:
        Sample entropy value
    """
    if not data or len(data) <= m:
        return 0.0
    
    data_array = np.array(data)
    
    if r is None:
        r = 0.2 * np.std(data_array)
    
    n = len(data_array)
    
    def _maxdist(xi, xj, m):
        """Calculate maximum distance between two patterns"""
        return max([abs(ua - va) for ua, va in zip(xi, xj)])
    
    def _phi(m):
        """Calculate phi(m)"""
        patterns = np.array([data_array[i:i + m] for i in range(n - m + 1)])
        C = np.zeros(n - m + 1)
        
        for i in range(n - m + 1):
            template = patterns[i]
            for j in range(n - m + 1):
                if _maxdist(template, patterns[j], m) <= r:
                    C[i] += 1.0
        
        phi = np.mean(np.log(C / (n - m + 1.0)))
        return phi
    
    return _phi(m) - _phi(m + 1)


def calculate_approximate_entropy(data: List[Union[float, int]], m: int = 2, r: float = None) -> float:
    """
    Calculate approximate entropy of a time series.
    
    Approximate entropy quantifies the regularity and complexity of time-series data.
    
    Args:
        data: Time series data
        m: Pattern length
        r: Tolerance for matching (defaults to 0.2 * std(data))
        
    Returns:
        Approximate entropy value
    """
    if not data or len(data) <= m:
        return 0.0
    
    data_array = np.array(data)
    
    if r is None:
        r = 0.2 * np.std(data_array)
    
    n = len(data_array)
    
    def _maxdist(xi, xj):
        """Calculate maximum distance between two patterns"""
        return max([abs(ua - va) for ua, va in zip(xi, xj)])
    
    def _phi(m):
        """Calculate phi(m)"""
        patterns = np.array([data_array[i:i + m] for i in range(n - m + 1)])
        C = np.zeros(n - m + 1)
        
        for i in range(n - m + 1):
            template = patterns[i]
            for j in range(n - m + 1):
                if _maxdist(template, patterns[j]) <= r:
                    C[i] += 1.0
        
        phi = np.mean([np.log(c / (n - m + 1.0)) for c in C])
        return phi
    
    return _phi(m) - _phi(m + 1)


def calculate_permutation_entropy(data: List[Union[float, int]], order: int = 3, delay: int = 1) -> float:
    """
    Calculate permutation entropy of a time series.
    
    Permutation entropy is a natural complexity measure for time series
    based on comparing neighboring values.
    
    Args:
        data: Time series data
        order: Order of permutation patterns
        delay: Time delay
        
    Returns:
        Permutation entropy value
    """
    if not data or len(data) < order:
        return 0.0
    
    data_array = np.array(data)
    n = len(data_array)
    
    # Generate all possible permutations
    from itertools import permutations
    all_perms = list(permutations(range(order)))
    perm_counts = {perm: 0 for perm in all_perms}
    
    # Count occurrences of each permutation pattern
    for i in range(n - (order - 1) * delay):
        # Extract subsequence
        subseq = [data_array[i + j * delay] for j in range(order)]
        
        # Get permutation pattern
        sorted_indices = sorted(range(order), key=lambda x: subseq[x])
        perm_pattern = tuple(sorted_indices)
        
        if perm_pattern in perm_counts:
            perm_counts[perm_pattern] += 1
    
    # Calculate probabilities
    total_patterns = sum(perm_counts.values())
    if total_patterns == 0:
        return 0.0
    
    probabilities = [count / total_patterns for count in perm_counts.values() if count > 0]
    
    # Calculate entropy
    if not probabilities:
        return 0.0
    
    entropy = -sum(p * np.log2(p) for p in probabilities)
    
    # Normalize by maximum possible entropy
    max_entropy = np.log2(math.factorial(order))
    
    return entropy / max_entropy if max_entropy > 0 else 0.0


def calculate_multiscale_entropy(data: List[Union[float, int]], max_scale: int = 10, m: int = 2, r: float = None) -> List[float]:
    """
    Calculate multiscale entropy of a time series.
    
    Multiscale entropy analyzes the complexity of a time series at multiple scales.
    
    Args:
        data: Time series data
        max_scale: Maximum scale factor
        m: Pattern length for sample entropy
        r: Tolerance for matching
        
    Returns:
        List of entropy values at different scales
    """
    if not data:
        return []
    
    data_array = np.array(data)
    
    if r is None:
        r = 0.2 * np.std(data_array)
    
    entropies = []
    
    for scale in range(1, max_scale + 1):
        # Coarse-grain the time series
        if scale == 1:
            coarse_grained = data_array
        else:
            n_coarse = len(data_array) // scale
            coarse_grained = np.array([
                np.mean(data_array[i * scale:(i + 1) * scale])
                for i in range(n_coarse)
            ])
        
        # Calculate sample entropy at this scale
        if len(coarse_grained) > m:
            entropy = calculate_sample_entropy(coarse_grained.tolist(), m, r)
            entropies.append(entropy)
        else:
            entropies.append(0.0)
    
    return entropies


def calculate_linguistic_complexity(text: str) -> Dict[str, float]:
    """
    Calculate various linguistic complexity measures for text.
    
    Args:
        text: Input text string
        
    Returns:
        Dictionary of complexity measures
    """
    if not text:
        return {'lexical_diversity': 0.0, 'entropy': 0.0, 'compression_ratio': 1.0}
    
    # Tokenize (simple word splitting)
    words = text.lower().split()
    
    if not words:
        return {'lexical_diversity': 0.0, 'entropy': 0.0, 'compression_ratio': 1.0}
    
    # Lexical diversity (Type-Token Ratio)
    unique_words = set(words)
    lexical_diversity = len(unique_words) / len(words)
    
    # Word frequency entropy
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    total_words = len(words)
    probabilities = [count / total_words for count in word_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities)
    
    # Compression ratio (simple estimate)
    original_length = len(text)
    compressed_length = len(set(text))  # Unique characters
    compression_ratio = compressed_length / original_length if original_length > 0 else 1.0
    
    return {
        'lexical_diversity': lexical_diversity,
        'entropy': entropy,
        'compression_ratio': compression_ratio,
        'unique_words': len(unique_words),
        'total_words': len(words)
    }

def calculate_enhanced_predictability_index(data: List[Union[float, int]], 
                                          scales: List[int] = None,
                                          tolerance_factor: float = 0.2) -> float:
    """
    Enhanced predictability index using multi-scale entropy analysis.
    
    This addresses the limitation identified in the expected failure test
    by combining multiple entropy measures across different scales.
    
    Args:
        data: Time series data
        scales: List of pattern lengths to analyze (default: [2, 3, 4])
        tolerance_factor: Tolerance for pattern matching
        
    Returns:
        Enhanced predictability score (0-1, higher = more predictable)
    """
    if scales is None:
        scales = [2, 3, 4]
    
    if not data or len(data) < max(scales):
        return 0.0
    
    data_array = np.array(data)
    std_data = np.std(data_array)
    
    if std_data == 0:  # Constant data is perfectly predictable
        return 1.0
    
    predictability_scores = []
    scale_weights = [1.0, 0.8, 0.6]  # Decreasing weights for higher scales
    
    for i, scale in enumerate(scales):
        if len(data) <= scale:
            continue
            
        # Calculate multiple entropy measures
        sample_ent = calculate_sample_entropy(data, scale, tolerance_factor * std_data)
        approx_ent = calculate_approximate_entropy(data, scale, tolerance_factor * std_data)
        perm_ent = calculate_permutation_entropy(data, scale)
        
        # Combine entropies (lower entropy = higher predictability)
        combined_entropy = (sample_ent + approx_ent + perm_ent) / 3.0
        
        # Convert to predictability score
        if combined_entropy > 0:
            scale_predictability = 1.0 / (1.0 + combined_entropy)
        else:
            scale_predictability = 1.0
        
        predictability_scores.append(scale_predictability)
    
    if not predictability_scores:
        return 0.0
    
    # Weighted average across scales
    weights = scale_weights[:len(predictability_scores)]
    if len(weights) < len(predictability_scores):
        weights.extend([0.5] * (len(predictability_scores) - len(weights)))
    
    return float(np.average(predictability_scores, weights=weights))
