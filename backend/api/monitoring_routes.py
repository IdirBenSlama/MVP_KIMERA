"""
Monitoring API Routes for Kimera SWM

Provides REST API endpoints for accessing the comprehensive monitoring system,
including entropy analysis, semantic metrics, thermodynamic analysis, and benchmarking.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from ..monitoring.system_observer import SystemObserver
from ..monitoring.benchmarking_suite import BenchmarkRunner
from ..vault import get_vault_manager
from ..core.geoid import GeoidState
from ..core.models import LinguisticGeoid

# Initialize router
router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = logging.getLogger(__name__)

# Global monitoring instances
system_observer = SystemObserver()
vault_manager = get_vault_manager(mode="understanding")
benchmark_runner = BenchmarkRunner()  # Create an instance of BenchmarkRunner


@router.get("/status")
async def get_monitoring_status():
    """Get current monitoring system status"""
    try:
        # Get basic system info
        all_geoids = vault_manager.get_all_geoids()
        vault_info = {
            'vault_a_scars': vault_manager.get_total_scar_count('vault_a'),
            'vault_b_scars': vault_manager.get_total_scar_count('vault_b'),
            'active_geoids': len(all_geoids)
        }
        
        # Get system summary
        summary = system_observer.get_system_summary()
        
        return {
            'status': 'active',
            'timestamp': datetime.now().isoformat(),
            'monitoring_active': True,
            'observer_context': system_observer.current_observer,
            'system_health': summary.get('system_health', {}),
            'vault_info': vault_info,
            'observation_count': summary.get('observation_count', 0),
            'last_observation': summary.get('last_observation'),
            'recent_alerts': len(summary.get('recent_alerts', []))
        }
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/observe")
async def trigger_system_observation():
    """Trigger a comprehensive system observation"""
    try:
        # Get current system state
        all_geoids = vault_manager.get_all_geoids()
        vault_info = {
            'vault_a_scars': vault_manager.get_total_scar_count('vault_a'),
            'vault_b_scars': vault_manager.get_total_scar_count('vault_b'),
            'active_geoids': len(all_geoids)
        }
        
        # Create mock linguistic geoids for demonstration
        # In a real system, these would come from the linguistic processing engine
        linguistic_geoids = []
        for i, geoid in enumerate(all_geoids[:5]):  # Sample first 5
            lg = LinguisticGeoid(
                primary_statement=f"Geoid {geoid.geoid_id} semantic analysis",
                confidence_score=0.8,
                source_geoid_id=geoid.geoid_id,
                supporting_scars=[],
                potential_ambiguities=[],
                explanation_lineage=f"observation_{i}"
            )
            linguistic_geoids.append(lg)
        
        # Perform observation
        snapshot = system_observer.observe_system(all_geoids, linguistic_geoids, vault_info)
        
        return {
            'timestamp': snapshot.timestamp.isoformat(),
            'observer_context': snapshot.observer_context,
            'entropy_metrics': {
                'shannon_entropy': snapshot.entropy_measurement.shannon_entropy,
                'thermodynamic_entropy': snapshot.entropy_measurement.thermodynamic_entropy,
                'relative_entropy': snapshot.entropy_measurement.relative_entropy,
                'system_complexity': snapshot.entropy_measurement.system_complexity
            },
            'semantic_metrics': {
                'semantic_entropy': snapshot.semantic_measurement.semantic_entropy,
                'meaning_density': snapshot.semantic_measurement.meaning_density,
                'context_coherence': snapshot.semantic_measurement.context_coherence,
                'semantic_efficiency': snapshot.semantic_measurement.semantic_efficiency,
                'information_utility': snapshot.semantic_measurement.information_utility
            },
            'thermodynamic_metrics': {
                'total_energy': snapshot.thermodynamic_state.total_energy,
                'temperature': snapshot.thermodynamic_state.temperature,
                'pressure': snapshot.thermodynamic_state.pressure,
                'efficiency': snapshot.thermodynamic_state.efficiency,
                'entropy_production': snapshot.thermodynamic_state.entropy_production
            },
            'system_health': snapshot.system_health,
            'metadata': snapshot.metadata
        }
    except Exception as e:
        logger.error(f"Error during system observation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entropy/trends")
async def get_entropy_trends(window_size: int = Query(100, ge=10, le=1000)):
    """Get entropy trends over recent observations"""
    try:
        trends = system_observer.entropy_monitor.get_entropy_trends(window_size)
        return {
            'window_size': window_size,
            'trends': trends,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting entropy trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entropy/anomalies")
async def get_entropy_anomalies(threshold_std: float = Query(2.0, ge=1.0, le=5.0)):
    """Detect entropy anomalies"""
    try:
        anomalies = system_observer.entropy_monitor.detect_entropy_anomalies(threshold_std)
        return {
            'threshold_std': threshold_std,
            'anomalies': anomalies,
            'count': len(anomalies),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error detecting entropy anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semantic/trends")
async def get_semantic_trends(window_size: int = Query(50, ge=10, le=500)):
    """Get semantic metrics trends"""
    try:
        trends = system_observer.semantic_collector.get_semantic_trends(window_size)
        return {
            'window_size': window_size,
            'trends': trends,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting semantic trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semantic/anomalies")
async def get_semantic_anomalies(threshold_std: float = Query(2.0, ge=1.0, le=5.0)):
    """Detect semantic anomalies"""
    try:
        anomalies = system_observer.semantic_collector.detect_semantic_anomalies(threshold_std)
        return {
            'threshold_std': threshold_std,
            'anomalies': anomalies,
            'count': len(anomalies),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error detecting semantic anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thermodynamic/trends")
async def get_thermodynamic_trends(window_size: int = Query(100, ge=10, le=1000)):
    """Get thermodynamic trends"""
    try:
        trends = system_observer.thermodynamic_analyzer.get_thermodynamic_trends(window_size)
        return {
            'window_size': window_size,
            'trends': trends,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting thermodynamic trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thermodynamic/efficiency")
async def get_thermodynamic_efficiency(window_size: int = Query(100, ge=10, le=1000)):
    """Get thermodynamic efficiency metrics"""
    try:
        efficiency = system_observer.thermodynamic_analyzer.calculate_thermodynamic_efficiency(window_size)
        return {
            'window_size': window_size,
            'efficiency_metrics': efficiency,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating thermodynamic efficiency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thermodynamic/constraints")
async def check_thermodynamic_constraints():
    """Check for thermodynamic constraint violations"""
    try:
        if not system_observer.thermodynamic_analyzer.states:
            return {
                'violations': [],
                'message': 'No thermodynamic states available for analysis',
                'timestamp': datetime.now().isoformat()
            }
        
        latest_state = list(system_observer.thermodynamic_analyzer.states)[-1]
        violations = system_observer.thermodynamic_analyzer.check_thermodynamic_constraints(latest_state)
        
        return {
            'violations': violations,
            'violation_count': len(violations),
            'latest_state_timestamp': latest_state.timestamp.isoformat(),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking thermodynamic constraints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/observer/context")
async def set_observer_context(context: str):
    """Set the observer context for monitoring"""
    try:
        system_observer.set_observer_context(context)
        return {
            'previous_context': system_observer.current_observer,
            'new_context': context,
            'available_contexts': list(system_observer.active_observers.keys()),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error setting observer context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/observer/contexts")
async def get_observer_contexts():
    """Get available observer contexts"""
    try:
        contexts = {}
        for name, profile in system_observer.active_observers.items():
            contexts[name] = {
                'name': profile.name,
                'attention_weights': profile.attention_weights,
                'temporal_focus': profile.temporal_focus,
                'analysis_depth': profile.analysis_depth,
                'priority_metrics': profile.priority_metrics,
                'is_current': name == system_observer.current_observer
            }
        
        return {
            'current_context': system_observer.current_observer,
            'available_contexts': contexts,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting observer contexts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_system_summary(window_size: int = Query(100, ge=10, le=1000)):
    """Get comprehensive system summary"""
    try:
        summary = system_observer.get_system_summary(window_size)
        return summary
    except Exception as e:
        logger.error(f"Error getting system summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_recent_alerts(hours: int = Query(24, ge=1, le=168)):
    """Get recent alerts"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [
            alert for alert in system_observer.alert_history
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        
        return {
            'alerts': recent_alerts,
            'count': len(recent_alerts),
            'hours_back': hours,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_type}")
async def generate_report(report_type: str):
    """Generate system report"""
    try:
        if report_type not in ['comprehensive', 'executive', 'technical']:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        report = system_observer.generate_report(report_type)
        return {
            'report_type': report_type,
            'report': report,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_observations(format: str = Query('json')):
    """Export all observations"""
    try:
        if format not in ['json']:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        data = system_observer.export_observations(format)
        return data
    except Exception as e:
        logger.error(f"Error exporting observations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Benchmarking endpoints
@router.get("/benchmark/suites")
async def get_benchmark_suites():
    """Get available benchmark suites"""
    try:
        suites = {}
        for name, suite in benchmark_runner.benchmark_suites.items():
            suites[name] = {
                'name': suite.name,
                'description': suite.description,
                'tests': suite.tests,
                'parameters': suite.parameters
            }
        
        return {
            'suites': suites,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting benchmark suites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark/run/{suite_name}")
async def run_benchmark_suite(suite_name: str, background_tasks: BackgroundTasks):
    """Run a benchmark suite"""
    try:
        if suite_name not in benchmark_runner.benchmark_suites:
            raise HTTPException(status_code=404, detail=f"Benchmark suite '{suite_name}' not found")
        
        # Run benchmark in background
        def run_benchmark():
            try:
                results = benchmark_runner.run_suite(suite_name)
                logger.info(f"Benchmark suite '{suite_name}' completed")
            except Exception as e:
                logger.error(f"Benchmark suite '{suite_name}' failed: {e}")
        
        background_tasks.add_task(run_benchmark)
        
        return {
            'message': f"Benchmark suite '{suite_name}' started",
            'suite_name': suite_name,
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error running benchmark suite: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/results")
async def get_benchmark_results(limit: int = Query(10, ge=1, le=100)):
    """Get recent benchmark results"""
    try:
        recent_results = benchmark_runner.results_history[-limit:]
        
        results = []
        for result in recent_results:
            results.append({
                'test_name': result.test_name,
                'timestamp': result.timestamp.isoformat(),
                'duration': result.duration,
                'success': result.success,
                'error_message': result.error_message,
                'key_metrics': {
                    k: v for k, v in result.metrics.items()
                    if isinstance(v, (int, float)) and not k.startswith('_')
                }
            })
        
        return {
            'results': results,
            'total_results': len(benchmark_runner.results_history),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting benchmark results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark/test/{test_name}")
async def run_benchmark_test(test_name: str, parameters: Optional[Dict[str, Any]] = None):
    """Run a single benchmark test"""
    try:
        if test_name not in benchmark_runner.test_registry:
            raise HTTPException(status_code=404, detail=f"Benchmark test '{test_name}' not found")
        
        result = benchmark_runner.run_test(test_name, parameters)
        
        return {
            'test_name': result.test_name,
            'timestamp': result.timestamp.isoformat(),
            'duration': result.duration,
            'success': result.success,
            'metrics': result.metrics,
            'parameters': result.parameters,
            'error_message': result.error_message,
            'metadata': result.metadata
        }
    except Exception as e:
        logger.error(f"Error running benchmark test: {e}")
        raise HTTPException(status_code=500, detail=str(e))
