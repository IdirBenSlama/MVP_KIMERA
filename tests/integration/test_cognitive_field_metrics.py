"""
Integration tests for Cognitive Field Dynamics Metrics System

Tests the comprehensive metrics collection, performance tracking, and analytics capabilities
of the Cognitive Field Dynamics system.
"""

import pytest
import asyncio
import numpy as np
import time
import tempfile
import os
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.engines.cognitive_field_dynamics import CognitiveFieldDynamics
from backend.monitoring.cognitive_field_metrics import CognitiveFieldMetricsCollector, get_metrics_collector

client = TestClient(app)

@pytest.fixture
def metrics_collector():
    """Create a fresh metrics collector for testing"""
    collector = CognitiveFieldMetricsCollector()
    return collector

@pytest.fixture
def cfd_engine():
    """Create a Cognitive Field Dynamics engine for testing"""
    return CognitiveFieldDynamics(dimension=4)

@pytest.fixture
def sample_fields(cfd_engine):
    """Create sample fields for testing"""
    fields = []
    embeddings = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0]),
    ]
    
    for i, embedding in enumerate(embeddings):
        field = cfd_engine.add_geoid(f"test_field_{i}", embedding)
        fields.append(field)
    
    return fields

class TestMetricsCollection:
    """Test basic metrics collection functionality"""
    
    def test_metrics_collector_initialization(self, metrics_collector):
        """Test metrics collector initializes properly"""
        assert metrics_collector.total_waves_created == 0
        assert metrics_collector.total_fields_created == 0
        assert metrics_collector.total_resonance_events == 0
        assert metrics_collector.total_collisions == 0
        assert len(metrics_collector.wave_metrics) == 0
        assert len(metrics_collector.field_metrics) == 0
    
    def test_field_creation_tracking(self, metrics_collector, cfd_engine):
        """Test field creation is properly tracked"""
        # Add a field
        embedding = np.array([1.0, 0.0, 0.0, 0.0])
        field = cfd_engine.add_geoid("test_field", embedding)
        
        # Track the field creation
        metrics_collector.track_field_creation(field)
        
        # Verify tracking
        assert metrics_collector.total_fields_created == 1
        assert "test_field" in metrics_collector.field_metrics
        
        field_metrics = metrics_collector.field_metrics["test_field"]
        assert field_metrics.field_id == "test_field"
        assert field_metrics.initial_strength == field.field_strength
        assert field_metrics.current_strength == field.field_strength
        assert field_metrics.resonance_frequency == field.resonance_frequency
        assert field_metrics.wave_interactions == 0
    
    def test_wave_creation_tracking(self, metrics_collector, cfd_engine, sample_fields):
        """Test wave creation is properly tracked"""
        # Get a wave from the engine (created during field addition)
        wave = cfd_engine.waves[0]
        
        # Track the wave
        wave_id = metrics_collector.track_wave_creation(wave)
        
        # Verify tracking
        assert metrics_collector.total_waves_created == 1
        assert wave_id in metrics_collector.wave_metrics
        
        wave_metrics = metrics_collector.wave_metrics[wave_id]
        assert wave_metrics.origin_id == wave.origin_id
        assert wave_metrics.initial_amplitude == wave.amplitude
        assert wave_metrics.current_amplitude == wave.amplitude
        assert wave_metrics.current_radius == wave.radius
        assert wave_metrics.fields_visited == 0
    
    @pytest.mark.asyncio
    async def test_system_snapshot_collection(self, metrics_collector, cfd_engine, sample_fields):
        """Test system snapshot collection"""
        # Collect a system snapshot
        system_metrics = await metrics_collector.collect_system_snapshot(cfd_engine)
        
        # Verify snapshot data
        assert system_metrics.total_fields == len(sample_fields)
        assert system_metrics.active_waves == len(cfd_engine.waves)
        assert system_metrics.evolution_time == cfd_engine.time
        assert system_metrics.memory_usage_mb > 0
        assert len(metrics_collector.system_metrics_history) == 1

class TestPerformanceMetrics:
    """Test performance metrics tracking"""
    
    def test_evolution_time_tracking(self, metrics_collector):
        """Test evolution time tracking"""
        # Track some evolution times
        times = [0.01, 0.015, 0.012, 0.008]
        for t in times:
            metrics_collector.track_evolution_time(t)
        
        # Verify tracking
        assert len(metrics_collector.evolution_times) == len(times)
        avg_time = metrics_collector._get_average_evolution_time()
        assert abs(avg_time - np.mean(times)) < 1e-6
    
    def test_wave_propagation_time_tracking(self, metrics_collector):
        """Test wave propagation time tracking"""
        # Track some propagation times
        times = [0.005, 0.007, 0.006, 0.004]
        for t in times:
            metrics_collector.track_wave_propagation_time(t)
        
        # Verify tracking
        assert len(metrics_collector.wave_propagation_times) == len(times)
        avg_time = metrics_collector._get_average_wave_propagation_time()
        assert abs(avg_time - np.mean(times)) < 1e-6
    
    def test_api_response_time_tracking(self, metrics_collector):
        """Test API response time tracking"""
        # Track response times for different endpoints
        endpoints = ["add_geoid", "find_neighbors", "get_influence"]
        times = [0.1, 0.05, 0.08]
        
        for endpoint, time_val in zip(endpoints, times):
            metrics_collector.track_api_response_time(endpoint, time_val)
        
        # Verify tracking
        for endpoint in endpoints:
            assert len(metrics_collector.api_response_times[endpoint]) == 1
    
    def test_performance_summary(self, metrics_collector, cfd_engine, sample_fields):
        """Test performance summary generation"""
        # Add some test data
        for field in sample_fields:
            metrics_collector.track_field_creation(field)
        
        for wave in cfd_engine.waves:
            metrics_collector.track_wave_creation(wave)
        
        metrics_collector.track_evolution_time(0.01)
        metrics_collector.track_wave_propagation_time(0.005)
        
        # Get performance summary
        summary = metrics_collector.get_performance_summary()
        
        # Verify summary structure
        assert "system_overview" in summary
        assert "timing_metrics" in summary
        assert "field_metrics" in summary
        assert "wave_metrics" in summary
        
        # Verify system overview
        system_overview = summary["system_overview"]
        assert system_overview["total_fields_created"] == len(sample_fields)
        assert system_overview["total_waves_created"] == len(cfd_engine.waves)
        
        # Verify timing metrics
        timing_metrics = summary["timing_metrics"]
        assert timing_metrics["average_evolution_time_ms"] == 10.0  # 0.01 * 1000
        assert timing_metrics["average_wave_propagation_time_ms"] == 5.0  # 0.005 * 1000

class TestMetricsExport:
    """Test metrics export functionality"""
    
    def test_metrics_export(self, metrics_collector, cfd_engine, sample_fields):
        """Test metrics export to JSON file"""
        # Add some test data
        for field in sample_fields:
            metrics_collector.track_field_creation(field)
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filepath = f.name
        
        try:
            metrics_collector.export_metrics(temp_filepath)
            
            # Verify file was created
            assert os.path.exists(temp_filepath)
            assert os.path.getsize(temp_filepath) > 0
            
            # Verify file contains valid JSON
            import json
            with open(temp_filepath, 'r') as f:
                data = json.load(f)
            
            assert "timestamp" in data
            assert "performance_summary" in data
            assert "collection_period" in data
            
        finally:
            # Clean up
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
    
    def test_metrics_reset(self, metrics_collector, cfd_engine, sample_fields):
        """Test metrics reset functionality"""
        # Add some test data
        for field in sample_fields:
            metrics_collector.track_field_creation(field)
        
        metrics_collector.track_evolution_time(0.01)
        
        # Verify data exists
        assert metrics_collector.total_fields_created > 0
        assert len(metrics_collector.field_metrics) > 0
        assert len(metrics_collector.evolution_times) > 0
        
        # Reset metrics
        metrics_collector.reset_metrics()
        
        # Verify everything is reset
        assert metrics_collector.total_fields_created == 0
        assert len(metrics_collector.field_metrics) == 0
        assert len(metrics_collector.evolution_times) == 0
        assert len(metrics_collector.wave_metrics) == 0

class TestAPIMetricsEndpoints:
    """Test metrics API endpoints"""
    
    def test_performance_metrics_endpoint(self):
        """Test /metrics/performance endpoint"""
        response = client.get("/cognitive-fields/metrics/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "system_status" in data
        assert "metrics" in data
        
        metrics = data["metrics"]
        assert "system_overview" in metrics
        assert "timing_metrics" in metrics
        assert "field_metrics" in metrics
        assert "wave_metrics" in metrics
    
    def test_system_metrics_endpoint(self):
        """Test /metrics/system endpoint"""
        response = client.get("/cognitive-fields/metrics/system")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "total_fields" in data
        assert "active_waves" in data
        assert "evolution_time" in data
        assert "performance" in data
        
        performance = data["performance"]
        assert "evolution_step_duration_ms" in performance
        assert "wave_propagation_time_ms" in performance
        assert "memory_usage_mb" in performance
    
    def test_field_metrics_endpoint(self):
        """Test /metrics/fields endpoint"""
        response = client.get("/cognitive-fields/metrics/fields")
        assert response.status_code == 200
        
        data = response.json()
        assert "field_count" in data
        assert "field_metrics" in data
        assert "summary" in data
        
        summary = data["summary"]
        assert "total_interactions" in summary
        assert "total_resonance_events" in summary
        assert "total_energy_in_system" in summary
    
    def test_wave_metrics_endpoint(self):
        """Test /metrics/waves endpoint"""
        response = client.get("/cognitive-fields/metrics/waves")
        assert response.status_code == 200
        
        data = response.json()
        assert "wave_count" in data
        assert "wave_metrics" in data
        assert "summary" in data
        
        summary = data["summary"]
        assert "total_waves_created" in summary
        assert "total_energy_transferred" in summary
        assert "total_resonance_events" in summary
    
    def test_metrics_export_endpoint(self):
        """Test /metrics/export endpoint"""
        # Test with default filename
        response = client.post("/cognitive-fields/metrics/export")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "Metrics exported" in data["message"]
        assert "timestamp" in data
    
    def test_metrics_reset_endpoint(self):
        """Test /metrics/reset endpoint"""
        response = client.post("/cognitive-fields/metrics/reset")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "reset" in data["message"]
        assert "timestamp" in data
    
    def test_evolution_step_endpoint(self):
        """Test /evolution/step endpoint"""
        response = client.get("/cognitive-fields/evolution/step?time_step=0.05")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "evolution_time" in data
        assert data["time_step"] == 0.05
        assert "duration_ms" in data
        assert "active_fields" in data
        assert "active_waves" in data

class TestIntegratedMetricsWorkflow:
    """Test complete metrics workflow with field evolution"""
    
    @pytest.mark.asyncio
    async def test_complete_metrics_workflow(self):
        """Test complete metrics collection during field evolution"""
        # Create engine and metrics collector
        cfd_engine = CognitiveFieldDynamics(dimension=4)
        metrics_collector = CognitiveFieldMetricsCollector()
        
        # Add fields and track them
        embeddings = [
            np.array([1.0, 0.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0, 0.0]),
            np.array([0.7071, 0.7071, 0.0, 0.0]),  # Should resonate with first two
        ]
        
        for i, embedding in enumerate(embeddings):
            field = cfd_engine.add_geoid(f"test_field_{i}", embedding)
            metrics_collector.track_field_creation(field)
        
        # Track initial waves
        for wave in cfd_engine.waves:
            metrics_collector.track_wave_creation(wave)
        
        # Evolve the system and track metrics
        evolution_start = time.time()
        await cfd_engine.evolve_fields(0.1)
        evolution_duration = time.time() - evolution_start
        
        metrics_collector.track_evolution_time(evolution_duration)
        
        # Collect system snapshot
        system_metrics = await metrics_collector.collect_system_snapshot(cfd_engine)
        
        # Verify metrics were collected
        assert metrics_collector.total_fields_created == 3
        assert metrics_collector.total_waves_created == 3
        assert len(metrics_collector.evolution_times) == 1
        assert len(metrics_collector.system_metrics_history) == 1
        
        # Verify system metrics
        assert system_metrics.total_fields == 3
        assert system_metrics.evolution_time > 0
        
        # Get performance summary
        summary = metrics_collector.get_performance_summary()
        assert summary["system_overview"]["total_fields_created"] == 3
        assert summary["timing_metrics"]["average_evolution_time_ms"] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 