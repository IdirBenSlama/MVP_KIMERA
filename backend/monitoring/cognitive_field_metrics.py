"""
Cognitive Field Dynamics Metrics Collector

This module provides comprehensive metrics collection and analysis for the Cognitive Field Dynamics system,
tracking wave propagation patterns, field evolution dynamics, resonance interactions, and performance characteristics.
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
import json
from datetime import datetime, timedelta

# Avoid circular imports by using TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engines.cognitive_field_dynamics import CognitiveFieldDynamics, SemanticField, SemanticWave

logger = logging.getLogger(__name__)

@dataclass
class WaveMetrics:
    """Metrics for individual wave tracking"""
    wave_id: str
    origin_id: str
    creation_time: float
    initial_amplitude: float
    current_amplitude: float
    current_radius: float
    propagation_speed: float
    fields_visited: int
    resonance_events: int
    total_energy_transferred: float

@dataclass
class FieldMetrics:
    """Metrics for individual field tracking"""
    field_id: str
    creation_time: float
    initial_strength: float
    current_strength: float
    resonance_frequency: float
    phase: float
    wave_interactions: int
    resonance_amplifications: int
    total_energy_received: float
    neighbor_count: int

@dataclass
class SystemMetrics:
    """Overall system performance metrics"""
    timestamp: float
    total_fields: int
    active_waves: int
    evolution_time: float
    evolution_step_duration: float
    wave_propagation_time: float
    collision_detection_time: float
    resonance_calculation_time: float
    memory_usage_mb: float
    cpu_usage_percent: float

@dataclass
class ResonancePattern:
    """Resonance interaction pattern"""
    frequency: float
    field_count: int
    average_strength: float
    coherence_measure: float
    dominant_phase: float

class CognitiveFieldMetricsCollector:
    """
    Comprehensive metrics collector for Cognitive Field Dynamics system.
    
    Tracks:
    - Wave propagation patterns and efficiency
    - Field evolution dynamics and resonance
    - System performance characteristics
    - Emergent clustering patterns
    - Anomaly detection metrics
    """
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        # Metrics storage
        self.wave_metrics: Dict[str, WaveMetrics] = {}
        self.field_metrics: Dict[str, FieldMetrics] = {}
        self.system_metrics_history: deque = deque(maxlen=max_history_size)
        self.resonance_patterns: Dict[float, ResonancePattern] = {}
        
        # Performance tracking
        self.evolution_times: deque = deque(maxlen=100)
        self.wave_propagation_times: deque = deque(maxlen=100)
        self.api_response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Event counters
        self.total_waves_created = 0
        self.total_fields_created = 0
        self.total_resonance_events = 0
        self.total_collisions = 0
        
        # Analysis cache
        self._analysis_cache: Dict[str, Tuple[float, Any]] = {}
        self._cache_ttl = 30.0  # 30 seconds
        
        logger.info("CognitiveFieldMetricsCollector initialized")
    
    async def collect_system_snapshot(self, cfd_engine: 'CognitiveFieldDynamics') -> SystemMetrics:
        """Collect a comprehensive system metrics snapshot"""
        start_time = time.time()
        
        # Basic counts
        total_fields = len(cfd_engine.fields)
        active_waves = len(cfd_engine.waves)
        
        # Memory usage (approximate)
        memory_usage = self._estimate_memory_usage(cfd_engine)
        
        # Create system metrics
        metrics = SystemMetrics(
            timestamp=start_time,
            total_fields=total_fields,
            active_waves=active_waves,
            evolution_time=cfd_engine.time,
            evolution_step_duration=self._get_average_evolution_time(),
            wave_propagation_time=self._get_average_wave_propagation_time(),
            collision_detection_time=0.0,  # Will be measured during evolution
            resonance_calculation_time=0.0,  # Will be measured during evolution
            memory_usage_mb=memory_usage,
            cpu_usage_percent=0.0  # Would need psutil for accurate measurement
        )
        
        self.system_metrics_history.append(metrics)
        return metrics
    
    def track_wave_creation(self, wave: 'SemanticWave') -> str:
        """Track creation of a new wave and return wave_id"""
        wave_id = f"{wave.origin_id}_{len(self.wave_metrics)}"
        
        metrics = WaveMetrics(
            wave_id=wave_id,
            origin_id=wave.origin_id,
            creation_time=time.time(),
            initial_amplitude=wave.amplitude,
            current_amplitude=wave.amplitude,
            current_radius=wave.radius,
            propagation_speed=wave.propagation_speed,
            fields_visited=0,
            resonance_events=0,
            total_energy_transferred=0.0
        )
        
        self.wave_metrics[wave_id] = metrics
        self.total_waves_created += 1
        
        logger.debug(f"Tracking new wave: {wave_id}")
        return wave_id
    
    def track_field_creation(self, field: 'SemanticField') -> None:
        """Track creation of a new field"""
        metrics = FieldMetrics(
            field_id=field.geoid_id,
            creation_time=time.time(),
            initial_strength=field.field_strength,
            current_strength=field.field_strength,
            resonance_frequency=field.resonance_frequency,
            phase=field.phase,
            wave_interactions=0,
            resonance_amplifications=0,
            total_energy_received=0.0,
            neighbor_count=0
        )
        
        self.field_metrics[field.geoid_id] = metrics
        self.total_fields_created += 1
        
        logger.debug(f"Tracking new field: {field.geoid_id}")
    
    def track_wave_field_interaction(self, wave_id: str, field_id: str, 
                                   energy_transferred: float, is_resonance: bool = False) -> None:
        """Track interaction between wave and field"""
        # Update wave metrics
        if wave_id in self.wave_metrics:
            wave_metrics = self.wave_metrics[wave_id]
            wave_metrics.fields_visited += 1
            wave_metrics.total_energy_transferred += energy_transferred
            if is_resonance:
                wave_metrics.resonance_events += 1
        
        # Update field metrics
        if field_id in self.field_metrics:
            field_metrics = self.field_metrics[field_id]
            field_metrics.wave_interactions += 1
            field_metrics.total_energy_received += energy_transferred
            if is_resonance:
                field_metrics.resonance_amplifications += 1
                self.total_resonance_events += 1
        
        self.total_collisions += 1
        
        logger.debug(f"Wave-field interaction: {wave_id} -> {field_id}, "
                    f"energy: {energy_transferred:.4f}, resonance: {is_resonance}")
    
    def update_field_strength(self, field_id: str, new_strength: float) -> None:
        """Update field strength tracking"""
        if field_id in self.field_metrics:
            self.field_metrics[field_id].current_strength = new_strength
    
    def update_wave_state(self, wave_id: str, amplitude: float, radius: float) -> None:
        """Update wave state tracking"""
        if wave_id in self.wave_metrics:
            metrics = self.wave_metrics[wave_id]
            metrics.current_amplitude = amplitude
            metrics.current_radius = radius
    
    def track_evolution_time(self, duration: float) -> None:
        """Track field evolution step duration"""
        self.evolution_times.append(duration)
    
    def track_wave_propagation_time(self, duration: float) -> None:
        """Track wave propagation processing time"""
        self.wave_propagation_times.append(duration)
    
    def track_api_response_time(self, endpoint: str, duration: float) -> None:
        """Track API endpoint response times"""
        self.api_response_times[endpoint].append(duration)
    
    def analyze_resonance_patterns(self, cfd_engine: 'CognitiveFieldDynamics') -> Dict[str, ResonancePattern]:
        """Analyze resonance patterns across all fields"""
        cache_key = "resonance_patterns"
        cached = self._get_cached_analysis(cache_key)
        if cached is not None:
            return cached
        
        # Group fields by resonance frequency (binned)
        frequency_bins = defaultdict(list)
        bin_size = 0.5  # Frequency bin size
        
        for field in cfd_engine.fields.values():
            bin_freq = round(field.resonance_frequency / bin_size) * bin_size
            frequency_bins[bin_freq].append(field)
        
        patterns = {}
        for freq, fields in frequency_bins.items():
            if len(fields) >= 2:  # Only consider patterns with multiple fields
                strengths = [f.field_strength for f in fields]
                phases = [f.phase for f in fields]
                
                pattern = ResonancePattern(
                    frequency=freq,
                    field_count=len(fields),
                    average_strength=np.mean(strengths),
                    coherence_measure=self._calculate_phase_coherence(phases),
                    dominant_phase=self._calculate_dominant_phase(phases)
                )
                patterns[freq] = pattern
        
        self._cache_analysis(cache_key, patterns)
        return patterns
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "system_overview": {
                "total_fields_created": self.total_fields_created,
                "total_waves_created": self.total_waves_created,
                "total_resonance_events": self.total_resonance_events,
                "total_collisions": self.total_collisions
            },
            "timing_metrics": {
                "average_evolution_time_ms": self._get_average_evolution_time() * 1000,
                "average_wave_propagation_time_ms": self._get_average_wave_propagation_time() * 1000,
                "evolution_time_std_ms": np.std(list(self.evolution_times)) * 1000 if self.evolution_times else 0,
                "api_response_times": {
                    endpoint: {
                        "average_ms": np.mean(times) * 1000,
                        "p95_ms": np.percentile(times, 95) * 1000,
                        "p99_ms": np.percentile(times, 99) * 1000
                    } for endpoint, times in self.api_response_times.items() if times
                }
            },
            "field_metrics": {
                "active_fields": len(self.field_metrics),
                "average_field_strength": np.mean([m.current_strength for m in self.field_metrics.values()]) if self.field_metrics else 0,
                "total_energy_in_system": sum(m.total_energy_received for m in self.field_metrics.values()),
                "most_active_field": self._get_most_active_field()
            },
            "wave_metrics": {
                "active_waves": len(self.wave_metrics),
                "average_wave_amplitude": np.mean([m.current_amplitude for m in self.wave_metrics.values()]) if self.wave_metrics else 0,
                "total_energy_transferred": sum(m.total_energy_transferred for m in self.wave_metrics.values()),
                "most_energetic_wave": self._get_most_energetic_wave()
            }
        }
    
    def get_resonance_analysis(self, cfd_engine: 'CognitiveFieldDynamics') -> Dict[str, Any]:
        """Get detailed resonance pattern analysis"""
        patterns = self.analyze_resonance_patterns(cfd_engine)
        
        return {
            "pattern_count": len(patterns),
            "dominant_frequencies": sorted(patterns.keys(), 
                                         key=lambda f: patterns[f].field_count, 
                                         reverse=True)[:5],
            "coherence_statistics": {
                "average_coherence": np.mean([p.coherence_measure for p in patterns.values()]) if patterns else 0,
                "max_coherence": max([p.coherence_measure for p in patterns.values()]) if patterns else 0,
                "coherent_patterns": len([p for p in patterns.values() if p.coherence_measure > 0.8])
            },
            "frequency_distribution": {
                freq: {
                    "field_count": pattern.field_count,
                    "average_strength": pattern.average_strength,
                    "coherence": pattern.coherence_measure
                } for freq, pattern in patterns.items()
            }
        }
    
    def export_metrics(self, filepath: str) -> None:
        """Export all collected metrics to JSON file"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "collection_period": {
                "start_time": min(m.creation_time for m in self.field_metrics.values()) if self.field_metrics else time.time(),
                "end_time": time.time(),
                "duration_hours": (time.time() - min(m.creation_time for m in self.field_metrics.values())) / 3600 if self.field_metrics else 0
            },
            "performance_summary": self.get_performance_summary(),
            "field_metrics": {
                field_id: {
                    "creation_time": metrics.creation_time,
                    "initial_strength": metrics.initial_strength,
                    "current_strength": metrics.current_strength,
                    "resonance_frequency": metrics.resonance_frequency,
                    "wave_interactions": metrics.wave_interactions,
                    "resonance_amplifications": metrics.resonance_amplifications,
                    "total_energy_received": metrics.total_energy_received
                } for field_id, metrics in self.field_metrics.items()
            },
            "wave_metrics": {
                wave_id: {
                    "origin_id": metrics.origin_id,
                    "creation_time": metrics.creation_time,
                    "initial_amplitude": metrics.initial_amplitude,
                    "current_amplitude": metrics.current_amplitude,
                    "current_radius": metrics.current_radius,
                    "fields_visited": metrics.fields_visited,
                    "resonance_events": metrics.resonance_events,
                    "total_energy_transferred": metrics.total_energy_transferred
                } for wave_id, metrics in self.wave_metrics.items()
            },
            "system_metrics_history": [
                {
                    "timestamp": m.timestamp,
                    "total_fields": m.total_fields,
                    "active_waves": m.active_waves,
                    "evolution_time": m.evolution_time,
                    "memory_usage_mb": m.memory_usage_mb
                } for m in list(self.system_metrics_history)
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")
    
    def reset_metrics(self) -> None:
        """Reset all collected metrics"""
        self.wave_metrics.clear()
        self.field_metrics.clear()
        self.system_metrics_history.clear()
        self.resonance_patterns.clear()
        self.evolution_times.clear()
        self.wave_propagation_times.clear()
        self.api_response_times.clear()
        
        self.total_waves_created = 0
        self.total_fields_created = 0
        self.total_resonance_events = 0
        self.total_collisions = 0
        
        self._analysis_cache.clear()
        
        logger.info("All metrics reset")
    
    # Private helper methods
    
    def _get_average_evolution_time(self) -> float:
        """Get average evolution step time"""
        return np.mean(list(self.evolution_times)) if self.evolution_times else 0.0
    
    def _get_average_wave_propagation_time(self) -> float:
        """Get average wave propagation time"""
        return np.mean(list(self.wave_propagation_times)) if self.wave_propagation_times else 0.0
    
    def _estimate_memory_usage(self, cfd_engine: 'CognitiveFieldDynamics') -> float:
        """Estimate memory usage in MB"""
        # Rough estimation based on data structures
        field_size = len(cfd_engine.fields) * 1024  # Approximate bytes per field
        wave_size = len(cfd_engine.waves) * 512     # Approximate bytes per wave
        metrics_size = len(self.field_metrics) * 256 + len(self.wave_metrics) * 256
        
        total_bytes = field_size + wave_size + metrics_size
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def _calculate_phase_coherence(self, phases: List[float]) -> float:
        """Calculate phase coherence measure"""
        if not phases:
            return 0.0
        
        # Convert phases to complex numbers and calculate coherence
        complex_phases = [np.exp(1j * phase) for phase in phases]
        coherence = abs(np.mean(complex_phases))
        return coherence
    
    def _calculate_dominant_phase(self, phases: List[float]) -> float:
        """Calculate dominant phase"""
        if not phases:
            return 0.0
        
        complex_phases = [np.exp(1j * phase) for phase in phases]
        mean_complex = np.mean(complex_phases)
        return np.angle(mean_complex)
    
    def _get_most_active_field(self) -> Optional[str]:
        """Get field with most wave interactions"""
        if not self.field_metrics:
            return None
        
        return max(self.field_metrics.keys(), 
                  key=lambda fid: self.field_metrics[fid].wave_interactions)
    
    def _get_most_energetic_wave(self) -> Optional[str]:
        """Get wave that transferred most energy"""
        if not self.wave_metrics:
            return None
        
        return max(self.wave_metrics.keys(),
                  key=lambda wid: self.wave_metrics[wid].total_energy_transferred)
    
    def _get_cached_analysis(self, key: str) -> Optional[Any]:
        """Get cached analysis result if still valid"""
        if key in self._analysis_cache:
            timestamp, result = self._analysis_cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return result
        return None
    
    def _cache_analysis(self, key: str, result: Any) -> None:
        """Cache analysis result with timestamp"""
        self._analysis_cache[key] = (time.time(), result)

# Global metrics collector instance
_global_metrics_collector: Optional[CognitiveFieldMetricsCollector] = None

def get_metrics_collector() -> CognitiveFieldMetricsCollector:
    """Get global metrics collector instance"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = CognitiveFieldMetricsCollector()
    return _global_metrics_collector

def reset_global_metrics() -> None:
    """Reset global metrics collector"""
    global _global_metrics_collector
    if _global_metrics_collector is not None:
        _global_metrics_collector.reset_metrics() 