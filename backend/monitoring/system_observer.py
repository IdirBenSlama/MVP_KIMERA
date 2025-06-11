"""
System Observer for Kimera SWM

Implements comprehensive system observation and monitoring, integrating all
monitoring components to provide a holistic view of system behavior.
Follows observer-dependent principles from semantic thermodynamics.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import asyncio
from collections import defaultdict, deque
import json

from ..core.geoid import GeoidState
from ..core.models import LinguisticGeoid
from .entropy_monitor import EntropyMonitor, EntropyMeasurement
from .semantic_metrics import SemanticMetricsCollector, SemanticMeasurement
from .thermodynamic_analyzer import ThermodynamicAnalyzer, ThermodynamicState


@dataclass
class SystemSnapshot:
    """Complete system state snapshot"""
    timestamp: datetime
    entropy_measurement: EntropyMeasurement
    semantic_measurement: SemanticMeasurement
    thermodynamic_state: ThermodynamicState
    system_health: Dict[str, Any]
    observer_context: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ObserverProfile:
    """Observer profile for context-dependent monitoring"""
    name: str
    attention_weights: Dict[str, float]
    temporal_focus: str  # 'short', 'medium', 'long'
    analysis_depth: str  # 'surface', 'moderate', 'deep'
    priority_metrics: List[str]
    alert_thresholds: Dict[str, float]


class SystemObserver:
    """
    Comprehensive system observer implementing observer-dependent monitoring
    
    Integrates entropy monitoring, semantic metrics, and thermodynamic analysis
    to provide a complete view of Kimera SWM system behavior.
    """
    
    def __init__(self, 
                 history_size: int = 1000,
                 observation_interval: float = 1.0,
                 vault_capacity: int = 10000):
        
        self.history_size = history_size
        self.observation_interval = observation_interval
        self.logger = logging.getLogger(__name__)
        
        # Initialize monitoring components
        self.entropy_monitor = EntropyMonitor(history_size)
        self.semantic_collector = SemanticMetricsCollector(history_size)
        self.thermodynamic_analyzer = ThermodynamicAnalyzer(history_size, vault_capacity)
        
        # System state tracking
        self.snapshots: deque = deque(maxlen=history_size)
        self.active_observers: Dict[str, ObserverProfile] = {}
        self.current_observer = 'default'
        
        # Alert system
        self.alert_callbacks: List[Callable] = []
        self.alert_history: deque = deque(maxlen=1000)
        
        # Performance tracking
        self.observation_times: deque = deque(maxlen=100)
        self.last_observation: Optional[datetime] = None
        
        # Initialize default observer profiles
        self._initialize_observer_profiles()
        
        # System health tracking
        self.health_indicators = {
            'entropy_stability': 1.0,
            'semantic_coherence': 1.0,
            'thermodynamic_efficiency': 1.0,
            'processing_speed': 1.0,
            'memory_utilization': 0.0,
            'error_rate': 0.0
        }
    
    def _initialize_observer_profiles(self):
        """Initialize default observer profiles"""
        
        # Analytical observer - focuses on precision and consistency
        self.active_observers['analytical'] = ObserverProfile(
            name='analytical',
            attention_weights={
                'entropy': 0.3,
                'thermodynamic': 0.4,
                'semantic': 0.3
            },
            temporal_focus='long',
            analysis_depth='deep',
            priority_metrics=['entropy_stability', 'thermodynamic_efficiency', 'reversibility_index'],
            alert_thresholds={
                'entropy_anomaly': 1.5,
                'efficiency_drop': 0.2,
                'temperature_spike': 2.0
            }
        )
        
        # Operational observer - focuses on system performance
        self.active_observers['operational'] = ObserverProfile(
            name='operational',
            attention_weights={
                'entropy': 0.2,
                'thermodynamic': 0.3,
                'semantic': 0.5
            },
            temporal_focus='short',
            analysis_depth='moderate',
            priority_metrics=['processing_speed', 'semantic_efficiency', 'information_utility'],
            alert_thresholds={
                'processing_delay': 2.0,
                'semantic_degradation': 1.8,
                'utility_drop': 0.3
            }
        )
        
        # Research observer - focuses on novel patterns and anomalies
        self.active_observers['research'] = ObserverProfile(
            name='research',
            attention_weights={
                'entropy': 0.4,
                'thermodynamic': 0.3,
                'semantic': 0.3
            },
            temporal_focus='medium',
            analysis_depth='deep',
            priority_metrics=['system_complexity', 'observer_dependency', 'ambiguity_index'],
            alert_thresholds={
                'complexity_spike': 1.2,
                'anomaly_detection': 1.0,
                'pattern_emergence': 0.8
            }
        )
        
        # Default observer - balanced monitoring
        self.active_observers['default'] = ObserverProfile(
            name='default',
            attention_weights={
                'entropy': 0.33,
                'thermodynamic': 0.33,
                'semantic': 0.34
            },
            temporal_focus='medium',
            analysis_depth='moderate',
            priority_metrics=['entropy_stability', 'semantic_coherence', 'thermodynamic_efficiency'],
            alert_thresholds={
                'general_anomaly': 2.0,
                'system_degradation': 1.5,
                'performance_drop': 0.25
            }
        )
    
    def set_observer_context(self, observer_name: str):
        """Set the current observer context"""
        if observer_name in self.active_observers:
            self.current_observer = observer_name
            self.logger.info(f"Observer context set to: {observer_name}")
        else:
            self.logger.warning(f"Unknown observer: {observer_name}, using default")
            self.current_observer = 'default'
    
    def add_observer_profile(self, profile: ObserverProfile):
        """Add a custom observer profile"""
        self.active_observers[profile.name] = profile
        self.logger.info(f"Added observer profile: {profile.name}")
    
    def observe_system(self, 
                      geoids: List[GeoidState],
                      linguistic_geoids: List[LinguisticGeoid],
                      vault_info: Dict[str, Any]) -> SystemSnapshot:
        """
        Perform comprehensive system observation
        """
        start_time = datetime.now()
        
        # Get current observer profile
        observer_profile = self.active_observers[self.current_observer]
        
        # Calculate entropy measurements
        entropy_measurement = self.entropy_monitor.calculate_system_entropy(geoids, vault_info)
        
        # Collect semantic metrics
        semantic_measurement = self.semantic_collector.collect_semantic_metrics(
            geoids, linguistic_geoids, self.current_observer
        )
        
        # Analyze thermodynamic state
        thermodynamic_state = self.thermodynamic_analyzer.analyze_thermodynamic_state(
            geoids, vault_info, entropy_measurement.shannon_entropy
        )
        
        # Calculate system health indicators
        system_health = self._calculate_system_health(
            entropy_measurement, semantic_measurement, thermodynamic_state
        )
        
        # Create system snapshot
        snapshot = SystemSnapshot(
            timestamp=start_time,
            entropy_measurement=entropy_measurement,
            semantic_measurement=semantic_measurement,
            thermodynamic_state=thermodynamic_state,
            system_health=system_health,
            observer_context=self.current_observer,
            metadata={
                'observer_profile': observer_profile.name,
                'geoid_count': len(geoids),
                'linguistic_geoid_count': len(linguistic_geoids),
                'vault_info': vault_info,
                'observation_duration': (datetime.now() - start_time).total_seconds()
            }
        )
        
        # Store snapshot
        self.snapshots.append(snapshot)
        
        # Update performance tracking
        observation_time = (datetime.now() - start_time).total_seconds()
        self.observation_times.append(observation_time)
        self.last_observation = datetime.now()
        
        # Check for alerts
        self._check_alerts(snapshot, observer_profile)
        
        # Update health indicators
        self._update_health_indicators(snapshot)
        
        return snapshot
    
    def _calculate_system_health(self, 
                               entropy_measurement: EntropyMeasurement,
                               semantic_measurement: SemanticMeasurement,
                               thermodynamic_state: ThermodynamicState) -> Dict[str, Any]:
        """Calculate overall system health indicators"""
        
        # Entropy stability (lower variance = better stability)
        entropy_stability = 1.0
        if len(self.snapshots) > 10:
            recent_entropies = [s.entropy_measurement.shannon_entropy for s in list(self.snapshots)[-10:]]
            entropy_variance = np.var(recent_entropies)
            entropy_mean = np.mean(recent_entropies)
            if entropy_mean > 0:
                entropy_stability = 1.0 / (1.0 + entropy_variance / entropy_mean)
        
        # Semantic coherence
        semantic_coherence = semantic_measurement.context_coherence
        
        # Thermodynamic efficiency
        thermodynamic_efficiency = thermodynamic_state.efficiency
        
        # Processing speed (inverse of observation time)
        avg_observation_time = np.mean(list(self.observation_times)) if self.observation_times else 1.0
        processing_speed = 1.0 / (1.0 + avg_observation_time)
        
        # Memory utilization
        total_geoids = entropy_measurement.geoid_count
        vault_capacity = thermodynamic_state.metadata.get('vault_capacity', 10000)
        memory_utilization = total_geoids / vault_capacity if vault_capacity > 0 else 0.0
        
        # Error rate (based on anomalies)
        error_rate = self._calculate_error_rate()
        
        return {
            'entropy_stability': entropy_stability,
            'semantic_coherence': semantic_coherence,
            'thermodynamic_efficiency': thermodynamic_efficiency,
            'processing_speed': processing_speed,
            'memory_utilization': memory_utilization,
            'error_rate': error_rate,
            'overall_health': np.mean([
                entropy_stability, semantic_coherence, thermodynamic_efficiency, 
                processing_speed, 1.0 - memory_utilization, 1.0 - error_rate
            ])
        }
    
    def _calculate_error_rate(self) -> float:
        """Calculate system error rate based on recent anomalies"""
        if len(self.snapshots) < 10:
            return 0.0
        
        recent_snapshots = list(self.snapshots)[-10:]
        
        # Count various types of anomalies
        entropy_anomalies = len(self.entropy_monitor.detect_entropy_anomalies(threshold_std=2.0))
        semantic_anomalies = len(self.semantic_collector.detect_semantic_anomalies(threshold_std=2.0))
        thermodynamic_anomalies = len(self.thermodynamic_analyzer.detect_thermodynamic_anomalies(threshold_std=2.0))
        
        total_anomalies = entropy_anomalies + semantic_anomalies + thermodynamic_anomalies
        total_observations = len(recent_snapshots)
        
        return min(total_anomalies / total_observations, 1.0) if total_observations > 0 else 0.0
    
    def _check_alerts(self, snapshot: SystemSnapshot, observer_profile: ObserverProfile):
        """Check for alert conditions based on observer profile"""
        alerts = []
        
        # Entropy-based alerts
        if 'entropy_anomaly' in observer_profile.alert_thresholds:
            entropy_anomalies = self.entropy_monitor.detect_entropy_anomalies(
                threshold_std=observer_profile.alert_thresholds['entropy_anomaly']
            )
            for anomaly in entropy_anomalies:
                alerts.append({
                    'type': 'entropy_anomaly',
                    'severity': anomaly.get('type', 'medium'),
                    'message': f"Entropy anomaly detected: {anomaly}",
                    'timestamp': snapshot.timestamp.isoformat(),
                    'observer': observer_profile.name
                })
        
        # Semantic alerts
        if 'semantic_degradation' in observer_profile.alert_thresholds:
            if snapshot.semantic_measurement.semantic_efficiency < observer_profile.alert_thresholds.get('semantic_degradation', 0.5):
                alerts.append({
                    'type': 'semantic_degradation',
                    'severity': 'medium',
                    'message': f"Semantic efficiency below threshold: {snapshot.semantic_measurement.semantic_efficiency:.3f}",
                    'timestamp': snapshot.timestamp.isoformat(),
                    'observer': observer_profile.name
                })
        
        # Thermodynamic alerts
        if 'efficiency_drop' in observer_profile.alert_thresholds:
            if snapshot.thermodynamic_state.efficiency < observer_profile.alert_thresholds['efficiency_drop']:
                alerts.append({
                    'type': 'efficiency_drop',
                    'severity': 'high',
                    'message': f"Thermodynamic efficiency drop: {snapshot.thermodynamic_state.efficiency:.3f}",
                    'timestamp': snapshot.timestamp.isoformat(),
                    'observer': observer_profile.name
                })
        
        # Temperature alerts
        if 'temperature_spike' in observer_profile.alert_thresholds:
            if snapshot.thermodynamic_state.temperature > observer_profile.alert_thresholds['temperature_spike']:
                alerts.append({
                    'type': 'temperature_spike',
                    'severity': 'medium',
                    'message': f"Temperature spike detected: {snapshot.thermodynamic_state.temperature:.3f}",
                    'timestamp': snapshot.timestamp.isoformat(),
                    'observer': observer_profile.name
                })
        
        # Store alerts and trigger callbacks
        for alert in alerts:
            self.alert_history.append(alert)
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {e}")
    
    def _update_health_indicators(self, snapshot: SystemSnapshot):
        """Update running health indicators"""
        self.health_indicators.update(snapshot.system_health)
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback function for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def get_system_summary(self, window_size: int = 100) -> Dict[str, Any]:
        """Get comprehensive system summary"""
        if not self.snapshots:
            return {}
        
        recent_snapshots = list(self.snapshots)[-window_size:]
        
        # Aggregate metrics
        entropy_trends = self.entropy_monitor.get_entropy_trends(window_size)
        semantic_trends = self.semantic_collector.get_semantic_trends(window_size)
        thermodynamic_trends = self.thermodynamic_analyzer.get_thermodynamic_trends(window_size)
        
        # Calculate averages
        avg_entropy = np.mean([s.entropy_measurement.shannon_entropy for s in recent_snapshots])
        avg_semantic_efficiency = np.mean([s.semantic_measurement.semantic_efficiency for s in recent_snapshots])
        avg_thermodynamic_efficiency = np.mean([s.thermodynamic_state.efficiency for s in recent_snapshots])
        
        # Recent alerts
        recent_alerts = [alert for alert in self.alert_history if 
                        datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(hours=1)]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_observer': self.current_observer,
            'system_health': self.health_indicators,
            'averages': {
                'entropy': avg_entropy,
                'semantic_efficiency': avg_semantic_efficiency,
                'thermodynamic_efficiency': avg_thermodynamic_efficiency
            },
            'trends': {
                'entropy': entropy_trends,
                'semantic': semantic_trends,
                'thermodynamic': thermodynamic_trends
            },
            'recent_alerts': recent_alerts,
            'observation_count': len(self.snapshots),
            'avg_observation_time': np.mean(list(self.observation_times)) if self.observation_times else 0.0,
            'last_observation': self.last_observation.isoformat() if self.last_observation else None
        }
    
    def export_observations(self, format: str = 'json') -> Any:
        """Export all observations for analysis"""
        if format == 'json':
            return {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_observations': len(self.snapshots),
                    'observer_profiles': {name: {
                        'attention_weights': profile.attention_weights,
                        'temporal_focus': profile.temporal_focus,
                        'analysis_depth': profile.analysis_depth,
                        'priority_metrics': profile.priority_metrics
                    } for name, profile in self.active_observers.items()}
                },
                'observations': [
                    {
                        'timestamp': s.timestamp.isoformat(),
                        'observer_context': s.observer_context,
                        'entropy': {
                            'shannon_entropy': s.entropy_measurement.shannon_entropy,
                            'thermodynamic_entropy': s.entropy_measurement.thermodynamic_entropy,
                            'relative_entropy': s.entropy_measurement.relative_entropy,
                            'system_complexity': s.entropy_measurement.system_complexity
                        },
                        'semantic': {
                            'semantic_entropy': s.semantic_measurement.semantic_entropy,
                            'meaning_density': s.semantic_measurement.meaning_density,
                            'context_coherence': s.semantic_measurement.context_coherence,
                            'semantic_efficiency': s.semantic_measurement.semantic_efficiency,
                            'information_utility': s.semantic_measurement.information_utility
                        },
                        'thermodynamic': {
                            'total_energy': s.thermodynamic_state.total_energy,
                            'temperature': s.thermodynamic_state.temperature,
                            'pressure': s.thermodynamic_state.pressure,
                            'efficiency': s.thermodynamic_state.efficiency,
                            'entropy_production': s.thermodynamic_state.entropy_production
                        },
                        'system_health': s.system_health,
                        'metadata': s.metadata
                    }
                    for s in self.snapshots
                ],
                'alerts': list(self.alert_history)
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def generate_report(self, report_type: str = 'comprehensive') -> str:
        """Generate human-readable system report"""
        summary = self.get_system_summary()
        
        if report_type == 'comprehensive':
            return self._generate_comprehensive_report(summary)
        elif report_type == 'executive':
            return self._generate_executive_report(summary)
        elif report_type == 'technical':
            return self._generate_technical_report(summary)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    def _generate_comprehensive_report(self, summary: Dict[str, Any]) -> str:
        """Generate comprehensive system report"""
        report = f"""
KIMERA SWM COMPREHENSIVE SYSTEM REPORT
=====================================
Generated: {summary['timestamp']}
Observer Context: {summary['current_observer']}
Total Observations: {summary['observation_count']}

SYSTEM HEALTH OVERVIEW
---------------------
Overall Health: {summary['system_health']['overall_health']:.3f}
Entropy Stability: {summary['system_health']['entropy_stability']:.3f}
Semantic Coherence: {summary['system_health']['semantic_coherence']:.3f}
Thermodynamic Efficiency: {summary['system_health']['thermodynamic_efficiency']:.3f}
Processing Speed: {summary['system_health']['processing_speed']:.3f}
Memory Utilization: {summary['system_health']['memory_utilization']:.3f}
Error Rate: {summary['system_health']['error_rate']:.3f}

AVERAGE METRICS
--------------
Shannon Entropy: {summary['averages']['entropy']:.3f}
Semantic Efficiency: {summary['averages']['semantic_efficiency']:.3f}
Thermodynamic Efficiency: {summary['averages']['thermodynamic_efficiency']:.3f}

RECENT ALERTS
------------
"""
        
        if summary['recent_alerts']:
            for alert in summary['recent_alerts'][-5:]:  # Last 5 alerts
                report += f"- {alert['type']}: {alert['message']} ({alert['timestamp']})\n"
        else:
            report += "No recent alerts\n"
        
        report += f"""
PERFORMANCE METRICS
------------------
Average Observation Time: {summary['avg_observation_time']:.3f}s
Last Observation: {summary['last_observation']}

OBSERVER PROFILES ACTIVE
-----------------------
"""
        
        for name, profile in self.active_observers.items():
            active_indicator = " (ACTIVE)" if name == self.current_observer else ""
            report += f"- {name}{active_indicator}: {profile.temporal_focus} focus, {profile.analysis_depth} analysis\n"
        
        return report
    
    def _generate_executive_report(self, summary: Dict[str, Any]) -> str:
        """Generate executive summary report"""
        health_status = "HEALTHY" if summary['system_health']['overall_health'] > 0.8 else \
                       "DEGRADED" if summary['system_health']['overall_health'] > 0.6 else "CRITICAL"
        
        return f"""
KIMERA SWM EXECUTIVE SUMMARY
===========================
Status: {health_status} ({summary['system_health']['overall_health']:.1%})
Observations: {summary['observation_count']}
Active Alerts: {len(summary['recent_alerts'])}

Key Metrics:
- System Efficiency: {summary['averages']['thermodynamic_efficiency']:.1%}
- Semantic Performance: {summary['averages']['semantic_efficiency']:.1%}
- Memory Usage: {summary['system_health']['memory_utilization']:.1%}
- Error Rate: {summary['system_health']['error_rate']:.1%}

Recommendations:
{self._generate_recommendations(summary)}
"""
    
    def _generate_technical_report(self, summary: Dict[str, Any]) -> str:
        """Generate technical analysis report"""
        return f"""
KIMERA SWM TECHNICAL ANALYSIS
============================
Observer: {summary['current_observer']}
Analysis Period: {summary['observation_count']} observations

ENTROPY ANALYSIS
---------------
Shannon Entropy: {summary['averages']['entropy']:.6f}
Entropy Stability: {summary['system_health']['entropy_stability']:.6f}

SEMANTIC ANALYSIS
----------------
Semantic Efficiency: {summary['averages']['semantic_efficiency']:.6f}
Context Coherence: {summary['system_health']['semantic_coherence']:.6f}

THERMODYNAMIC ANALYSIS
---------------------
Efficiency: {summary['averages']['thermodynamic_efficiency']:.6f}
Processing Speed: {summary['system_health']['processing_speed']:.6f}

SYSTEM DIAGNOSTICS
-----------------
Memory Utilization: {summary['system_health']['memory_utilization']:.6f}
Error Rate: {summary['system_health']['error_rate']:.6f}
Avg Observation Time: {summary['avg_observation_time']:.6f}s

ANOMALY DETECTION
----------------
Recent Alerts: {len(summary['recent_alerts'])}
Alert Types: {set(alert['type'] for alert in summary['recent_alerts'])}
"""
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> str:
        """Generate system recommendations based on current state"""
        recommendations = []
        
        if summary['system_health']['overall_health'] < 0.7:
            recommendations.append("- System health below optimal, investigate recent changes")
        
        if summary['system_health']['memory_utilization'] > 0.8:
            recommendations.append("- High memory utilization, consider vault rebalancing")
        
        if summary['system_health']['error_rate'] > 0.1:
            recommendations.append("- Elevated error rate, review system logs")
        
        if summary['averages']['thermodynamic_efficiency'] < 0.5:
            recommendations.append("- Low thermodynamic efficiency, optimize processing algorithms")
        
        if len(summary['recent_alerts']) > 10:
            recommendations.append("- High alert frequency, review alert thresholds")
        
        if not recommendations:
            recommendations.append("- System operating within normal parameters")
        
        return "\n".join(recommendations)
