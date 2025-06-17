"""
Enhanced Entropy Monitor with SciPy Integration

This module extends the existing entropy monitoring capabilities with advanced
statistical methods powered by SciPy. It provides more sophisticated entropy
calculations while maintaining full backward compatibility.

Key enhancements:
1. Advanced entropy estimators (Miller-Madow, Dirichlet-based)
2. Differential entropy for continuous distributions
3. Multi-scale entropy analysis for complex systems
4. Enhanced anomaly detection using statistical distributions
5. Adaptive entropy thresholds based on system state
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from collections import defaultdict, deque

# Import base classes
from .entropy_monitor import EntropyMonitor, EntropyMeasurement, EntropyEstimator
from ..core.enhanced_entropy import EnhancedEntropyCalculator
from ..core.geoid import GeoidState

# SciPy imports with fallback
try:
    import scipy.stats as stats
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class EnhancedEntropyMeasurement(EntropyMeasurement):
    """Extended entropy measurement with advanced metrics"""
    differential_entropy: float = 0.0
    jensen_shannon_divergence: float = 0.0
    multiscale_entropy: Dict[int, float] = field(default_factory=dict)
    entropy_rate: float = 0.0
    complexity_index: float = 0.0
    predictability_score: float = 0.0
    anomaly_score: float = 0.0
    adaptive_threshold: float = 0.0


class EnhancedEntropyMonitor(EntropyMonitor):
    """
    Enhanced entropy monitoring with SciPy-powered advanced analytics.
    
    This class extends the base EntropyMonitor with sophisticated statistical
    methods for entropy calculation, anomaly detection, and system analysis.
    """
    
    def __init__(self, history_size: int = 1000, 
                 estimation_method: str = 'chao_shen',
                 use_scipy: bool = True,
                 adaptive_thresholds: bool = True):
        """
        Initialize enhanced entropy monitor.
        
        Args:
            history_size: Number of measurements to keep in history
            estimation_method: Base estimation method
            use_scipy: Whether to use SciPy enhancements
            adaptive_thresholds: Whether to use adaptive anomaly thresholds
        """
        super().__init__(history_size, estimation_method)
        
        self.use_scipy = use_scipy and SCIPY_AVAILABLE
        self.adaptive_thresholds = adaptive_thresholds
        self.enhanced_calculator = EnhancedEntropyCalculator(use_scipy=self.use_scipy)
        
        # Enhanced tracking
        self.system_phase_history: deque = deque(maxlen=100)
        self.complexity_trends: deque = deque(maxlen=100)
        self.anomaly_scores: deque = deque(maxlen=100)
        
        # Adaptive parameters
        self.baseline_complexity: Optional[float] = None
        self.system_maturity: float = 0.0  # 0-1 scale
        
        self.logger.info(f"Enhanced entropy monitor initialized (SciPy: {self.use_scipy})")
    
    def calculate_enhanced_entropy(self, geoids: List[GeoidState], 
                                 vault_info: Dict[str, Any]) -> EnhancedEntropyMeasurement:
        """
        Calculate comprehensive entropy measurements with SciPy enhancements.
        
        Args:
            geoids: List of geoid states
            vault_info: Vault information dictionary
        
        Returns:
            Enhanced entropy measurement with advanced metrics
        """
        # Get base measurement
        base_measurement = self.calculate_system_entropy(geoids, vault_info)
        
        if not geoids:
            return self._create_empty_enhanced_measurement(base_measurement)
        
        # Extract semantic feature data for advanced analysis
        feature_data = self._extract_feature_data(geoids)
        
        # Calculate enhanced metrics
        enhanced_metrics = self._calculate_enhanced_metrics(
            geoids, feature_data, vault_info, base_measurement
        )
        
        # Create enhanced measurement
        enhanced_measurement = EnhancedEntropyMeasurement(
            # Base fields
            timestamp=base_measurement.timestamp,
            shannon_entropy=base_measurement.shannon_entropy,
            thermodynamic_entropy=base_measurement.thermodynamic_entropy,
            relative_entropy=base_measurement.relative_entropy,
            conditional_entropy=base_measurement.conditional_entropy,
            mutual_information=base_measurement.mutual_information,
            system_complexity=base_measurement.system_complexity,
            geoid_count=base_measurement.geoid_count,
            vault_distribution=base_measurement.vault_distribution,
            metadata=base_measurement.metadata,
            
            # Enhanced fields
            differential_entropy=enhanced_metrics['differential_entropy'],
            jensen_shannon_divergence=enhanced_metrics['jensen_shannon_divergence'],
            multiscale_entropy=enhanced_metrics['multiscale_entropy'],
            entropy_rate=enhanced_metrics['entropy_rate'],
            complexity_index=enhanced_metrics['complexity_index'],
            predictability_score=enhanced_metrics['predictability_score'],
            anomaly_score=enhanced_metrics['anomaly_score'],
            adaptive_threshold=enhanced_metrics['adaptive_threshold']
        )
        
        # Update tracking
        self._update_enhanced_tracking(enhanced_measurement)
        
        return enhanced_measurement
    
    def _extract_feature_data(self, geoids: List[GeoidState]) -> Dict[str, Any]:
        """Extract feature data for advanced analysis."""
        feature_values = []
        feature_names = set()
        activation_sequences = []
        
        for geoid in geoids:
            # Collect all feature values
            values = list(geoid.semantic_state.values())
            if values:
                feature_values.extend(values)
                feature_names.update(geoid.semantic_state.keys())
                activation_sequences.append(np.mean(values))
        
        return {
            'feature_values': feature_values,
            'feature_names': list(feature_names),
            'activation_sequences': activation_sequences,
            'geoid_activations': [sum(g.semantic_state.values()) for g in geoids]
        }
    
    def _calculate_enhanced_metrics(self, geoids: List[GeoidState],
                                  feature_data: Dict[str, Any],
                                  vault_info: Dict[str, Any],
                                  base_measurement: EntropyMeasurement) -> Dict[str, Any]:
        """Calculate enhanced entropy metrics."""
        metrics = {}
        
        # 1. Differential Entropy
        if feature_data['feature_values']:
            metrics['differential_entropy'] = self.enhanced_calculator.differential_entropy(
                feature_data['feature_values'], 'gaussian'
            )
        else:
            metrics['differential_entropy'] = 0.0
        
        # 2. Jensen-Shannon Divergence (current vs baseline)
        if self.baseline_distribution is not None and feature_data['feature_values']:
            current_dist = self._create_current_distribution(feature_data)
            if len(current_dist) == len(self.baseline_distribution):
                metrics['jensen_shannon_divergence'] = self.enhanced_calculator.jensen_shannon_divergence(
                    current_dist, self.baseline_distribution.tolist()
                )
            else:
                metrics['jensen_shannon_divergence'] = 0.0
        else:
            metrics['jensen_shannon_divergence'] = 0.0
        
        # 3. Multiscale Entropy
        if feature_data['activation_sequences'] and len(feature_data['activation_sequences']) > 10:
            metrics['multiscale_entropy'] = self.enhanced_calculator.multiscale_entropy(
                feature_data['activation_sequences'], scales=[1, 2, 3, 4, 5]
            )
        else:
            metrics['multiscale_entropy'] = {}
        
        # 4. Entropy Rate
        if feature_data['geoid_activations'] and len(feature_data['geoid_activations']) > 5:
            # Discretize activations for entropy rate calculation
            discretized = self._discretize_sequence(feature_data['geoid_activations'])
            metrics['entropy_rate'] = self.enhanced_calculator.entropy_rate(discretized, order=2)
        else:
            metrics['entropy_rate'] = 0.0
        
        # 5. Complexity Index
        metrics['complexity_index'] = self._calculate_complexity_index(
            base_measurement, metrics['multiscale_entropy']
        )
        
        # 6. Predictability Score
        metrics['predictability_score'] = self._calculate_predictability_score(
            feature_data, metrics['entropy_rate']
        )
        
        # 7. Anomaly Score
        metrics['anomaly_score'] = self._calculate_anomaly_score(base_measurement)
        
        # 8. Adaptive Threshold
        metrics['adaptive_threshold'] = self._calculate_adaptive_threshold(
            base_measurement, vault_info
        )
        
        return metrics
    
    def _create_current_distribution(self, feature_data: Dict[str, Any]) -> List[float]:
        """Create current probability distribution from feature data."""
        if not feature_data['feature_values']:
            return []
        
        # Create histogram of feature values
        values = np.array(feature_data['feature_values'])
        hist, _ = np.histogram(values, bins=len(self.baseline_distribution))
        
        # Normalize to probability distribution
        total = np.sum(hist)
        if total > 0:
            return (hist / total).tolist()
        else:
            return [1.0 / len(hist)] * len(hist)
    
    def _discretize_sequence(self, sequence: List[float], bins: int = 5) -> List[int]:
        """Discretize continuous sequence for entropy rate calculation."""
        if not sequence:
            return []
        
        seq_array = np.array(sequence)
        if np.std(seq_array) == 0:
            return [0] * len(sequence)
        
        # Use quantile-based binning
        quantiles = np.linspace(0, 1, bins + 1)
        bin_edges = np.quantile(seq_array, quantiles)
        
        # Ensure unique bin edges
        bin_edges = np.unique(bin_edges)
        if len(bin_edges) < 2:
            return [0] * len(sequence)
        
        digitized = np.digitize(seq_array, bin_edges) - 1
        return np.clip(digitized, 0, len(bin_edges) - 2).tolist()
    
    def _calculate_complexity_index(self, base_measurement: EntropyMeasurement,
                                  multiscale_entropy: Dict[int, float]) -> float:
        """Calculate complexity index from multiscale entropy."""
        if not multiscale_entropy:
            return base_measurement.system_complexity / 100.0  # Normalize
        
        # Complexity index based on multiscale entropy profile
        entropy_values = list(multiscale_entropy.values())
        if not entropy_values:
            return 0.0
        
        # Calculate complexity as variance in entropy across scales
        entropy_variance = np.var(entropy_values)
        entropy_mean = np.mean(entropy_values)
        
        # Normalize complexity index
        if entropy_mean > 0:
            complexity_index = entropy_variance / entropy_mean
        else:
            complexity_index = 0.0
        
        return min(complexity_index, 1.0)  # Cap at 1.0
    
    def _calculate_predictability_score(self, feature_data: Dict[str, Any],
                                      entropy_rate: float) -> float:
        """Calculate predictability score from entropy rate and patterns."""
        if entropy_rate <= 0:
            return 1.0  # Perfect predictability
        
        # Base predictability from entropy rate
        base_predictability = 1.0 / (1.0 + entropy_rate)
        
        # Adjust based on feature consistency
        if feature_data['activation_sequences'] and len(feature_data['activation_sequences']) > 3:
            sequence = np.array(feature_data['activation_sequences'])
            
            # Calculate autocorrelation for pattern detection
            if self.use_scipy and len(sequence) > 5:
                try:
                    autocorr = signal.correlate(sequence, sequence, mode='full')
                    autocorr = autocorr[autocorr.size // 2:]
                    autocorr = autocorr / autocorr[0]  # Normalize
                    
                    # Predictability boost from strong autocorrelation
                    if len(autocorr) > 1:
                        pattern_strength = np.mean(np.abs(autocorr[1:min(5, len(autocorr))]))
                        base_predictability += pattern_strength * 0.2
                except:
                    pass
        
        return min(base_predictability, 1.0)
    
    def _calculate_anomaly_score(self, base_measurement: EntropyMeasurement) -> float:
        """Calculate anomaly score based on historical patterns."""
        if len(self.measurements) < 10:
            return 0.0
        
        # Get recent entropy values
        recent_entropies = [m.shannon_entropy for m in list(self.measurements)[-20:]]
        current_entropy = base_measurement.shannon_entropy
        
        if self.use_scipy and len(recent_entropies) > 5:
            try:
                # Use statistical test for anomaly detection
                mean_entropy = np.mean(recent_entropies)
                std_entropy = np.std(recent_entropies)
                
                if std_entropy > 0:
                    z_score = abs(current_entropy - mean_entropy) / std_entropy
                    # Convert z-score to anomaly probability
                    anomaly_score = min(z_score / 3.0, 1.0)  # 3-sigma rule
                else:
                    anomaly_score = 0.0
                
                return anomaly_score
            except:
                pass
        
        # Fallback to simple threshold-based detection
        if recent_entropies:
            mean_entropy = np.mean(recent_entropies)
            deviation = abs(current_entropy - mean_entropy)
            max_deviation = max(recent_entropies) - min(recent_entropies)
            
            if max_deviation > 0:
                return min(deviation / max_deviation, 1.0)
        
        return 0.0
    
    def _calculate_adaptive_threshold(self, base_measurement: EntropyMeasurement,
                                    vault_info: Dict[str, Any]) -> float:
        """Calculate adaptive threshold based on system state."""
        if not self.adaptive_thresholds:
            return 0.05  # Default threshold
        
        # Base threshold
        base_threshold = 0.05
        
        # Adjust based on system complexity
        complexity_factor = 1.0 + (base_measurement.system_complexity / 100.0) * 0.2
        
        # Adjust based on vault balance
        total_scars = vault_info.get('vault_a_scars', 0) + vault_info.get('vault_b_scars', 0)
        if total_scars > 0:
            vault_balance = min(vault_info.get('vault_a_scars', 0), 
                              vault_info.get('vault_b_scars', 0)) / total_scars
            balance_factor = 1.0 + (0.5 - vault_balance) * 0.3  # Penalty for imbalance
        else:
            balance_factor = 1.0
        
        # Adjust based on system maturity
        maturity_factor = 1.0 - (self.system_maturity * 0.2)  # More lenient as system matures
        
        adaptive_threshold = base_threshold * complexity_factor * balance_factor * maturity_factor
        
        return max(adaptive_threshold, 0.01)  # Minimum threshold
    
    def _update_enhanced_tracking(self, measurement: EnhancedEntropyMeasurement) -> None:
        """Update enhanced tracking metrics."""
        # Update system phase
        if len(self.measurements) >= 3:
            recent_measurements = list(self.measurements)[-3:]
            phase = self.detect_system_phase(recent_measurements)
            self.system_phase_history.append(phase)
        
        # Update complexity trends
        self.complexity_trends.append(measurement.complexity_index)
        
        # Update anomaly scores
        self.anomaly_scores.append(measurement.anomaly_score)
        
        # Update system maturity
        if len(self.measurements) > 0:
            self.system_maturity = min(len(self.measurements) / 1000.0, 1.0)
        
        # Update baseline complexity
        if self.baseline_complexity is None:
            self.baseline_complexity = measurement.system_complexity
    
    def _create_empty_enhanced_measurement(self, base_measurement: EntropyMeasurement) -> EnhancedEntropyMeasurement:
        """Create empty enhanced measurement for edge cases."""
        return EnhancedEntropyMeasurement(
            timestamp=base_measurement.timestamp,
            shannon_entropy=0.0,
            thermodynamic_entropy=0.0,
            relative_entropy=0.0,
            conditional_entropy=0.0,
            mutual_information=0.0,
            system_complexity=0.0,
            geoid_count=0,
            vault_distribution=base_measurement.vault_distribution,
            differential_entropy=0.0,
            jensen_shannon_divergence=0.0,
            multiscale_entropy={},
            entropy_rate=0.0,
            complexity_index=0.0,
            predictability_score=1.0,
            anomaly_score=0.0,
            adaptive_threshold=0.05
        )
    
    def get_enhanced_trends(self, window_size: int = 100) -> Dict[str, List[float]]:
        """Get enhanced entropy trends with additional metrics."""
        base_trends = self.get_entropy_trends(window_size)
        
        if not hasattr(self, 'measurements') or len(self.measurements) < 2:
            return base_trends
        
        # Get enhanced measurements
        enhanced_measurements = [m for m in self.measurements if isinstance(m, EnhancedEntropyMeasurement)]
        recent_enhanced = enhanced_measurements[-window_size:]
        
        if recent_enhanced:
            base_trends.update({
                'differential_entropy': [m.differential_entropy for m in recent_enhanced],
                'jensen_shannon_divergence': [m.jensen_shannon_divergence for m in recent_enhanced],
                'complexity_index': [m.complexity_index for m in recent_enhanced],
                'predictability_score': [m.predictability_score for m in recent_enhanced],
                'anomaly_score': [m.anomaly_score for m in recent_enhanced],
                'adaptive_threshold': [m.adaptive_threshold for m in recent_enhanced]
            })
        
        return base_trends
    
    def detect_enhanced_anomalies(self, threshold_percentile: float = 95.0) -> List[Dict[str, Any]]:
        """Enhanced anomaly detection using multiple metrics."""
        if len(self.anomaly_scores) < 10:
            return []
        
        # Calculate adaptive threshold
        if self.use_scipy:
            try:
                threshold = np.percentile(list(self.anomaly_scores), threshold_percentile)
            except:
                threshold = 0.8  # Fallback
        else:
            sorted_scores = sorted(self.anomaly_scores)
            idx = int(len(sorted_scores) * threshold_percentile / 100.0)
            threshold = sorted_scores[min(idx, len(sorted_scores) - 1)]
        
        # Find anomalies
        anomalies = []
        recent_measurements = list(self.measurements)[-10:]
        
        for measurement in recent_measurements:
            if isinstance(measurement, EnhancedEntropyMeasurement):
                if measurement.anomaly_score > threshold:
                    anomalies.append({
                        'timestamp': measurement.timestamp.isoformat(),
                        'anomaly_score': measurement.anomaly_score,
                        'shannon_entropy': measurement.shannon_entropy,
                        'complexity_index': measurement.complexity_index,
                        'predictability_score': measurement.predictability_score,
                        'threshold': threshold,
                        'severity': 'high' if measurement.anomaly_score > threshold * 1.5 else 'medium'
                    })
        
        return anomalies
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report."""
        if not self.measurements:
            return {'status': 'no_data', 'health_score': 0.0}
        
        recent_measurements = list(self.measurements)[-10:]
        enhanced_measurements = [m for m in recent_measurements if isinstance(m, EnhancedEntropyMeasurement)]
        
        if not enhanced_measurements:
            return {'status': 'basic_monitoring', 'health_score': 0.5}
        
        latest = enhanced_measurements[-1]
        
        # Calculate health score
        health_components = {
            'entropy_stability': 1.0 - min(latest.anomaly_score, 1.0),
            'predictability': latest.predictability_score,
            'complexity_balance': 1.0 - abs(latest.complexity_index - 0.5) * 2,  # Optimal complexity around 0.5
            'system_maturity': self.system_maturity
        }
        
        health_score = np.mean(list(health_components.values()))
        
        # Determine status
        if health_score > 0.8:
            status = 'excellent'
        elif health_score > 0.6:
            status = 'good'
        elif health_score > 0.4:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'status': status,
            'health_score': health_score,
            'components': health_components,
            'latest_metrics': {
                'shannon_entropy': latest.shannon_entropy,
                'differential_entropy': latest.differential_entropy,
                'complexity_index': latest.complexity_index,
                'predictability_score': latest.predictability_score,
                'anomaly_score': latest.anomaly_score
            },
            'recommendations': self._generate_health_recommendations(health_components, latest)
        }
    
    def _generate_health_recommendations(self, health_components: Dict[str, float],
                                       latest: EnhancedEntropyMeasurement) -> List[str]:
        """Generate health recommendations based on current state."""
        recommendations = []
        
        if health_components['entropy_stability'] < 0.6:
            recommendations.append("High entropy instability detected - consider system stabilization")
        
        if health_components['predictability'] < 0.4:
            recommendations.append("Low predictability - system may benefit from pattern reinforcement")
        
        if health_components['complexity_balance'] < 0.5:
            if latest.complexity_index > 0.7:
                recommendations.append("System complexity too high - consider simplification")
            else:
                recommendations.append("System complexity too low - may need more diverse inputs")
        
        if latest.anomaly_score > 0.8:
            recommendations.append("High anomaly score - investigate recent system changes")
        
        if not recommendations:
            recommendations.append("System operating within normal parameters")
        
        return recommendations


# Convenience function for easy integration
def create_enhanced_entropy_monitor(use_scipy: bool = True,
                                  adaptive_thresholds: bool = True) -> EnhancedEntropyMonitor:
    """Create enhanced entropy monitor with optimal settings."""
    return EnhancedEntropyMonitor(
        history_size=1000,
        estimation_method='chao_shen',
        use_scipy=use_scipy,
        adaptive_thresholds=adaptive_thresholds
    )