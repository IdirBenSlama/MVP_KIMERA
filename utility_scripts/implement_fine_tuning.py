#!/usr/bin/env python3
"""
KIMERA SWM Fine-Tuning Implementation Script

This script implements the highest priority fine-tuning opportunities
identified in the comprehensive analysis.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
from dataclasses import dataclass, asdict
import sqlite3

# Configuration for fine-tuning parameters
@dataclass
class FineTuningConfig:
    """Centralized configuration for all tunable parameters"""
    
    # Contradiction Engine Parameters
    contradiction_base_threshold: float = 0.3
    contradiction_adaptive_range: Tuple[float, float] = (0.1, 0.6)
    contradiction_adjustment_sensitivity: float = 0.05
    
    # Proactive Detection Parameters
    proactive_base_batch_size: int = 50
    proactive_max_batch_size: int = 200
    proactive_scan_interval_base: int = 6  # hours
    proactive_similarity_threshold_base: float = 0.7
    
    # Vault Management Parameters
    vault_balance_threshold_base: float = 1.5
    vault_rebalance_sensitivity: float = 0.1
    
    # Background Jobs Parameters
    decay_rate_base: float = 0.1
    crystallization_threshold_base: float = 20.0
    fusion_similarity_threshold: float = 0.9
    
    # SPDE Parameters
    spde_diffusion_rate_base: float = 0.5
    spde_decay_factor_base: float = 1.0
    
    # Activation Manager Parameters
    activation_entropy_boost_threshold: float = 3.5
    activation_entropy_damping_threshold: float = 1.0
    activation_damping_factor: float = 0.7
    activation_floor_threshold: float = 1e-9
    
    # Performance Tracking
    performance_window_size: int = 100
    optimization_interval_minutes: int = 30


class PerformanceTracker:
    """Tracks parameter performance for optimization"""
    
    def __init__(self, config: FineTuningConfig):
        self.config = config
        self.metrics = {}
        self.performance_history = []
        
    def track_parameter_performance(self, parameter_name: str, value: float, 
                                  outcome_metrics: Dict[str, float]):
        """Track performance of a parameter value"""
        timestamp = datetime.utcnow()
        
        if parameter_name not in self.metrics:
            self.metrics[parameter_name] = []
            
        self.metrics[parameter_name].append({
            'value': value,
            'outcome_metrics': outcome_metrics,
            'timestamp': timestamp.isoformat(),
            'composite_score': self._calculate_composite_score(outcome_metrics)
        })
        
        # Keep only recent history
        cutoff = timestamp - timedelta(days=7)
        self.metrics[parameter_name] = [
            m for m in self.metrics[parameter_name] 
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]
    
    def _calculate_composite_score(self, metrics: Dict[str, float]) -> float:
        """Calculate composite performance score"""
        weights = {
            'scar_utilization_rate': 0.3,
            'contradiction_detection_rate': 0.25,
            'processing_speed': 0.2,
            'system_stability': 0.15,
            'resource_efficiency': 0.1
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric, value in metrics.items():
            if metric in weights:
                score += weights[metric] * value
                total_weight += weights[metric]
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def get_optimal_value(self, parameter_name: str) -> float:
        """Get historically optimal value for a parameter"""
        if parameter_name not in self.metrics or not self.metrics[parameter_name]:
            return None
            
        # Find value with highest composite score
        best_entry = max(self.metrics[parameter_name], 
                        key=lambda x: x['composite_score'])
        return best_entry['value']
    
    def get_performance_trend(self, parameter_name: str) -> str:
        """Get performance trend for a parameter"""
        if parameter_name not in self.metrics or len(self.metrics[parameter_name]) < 5:
            return "insufficient_data"
            
        recent_scores = [m['composite_score'] for m in self.metrics[parameter_name][-5:]]
        older_scores = [m['composite_score'] for m in self.metrics[parameter_name][-10:-5]]
        
        if not older_scores:
            return "insufficient_data"
            
        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)
        
        if recent_avg > older_avg * 1.05:
            return "improving"
        elif recent_avg < older_avg * 0.95:
            return "degrading"
        else:
            return "stable"


class AdaptiveParameterManager:
    """Manages adaptive parameter adjustment"""
    
    def __init__(self, config: FineTuningConfig, tracker: PerformanceTracker):
        self.config = config
        self.tracker = tracker
        self.current_parameters = asdict(config)
        self.adjustment_history = []
        
    def adjust_contradiction_threshold(self, system_metrics: Dict[str, float]) -> float:
        """Dynamically adjust contradiction detection threshold"""
        base_threshold = self.config.contradiction_base_threshold
        min_threshold, max_threshold = self.config.contradiction_adaptive_range
        
        # Factors influencing threshold adjustment
        scar_utilization = system_metrics.get('scar_utilization_rate', 0.036)
        contradiction_rate = system_metrics.get('contradictions_per_hour', 10.0)
        system_load = system_metrics.get('system_load', 0.5)
        
        # Adjustment logic
        adjustment = 0.0
        
        # If utilization is low, lower threshold to detect more contradictions
        if scar_utilization < 0.05:
            adjustment -= 0.05
        elif scar_utilization > 0.15:
            adjustment += 0.02
            
        # If contradiction rate is too high, raise threshold
        if contradiction_rate > 50:
            adjustment += 0.03
        elif contradiction_rate < 5:
            adjustment -= 0.02
            
        # Adjust for system load
        if system_load > 0.8:
            adjustment += 0.01  # Reduce sensitivity under high load
            
        new_threshold = np.clip(
            base_threshold + adjustment,
            min_threshold,
            max_threshold
        )
        
        self.current_parameters['contradiction_threshold'] = new_threshold
        return new_threshold
    
    def adjust_batch_size(self, system_metrics: Dict[str, float]) -> int:
        """Dynamically adjust proactive detection batch size"""
        base_size = self.config.proactive_base_batch_size
        max_size = self.config.proactive_max_batch_size
        
        geoid_count = system_metrics.get('total_geoids', 168)
        system_load = system_metrics.get('system_load', 0.5)
        memory_usage = system_metrics.get('memory_usage', 0.5)
        
        # Calculate optimal batch size
        optimal_size = min(max_size, max(20, geoid_count // 10))
        
        # Adjust for system conditions
        if system_load > 0.8:
            optimal_size = int(optimal_size * 0.7)  # Reduce under high load
        elif system_load < 0.3:
            optimal_size = int(optimal_size * 1.3)  # Increase under low load
            
        if memory_usage > 0.8:
            optimal_size = int(optimal_size * 0.6)  # Reduce under high memory usage
            
        optimal_size = max(10, min(max_size, optimal_size))
        self.current_parameters['batch_size'] = optimal_size
        return optimal_size
    
    def adjust_scan_interval(self, system_metrics: Dict[str, float]) -> int:
        """Dynamically adjust proactive scan interval"""
        base_interval = self.config.proactive_scan_interval_base
        
        activity_rate = system_metrics.get('geoid_creation_rate', 1.0)  # per hour
        contradiction_rate = system_metrics.get('contradictions_per_hour', 10.0)
        
        # More activity = more frequent scans
        if activity_rate > 10:
            interval = max(1, base_interval // 2)  # Scan every 3 hours
        elif activity_rate > 5:
            interval = max(2, int(base_interval * 0.75))  # Scan every 4.5 hours
        elif activity_rate < 1:
            interval = min(24, base_interval * 2)  # Scan every 12 hours
        else:
            interval = base_interval
            
        self.current_parameters['scan_interval'] = interval
        return interval
    
    def adjust_vault_threshold(self, system_metrics: Dict[str, float]) -> float:
        """Dynamically adjust vault balance threshold"""
        base_threshold = self.config.vault_balance_threshold_base
        
        vault_activity = system_metrics.get('scars_per_hour', 5.0)
        system_stability = system_metrics.get('system_stability', 0.8)
        
        # Higher activity = tighter threshold for better balance
        if vault_activity > 20:
            threshold = base_threshold * 0.8  # Tighter balance
        elif vault_activity > 10:
            threshold = base_threshold * 0.9
        elif vault_activity < 2:
            threshold = base_threshold * 1.3  # Looser balance
        else:
            threshold = base_threshold
            
        # Adjust for system stability
        if system_stability < 0.7:
            threshold *= 1.2  # Looser threshold for unstable system
            
        self.current_parameters['vault_threshold'] = threshold
        return threshold


class SystemMetricsCollector:
    """Collects system metrics for parameter optimization"""
    
    def __init__(self, db_path: str = "kimera_swm.db"):
        self.db_path = db_path
        
    def collect_current_metrics(self) -> Dict[str, float]:
        """Collect current system performance metrics"""
        metrics = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Basic counts
                cursor.execute("SELECT COUNT(*) FROM geoids")
                total_geoids = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM scars")
                total_scars = cursor.fetchone()[0]
                
                # SCAR utilization
                cursor.execute("SELECT geoids FROM scars")
                scar_geoids = cursor.fetchall()
                referenced_geoids = set()
                for (geoids_json,) in scar_geoids:
                    try:
                        import json
                        geoid_list = json.loads(geoids_json)
                        referenced_geoids.update(geoid_list)
                    except:
                        continue
                
                utilization_rate = len(referenced_geoids) / max(total_geoids, 1)
                
                # Recent activity (last 24 hours)
                cursor.execute("""
                    SELECT COUNT(*) FROM scars 
                    WHERE datetime(timestamp) > datetime('now', '-24 hours')
                """)
                recent_scars = cursor.fetchone()[0]
                
                # Calculate rates
                scars_per_hour = recent_scars / 24.0
                
                metrics.update({
                    'total_geoids': total_geoids,
                    'total_scars': total_scars,
                    'scar_utilization_rate': utilization_rate,
                    'scars_per_hour': scars_per_hour,
                    'contradictions_per_hour': scars_per_hour * 1.2,  # Estimate
                    'geoid_creation_rate': 1.0,  # Default estimate
                    'system_load': 0.5,  # Default estimate
                    'memory_usage': 0.4,  # Default estimate
                    'system_stability': 0.8,  # Default estimate
                    'processing_speed': 1.0,  # Default estimate
                    'resource_efficiency': 0.7  # Default estimate
                })
                
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            # Return default metrics
            metrics = {
                'total_geoids': 168,
                'total_scars': 7,
                'scar_utilization_rate': 0.036,
                'scars_per_hour': 1.0,
                'contradictions_per_hour': 1.2,
                'geoid_creation_rate': 1.0,
                'system_load': 0.5,
                'memory_usage': 0.4,
                'system_stability': 0.8,
                'processing_speed': 1.0,
                'resource_efficiency': 0.7
            }
            
        return metrics


class FineTuningOrchestrator:
    """Main orchestrator for fine-tuning operations"""
    
    def __init__(self, config_path: str = "config/fine_tuning_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_or_create_config()
        self.tracker = PerformanceTracker(self.config)
        self.parameter_manager = AdaptiveParameterManager(self.config, self.tracker)
        self.metrics_collector = SystemMetricsCollector()
        self.last_optimization = None
        
    def _load_or_create_config(self) -> FineTuningConfig:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                return FineTuningConfig(**config_data)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
                
        return FineTuningConfig()
    
    def save_config(self):
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(asdict(self.config), f, indent=2)
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """Run a complete optimization cycle"""
        print("🔧 Starting fine-tuning optimization cycle...")
        
        # Collect current metrics
        current_metrics = self.metrics_collector.collect_current_metrics()
        print(f"📊 Current metrics: {current_metrics}")
        
        # Track current parameter performance
        self._track_current_performance(current_metrics)
        
        # Adjust parameters based on metrics
        adjustments = self._adjust_parameters(current_metrics)
        
        # Save updated configuration
        self.save_config()
        
        # Record optimization
        optimization_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': current_metrics,
            'adjustments': adjustments,
            'new_parameters': self.parameter_manager.current_parameters
        }
        
        self.last_optimization = optimization_record
        
        print(f"✅ Optimization cycle complete. Adjustments: {adjustments}")
        return optimization_record
    
    def _track_current_performance(self, metrics: Dict[str, float]):
        """Track performance of current parameters"""
        current_params = self.parameter_manager.current_parameters
        
        # Track key parameters
        key_params = [
            'contradiction_threshold',
            'batch_size',
            'scan_interval',
            'vault_threshold'
        ]
        
        for param in key_params:
            if param in current_params:
                self.tracker.track_parameter_performance(
                    param, 
                    current_params[param], 
                    metrics
                )
    
    def _adjust_parameters(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Adjust parameters based on current metrics"""
        adjustments = {}
        
        # Adjust contradiction threshold
        old_threshold = self.config.contradiction_base_threshold
        new_threshold = self.parameter_manager.adjust_contradiction_threshold(metrics)
        if abs(new_threshold - old_threshold) > 0.01:
            adjustments['contradiction_threshold'] = {
                'old': old_threshold,
                'new': new_threshold,
                'change': new_threshold - old_threshold
            }
            self.config.contradiction_base_threshold = new_threshold
        
        # Adjust batch size
        old_batch = self.config.proactive_base_batch_size
        new_batch = self.parameter_manager.adjust_batch_size(metrics)
        if new_batch != old_batch:
            adjustments['batch_size'] = {
                'old': old_batch,
                'new': new_batch,
                'change': new_batch - old_batch
            }
            self.config.proactive_base_batch_size = new_batch
        
        # Adjust scan interval
        old_interval = self.config.proactive_scan_interval_base
        new_interval = self.parameter_manager.adjust_scan_interval(metrics)
        if new_interval != old_interval:
            adjustments['scan_interval'] = {
                'old': old_interval,
                'new': new_interval,
                'change': new_interval - old_interval
            }
            self.config.proactive_scan_interval_base = new_interval
        
        # Adjust vault threshold
        old_vault_threshold = self.config.vault_balance_threshold_base
        new_vault_threshold = self.parameter_manager.adjust_vault_threshold(metrics)
        if abs(new_vault_threshold - old_vault_threshold) > 0.05:
            adjustments['vault_threshold'] = {
                'old': old_vault_threshold,
                'new': new_vault_threshold,
                'change': new_vault_threshold - old_vault_threshold
            }
            self.config.vault_balance_threshold_base = new_vault_threshold
        
        return adjustments
    
    def get_optimization_report(self) -> str:
        """Generate optimization report"""
        if not self.last_optimization:
            return "No optimization cycles completed yet."
        
        opt = self.last_optimization
        report = f"""
🔧 KIMERA SWM Fine-Tuning Report
Generated: {datetime.utcnow().isoformat()}

📊 Current System Metrics:
  • Total Geoids: {opt['metrics']['total_geoids']}
  • Total SCARs: {opt['metrics']['total_scars']}
  • SCAR Utilization: {opt['metrics']['scar_utilization_rate']:.3f} ({opt['metrics']['scar_utilization_rate']*100:.1f}%)
  • SCARs per Hour: {opt['metrics']['scars_per_hour']:.1f}
  • System Load: {opt['metrics']['system_load']:.3f}

🎯 Parameter Adjustments Made:
"""
        
        if opt['adjustments']:
            for param, change in opt['adjustments'].items():
                direction = "↗️" if change['change'] > 0 else "↘️"
                report += f"  • {param}: {change['old']:.3f} → {change['new']:.3f} {direction}\n"
        else:
            report += "  • No adjustments needed - parameters are optimal\n"
        
        report += f"""
⚙️ Current Parameter Values:
  • Contradiction Threshold: {self.config.contradiction_base_threshold:.3f}
  • Batch Size: {self.config.proactive_base_batch_size}
  • Scan Interval: {self.config.proactive_scan_interval_base} hours
  • Vault Threshold: {self.config.vault_balance_threshold_base:.3f}

📈 Performance Trends:
"""
        
        for param in ['contradiction_threshold', 'batch_size', 'scan_interval', 'vault_threshold']:
            trend = self.tracker.get_performance_trend(param)
            trend_icon = {"improving": "📈", "stable": "➡️", "degrading": "📉", "insufficient_data": "❓"}
            report += f"  • {param}: {trend} {trend_icon.get(trend, '❓')}\n"
        
        return report


def main():
    """Main function to run fine-tuning operations"""
    print("🚀 KIMERA SWM Fine-Tuning System")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = FineTuningOrchestrator()
    
    # Run optimization cycle
    result = orchestrator.run_optimization_cycle()
    
    # Generate and display report
    report = orchestrator.get_optimization_report()
    print(report)
    
    # Save optimization history
    history_file = Path("logs/fine_tuning_history.json")
    history_file.parent.mkdir(parents=True, exist_ok=True)
    
    history = []
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(result)
    
    # Keep only last 100 optimization cycles
    history = history[-100:]
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"\n💾 Optimization history saved to {history_file}")
    print(f"📁 Configuration saved to {orchestrator.config_path}")
    
    return result


if __name__ == "__main__":
    main()