"""
Semantic Metrics Collector for Kimera SWM

Implements semantic thermodynamics monitoring following the emerging concepts
outlined in the computational tools specification. Focuses on observer-dependent
entropy retrieval and semantic information processing metrics.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging
from collections import defaultdict, Counter
import re
import math

from ..core.geoid import GeoidState
from ..core.models import LinguisticGeoid


@dataclass
class SemanticMeasurement:
    """Container for semantic measurement data"""
    timestamp: datetime
    semantic_entropy: float
    semantic_complexity: float
    meaning_density: float
    context_coherence: float
    observer_dependency: float
    syntax_to_semantics_ratio: float
    semantic_efficiency: float
    ambiguity_index: float
    information_utility: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class SemanticAnalyzer:
    """
    Advanced semantic analysis tools implementing concepts from semantic thermodynamics
    """
    
    @staticmethod
    def calculate_semantic_entropy(linguistic_geoids: List[LinguisticGeoid], 
                                 context_weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate semantic entropy based on meaning distribution
        Following observer-dependent entropy retrieval (ODER) framework concepts
        """
        if not linguistic_geoids:
            return 0.0
        
        # Extract semantic content indicators
        semantic_features = []
        for lg in linguistic_geoids:
            # Confidence as semantic certainty measure
            semantic_features.append(lg.confidence_score)
            
            # Ambiguity as semantic uncertainty
            ambiguity_factor = len(lg.potential_ambiguities) / 10.0  # Normalize
            semantic_features.append(1.0 - ambiguity_factor)
            
            # Supporting evidence as semantic strength
            support_factor = len(lg.supporting_scars) / 5.0  # Normalize
            semantic_features.append(min(support_factor, 1.0))
        
        # Apply context weights if provided (observer dependency)
        if context_weights:
            weighted_features = []
            for i, feature in enumerate(semantic_features):
                weight_key = f"feature_{i % len(context_weights)}"
                weight = context_weights.get(weight_key, 1.0)
                weighted_features.append(feature * weight)
            semantic_features = weighted_features
        
        # Normalize to probability distribution
        total = sum(semantic_features)
        if total == 0:
            return 0.0
        
        probabilities = np.array(semantic_features) / total
        probabilities = probabilities[probabilities > 0]
        
        # Calculate semantic entropy
        return float(-np.sum(probabilities * np.log2(probabilities)))
    
    @staticmethod
    def measure_meaning_density(text: str, semantic_keywords: Set[str]) -> float:
        """
        Measure the density of meaningful content in text
        Higher density indicates more semantic information per unit
        """
        if not text or not semantic_keywords:
            return 0.0
        
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        meaningful_words = sum(1 for word in words if word in semantic_keywords)
        return meaningful_words / len(words)
    
    @staticmethod
    def calculate_context_coherence(geoids: List[GeoidState]) -> float:
        """
        Measure how coherent the semantic context is across geoids
        Based on feature overlap and consistency
        """
        if len(geoids) < 2:
            return 1.0
        
        # Collect all semantic features
        all_features = set()
        geoid_features = []
        
        for geoid in geoids:
            features = set(geoid.semantic_state.keys())
            all_features.update(features)
            geoid_features.append(features)
        
        if not all_features:
            return 0.0
        
        # Calculate pairwise coherence
        coherence_scores = []
        for i in range(len(geoid_features)):
            for j in range(i + 1, len(geoid_features)):
                intersection = len(geoid_features[i] & geoid_features[j])
                union = len(geoid_features[i] | geoid_features[j])
                if union > 0:
                    coherence_scores.append(intersection / union)
        
        return np.mean(coherence_scores) if coherence_scores else 0.0
    
    @staticmethod
    def measure_observer_dependency(measurements: List[SemanticMeasurement], 
                                  observer_contexts: List[Dict[str, float]]) -> float:
        """
        Measure how much semantic measurements depend on observer context
        Higher values indicate more observer-dependent semantics
        """
        if len(measurements) < 2 or len(observer_contexts) < 2:
            return 0.0
        
        # Calculate variance in semantic entropy across different observer contexts
        entropy_values = [m.semantic_entropy for m in measurements]
        entropy_variance = np.var(entropy_values)
        
        # Normalize by mean to get relative variance
        entropy_mean = np.mean(entropy_values)
        if entropy_mean == 0:
            return 0.0
        
        return entropy_variance / entropy_mean
    
    @staticmethod
    def calculate_syntax_to_semantics_ratio(text: str, semantic_score: float) -> float:
        """
        Calculate the ratio of syntactic complexity to semantic content
        Lower ratios indicate more efficient semantic encoding
        """
        if not text:
            return 0.0
        
        # Syntactic complexity measures
        word_count = len(re.findall(r'\b\w+\b', text))
        sentence_count = len(re.findall(r'[.!?]+', text))
        avg_word_length = np.mean([len(word) for word in re.findall(r'\b\w+\b', text)]) if word_count > 0 else 0
        
        syntactic_complexity = word_count * 0.4 + sentence_count * 0.3 + avg_word_length * 0.3
        
        if semantic_score == 0:
            return float('inf')
        
        return syntactic_complexity / semantic_score


class SemanticMetricsCollector:
    """
    Comprehensive semantic metrics collection for Kimera SWM
    
    Implements semantic thermodynamics monitoring with focus on meaning,
    context, and observer-dependent measures.
    """
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.measurements: List[SemanticMeasurement] = []
        self.logger = logging.getLogger(__name__)
        
        # Semantic knowledge base (can be expanded)
        self.semantic_keywords = {
            'knowledge', 'understanding', 'meaning', 'concept', 'idea', 'thought',
            'reasoning', 'logic', 'inference', 'conclusion', 'analysis', 'synthesis',
            'pattern', 'relationship', 'connection', 'association', 'correlation',
            'context', 'relevance', 'significance', 'importance', 'value', 'utility',
            'information', 'data', 'evidence', 'proof', 'support', 'validation',
            'semantic', 'syntactic', 'linguistic', 'cognitive', 'mental', 'neural'
        }
        
        # Observer context templates
        self.observer_contexts = {
            'analytical': {'precision': 0.9, 'creativity': 0.3, 'speed': 0.6},
            'creative': {'precision': 0.4, 'creativity': 0.9, 'speed': 0.7},
            'balanced': {'precision': 0.6, 'creativity': 0.6, 'speed': 0.6},
            'rapid': {'precision': 0.3, 'creativity': 0.4, 'speed': 0.9}
        }
        
        # Baseline measurements for comparison
        self.baseline_measurement: Optional[SemanticMeasurement] = None
    
    def collect_semantic_metrics(self, 
                                geoids: List[GeoidState],
                                linguistic_geoids: List[LinguisticGeoid],
                                observer_context: str = 'balanced') -> SemanticMeasurement:
        """
        Collect comprehensive semantic metrics for current system state
        """
        timestamp = datetime.now()
        
        # Get observer context weights
        context_weights = self.observer_contexts.get(observer_context, self.observer_contexts['balanced'])
        
        # Calculate semantic entropy
        semantic_entropy = SemanticAnalyzer.calculate_semantic_entropy(
            linguistic_geoids, context_weights
        )
        
        # Calculate semantic complexity
        semantic_complexity = self._calculate_semantic_complexity(geoids, linguistic_geoids)
        
        # Calculate meaning density
        all_text = ' '.join([lg.primary_statement for lg in linguistic_geoids])
        meaning_density = SemanticAnalyzer.measure_meaning_density(all_text, self.semantic_keywords)
        
        # Calculate context coherence
        context_coherence = SemanticAnalyzer.calculate_context_coherence(geoids)
        
        # Calculate observer dependency
        observer_dependency = self._calculate_observer_dependency()
        
        # Calculate syntax-to-semantics ratio
        syntax_to_semantics_ratio = self._calculate_avg_syntax_semantics_ratio(linguistic_geoids)
        
        # Calculate semantic efficiency
        semantic_efficiency = self._calculate_semantic_efficiency(
            semantic_entropy, semantic_complexity, meaning_density
        )
        
        # Calculate ambiguity index
        ambiguity_index = self._calculate_ambiguity_index(linguistic_geoids)
        
        # Calculate information utility
        information_utility = self._calculate_information_utility(
            geoids, linguistic_geoids, context_weights
        )
        
        measurement = SemanticMeasurement(
            timestamp=timestamp,
            semantic_entropy=semantic_entropy,
            semantic_complexity=semantic_complexity,
            meaning_density=meaning_density,
            context_coherence=context_coherence,
            observer_dependency=observer_dependency,
            syntax_to_semantics_ratio=syntax_to_semantics_ratio,
            semantic_efficiency=semantic_efficiency,
            ambiguity_index=ambiguity_index,
            information_utility=information_utility,
            metadata={
                'observer_context': observer_context,
                'geoid_count': len(geoids),
                'linguistic_geoid_count': len(linguistic_geoids),
                'context_weights': context_weights,
                'semantic_keyword_count': len(self.semantic_keywords)
            }
        )
        
        self.measurements.append(measurement)
        
        # Maintain history size
        if len(self.measurements) > self.history_size:
            self.measurements = self.measurements[-self.history_size:]
        
        # Set baseline if first measurement
        if self.baseline_measurement is None:
            self.baseline_measurement = measurement
        
        return measurement
    
    def _calculate_semantic_complexity(self, geoids: List[GeoidState], 
                                     linguistic_geoids: List[LinguisticGeoid]) -> float:
        """Calculate overall semantic complexity of the system"""
        if not geoids and not linguistic_geoids:
            return 0.0
        
        # Geoid semantic complexity
        geoid_complexity = 0.0
        if geoids:
            unique_features = set()
            feature_interactions = 0
            
            for geoid in geoids:
                unique_features.update(geoid.semantic_state.keys())
                # Count feature co-occurrences as interactions
                features = list(geoid.semantic_state.keys())
                feature_interactions += len(features) * (len(features) - 1) / 2
            
            geoid_complexity = len(unique_features) + feature_interactions * 0.1
        
        # Linguistic complexity
        linguistic_complexity = 0.0
        if linguistic_geoids:
            total_ambiguities = sum(len(lg.potential_ambiguities) for lg in linguistic_geoids)
            total_scars = sum(len(lg.supporting_scars) for lg in linguistic_geoids)
            avg_confidence_variance = np.var([lg.confidence_score for lg in linguistic_geoids])
            
            linguistic_complexity = (
                total_ambiguities * 0.4 +
                total_scars * 0.3 +
                avg_confidence_variance * 10 * 0.3  # Scale variance
            )
        
        return geoid_complexity + linguistic_complexity
    
    def _calculate_observer_dependency(self) -> float:
        """Calculate observer dependency based on measurement variance across contexts"""
        if len(self.measurements) < 4:
            return 0.0
        
        # Group measurements by observer context
        context_groups = defaultdict(list)
        for measurement in self.measurements[-20:]:  # Last 20 measurements
            context = measurement.metadata.get('observer_context', 'unknown')
            context_groups[context].append(measurement.semantic_entropy)
        
        if len(context_groups) < 2:
            return 0.0
        
        # Calculate variance across contexts
        context_means = [np.mean(values) for values in context_groups.values()]
        overall_mean = np.mean(context_means)
        
        if overall_mean == 0:
            return 0.0
        
        context_variance = np.var(context_means)
        return context_variance / overall_mean
    
    def _calculate_avg_syntax_semantics_ratio(self, linguistic_geoids: List[LinguisticGeoid]) -> float:
        """Calculate average syntax-to-semantics ratio across linguistic geoids"""
        if not linguistic_geoids:
            return 0.0
        
        ratios = []
        for lg in linguistic_geoids:
            semantic_score = lg.confidence_score * (1 - len(lg.potential_ambiguities) * 0.1)
            ratio = SemanticAnalyzer.calculate_syntax_to_semantics_ratio(
                lg.primary_statement, semantic_score
            )
            if not math.isinf(ratio):
                ratios.append(ratio)
        
        return np.mean(ratios) if ratios else 0.0
    
    def _calculate_semantic_efficiency(self, semantic_entropy: float, 
                                     semantic_complexity: float, 
                                     meaning_density: float) -> float:
        """
        Calculate semantic efficiency: how much meaning per unit of complexity
        Higher values indicate more efficient semantic processing
        """
        if semantic_complexity == 0:
            return 0.0
        
        # Combine semantic measures
        semantic_value = semantic_entropy * 0.4 + meaning_density * 0.6
        
        return semantic_value / semantic_complexity
    
    def _calculate_ambiguity_index(self, linguistic_geoids: List[LinguisticGeoid]) -> float:
        """Calculate system-wide ambiguity index"""
        if not linguistic_geoids:
            return 0.0
        
        total_ambiguities = sum(len(lg.potential_ambiguities) for lg in linguistic_geoids)
        total_statements = len(linguistic_geoids)
        
        # Normalize by confidence scores (lower confidence = higher ambiguity)
        confidence_factor = 1 - np.mean([lg.confidence_score for lg in linguistic_geoids])
        
        base_ambiguity = total_ambiguities / total_statements if total_statements > 0 else 0
        
        return base_ambiguity * (1 + confidence_factor)
    
    def _calculate_information_utility(self, geoids: List[GeoidState],
                                     linguistic_geoids: List[LinguisticGeoid],
                                     context_weights: Dict[str, float]) -> float:
        """
        Calculate information utility: how useful the semantic information is
        for achieving system goals (context-dependent)
        """
        if not geoids and not linguistic_geoids:
            return 0.0
        
        # Task-oriented utility based on context weights
        precision_weight = context_weights.get('precision', 0.5)
        creativity_weight = context_weights.get('creativity', 0.5)
        speed_weight = context_weights.get('speed', 0.5)
        
        # Precision utility: high confidence, low ambiguity
        precision_utility = 0.0
        if linguistic_geoids:
            avg_confidence = np.mean([lg.confidence_score for lg in linguistic_geoids])
            avg_ambiguity = np.mean([len(lg.potential_ambiguities) for lg in linguistic_geoids])
            precision_utility = avg_confidence * (1 - min(avg_ambiguity / 5.0, 1.0))
        
        # Creativity utility: diverse features, novel combinations
        creativity_utility = 0.0
        if geoids:
            all_features = set()
            for geoid in geoids:
                all_features.update(geoid.semantic_state.keys())
            feature_diversity = len(all_features) / len(geoids) if geoids else 0
            creativity_utility = min(feature_diversity / 5.0, 1.0)  # Normalize
        
        # Speed utility: processing efficiency (inverse of complexity)
        speed_utility = 0.0
        if linguistic_geoids:
            avg_statement_length = np.mean([len(lg.primary_statement) for lg in linguistic_geoids])
            speed_utility = 1.0 / (1.0 + avg_statement_length / 100.0)  # Normalize
        
        # Weighted combination
        total_utility = (
            precision_utility * precision_weight +
            creativity_utility * creativity_weight +
            speed_utility * speed_weight
        )
        
        return total_utility / (precision_weight + creativity_weight + speed_weight)
    
    def get_semantic_trends(self, window_size: int = 50) -> Dict[str, List[float]]:
        """Get semantic trends over recent measurements"""
        if len(self.measurements) < 2:
            return {}
        
        recent_measurements = self.measurements[-window_size:]
        
        return {
            'semantic_entropy': [m.semantic_entropy for m in recent_measurements],
            'semantic_complexity': [m.semantic_complexity for m in recent_measurements],
            'meaning_density': [m.meaning_density for m in recent_measurements],
            'context_coherence': [m.context_coherence for m in recent_measurements],
            'semantic_efficiency': [m.semantic_efficiency for m in recent_measurements],
            'ambiguity_index': [m.ambiguity_index for m in recent_measurements],
            'information_utility': [m.information_utility for m in recent_measurements],
            'timestamps': [m.timestamp.isoformat() for m in recent_measurements]
        }
    
    def detect_semantic_anomalies(self, threshold_std: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalous semantic measurements"""
        if len(self.measurements) < 10:
            return []
        
        recent_measurements = self.measurements[-50:]  # Last 50 measurements
        
        anomalies = []
        
        # Check semantic entropy anomalies
        entropy_values = [m.semantic_entropy for m in recent_measurements]
        entropy_mean = np.mean(entropy_values)
        entropy_std = np.std(entropy_values)
        
        for measurement in recent_measurements[-5:]:  # Check last 5
            if abs(measurement.semantic_entropy - entropy_mean) > threshold_std * entropy_std:
                anomalies.append({
                    'timestamp': measurement.timestamp.isoformat(),
                    'type': 'semantic_entropy_anomaly',
                    'value': measurement.semantic_entropy,
                    'deviation': abs(measurement.semantic_entropy - entropy_mean) / entropy_std,
                    'severity': 'high' if measurement.semantic_entropy > entropy_mean else 'low'
                })
        
        # Check semantic efficiency anomalies
        efficiency_values = [m.semantic_efficiency for m in recent_measurements]
        efficiency_mean = np.mean(efficiency_values)
        efficiency_std = np.std(efficiency_values)
        
        for measurement in recent_measurements[-5:]:
            if abs(measurement.semantic_efficiency - efficiency_mean) > threshold_std * efficiency_std:
                anomalies.append({
                    'timestamp': measurement.timestamp.isoformat(),
                    'type': 'semantic_efficiency_anomaly',
                    'value': measurement.semantic_efficiency,
                    'deviation': abs(measurement.semantic_efficiency - efficiency_mean) / efficiency_std,
                    'severity': 'low' if measurement.semantic_efficiency < efficiency_mean else 'high'
                })
        
        return anomalies
    
    def export_semantic_data(self) -> List[Dict[str, Any]]:
        """Export semantic measurements for analysis"""
        return [
            {
                'timestamp': m.timestamp.isoformat(),
                'semantic_entropy': m.semantic_entropy,
                'semantic_complexity': m.semantic_complexity,
                'meaning_density': m.meaning_density,
                'context_coherence': m.context_coherence,
                'observer_dependency': m.observer_dependency,
                'syntax_to_semantics_ratio': m.syntax_to_semantics_ratio,
                'semantic_efficiency': m.semantic_efficiency,
                'ambiguity_index': m.ambiguity_index,
                'information_utility': m.information_utility,
                'metadata': m.metadata
            }
            for m in self.measurements
        ]
