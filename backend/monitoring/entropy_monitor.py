"""
Entropy Monitor for Kimera SWM

Implements comprehensive entropy calculation and monitoring following the methodologies
outlined in the computational tools specification. Provides both Shannon information-theoretic
entropy and thermodynamic entropy measures for the semantic working memory system.
"""

import numpy as np
import scipy.stats
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from collections import defaultdict, deque
import math

from ..core.geoid import GeoidState


@dataclass
class EntropyMeasurement:
    """Container for entropy measurement data"""
    timestamp: datetime
    shannon_entropy: float
    thermodynamic_entropy: float
    relative_entropy: float
    conditional_entropy: float
    mutual_information: float
    system_complexity: float
    geoid_count: int
    vault_distribution: Dict[str, int]
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntropyEstimator:
    """
    Advanced entropy estimation using multiple estimators as recommended
    in the benchmarking specification
    """
    
    @staticmethod
    def shannon_entropy_mle(probabilities: np.ndarray, base: float = 2.0) -> float:
        """Maximum Likelihood Estimator (plug-in estimator)"""
        probabilities = probabilities[probabilities > 0]
        if len(probabilities) == 0:
            return 0.0
        return float(-np.sum(probabilities * np.log(probabilities) / np.log(base)))
    
    @staticmethod
    def miller_madow_entropy(probabilities: np.ndarray, sample_size: int, base: float = 2.0) -> float:
        """Miller-Madow bias-corrected estimator"""
        mle_entropy = EntropyEstimator.shannon_entropy_mle(probabilities, base)
        n_observed = np.sum(probabilities > 0)
        correction = (n_observed - 1) / (2 * sample_size * np.log(base))
        return mle_entropy + correction
    
    @staticmethod
    def chao_shen_entropy(counts: np.ndarray, base: float = 2.0) -> float:
        """Chao-Shen estimator - superior convergence properties"""
        n = np.sum(counts)
        if n == 0:
            return 0.0
        
        # Calculate coverage probability
        f1 = np.sum(counts == 1)  # singletons
        coverage = 1 - f1 / n if n > 0 else 1
        
        # Adjusted counts
        adjusted_counts = counts * coverage
        probabilities = adjusted_counts / np.sum(adjusted_counts)
        
        return EntropyEstimator.shannon_entropy_mle(probabilities, base)
    
    @staticmethod
    def relative_entropy_kl(p: np.ndarray, q: np.ndarray, base: float = 2.0) -> float:
        """Kullback-Leibler divergence"""
        p = p[p > 0]
        q = q[q > 0]
        if len(p) != len(q) or len(p) == 0:
            return float('inf')
        return float(np.sum(p * np.log(p / q) / np.log(base)))
    
    @staticmethod
    def mutual_information(joint_probs: np.ndarray, marginal_x: np.ndarray, 
                          marginal_y: np.ndarray, base: float = 2.0) -> float:
        """Mutual information calculation"""
        joint_probs = joint_probs[joint_probs > 0]
        if len(joint_probs) == 0:
            return 0.0
        
        # Calculate using definition: I(X;Y) = H(X) + H(Y) - H(X,Y)
        h_x = EntropyEstimator.shannon_entropy_mle(marginal_x, base)
        h_y = EntropyEstimator.shannon_entropy_mle(marginal_y, base)
        h_xy = EntropyEstimator.shannon_entropy_mle(joint_probs, base)
        
        return h_x + h_y - h_xy


class EntropyMonitor:
    """
    Comprehensive entropy monitoring for Kimera SWM system
    
    Implements multiple entropy measures and estimation techniques following
    the computational tools specification for benchmarking entropy.
    """
    
    def __init__(self, history_size: int = 1000, estimation_method: str = 'chao_shen'):
        self.history_size = history_size
        self.estimation_method = estimation_method
        self.measurements: deque = deque(maxlen=history_size)
        self.logger = logging.getLogger(__name__)
        
        # Baseline distributions for relative entropy calculations
        self.baseline_distribution: Optional[np.ndarray] = None
        self.reference_timestamp: Optional[datetime] = None
        
        # System state tracking
        self.geoid_states: Dict[str, GeoidState] = {}
        self.vault_distributions: Dict[str, List[float]] = defaultdict(list)
        
    def set_baseline(self, geoids: List[GeoidState]) -> None:
        """Set baseline distribution for relative entropy calculations"""
        if not geoids:
            return
            
        # Aggregate semantic features across all geoids
        all_features = {}
        for geoid in geoids:
            for feature, value in geoid.semantic_state.items():
                if feature not in all_features:
                    all_features[feature] = []
                all_features[feature].append(value)
        
        # Create baseline probability distribution
        feature_means = {k: np.mean(v) for k, v in all_features.items()}
        total = sum(feature_means.values())
        if total > 0:
            self.baseline_distribution = np.array(list(feature_means.values())) / total
        
        self.reference_timestamp = datetime.now()
        self.logger.info(f"Baseline distribution set with {len(all_features)} features")
    
    def calculate_system_entropy(self, geoids: List[GeoidState], 
                                vault_info: Dict[str, Any]) -> EntropyMeasurement:
        """
        Calculate various entropy measures for the current system state.

        If the provided list of geoids is empty, this function returns a zero-filled
        EntropyMeasurement object to ensure downstream stability.
        """
        timestamp = datetime.now()
        
        if not geoids:
            # Return a zero-value measurement if there are no geoids
            return EntropyMeasurement(
                timestamp=timestamp,
                shannon_entropy=0.0,
                thermodynamic_entropy=0.0,
                relative_entropy=0.0,
                conditional_entropy=0.0,
                mutual_information=0.0,
                system_complexity=0.0,
                geoid_count=0,
                vault_distribution={'vault_a': 0, 'vault_b': 0, 'total_scars': 0}
            )
        
        # Update internal state
        self.geoid_states = {g.geoid_id: g for g in geoids}
        
        # Aggregate all semantic features and their activations
        feature_aggregation = defaultdict(float)
        for geoid in geoids:
            for feature, value in geoid.semantic_state.items():
                feature_aggregation[feature] += value
        
        # Calculate probability distributions
        total_activation = sum(feature_aggregation.values())
        
        if total_activation == 0:
            probabilities = np.array([1.0])  # Uniform distribution for empty state
        else:
            probabilities = np.array(list(feature_aggregation.values())) / total_activation
        
        # Shannon entropy using selected estimator
        if self.estimation_method == 'mle':
            shannon_entropy = EntropyEstimator.shannon_entropy_mle(probabilities)
        elif self.estimation_method == 'miller_madow':
            sample_size = len(geoids)
            shannon_entropy = EntropyEstimator.miller_madow_entropy(probabilities, sample_size)
        elif self.estimation_method == 'chao_shen':
            # Convert probabilities back to counts for Chao-Shen
            counts = np.array([v for v in feature_aggregation.values()])
            shannon_entropy = EntropyEstimator.chao_shen_entropy(counts)
        else:
            shannon_entropy = EntropyEstimator.shannon_entropy_mle(probabilities)
        
        # Thermodynamic entropy (using Gibbs formulation)
        thermodynamic_entropy = self._calculate_thermodynamic_entropy(geoids)
        
        # Relative entropy (KL divergence from baseline)
        relative_entropy = 0.0
        if self.baseline_distribution is not None and len(probabilities) == len(self.baseline_distribution):
            relative_entropy = EntropyEstimator.relative_entropy_kl(probabilities, self.baseline_distribution)
        
        # Conditional entropy and mutual information
        conditional_entropy, mutual_information = self._calculate_conditional_measures(geoids)
        
        # System complexity measure
        system_complexity = self._calculate_system_complexity(geoids, vault_info)
        
        # Vault distribution analysis
        vault_distribution = self._analyze_vault_distribution(vault_info)
        
        measurement = EntropyMeasurement(
            timestamp=timestamp,
            shannon_entropy=shannon_entropy,
            thermodynamic_entropy=thermodynamic_entropy,
            relative_entropy=relative_entropy,
            conditional_entropy=conditional_entropy,
            mutual_information=mutual_information,
            system_complexity=system_complexity,
            geoid_count=len(geoids),
            vault_distribution=vault_distribution,
            metadata={
                'estimation_method': self.estimation_method,
                'feature_count': len(feature_aggregation),
                'total_activation': total_activation,
                'has_baseline': self.baseline_distribution is not None
            }
        )
        
        self.measurements.append(measurement)
        return measurement
    
    def _calculate_thermodynamic_entropy(self, geoids: List[GeoidState]) -> float:
        """
        Calculate thermodynamic entropy using statistical mechanics principles.
        
        This method follows the Gibbs formulation: S = -k_B * sum(p_i * ln(p_i)).
        It uses the total semantic activation of a geoid as a proxy for its "energy"
        and filters out any geoids with non-positive energy to prevent log(0) errors.
        """
        if not geoids:
            return 0.0
        
        # Calculate energy-like quantities from semantic activations
        energies = []
        for geoid in geoids:
            # Use total semantic activation as proxy for "energy"
            energy = sum(geoid.semantic_state.values())
            if energy > 0:  # Ensure we only consider positive energy states
                energies.append(energy)
        
        if not energies or sum(energies) == 0:
            return 0.0
        
        # Normalize to get probability distribution (Boltzmann-like)
        total_energy = sum(energies)
        probabilities = np.array(energies) / total_energy
        
        # Calculate thermodynamic entropy (using natural log for thermodynamic convention)
        return float(-np.sum(probabilities * np.log(probabilities + 1e-12)))
    
    def _calculate_conditional_measures(self, geoids: List[GeoidState]) -> Tuple[float, float]:
        """Calculate conditional entropy and mutual information between semantic and symbolic states"""
        if len(geoids) < 2:
            return 0.0, 0.0
        
        # Extract semantic and symbolic features
        semantic_features = []
        symbolic_features = []
        
        for geoid in geoids:
            # Semantic state vector
            semantic_vector = list(geoid.semantic_state.values())
            if semantic_vector:
                semantic_features.append(np.mean(semantic_vector))
            else:
                semantic_features.append(0.0)
            
            # Symbolic state complexity (proxy)
            symbolic_complexity = len(str(geoid.symbolic_state))
            symbolic_features.append(symbolic_complexity)
        
        # Discretize for entropy calculation
        semantic_bins = np.histogram_bin_edges(semantic_features, bins=10)
        symbolic_bins = np.histogram_bin_edges(symbolic_features, bins=10)
        
        semantic_discrete = np.digitize(semantic_features, semantic_bins)
        symbolic_discrete = np.digitize(symbolic_features, symbolic_bins)
        
        # Calculate joint and marginal distributions
        joint_counts = np.histogram2d(semantic_discrete, symbolic_discrete, 
                                    bins=[len(semantic_bins)-1, len(symbolic_bins)-1])[0]
        joint_probs = joint_counts / np.sum(joint_counts) if np.sum(joint_counts) > 0 else joint_counts
        
        marginal_semantic = np.sum(joint_probs, axis=1)
        marginal_symbolic = np.sum(joint_probs, axis=0)
        
        # Calculate measures
        h_semantic = EntropyEstimator.shannon_entropy_mle(marginal_semantic)
        h_symbolic = EntropyEstimator.shannon_entropy_mle(marginal_symbolic)
        h_joint = EntropyEstimator.shannon_entropy_mle(joint_probs.flatten())
        
        conditional_entropy = h_joint - h_semantic  # H(Y|X) = H(X,Y) - H(X)
        mutual_information = h_semantic + h_symbolic - h_joint  # I(X;Y) = H(X) + H(Y) - H(X,Y)
        
        return conditional_entropy, mutual_information
    
    
    def _calculate_system_complexity_adaptive(self, geoids: List[GeoidState], 
                                            vault_info: Dict[str, Any],
                                            system_phase: str = 'balanced') -> float:
        """
        Calculate system complexity with phase-aware weighting.
        
        This enhanced version adapts complexity calculation based on system phase,
        providing more accurate complexity assessment for different operational modes.
        """
        if not geoids:
            return 0.0
        
        # Calculate base complexity components
        structural_complexity = self._calculate_structural_complexity(geoids)
        interaction_complexity = self._calculate_interaction_complexity(geoids)
        vault_complexity = self._calculate_vault_complexity(vault_info)
        
        # Phase-dependent weights
        if system_phase == 'exploration':
            weights = [0.5, 0.3, 0.2]  # Emphasize structural diversity
        elif system_phase == 'consolidation':
            weights = [0.3, 0.5, 0.2]  # Emphasize interactions
        elif system_phase == 'optimization':
            weights = [0.2, 0.3, 0.5]  # Emphasize vault efficiency
        else:  # balanced
            weights = [0.4, 0.4, 0.2]  # Default balanced approach
        
        # Calculate weighted complexity
        total_complexity = (
            structural_complexity * weights[0] +
            interaction_complexity * weights[1] +
            vault_complexity * weights[2]
        )
        
        return total_complexity
    
    def _calculate_structural_complexity(self, geoids: List[GeoidState]) -> float:
        """Calculate structural complexity (unique features)"""
        unique_features = set()
        for geoid in geoids:
            unique_features.update(geoid.semantic_state.keys())
        return len(unique_features)
    
    def _calculate_interaction_complexity(self, geoids: List[GeoidState]) -> float:
        """Calculate interaction complexity (feature co-occurrence)"""
        feature_cooccurrence = defaultdict(set)
        for geoid in geoids:
            features = list(geoid.semantic_state.keys())
            for i, f1 in enumerate(features):
                for f2 in features[i+1:]:
                    feature_cooccurrence[f1].add(f2)
                    feature_cooccurrence[f2].add(f1)
        
        return sum(len(connections) for connections in feature_cooccurrence.values())
    
    def _calculate_vault_complexity(self, vault_info: Dict[str, Any]) -> float:
        """Calculate vault complexity"""
        return sum(vault_info.get(f'{vault}_scars', 0) for vault in ['vault_a', 'vault_b'])
    
    def detect_system_phase(self, recent_measurements: List[EntropyMeasurement]) -> str:
        """
        Detect current system phase based on entropy and complexity trends.
        """
        if len(recent_measurements) < 3:
            return 'balanced'
        
        # Extract trends
        entropies = [m.shannon_entropy for m in recent_measurements[-5:]]
        complexities = [m.system_complexity for m in recent_measurements[-5:]]
        
        # Calculate slopes
        entropy_slope = np.polyfit(range(len(entropies)), entropies, 1)[0] if len(entropies) > 1 else 0
        complexity_slope = np.polyfit(range(len(complexities)), complexities, 1)[0] if len(complexities) > 1 else 0
        
        # Phase detection logic
        if entropy_slope > 0.1 and complexity_slope > 0.1:
            return 'exploration'  # Increasing entropy and complexity
        elif entropy_slope < -0.1:
            return 'consolidation'  # Decreasing entropy
        elif complexity_slope < -0.1:
            return 'optimization'  # Decreasing complexity
        else:
            return 'balanced'  # Stable or mixed signals

    def _calculate_system_complexity(self, geoids: List[GeoidState], 
                                   vault_info: Dict[str, Any]) -> float:
        """
        Calculate system complexity using multiple measures
        Inspired by Kolmogorov complexity concepts
        """
        if not geoids:
            return 0.0
        
        # Structural complexity
        unique_features = set()
        for geoid in geoids:
            unique_features.update(geoid.semantic_state.keys())
        structural_complexity = len(unique_features)
        
        # Interaction complexity (based on feature co-occurrence)
        feature_cooccurrence = defaultdict(set)
        for geoid in geoids:
            features = list(geoid.semantic_state.keys())
            for i, f1 in enumerate(features):
                for f2 in features[i+1:]:
                    feature_cooccurrence[f1].add(f2)
                    feature_cooccurrence[f2].add(f1)
        
        interaction_complexity = sum(len(connections) for connections in feature_cooccurrence.values())
        
        # Vault complexity
        vault_complexity = sum(vault_info.get(f'{vault}_scars', 0) for vault in ['vault_a', 'vault_b'])
        
        # Normalize and combine
        total_complexity = (
            structural_complexity * 0.4 +
            interaction_complexity * 0.4 +
            vault_complexity * 0.2
        )
        
        return total_complexity
    
    def _analyze_vault_distribution(self, vault_info: Dict[str, Any]) -> Dict[str, int]:
        """Analyze distribution of information across vaults"""
        return {
            'vault_a': vault_info.get('vault_a_scars', 0),
            'vault_b': vault_info.get('vault_b_scars', 0),
            'total_scars': vault_info.get('vault_a_scars', 0) + vault_info.get('vault_b_scars', 0)
        }
    
    def get_entropy_trends(self, window_size: int = 100) -> Dict[str, List[float]]:
        """Get entropy trends over recent measurements"""
        if len(self.measurements) < 2:
            return {}
        
        recent_measurements = list(self.measurements)[-window_size:]
        
        return {
            'shannon_entropy': [m.shannon_entropy for m in recent_measurements],
            'thermodynamic_entropy': [m.thermodynamic_entropy for m in recent_measurements],
            'relative_entropy': [m.relative_entropy for m in recent_measurements],
            'system_complexity': [m.system_complexity for m in recent_measurements],
            'timestamps': [m.timestamp.isoformat() for m in recent_measurements]
        }
    
    def detect_entropy_anomalies(self, threshold_std: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalous entropy measurements"""
        if len(self.measurements) < 10:
            return []
        
        recent_measurements = list(self.measurements)[-100:]  # Last 100 measurements
        shannon_values = [m.shannon_entropy for m in recent_measurements]
        
        mean_entropy = np.mean(shannon_values)
        std_entropy = np.std(shannon_values)
        
        anomalies = []
        for measurement in recent_measurements[-10:]:  # Check last 10
            if abs(measurement.shannon_entropy - mean_entropy) > threshold_std * std_entropy:
                anomalies.append({
                    'timestamp': measurement.timestamp.isoformat(),
                    'shannon_entropy': measurement.shannon_entropy,
                    'deviation': abs(measurement.shannon_entropy - mean_entropy) / std_entropy,
                    'type': 'high' if measurement.shannon_entropy > mean_entropy else 'low'
                })
        
        return anomalies
    
    def export_measurements(self, format: str = 'dict') -> Any:
        """Export measurements for analysis"""
        if format == 'dict':
            return [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'shannon_entropy': m.shannon_entropy,
                    'thermodynamic_entropy': m.thermodynamic_entropy,
                    'relative_entropy': m.relative_entropy,
                    'conditional_entropy': m.conditional_entropy,
                    'mutual_information': m.mutual_information,
                    'system_complexity': m.system_complexity,
                    'geoid_count': m.geoid_count,
                    'vault_distribution': m.vault_distribution,
                    'metadata': m.metadata
                }
                for m in self.measurements
            ]
        else:
            raise ValueError(f"Unsupported export format: {format}")
