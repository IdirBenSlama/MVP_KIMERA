"""
Advanced Statistical Monitor for Kimera SWM

This module extends the existing monitoring capabilities with advanced statistical
analysis powered by statsmodels. It provides real-time statistical monitoring,
anomaly detection, and predictive analytics for the semantic system.

Key Features:
1. Real-time statistical process control
2. Advanced anomaly detection using statistical models
3. Predictive monitoring with forecasting
4. Statistical quality control for semantic processes
5. Automated model selection and validation

Author: Kimera SWM Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import threading
import time
from collections import deque
import warnings

# Core Kimera imports
from .entropy_monitor import EntropyMonitor
from .system_observer import SystemObserver
from ..core.statistical_modeling import (
    StatisticalModelResult, 
    statistical_engine,
    STATSMODELS_AVAILABLE
)
from ..core.native_math import NativeStats

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning, module='statsmodels')

try:
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.stats.outliers_influence import OLSInfluence
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class StatisticalAlert:
    """Statistical alert for anomalous conditions"""
    alert_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    metric_name: str
    current_value: float
    expected_range: Tuple[float, float]
    confidence_level: float
    timestamp: datetime = field(default_factory=datetime.now)
    statistical_test: Optional[str] = None
    p_value: Optional[float] = None

@dataclass
class StatisticalControlLimits:
    """Statistical process control limits"""
    center_line: float
    upper_control_limit: float
    lower_control_limit: float
    upper_warning_limit: float
    lower_warning_limit: float
    method: str
    confidence_level: float = 0.95

class StatisticalProcessController:
    """
    Statistical Process Control (SPC) for semantic system monitoring.
    
    Implements control charts and statistical monitoring for detecting
    when the semantic system is operating outside normal parameters.
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_buffer = deque(maxlen=window_size)
        self.control_limits = {}
        self.alerts = deque(maxlen=1000)
        
    def add_measurement(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Add a new measurement for statistical monitoring"""
        if timestamp is None:
            timestamp = datetime.now()
            
        measurement = {
            'metric': metric_name,
            'value': value,
            'timestamp': timestamp
        }
        
        self.data_buffer.append(measurement)
        
        # Update control limits if we have enough data
        if len(self.data_buffer) >= 20:
            self._update_control_limits(metric_name)
            self._check_control_limits(metric_name, value, timestamp)
    
    def _update_control_limits(self, metric_name: str):
        """Update statistical control limits for a metric"""
        # Get recent data for this metric
        metric_data = [m['value'] for m in self.data_buffer if m['metric'] == metric_name]
        
        if len(metric_data) < 10:
            return
        
        if STATSMODELS_AVAILABLE:
            self._update_advanced_control_limits(metric_name, metric_data)
        else:
            self._update_basic_control_limits(metric_name, metric_data)
    
    def _update_advanced_control_limits(self, metric_name: str, data: List[float]):
        """Update control limits using advanced statistical methods"""
        try:
            # Convert to pandas series
            ts = pd.Series(data)
            
            # Test for stationarity
            adf_result = adfuller(ts)
            is_stationary = adf_result[1] < 0.05
            
            if is_stationary:
                # Use direct statistics for stationary data
                mean_val = ts.mean()
                std_val = ts.std()
            else:
                # Use differenced data for non-stationary series
                diff_ts = ts.diff().dropna()
                mean_val = ts.mean()  # Use original mean
                std_val = diff_ts.std()  # Use differenced std
            
            # Calculate control limits (3-sigma rule)
            ucl = mean_val + 3 * std_val
            lcl = mean_val - 3 * std_val
            uwl = mean_val + 2 * std_val  # Warning limits
            lwl = mean_val - 2 * std_val
            
            self.control_limits[metric_name] = StatisticalControlLimits(
                center_line=float(mean_val),
                upper_control_limit=float(ucl),
                lower_control_limit=float(lcl),
                upper_warning_limit=float(uwl),
                lower_warning_limit=float(lwl),
                method='advanced_spc',
                confidence_level=0.997  # 3-sigma
            )
            
        except Exception as e:
            logger.warning(f"Advanced control limits failed for {metric_name}: {e}")
            self._update_basic_control_limits(metric_name, data)
    
    def _update_basic_control_limits(self, metric_name: str, data: List[float]):
        """Update control limits using basic statistical methods"""
        mean_val = NativeStats.mean(data)
        std_val = NativeStats.std(data)
        
        # 3-sigma control limits
        ucl = mean_val + 3 * std_val
        lcl = mean_val - 3 * std_val
        uwl = mean_val + 2 * std_val
        lwl = mean_val - 2 * std_val
        
        self.control_limits[metric_name] = StatisticalControlLimits(
            center_line=mean_val,
            upper_control_limit=ucl,
            lower_control_limit=lcl,
            upper_warning_limit=uwl,
            lower_warning_limit=lwl,
            method='basic_spc',
            confidence_level=0.997
        )
    
    def _check_control_limits(self, metric_name: str, value: float, timestamp: datetime):
        """Check if a value violates control limits"""
        if metric_name not in self.control_limits:
            return
        
        limits = self.control_limits[metric_name]
        
        # Check for violations
        if value > limits.upper_control_limit:
            alert = StatisticalAlert(
                alert_type='control_limit_violation',
                severity='critical',
                message=f'{metric_name} exceeded upper control limit',
                metric_name=metric_name,
                current_value=value,
                expected_range=(limits.lower_control_limit, limits.upper_control_limit),
                confidence_level=limits.confidence_level,
                timestamp=timestamp,
                statistical_test='control_chart'
            )
            self.alerts.append(alert)
            
        elif value < limits.lower_control_limit:
            alert = StatisticalAlert(
                alert_type='control_limit_violation',
                severity='critical',
                message=f'{metric_name} fell below lower control limit',
                metric_name=metric_name,
                current_value=value,
                expected_range=(limits.lower_control_limit, limits.upper_control_limit),
                confidence_level=limits.confidence_level,
                timestamp=timestamp,
                statistical_test='control_chart'
            )
            self.alerts.append(alert)
            
        elif value > limits.upper_warning_limit:
            alert = StatisticalAlert(
                alert_type='warning_limit_violation',
                severity='medium',
                message=f'{metric_name} exceeded upper warning limit',
                metric_name=metric_name,
                current_value=value,
                expected_range=(limits.lower_warning_limit, limits.upper_warning_limit),
                confidence_level=0.95,
                timestamp=timestamp,
                statistical_test='control_chart'
            )
            self.alerts.append(alert)
            
        elif value < limits.lower_warning_limit:
            alert = StatisticalAlert(
                alert_type='warning_limit_violation',
                severity='medium',
                message=f'{metric_name} fell below lower warning limit',
                metric_name=metric_name,
                current_value=value,
                expected_range=(limits.lower_warning_limit, limits.upper_warning_limit),
                confidence_level=0.95,
                timestamp=timestamp,
                statistical_test='control_chart'
            )
            self.alerts.append(alert)
    
    def get_recent_alerts(self, hours: int = 24) -> List[StatisticalAlert]:
        """Get alerts from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff_time]

class PredictiveMonitor:
    """
    Predictive monitoring using statistical forecasting models.
    
    Provides early warning of potential system issues by forecasting
    key metrics and detecting when predictions indicate problems.
    """
    
    def __init__(self, forecast_horizon: int = 10):
        self.forecast_horizon = forecast_horizon
        self.models = {}
        self.forecasts = {}
        
    def update_forecast(self, metric_name: str, historical_data: List[float]) -> Optional[List[float]]:
        """Update forecast for a specific metric"""
        if not STATSMODELS_AVAILABLE or len(historical_data) < 10:
            return self._simple_forecast(historical_data)
        
        try:
            # Fit ARIMA model
            ts = pd.Series(historical_data)
            model = ARIMA(ts, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(steps=self.forecast_horizon)
            confidence_intervals = fitted_model.get_forecast(steps=self.forecast_horizon).conf_int()
            
            self.models[metric_name] = fitted_model
            self.forecasts[metric_name] = {
                'forecast': forecast.tolist(),
                'confidence_intervals': confidence_intervals.values.tolist(),
                'timestamp': datetime.now()
            }
            
            return forecast.tolist()
            
        except Exception as e:
            logger.warning(f"ARIMA forecast failed for {metric_name}: {e}")
            return self._simple_forecast(historical_data)
    
    def _simple_forecast(self, historical_data: List[float]) -> List[float]:
        """Simple trend-based forecast when advanced methods fail"""
        if len(historical_data) < 2:
            return [historical_data[-1]] * self.forecast_horizon if historical_data else [0.0] * self.forecast_horizon
        
        # Simple linear trend
        recent_data = historical_data[-min(10, len(historical_data)):]
        trend = (recent_data[-1] - recent_data[0]) / len(recent_data)
        last_value = historical_data[-1]
        
        forecast = []
        for i in range(1, self.forecast_horizon + 1):
            forecast.append(last_value + trend * i)
        
        return forecast
    
    def detect_forecast_anomalies(self, metric_name: str, threshold: float = 2.0) -> List[StatisticalAlert]:
        """Detect potential future anomalies based on forecasts"""
        alerts = []
        
        if metric_name not in self.forecasts:
            return alerts
        
        forecast_data = self.forecasts[metric_name]
        forecast_values = forecast_data['forecast']
        
        # Calculate forecast statistics
        forecast_mean = NativeStats.mean(forecast_values)
        forecast_std = NativeStats.std(forecast_values)
        
        # Check for extreme forecast values
        for i, value in enumerate(forecast_values):
            if abs(value - forecast_mean) > threshold * forecast_std:
                alert = StatisticalAlert(
                    alert_type='forecast_anomaly',
                    severity='medium',
                    message=f'Forecast predicts anomalous {metric_name} in {i+1} steps',
                    metric_name=metric_name,
                    current_value=value,
                    expected_range=(forecast_mean - threshold * forecast_std, 
                                  forecast_mean + threshold * forecast_std),
                    confidence_level=0.95,
                    statistical_test='forecast_analysis'
                )
                alerts.append(alert)
        
        return alerts

class AdvancedStatisticalMonitor:
    """
    Main advanced statistical monitoring system that integrates all
    statistical monitoring capabilities for Kimera SWM.
    """
    
    def __init__(self, 
                 entropy_monitor: Optional[EntropyMonitor] = None,
                 system_observer: Optional[SystemObserver] = None):
        self.entropy_monitor = entropy_monitor
        self.system_observer = system_observer
        
        # Statistical components
        self.process_controller = StatisticalProcessController()
        self.predictive_monitor = PredictiveMonitor()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.monitoring_interval = 30  # seconds
        
        # Data storage
        self.metric_history = {}
        self.analysis_results = {}
        
    def start_monitoring(self):
        """Start continuous statistical monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Advanced statistical monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous statistical monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Advanced statistical monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_and_analyze_metrics()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_and_analyze_metrics(self):
        """Collect current metrics and perform statistical analysis"""
        current_time = datetime.now()
        
        # Collect entropy metrics
        if self.entropy_monitor:
            try:
                entropy_measurement = self.entropy_monitor.calculate_system_entropy()
                if hasattr(entropy_measurement, 'shannon_entropy'):
                    self._record_metric('shannon_entropy', 
                                      entropy_measurement.shannon_entropy, 
                                      current_time)
                
                if hasattr(entropy_measurement, 'thermodynamic_entropy'):
                    self._record_metric('thermodynamic_entropy', 
                                      entropy_measurement.thermodynamic_entropy, 
                                      current_time)
            except Exception as e:
                logger.warning(f"Failed to collect entropy metrics: {e}")
        
        # Collect system observer metrics
        if self.system_observer:
            try:
                system_health = self.system_observer.get_system_health_score()
                self._record_metric('system_health', system_health, current_time)
                
                stability_score = self.system_observer.calculate_stability_score()
                self._record_metric('stability_score', stability_score, current_time)
            except Exception as e:
                logger.warning(f"Failed to collect system observer metrics: {e}")
        
        # Perform statistical analysis
        self._perform_statistical_analysis()
    
    def _record_metric(self, metric_name: str, value: float, timestamp: datetime):
        """Record a metric value and update statistical monitoring"""
        # Store in history
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = deque(maxlen=1000)
        
        self.metric_history[metric_name].append({
            'value': value,
            'timestamp': timestamp
        })
        
        # Update statistical process control
        self.process_controller.add_measurement(metric_name, value, timestamp)
        
        # Update forecasts periodically
        if len(self.metric_history[metric_name]) % 10 == 0:  # Every 10 measurements
            historical_values = [m['value'] for m in self.metric_history[metric_name]]
            self.predictive_monitor.update_forecast(metric_name, historical_values)
    
    def _perform_statistical_analysis(self):
        """Perform comprehensive statistical analysis of collected data"""
        try:
            # Prepare data for comprehensive analysis
            system_data = {}
            
            # Extract entropy history
            if 'shannon_entropy' in self.metric_history:
                entropy_values = [m['value'] for m in self.metric_history['shannon_entropy']]
                entropy_timestamps = [m['timestamp'] for m in self.metric_history['shannon_entropy']]
                system_data['entropy_history'] = entropy_values
                system_data['timestamps'] = entropy_timestamps
            
            # Extract other metrics for analysis
            if 'system_health' in self.metric_history and 'stability_score' in self.metric_history:
                system_data['semantic_features'] = {
                    'system_health': [m['value'] for m in self.metric_history['system_health']],
                    'stability_score': [m['value'] for m in self.metric_history['stability_score']]
                }
            
            # Perform comprehensive analysis
            if system_data:
                self.analysis_results = statistical_engine.comprehensive_analysis(system_data)
                
        except Exception as e:
            logger.error(f"Error in statistical analysis: {e}")
    
    def get_statistical_summary(self) -> Dict[str, Any]:
        """Get comprehensive statistical summary of system state"""
        summary = {
            'monitoring_status': self.is_monitoring,
            'metrics_tracked': list(self.metric_history.keys()),
            'recent_alerts': len(self.process_controller.get_recent_alerts()),
            'control_limits': {name: {
                'center_line': limits.center_line,
                'ucl': limits.upper_control_limit,
                'lcl': limits.lower_control_limit,
                'method': limits.method
            } for name, limits in self.process_controller.control_limits.items()},
            'forecasts_available': list(self.predictive_monitor.forecasts.keys()),
            'analysis_results': {}
        }
        
        # Add analysis results summary
        for analysis_type, result in self.analysis_results.items():
            if isinstance(result, StatisticalModelResult):
                summary['analysis_results'][analysis_type] = {
                    'model_type': result.model_type,
                    'key_statistics': result.statistics,
                    'timestamp': result.timestamp.isoformat() if result.timestamp else None
                }
        
        return summary
    
    def get_alerts(self, severity_filter: Optional[str] = None, hours: int = 24) -> List[StatisticalAlert]:
        """Get recent alerts with optional severity filtering"""
        alerts = self.process_controller.get_recent_alerts(hours)
        
        # Add forecast alerts
        for metric_name in self.predictive_monitor.forecasts.keys():
            forecast_alerts = self.predictive_monitor.detect_forecast_anomalies(metric_name)
            alerts.extend(forecast_alerts)
        
        # Filter by severity if specified
        if severity_filter:
            alerts = [alert for alert in alerts if alert.severity == severity_filter]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_forecast(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Get forecast for a specific metric"""
        return self.predictive_monitor.forecasts.get(metric_name)

# Global instance for easy access
advanced_monitor = AdvancedStatisticalMonitor()

def get_advanced_monitor() -> AdvancedStatisticalMonitor:
    """Get the global advanced statistical monitor instance"""
    return advanced_monitor

def initialize_advanced_monitoring(entropy_monitor: Optional[EntropyMonitor] = None,
                                 system_observer: Optional[SystemObserver] = None) -> AdvancedStatisticalMonitor:
    """Initialize advanced monitoring with existing monitors"""
    global advanced_monitor
    advanced_monitor = AdvancedStatisticalMonitor(entropy_monitor, system_observer)
    return advanced_monitor