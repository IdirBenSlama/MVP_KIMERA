"""
Temporal Dynamics Engine
Adds time-aware semantic processing and temporal understanding
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)

class TemporalScale(Enum):
    """Different temporal scales for analysis"""
    INSTANTANEOUS = "instantaneous"  # < 1 second
    IMMEDIATE = "immediate"          # 1-60 seconds
    SHORT_TERM = "short_term"        # 1-60 minutes
    MEDIUM_TERM = "medium_term"      # 1-24 hours
    LONG_TERM = "long_term"          # 1-30 days
    EXTENDED = "extended"            # > 30 days

@dataclass
class TemporalPattern:
    """Represents a temporal pattern in concept behavior"""
    pattern_type: str  # periodic, trending, sporadic, etc.
    period: Optional[float] = None  # For periodic patterns
    trend: Optional[str] = None  # increasing, decreasing, stable
    confidence: float = 0.0
    observations: List[Tuple[float, Any]] = None  # (timestamp, value) pairs
    
    def __post_init__(self):
        if self.observations is None:
            self.observations = []

@dataclass
class TemporalContext:
    """Temporal context for a concept"""
    concept: str
    duration: Optional[Dict[str, float]] = None  # min, max, typical
    frequency: Optional[Dict[str, float]] = None  # occurrences per time unit
    patterns: List[TemporalPattern] = None
    lifecycle: Optional[Dict[str, Any]] = None  # birth, growth, decay phases
    temporal_associations: Dict[str, float] = None  # Related concepts in time
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = []
        if self.temporal_associations is None:
            self.temporal_associations = {}


class TemporalDynamicsEngine:
    """
    Engine for understanding temporal aspects of concepts and their evolution.
    Provides time-aware semantic processing capabilities.
    """
    
    def __init__(self):
        # Temporal knowledge base
        self.temporal_knowledge = {}
        
        # Pattern detection parameters
        self.min_observations = 3
        self.pattern_confidence_threshold = 0.6
        
        # Temporal association matrix
        self.temporal_associations = defaultdict(lambda: defaultdict(float))
        
        # Initialize with basic temporal knowledge
        self._init_temporal_knowledge()
        
        logger.info("Temporal Dynamics Engine initialized")
    
    def _init_temporal_knowledge(self):
        """Initialize basic temporal knowledge about concepts"""
        # Natural phenomena
        self.temporal_knowledge['day'] = {
            'duration': {'typical': 86400, 'min': 86400, 'max': 86400},  # seconds
            'frequency': {'per_week': 7, 'per_month': 30, 'per_year': 365},
            'patterns': [TemporalPattern('periodic', period=86400, confidence=1.0)],
            'lifecycle': {'type': 'cyclic', 'phases': ['dawn', 'morning', 'noon', 'evening', 'night']}
        }
        
        self.temporal_knowledge['season'] = {
            'duration': {'typical': 7776000, 'min': 7776000, 'max': 7776000},  # ~90 days
            'frequency': {'per_year': 4},
            'patterns': [TemporalPattern('periodic', period=31536000/4, confidence=1.0)],
            'lifecycle': {'type': 'cyclic', 'phases': ['spring', 'summer', 'fall', 'winter']}
        }
        
        # Human activities
        self.temporal_knowledge['meal'] = {
            'duration': {'typical': 1800, 'min': 600, 'max': 7200},  # 30 min typical
            'frequency': {'per_day': 3, 'per_week': 21},
            'patterns': [TemporalPattern('periodic', period=28800, confidence=0.8)],  # ~8 hours
            'lifecycle': {'type': 'discrete', 'phases': ['preparation', 'eating', 'cleanup']}
        }
        
        self.temporal_knowledge['sleep'] = {
            'duration': {'typical': 28800, 'min': 14400, 'max': 36000},  # 8 hours typical
            'frequency': {'per_day': 1, 'per_week': 7},
            'patterns': [TemporalPattern('periodic', period=86400, confidence=0.9)],
            'lifecycle': {'type': 'continuous', 'phases': ['light', 'deep', 'REM']}
        }
        
        # Events
        self.temporal_knowledge['lightning'] = {
            'duration': {'typical': 0.0002, 'min': 0.0001, 'max': 0.001},  # milliseconds
            'frequency': {'per_storm': 100, 'variable': True},
            'patterns': [TemporalPattern('sporadic', confidence=0.7)],
            'lifecycle': {'type': 'instantaneous'}
        }
        
        self.temporal_knowledge['rain'] = {
            'duration': {'typical': 3600, 'min': 300, 'max': 86400},  # 1 hour typical
            'frequency': {'variable': True, 'seasonal': True},
            'patterns': [TemporalPattern('sporadic', confidence=0.6)],
            'lifecycle': {'type': 'continuous', 'phases': ['drizzle', 'steady', 'heavy', 'tapering']}
        }
    
    def contextualize(self, concept: str, 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add temporal context to a concept.
        
        Args:
            concept: The concept to contextualize
            context: Optional additional context
            
        Returns:
            Temporal context information
        """
        logger.debug(f"Contextualizing temporal aspects of: {concept}")
        
        # Check if we have direct temporal knowledge
        if concept.lower() in self.temporal_knowledge:
            known = self.temporal_knowledge[concept.lower()]
            temporal_ctx = TemporalContext(
                concept=concept,
                duration=known.get('duration'),
                frequency=known.get('frequency'),
                patterns=known.get('patterns', []),
                lifecycle=known.get('lifecycle'),
                confidence=0.9
            )
        else:
            # Infer temporal properties
            temporal_ctx = self._infer_temporal_context(concept, context)
        
        # Add temporal associations
        temporal_ctx.temporal_associations = self._find_temporal_associations(concept)
        
        # Analyze patterns if we have observations
        if context and 'observations' in context:
            patterns = self._detect_temporal_patterns(context['observations'])
            temporal_ctx.patterns.extend(patterns)
        
        return {
            'duration': temporal_ctx.duration,
            'frequency': temporal_ctx.frequency,
            'patterns': [self._pattern_to_dict(p) for p in temporal_ctx.patterns],
            'lifecycle': temporal_ctx.lifecycle,
            'temporal_associations': temporal_ctx.temporal_associations,
            'confidence': temporal_ctx.confidence,
            'temporal_scale': self._determine_temporal_scale(temporal_ctx)
        }
    
    def _infer_temporal_context(self, concept: str, 
                               context: Optional[Dict[str, Any]]) -> TemporalContext:
        """Infer temporal properties when not directly known"""
        temporal_ctx = TemporalContext(concept=concept, confidence=0.5)
        
        concept_lower = concept.lower()
        
        # Duration inference based on concept type
        if any(word in concept_lower for word in ['instant', 'moment', 'flash']):
            temporal_ctx.duration = {'typical': 1, 'min': 0.1, 'max': 5}
            temporal_ctx.lifecycle = {'type': 'instantaneous'}
        elif any(word in concept_lower for word in ['quick', 'fast', 'rapid']):
            temporal_ctx.duration = {'typical': 60, 'min': 10, 'max': 300}
        elif any(word in concept_lower for word in ['slow', 'gradual', 'lengthy']):
            temporal_ctx.duration = {'typical': 3600, 'min': 1800, 'max': 86400}
        elif any(word in concept_lower for word in ['eternal', 'permanent', 'forever']):
            temporal_ctx.duration = {'typical': float('inf'), 'min': 31536000, 'max': float('inf')}
        
        # Frequency inference
        if any(word in concept_lower for word in ['daily', 'everyday']):
            temporal_ctx.frequency = {'per_day': 1, 'per_week': 7}
            temporal_ctx.patterns = [TemporalPattern('periodic', period=86400, confidence=0.7)]
        elif any(word in concept_lower for word in ['weekly']):
            temporal_ctx.frequency = {'per_week': 1, 'per_month': 4}
            temporal_ctx.patterns = [TemporalPattern('periodic', period=604800, confidence=0.7)]
        elif any(word in concept_lower for word in ['rare', 'occasional']):
            temporal_ctx.frequency = {'variable': True, 'typical': 0.01}
            temporal_ctx.patterns = [TemporalPattern('sporadic', confidence=0.6)]
        
        # Lifecycle inference
        if any(word in concept_lower for word in ['cycle', 'circular', 'repeating']):
            temporal_ctx.lifecycle = {'type': 'cyclic'}
        elif any(word in concept_lower for word in ['grow', 'decay', 'age']):
            temporal_ctx.lifecycle = {'type': 'progressive', 'phases': ['birth', 'growth', 'maturity', 'decay']}
        
        # Use context if provided
        if context:
            if 'duration' in context:
                temporal_ctx.duration = context['duration']
                temporal_ctx.confidence = 0.8
            if 'frequency' in context:
                temporal_ctx.frequency = context['frequency']
                temporal_ctx.confidence = 0.8
        
        return temporal_ctx
    
    def _detect_temporal_patterns(self, observations: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """Detect temporal patterns from observations"""
        patterns = []
        
        if len(observations) < self.min_observations:
            return patterns
        
        # Extract timestamps and values
        timestamps = []
        values = []
        
        for obs in observations:
            if 'timestamp' in obs and 'value' in obs:
                timestamps.append(obs['timestamp'])
                values.append(obs['value'])
        
        if len(timestamps) < self.min_observations:
            return patterns
        
        # Sort by timestamp
        sorted_data = sorted(zip(timestamps, values))
        timestamps, values = zip(*sorted_data)
        
        # Check for periodicity
        periodic_pattern = self._check_periodicity(timestamps)
        if periodic_pattern:
            patterns.append(periodic_pattern)
        
        # Check for trends
        trend_pattern = self._check_trends(timestamps, values)
        if trend_pattern:
            patterns.append(trend_pattern)
        
        # Check for clustering (sporadic events)
        cluster_pattern = self._check_clustering(timestamps)
        if cluster_pattern:
            patterns.append(cluster_pattern)
        
        return patterns
    
    def _check_periodicity(self, timestamps: List[float]) -> Optional[TemporalPattern]:
        """Check if timestamps show periodic behavior"""
        if len(timestamps) < 3:
            return None
        
        # Calculate intervals
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if not intervals:
            return None
        
        # Check if intervals are consistent
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # Low variance indicates periodicity
        if std_interval / mean_interval < 0.2:  # Less than 20% variation
            return TemporalPattern(
                pattern_type='periodic',
                period=mean_interval,
                confidence=0.8 - (std_interval / mean_interval)
            )
        
        return None
    
    def _check_trends(self, timestamps: List[float], values: List[Any]) -> Optional[TemporalPattern]:
        """Check for trending patterns in values over time"""
        # Convert values to numeric if possible
        numeric_values = []
        for v in values:
            try:
                numeric_values.append(float(v))
            except:
                return None  # Can't detect trends in non-numeric data
        
        if len(numeric_values) < 3:
            return None
        
        # Simple linear regression
        x = np.array(timestamps)
        y = np.array(numeric_values)
        
        # Normalize timestamps
        x = x - x[0]
        
        # Calculate slope
        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        
        # Determine trend type
        if abs(slope) < 0.01:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        # Calculate R-squared for confidence
        y_mean = np.mean(y)
        ss_tot = np.sum((y - y_mean)**2)
        y_pred = slope * x + y_mean
        ss_res = np.sum((y - y_pred)**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        if r_squared > 0.5:  # Reasonable correlation
            return TemporalPattern(
                pattern_type='trending',
                trend=trend,
                confidence=r_squared,
                observations=list(zip(timestamps, numeric_values))
            )
        
        return None
    
    def _check_clustering(self, timestamps: List[float]) -> Optional[TemporalPattern]:
        """Check if events cluster in time (sporadic pattern)"""
        if len(timestamps) < 3:
            return None
        
        # Calculate intervals
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        # High variance indicates sporadic behavior
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if std_interval / mean_interval > 0.5:  # More than 50% variation
            return TemporalPattern(
                pattern_type='sporadic',
                confidence=min(0.9, std_interval / mean_interval)
            )
        
        return None
    
    def _find_temporal_associations(self, concept: str) -> Dict[str, float]:
        """Find concepts that are temporally associated"""
        associations = {}
        
        # Check stored associations
        if concept in self.temporal_associations:
            associations.update(self.temporal_associations[concept])
        
        # Add known temporal relationships
        temporal_pairs = {
            'day': ['night', 'sunrise', 'sunset'],
            'night': ['day', 'sleep', 'moon'],
            'spring': ['summer', 'flowers', 'growth'],
            'summer': ['fall', 'heat', 'vacation'],
            'fall': ['winter', 'leaves', 'harvest'],
            'winter': ['spring', 'cold', 'snow'],
            'cause': ['effect'],
            'before': ['after'],
            'start': ['end', 'finish'],
            'birth': ['death', 'life'],
            'past': ['present', 'future']
        }
        
        concept_lower = concept.lower()
        if concept_lower in temporal_pairs:
            for associated in temporal_pairs[concept_lower]:
                associations[associated] = 0.8
        
        # Check reverse associations
        for key, values in temporal_pairs.items():
            if concept_lower in values:
                associations[key] = 0.8
        
        return associations
    
    def _determine_temporal_scale(self, temporal_ctx: TemporalContext) -> str:
        """Determine the temporal scale of a concept"""
        if not temporal_ctx.duration:
            return TemporalScale.INSTANTANEOUS.value
        
        typical_duration = temporal_ctx.duration.get('typical', 0)
        
        if typical_duration < 1:
            return TemporalScale.INSTANTANEOUS.value
        elif typical_duration < 60:
            return TemporalScale.IMMEDIATE.value
        elif typical_duration < 3600:
            return TemporalScale.SHORT_TERM.value
        elif typical_duration < 86400:
            return TemporalScale.MEDIUM_TERM.value
        elif typical_duration < 2592000:  # 30 days
            return TemporalScale.LONG_TERM.value
        else:
            return TemporalScale.EXTENDED.value
    
    def _pattern_to_dict(self, pattern: TemporalPattern) -> Dict[str, Any]:
        """Convert TemporalPattern to dictionary"""
        return {
            'type': pattern.pattern_type,
            'period': pattern.period,
            'trend': pattern.trend,
            'confidence': pattern.confidence,
            'observation_count': len(pattern.observations)
        }
    
    def predict_next_occurrence(self, concept: str, 
                               last_occurrence: float,
                               pattern: Optional[TemporalPattern] = None) -> Optional[Dict[str, Any]]:
        """
        Predict when a concept will next occur based on temporal patterns.
        
        Args:
            concept: The concept to predict
            last_occurrence: Timestamp of last occurrence
            pattern: Optional known pattern to use
            
        Returns:
            Prediction with timestamp and confidence
        """
        if not pattern:
            # Try to find pattern from knowledge base
            if concept.lower() in self.temporal_knowledge:
                patterns = self.temporal_knowledge[concept.lower()].get('patterns', [])
                if patterns:
                    pattern = patterns[0]  # Use primary pattern
        
        if not pattern:
            return None
        
        prediction = {
            'concept': concept,
            'last_occurrence': last_occurrence,
            'pattern_used': pattern.pattern_type
        }
        
        if pattern.pattern_type == 'periodic' and pattern.period:
            # Simple periodic prediction
            prediction['next_occurrence'] = last_occurrence + pattern.period
            prediction['confidence'] = pattern.confidence
            prediction['uncertainty_range'] = pattern.period * 0.1  # 10% uncertainty
        
        elif pattern.pattern_type == 'trending' and pattern.observations:
            # Extrapolate from trend
            if len(pattern.observations) >= 2:
                # Simple linear extrapolation
                times = [obs[0] for obs in pattern.observations]
                last_interval = times[-1] - times[-2]
                prediction['next_occurrence'] = last_occurrence + last_interval
                prediction['confidence'] = pattern.confidence * 0.8  # Less confident
                prediction['uncertainty_range'] = last_interval * 0.3
        
        elif pattern.pattern_type == 'sporadic':
            # Can't predict sporadic events precisely
            prediction['next_occurrence'] = None
            prediction['confidence'] = 0.1
            prediction['note'] = 'Sporadic pattern - occurrence unpredictable'
        
        return prediction
    
    def analyze_temporal_evolution(self, concept: str,
                                 time_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze how a concept evolves over time.
        
        Args:
            concept: The concept to analyze
            time_series: List of observations with timestamps and states
            
        Returns:
            Analysis of temporal evolution
        """
        if len(time_series) < 2:
            return {'error': 'Insufficient data for temporal analysis'}
        
        # Sort by timestamp
        sorted_series = sorted(time_series, key=lambda x: x['timestamp'])
        
        # Identify phases
        phases = self._identify_phases(sorted_series)
        
        # Calculate rates of change
        change_rates = self._calculate_change_rates(sorted_series)
        
        # Detect anomalies
        anomalies = self._detect_temporal_anomalies(sorted_series)
        
        # Determine lifecycle stage
        lifecycle_stage = self._determine_lifecycle_stage(concept, sorted_series)
        
        return {
            'concept': concept,
            'time_span': sorted_series[-1]['timestamp'] - sorted_series[0]['timestamp'],
            'observation_count': len(sorted_series),
            'phases': phases,
            'change_rates': change_rates,
            'anomalies': anomalies,
            'lifecycle_stage': lifecycle_stage,
            'evolution_type': self._classify_evolution(phases, change_rates)
        }
    
    def _identify_phases(self, time_series: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify distinct phases in temporal evolution"""
        phases = []
        
        # Simple phase detection based on value changes
        current_phase = {
            'start': time_series[0]['timestamp'],
            'values': [time_series[0].get('value', time_series[0].get('state'))]
        }
        
        for i in range(1, len(time_series)):
            current_value = time_series[i].get('value', time_series[i].get('state'))
            prev_value = time_series[i-1].get('value', time_series[i-1].get('state'))
            
            # Detect significant change
            if self._is_significant_change(prev_value, current_value):
                # End current phase
                current_phase['end'] = time_series[i-1]['timestamp']
                current_phase['duration'] = current_phase['end'] - current_phase['start']
                phases.append(current_phase)
                
                # Start new phase
                current_phase = {
                    'start': time_series[i]['timestamp'],
                    'values': [current_value]
                }
            else:
                current_phase['values'].append(current_value)
        
        # Add final phase
        current_phase['end'] = time_series[-1]['timestamp']
        current_phase['duration'] = current_phase['end'] - current_phase['start']
        phases.append(current_phase)
        
        return phases
    
    def _is_significant_change(self, value1: Any, value2: Any) -> bool:
        """Determine if change between values is significant"""
        if type(value1) != type(value2):
            return True
        
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            # Numeric comparison
            if value1 == 0:
                return abs(value2) > 0.1
            return abs(value2 - value1) / abs(value1) > 0.2  # 20% change
        
        return value1 != value2
    
    def _calculate_change_rates(self, time_series: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate rates of change over time"""
        rates = {
            'average': 0.0,
            'maximum': 0.0,
            'minimum': float('inf'),
            'acceleration': 0.0
        }
        
        if len(time_series) < 2:
            return rates
        
        # Calculate rates between consecutive points
        point_rates = []
        
        for i in range(1, len(time_series)):
            time_diff = time_series[i]['timestamp'] - time_series[i-1]['timestamp']
            if time_diff > 0:
                value1 = time_series[i-1].get('value', 0)
                value2 = time_series[i].get('value', 0)
                
                try:
                    rate = (float(value2) - float(value1)) / time_diff
                    point_rates.append(rate)
                except:
                    pass
        
        if point_rates:
            rates['average'] = np.mean(point_rates)
            rates['maximum'] = max(point_rates)
            rates['minimum'] = min(point_rates)
            
            # Calculate acceleration (rate of rate change)
            if len(point_rates) > 1:
                rate_changes = [point_rates[i+1] - point_rates[i] 
                               for i in range(len(point_rates)-1)]
                rates['acceleration'] = np.mean(rate_changes)
        
        return rates
    
    def _detect_temporal_anomalies(self, time_series: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in temporal patterns"""
        anomalies = []
        
        if len(time_series) < 3:
            return anomalies
        
        # Check for unusual intervals
        intervals = []
        for i in range(1, len(time_series)):
            interval = time_series[i]['timestamp'] - time_series[i-1]['timestamp']
            intervals.append(interval)
        
        if intervals:
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            for i, interval in enumerate(intervals):
                # Anomaly if interval is more than 2 standard deviations from mean
                if abs(interval - mean_interval) > 2 * std_interval:
                    anomalies.append({
                        'type': 'interval_anomaly',
                        'index': i + 1,
                        'timestamp': time_series[i + 1]['timestamp'],
                        'expected_interval': mean_interval,
                        'actual_interval': interval,
                        'severity': abs(interval - mean_interval) / std_interval
                    })
        
        return anomalies
    
    def _determine_lifecycle_stage(self, concept: str, 
                                 time_series: List[Dict[str, Any]]) -> Optional[str]:
        """Determine current lifecycle stage of a concept"""
        # Check if concept has known lifecycle
        if concept.lower() in self.temporal_knowledge:
            lifecycle = self.temporal_knowledge[concept.lower()].get('lifecycle')
            if lifecycle and 'phases' in lifecycle:
                # Simple heuristic: divide time span by number of phases
                phases = lifecycle['phases']
                time_span = time_series[-1]['timestamp'] - time_series[0]['timestamp']
                phase_duration = time_span / len(phases)
                
                current_time = time_series[-1]['timestamp']
                elapsed = current_time - time_series[0]['timestamp']
                phase_index = min(int(elapsed / phase_duration), len(phases) - 1)
                
                return phases[phase_index]
        
        # Generic lifecycle detection based on value trends
        if len(time_series) >= 3:
            # Get values from first, middle, and last thirds
            third = len(time_series) // 3
            early_values = [ts.get('value', 0) for ts in time_series[:third]]
            mid_values = [ts.get('value', 0) for ts in time_series[third:2*third]]
            late_values = [ts.get('value', 0) for ts in time_series[2*third:]]
            
            try:
                early_avg = np.mean([float(v) for v in early_values])
                mid_avg = np.mean([float(v) for v in mid_values])
                late_avg = np.mean([float(v) for v in late_values])
                
                if late_avg > mid_avg > early_avg:
                    return 'growth'
                elif early_avg > mid_avg > late_avg:
                    return 'decay'
                elif mid_avg > early_avg and mid_avg > late_avg:
                    return 'maturity'
                else:
                    return 'stable'
            except:
                pass
        
        return None
    
    def _classify_evolution(self, phases: List[Dict[str, Any]], 
                          change_rates: Dict[str, float]) -> str:
        """Classify the type of temporal evolution"""
        if len(phases) == 1:
            return 'static'
        
        if change_rates['acceleration'] > 0.1:
            return 'accelerating'
        elif change_rates['acceleration'] < -0.1:
            return 'decelerating'
        elif abs(change_rates['average']) < 0.01:
            return 'stable'
        elif len(phases) > 3:
            return 'complex'
        else:
            return 'evolving'