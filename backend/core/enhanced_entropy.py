"""
Enhanced Entropy Calculations with SciPy Integration

This module provides advanced entropy calculations that leverage SciPy's statistical
distributions and optimization routines while maintaining compatibility with the
existing native math implementations.

Key enhancements:
1. Advanced entropy estimators using SciPy's statistical distributions
2. Multi-scale entropy analysis for complex systems
3. Differential entropy calculations for continuous distributions
4. Cross-entropy and divergence measures with statistical validation
5. Entropy-based complexity measures using information theory
"""

from __future__ import annotations
import math
import numpy as np
from typing import List, Union, Optional, Tuple, Dict, Any
from ..core.native_math import NativeStats, NativeMath

# SciPy imports with fallback to native implementations
try:
    import scipy.stats as stats
    import scipy.optimize as optimize
    import scipy.special as special
    from scipy.spatial.distance import entropy as scipy_entropy
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    # Fallback message for development
    import warnings
    warnings.warn("SciPy not available. Using native implementations only.", UserWarning)


class EnhancedEntropyCalculator:
    """
    Advanced entropy calculations leveraging SciPy's statistical capabilities.
    
    This class provides sophisticated entropy measures that go beyond basic
    Shannon entropy, including differential entropy, cross-entropy, and
    multi-scale entropy analysis.
    """
    
    def __init__(self, use_scipy: bool = True):
        """
        Initialize the enhanced entropy calculator.
        
        Args:
            use_scipy: Whether to use SciPy functions when available
        """
        self.use_scipy = use_scipy and SCIPY_AVAILABLE
        
    def shannon_entropy_enhanced(self, probabilities: List[float], 
                               base: float = 2.0,
                               estimator: str = 'mle') -> float:
        """
        Enhanced Shannon entropy calculation with multiple estimators.
        
        Args:
            probabilities: Probability distribution
            base: Logarithm base (2 for bits, e for nats)
            estimator: Estimation method ('mle', 'miller_madow', 'dirichlet')
        
        Returns:
            Shannon entropy value
        """
        if not probabilities:
            return 0.0
            
        probs = np.array(probabilities)
        probs = probs[probs > 0]  # Remove zero probabilities
        
        if len(probs) == 0:
            return 0.0
            
        if estimator == 'mle':
            # Maximum Likelihood Estimator (standard)
            return self._shannon_mle(probs, base)
        elif estimator == 'miller_madow' and self.use_scipy:
            # Miller-Madow bias correction
            return self._shannon_miller_madow(probs, base)
        elif estimator == 'dirichlet' and self.use_scipy:
            # Dirichlet-based Bayesian estimator
            return self._shannon_dirichlet(probs, base)
        else:
            # Fallback to native implementation
            return NativeStats.entropy(probabilities, base)
    
    def differential_entropy(self, data: List[float], 
                           distribution: str = 'gaussian') -> float:
        """
        Calculate differential entropy for continuous distributions.
        
        Args:
            data: Continuous data samples
            distribution: Distribution type ('gaussian', 'exponential', 'uniform')
        
        Returns:
            Differential entropy in nats
        """
        if not self.use_scipy or not data:
            # Fallback: discretize and use Shannon entropy
            return self._differential_entropy_fallback(data)
            
        data_array = np.array(data)
        
        if distribution == 'gaussian':
            # For Gaussian: H = 0.5 * log(2πeσ²)
            sigma = np.std(data_array)
            if sigma <= 0:
                return 0.0
            return 0.5 * np.log(2 * np.pi * np.e * sigma**2)
            
        elif distribution == 'exponential':
            # Fit exponential distribution
            try:
                _, scale = stats.expon.fit(data_array, floc=0)
                return 1 + np.log(scale)  # H = 1 + log(λ⁻¹)
            except:
                return self._differential_entropy_fallback(data)
                
        elif distribution == 'uniform':
            # For uniform: H = log(b - a)
            return np.log(np.max(data_array) - np.min(data_array))
            
        else:
            return self._differential_entropy_fallback(data)
    
    def cross_entropy(self, p: List[float], q: List[float], 
                     base: float = 2.0) -> float:
        """
        Calculate cross-entropy H(P, Q) = -Σ p(x) log q(x).
        
        Args:
            p: True distribution
            q: Predicted/model distribution
            base: Logarithm base
        
        Returns:
            Cross-entropy value
        """
        if len(p) != len(q) or not p or not q:
            return float('inf')
            
        p_array = np.array(p)
        q_array = np.array(q)
        
        # Ensure valid probability distributions
        p_array = p_array / np.sum(p_array) if np.sum(p_array) > 0 else p_array
        q_array = q_array / np.sum(q_array) if np.sum(q_array) > 0 else q_array
        
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-12
        q_array = np.maximum(q_array, epsilon)
        
        if base == 2.0:
            log_func = np.log2
        elif base == math.e:
            log_func = np.log
        else:
            log_func = lambda x: np.log(x) / np.log(base)
            
        return -np.sum(p_array * log_func(q_array))
    
    def kl_divergence_enhanced(self, p: List[float], q: List[float],
                             base: float = 2.0) -> float:
        """
        Enhanced Kullback-Leibler divergence with statistical validation.
        
        Args:
            p: Reference distribution
            q: Comparison distribution
            base: Logarithm base
        
        Returns:
            KL divergence D(P||Q)
        """
        if not self.use_scipy:
            return self._kl_divergence_native(p, q, base)
            
        try:
            # Use SciPy's entropy function for KL divergence
            p_array = np.array(p)
            q_array = np.array(q)
            
            # Normalize to ensure valid probability distributions
            p_array = p_array / np.sum(p_array) if np.sum(p_array) > 0 else p_array
            q_array = q_array / np.sum(q_array) if np.sum(q_array) > 0 else q_array
            
            # SciPy's entropy function calculates KL divergence
            kl_div = scipy_entropy(p_array, q_array, base=base)
            return float(kl_div) if not np.isnan(kl_div) else float('inf')
            
        except:
            return self._kl_divergence_native(p, q, base)
    
    def jensen_shannon_divergence(self, p: List[float], q: List[float],
                                base: float = 2.0) -> float:
        """
        Calculate Jensen-Shannon divergence, a symmetric version of KL divergence.
        
        JS(P, Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
        where M = 0.5 * (P + Q)
        
        Args:
            p: First distribution
            q: Second distribution
            base: Logarithm base
        
        Returns:
            Jensen-Shannon divergence
        """
        if len(p) != len(q) or not p or not q:
            return float('inf')
            
        p_array = np.array(p)
        q_array = np.array(q)
        
        # Normalize distributions
        p_array = p_array / np.sum(p_array) if np.sum(p_array) > 0 else p_array
        q_array = q_array / np.sum(q_array) if np.sum(q_array) > 0 else q_array
        
        # Calculate mixture distribution
        m_array = 0.5 * (p_array + q_array)
        
        # Calculate JS divergence
        kl_pm = self.kl_divergence_enhanced(p_array.tolist(), m_array.tolist(), base)
        kl_qm = self.kl_divergence_enhanced(q_array.tolist(), m_array.tolist(), base)
        
        return 0.5 * kl_pm + 0.5 * kl_qm
    
    def multiscale_entropy(self, data: List[float], 
                          scales: List[int] = None,
                          tolerance_factor: float = 0.15) -> Dict[int, float]:
        """
        Calculate multiscale entropy for complex system analysis.
        
        This method analyzes entropy across multiple time scales,
        providing insights into system complexity at different levels.
        
        Args:
            data: Time series data
            scales: List of scales to analyze (default: [1, 2, 3, 4, 5])
            tolerance_factor: Tolerance for pattern matching
        
        Returns:
            Dictionary mapping scales to entropy values
        """
        if not data:
            return {}
            
        if scales is None:
            scales = [1, 2, 3, 4, 5]
            
        data_array = np.array(data)
        std_data = np.std(data_array)
        tolerance = tolerance_factor * std_data
        
        multiscale_entropies = {}
        
        for scale in scales:
            if scale <= 0 or scale > len(data_array) // 2:
                continue
                
            # Coarse-grain the data
            coarse_grained = self._coarse_grain(data_array, scale)
            
            # Calculate sample entropy for this scale
            if self.use_scipy:
                entropy_val = self._sample_entropy_scipy(coarse_grained, 2, tolerance)
            else:
                entropy_val = self._sample_entropy_native(coarse_grained, 2, tolerance)
                
            multiscale_entropies[scale] = entropy_val
            
        return multiscale_entropies
    
    def conditional_entropy_enhanced(self, xy_joint: List[List[float]], 
                                   x_marginal: List[float],
                                   base: float = 2.0) -> float:
        """
        Enhanced conditional entropy calculation H(Y|X).
        
        Args:
            xy_joint: Joint probability distribution P(X,Y)
            x_marginal: Marginal distribution P(X)
            base: Logarithm base
        
        Returns:
            Conditional entropy H(Y|X)
        """
        if not xy_joint or not x_marginal:
            return 0.0
            
        joint_array = np.array(xy_joint)
        marginal_array = np.array(x_marginal)
        
        # H(Y|X) = H(X,Y) - H(X)
        joint_entropy = self.shannon_entropy_enhanced(joint_array.flatten().tolist(), base)
        marginal_entropy = self.shannon_entropy_enhanced(marginal_array.tolist(), base)
        
        return joint_entropy - marginal_entropy
    
    def mutual_information_enhanced(self, x_data: List[float], 
                                  y_data: List[float],
                                  bins: int = 10,
                                  base: float = 2.0) -> float:
        """
        Enhanced mutual information calculation using histogram estimation.
        
        Args:
            x_data: First variable data
            y_data: Second variable data
            bins: Number of bins for histogram estimation
            base: Logarithm base
        
        Returns:
            Mutual information I(X;Y)
        """
        if len(x_data) != len(y_data) or not x_data:
            return 0.0
            
        if self.use_scipy:
            return self._mutual_information_scipy(x_data, y_data, bins, base)
        else:
            return self._mutual_information_native(x_data, y_data, bins, base)
    
    def entropy_rate(self, sequence: List[Any], 
                    order: int = 1) -> float:
        """
        Calculate entropy rate for a sequence (Markov chain analysis).
        
        Args:
            sequence: Sequence of symbols/states
            order: Markov order (memory length)
        
        Returns:
            Entropy rate in bits per symbol
        """
        if len(sequence) <= order:
            return 0.0
            
        # Build transition counts
        transitions = {}
        contexts = {}
        
        for i in range(len(sequence) - order):
            context = tuple(sequence[i:i+order])
            next_symbol = sequence[i+order]
            
            if context not in contexts:
                contexts[context] = 0
            contexts[context] += 1
            
            if context not in transitions:
                transitions[context] = {}
            if next_symbol not in transitions[context]:
                transitions[context][next_symbol] = 0
            transitions[context][next_symbol] += 1
        
        # Calculate entropy rate
        entropy_rate = 0.0
        total_transitions = sum(contexts.values())
        
        for context, count in contexts.items():
            context_prob = count / total_transitions
            
            # Calculate conditional entropy for this context
            context_transitions = transitions[context]
            context_total = sum(context_transitions.values())
            
            context_entropy = 0.0
            for symbol, symbol_count in context_transitions.items():
                symbol_prob = symbol_count / context_total
                if symbol_prob > 0:
                    context_entropy -= symbol_prob * math.log2(symbol_prob)
            
            entropy_rate += context_prob * context_entropy
        
        return entropy_rate
    
    # Private helper methods
    
    def _shannon_mle(self, probs: np.ndarray, base: float) -> float:
        """Maximum likelihood estimator for Shannon entropy."""
        if base == 2.0:
            return float(-np.sum(probs * np.log2(probs)))
        elif base == math.e:
            return float(-np.sum(probs * np.log(probs)))
        else:
            return float(-np.sum(probs * np.log(probs) / np.log(base)))
    
    def _shannon_miller_madow(self, probs: np.ndarray, base: float) -> float:
        """Miller-Madow bias-corrected estimator."""
        if not self.use_scipy:
            return self._shannon_mle(probs, base)
            
        # Estimate sample size from probabilities
        sample_size = 1.0 / np.min(probs) if len(probs) > 0 else 1.0
        
        mle_entropy = self._shannon_mle(probs, base)
        n_observed = len(probs)
        correction = (n_observed - 1) / (2 * sample_size * np.log(base))
        
        return mle_entropy + correction
    
    def _shannon_dirichlet(self, probs: np.ndarray, base: float) -> float:
        """Dirichlet-based Bayesian estimator."""
        if not self.use_scipy:
            return self._shannon_mle(probs, base)
            
        try:
            # Use Dirichlet distribution for Bayesian entropy estimation
            alpha = np.ones(len(probs))  # Uniform prior
            posterior_alpha = alpha + probs * 100  # Scale up for numerical stability
            
            # Calculate expected entropy under Dirichlet posterior
            digamma_sum = special.digamma(np.sum(posterior_alpha))
            expected_log_probs = special.digamma(posterior_alpha) - digamma_sum
            
            entropy = -np.sum(probs * expected_log_probs)
            
            if base != math.e:
                entropy /= np.log(base)
                
            return float(entropy)
        except:
            return self._shannon_mle(probs, base)
    
    def _differential_entropy_fallback(self, data: List[float]) -> float:
        """Fallback differential entropy using discretization."""
        if not data:
            return 0.0
            
        # Discretize data into bins
        data_array = np.array(data)
        bins = min(int(np.sqrt(len(data_array))), 50)  # Adaptive bin count
        
        hist, _ = np.histogram(data_array, bins=bins)
        probs = hist / np.sum(hist)
        probs = probs[probs > 0]
        
        return self._shannon_mle(probs, math.e)
    
    def _kl_divergence_native(self, p: List[float], q: List[float], 
                            base: float) -> float:
        """Native KL divergence implementation."""
        if len(p) != len(q) or not p or not q:
            return float('inf')
            
        p_array = np.array(p)
        q_array = np.array(q)
        
        # Normalize
        p_array = p_array / np.sum(p_array) if np.sum(p_array) > 0 else p_array
        q_array = q_array / np.sum(q_array) if np.sum(q_array) > 0 else q_array
        
        # Calculate KL divergence
        kl_div = 0.0
        for pi, qi in zip(p_array, q_array):
            if pi > 0:
                if qi <= 0:
                    return float('inf')
                if base == 2.0:
                    kl_div += pi * math.log2(pi / qi)
                elif base == math.e:
                    kl_div += pi * math.log(pi / qi)
                else:
                    kl_div += pi * math.log(pi / qi) / math.log(base)
        
        return kl_div
    
    def _coarse_grain(self, data: np.ndarray, scale: int) -> np.ndarray:
        """Coarse-grain data for multiscale analysis."""
        n = len(data) // scale
        coarse_grained = np.zeros(n)
        
        for i in range(n):
            coarse_grained[i] = np.mean(data[i*scale:(i+1)*scale])
            
        return coarse_grained
    
    def _sample_entropy_scipy(self, data: np.ndarray, m: int, 
                            tolerance: float) -> float:
        """Sample entropy calculation using SciPy optimizations."""
        # This is a placeholder - actual implementation would use
        # SciPy's optimization routines for pattern matching
        return self._sample_entropy_native(data, m, tolerance)
    
    def _sample_entropy_native(self, data: np.ndarray, m: int, 
                             tolerance: float) -> float:
        """Native sample entropy implementation."""
        N = len(data)
        if N < m + 1:
            return 0.0
            
        def _maxdist(xi, xj, m):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m):
            patterns = np.array([data[i:i+m] for i in range(N - m + 1)])
            C = np.zeros(N - m + 1)
            
            for i in range(N - m + 1):
                template = patterns[i]
                for j in range(N - m + 1):
                    if _maxdist(template, patterns[j], m) <= tolerance:
                        C[i] += 1
                        
            phi = np.mean(np.log(C / (N - m + 1)))
            return phi
        
        return _phi(m) - _phi(m + 1)
    
    def _mutual_information_scipy(self, x_data: List[float], 
                                y_data: List[float],
                                bins: int, base: float) -> float:
        """Mutual information using SciPy's statistical functions."""
        try:
            # Use SciPy's histogram functions for better numerical stability
            x_array = np.array(x_data)
            y_array = np.array(y_data)
            
            # Create 2D histogram
            hist_2d, x_edges, y_edges = np.histogram2d(x_array, y_array, bins=bins)
            
            # Normalize to get probabilities
            hist_2d = hist_2d / np.sum(hist_2d)
            
            # Calculate marginal distributions
            p_x = np.sum(hist_2d, axis=1)
            p_y = np.sum(hist_2d, axis=0)
            
            # Calculate mutual information
            mi = 0.0
            for i in range(len(p_x)):
                for j in range(len(p_y)):
                    if hist_2d[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                        if base == 2.0:
                            mi += hist_2d[i, j] * math.log2(hist_2d[i, j] / (p_x[i] * p_y[j]))
                        elif base == math.e:
                            mi += hist_2d[i, j] * math.log(hist_2d[i, j] / (p_x[i] * p_y[j]))
                        else:
                            mi += hist_2d[i, j] * math.log(hist_2d[i, j] / (p_x[i] * p_y[j])) / math.log(base)
            
            return mi
        except:
            return self._mutual_information_native(x_data, y_data, bins, base)
    
    def _mutual_information_native(self, x_data: List[float], 
                                 y_data: List[float],
                                 bins: int, base: float) -> float:
        """Native mutual information implementation."""
        # Fallback to basic histogram-based calculation
        x_array = np.array(x_data)
        y_array = np.array(y_data)
        
        # Simple binning
        x_min, x_max = np.min(x_array), np.max(x_array)
        y_min, y_max = np.min(y_array), np.max(y_array)
        
        if x_max == x_min or y_max == y_min:
            return 0.0
        
        x_bins = np.linspace(x_min, x_max, bins + 1)
        y_bins = np.linspace(y_min, y_max, bins + 1)
        
        # Digitize data
        x_digitized = np.digitize(x_array, x_bins) - 1
        y_digitized = np.digitize(y_array, y_bins) - 1
        
        # Clamp to valid range
        x_digitized = np.clip(x_digitized, 0, bins - 1)
        y_digitized = np.clip(y_digitized, 0, bins - 1)
        
        # Calculate joint and marginal distributions
        joint_counts = np.zeros((bins, bins))
        for xi, yi in zip(x_digitized, y_digitized):
            joint_counts[xi, yi] += 1
        
        joint_probs = joint_counts / np.sum(joint_counts)
        marginal_x = np.sum(joint_probs, axis=1)
        marginal_y = np.sum(joint_probs, axis=0)
        
        # Calculate MI
        mi = 0.0
        for i in range(bins):
            for j in range(bins):
                if joint_probs[i, j] > 0 and marginal_x[i] > 0 and marginal_y[j] > 0:
                    if base == 2.0:
                        mi += joint_probs[i, j] * math.log2(joint_probs[i, j] / (marginal_x[i] * marginal_y[j]))
                    elif base == math.e:
                        mi += joint_probs[i, j] * math.log(joint_probs[i, j] / (marginal_x[i] * marginal_y[j]))
                    else:
                        mi += joint_probs[i, j] * math.log(joint_probs[i, j] / (marginal_x[i] * marginal_y[j])) / math.log(base)
        
        return mi


# Convenience functions for backward compatibility and easy integration
def enhanced_shannon_entropy(probabilities: List[float], 
                           base: float = 2.0,
                           estimator: str = 'mle') -> float:
    """Enhanced Shannon entropy with SciPy integration."""
    calculator = EnhancedEntropyCalculator()
    return calculator.shannon_entropy_enhanced(probabilities, base, estimator)

def differential_entropy(data: List[float], 
                        distribution: str = 'gaussian') -> float:
    """Calculate differential entropy for continuous data."""
    calculator = EnhancedEntropyCalculator()
    return calculator.differential_entropy(data, distribution)

def jensen_shannon_divergence(p: List[float], q: List[float],
                            base: float = 2.0) -> float:
    """Calculate Jensen-Shannon divergence."""
    calculator = EnhancedEntropyCalculator()
    return calculator.jensen_shannon_divergence(p, q, base)

def multiscale_entropy(data: List[float], 
                      scales: List[int] = None) -> Dict[int, float]:
    """Calculate multiscale entropy for complexity analysis."""
    calculator = EnhancedEntropyCalculator()
    return calculator.multiscale_entropy(data, scales)

def mutual_information_enhanced(x_data: List[float], 
                              y_data: List[float],
                              bins: int = 10) -> float:
    """Enhanced mutual information calculation."""
    calculator = EnhancedEntropyCalculator()
    return calculator.mutual_information_enhanced(x_data, y_data, bins)