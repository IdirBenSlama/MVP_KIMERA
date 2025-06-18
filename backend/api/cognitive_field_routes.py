from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Tuple, Set, Optional, Any
import numpy as np
import asyncio
from datetime import datetime
import logging
import time

from ..engines.cognitive_field_dynamics import CognitiveFieldDynamics, SemanticField
from ..vault.database import SessionLocal, GeoidDB
from ..vault.crud import get_geoids_with_embeddings
from ..monitoring.cognitive_field_metrics import get_metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/cognitive-fields",
    tags=["Cognitive Field Dynamics"],
)

# --- Service Initialization ---
field_service = CognitiveFieldDynamics(dimension=1024)  # Standard embedding dimension
evolution_task: Optional[asyncio.Task] = None
metrics_collector = get_metrics_collector()

# --- Pydantic Models ---
class AddGeoidRequest(BaseModel):
    geoid_id: str
    embedding: List[float]

class FindNeighborsRequest(BaseModel):
    geoid_id: str
    energy_threshold: float = 0.1

class InfluenceFieldResponse(BaseModel):
    geoid_id: str
    influence_map: Dict[str, float]
    total_influence: float
    average_influence: float

class FieldEvolutionControl(BaseModel):
    action: str = Field(..., description="Action to perform: 'start', 'stop', 'status'")
    time_step: float = 0.1

class SemanticAnomalyResponse(BaseModel):
    anomalies: List[Dict[str, Any]]
    total_fields: int
    field_health: float

class GeoidInput(BaseModel):
    geoid_id: str
    embedding: List[float]

class NeighborRequest(BaseModel):
    geoid_id: str
    energy_threshold: float = 0.1

# --- Helper Functions ---
def _classify_interaction(strength: float) -> str:
    """Classify interaction type based on strength"""
    if strength > 0.8:
        return "strong_resonance"
    elif strength > 0.5:
        return "moderate_coupling"
    elif strength > 0.2:
        return "weak_interaction"
    else:
        return "minimal_presence"

def _classify_influence(strength: float) -> str:
    """Classify influence type based on strength"""
    if strength > 0.7:
        return "dominant_influence"
    elif strength > 0.4:
        return "significant_influence"
    elif strength > 0.1:
        return "peripheral_influence"
    else:
        return "negligible_influence"

def _calculate_cluster_signature(cluster: Set[str]) -> Dict:
    """Calculate a resonance signature for a cluster"""
    if not cluster:
        return {}
    frequencies = []
    phases = []
    for geoid_id in cluster:
        if geoid_id in field_service.fields:
            field = field_service.fields[geoid_id]
            frequencies.append(field.resonance_frequency)
            phases.append(field.phase)
    return {
        "avg_frequency": float(np.mean(frequencies)) if frequencies else 0.0,
        "frequency_variance": float(np.var(frequencies)) if frequencies else 0.0,
        "phase_coherence": float(np.abs(np.mean(np.exp(1j * np.array(phases))))) if phases else 0.0
    }

async def _run_field_evolution(time_step: float):
    """Background task for field evolution"""
    try:
        while True:
            await field_service.evolve_fields(time_step)
            await asyncio.sleep(time_step)
    except asyncio.CancelledError:
        print("Field evolution stopped")
        raise

# --- API Endpoints ---
@router.post("/geoid/add")
async def add_geoid_to_field(geoid_input: GeoidInput) -> Dict[str, Any]:
    """
    Add a geoid to the semantic field.
    This creates a new field source in the semantic space.
    """
    try:
        embedding = np.array(geoid_input.embedding, dtype=np.float32)
        field = field_service.add_geoid(geoid_input.geoid_id, embedding)
        if field is None:
            raise HTTPException(status_code=400, detail="Could not create field for geoid. Embedding may be empty.")

        return {
            "geoid_id": field.geoid_id,
            "status": "added",
            "resonance_frequency": float(field.resonance_frequency),
            "phase": float(field.phase)
        }
    except Exception as e:
        logger.error(f"Error adding geoid to field: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/geoid/add_from_db")
async def add_geoids_from_db(limit: int = Query(100, description="Maximum number of geoids to load")):
    """
    Load geoids from the database and add them to the semantic field.
    """
    try:
        geoids_data = get_geoids_with_embeddings(limit=limit)
        added_count = 0
        
        for geoid_id, embedding in geoids_data:
            if embedding is not None:
                field_service.add_geoid(geoid_id, np.array(embedding))
                added_count += 1
        
        return {
            "status": f"Added {added_count} geoids from DB to semantic field."
        }
    except Exception as e:
        logger.error(f"Error loading geoids from database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/neighbors/find")
async def find_semantic_neighbors(request: NeighborRequest) -> Dict[str, Any]:
    """
    Find semantic neighbors through field interactions.
    This is a dynamic alternative to traditional kNN.
    """
    try:
        neighbors = field_service.find_semantic_neighbors(
            request.geoid_id, request.energy_threshold
        )
        return {
            "geoid_id": request.geoid_id,
            "neighbors": [
                {
                    "geoid_id": neighbor_id,
                    "interaction_strength": strength,
                    "classification": _classify_interaction(strength)
                }
                for neighbor_id, strength in neighbors
            ],
            "neighbor_count": len(neighbors)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error finding neighbors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/influence/{geoid_id}", response_model=InfluenceFieldResponse)
async def get_influence_field(geoid_id: str):
    """
    Find the influence field of a geoid.
    This is a continuous alternative to RkNN.
    """
    try:
        influence_map = field_service.find_influence_field(geoid_id)
        return {
            "geoid_id": geoid_id,
            "influence_map": influence_map,
            "total_influence": sum(influence_map.values()),
            "average_influence": sum(influence_map.values()) / len(influence_map) if influence_map else 0
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting influence field: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies/detect", response_model=SemanticAnomalyResponse)
async def detect_semantic_anomalies():
    """
    Detect semantic anomalies through field analysis.
    More sophisticated than simple contradiction detection.
    """
    try:
        anomalies = field_service.detect_semantic_anomalies()
        total_fields = len(field_service.fields)
        anomaly_count = len(anomalies)
        field_health = 1.0 - (anomaly_count / total_fields) if total_fields > 0 else 1.0
        return SemanticAnomalyResponse(
            anomalies=anomalies,
            total_fields=total_fields,
            field_health=field_health
        )
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/resonance")
async def find_resonance_clusters():
    """
    Find semantic clusters through resonance patterns.
    Clusters emerge naturally from field interactions.
    """
    try:
        clusters = field_service.find_semantic_clusters_by_resonance()
        return {
            "clusters": [
                {
                    "cluster_id": i,
                    "geoid_ids": list(cluster),
                    "size": len(cluster),
                    "resonance_signature": _calculate_cluster_signature(cluster)
                }
                for i, cluster in enumerate(clusters)
            ],
            "total_clusters": len(clusters),
            "clustering_method": "resonance_pattern"
        }
    except Exception as e:
        logger.error(f"Error finding clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/field-map")
async def get_semantic_field_map():
    """
    Get a map of the entire semantic field space.
    Provides a holistic view of semantic relationships.
    """
    try:
        field_map = {
            "fields": {},
            "interactions": {},
            "topology": {
                "critical_points": len(field_service.field_topology.critical_points),
                "vortices": len(field_service.field_topology.vortices)
            }
        }
        for geoid_id, field in field_service.fields.items():
            field_map["fields"][geoid_id] = {
                "resonance_frequency": float(field.resonance_frequency),
                "phase": float(field.phase),
                "field_strength": float(field.field_strength)
            }
        
        all_interactions = []
        for source_id, targets in field_service.field_interactions.items():
            for target_id, strength in targets.items():
                all_interactions.append({
                    "source": source_id,
                    "target": target_id,
                    "strength": strength
                })
        
        top_interactions = sorted(
            all_interactions,
            key=lambda x: abs(x["strength"]),
            reverse=True
        )[:50]
        field_map["interactions"] = top_interactions
        return field_map
    except Exception as e:
        logger.error(f"Error getting field map: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Metrics Endpoints ---

@router.get("/metrics/performance")
async def get_performance_metrics():
    """Get comprehensive performance metrics."""
    try:
        # Collect current system snapshot
        await metrics_collector.collect_system_snapshot(field_service)
        
        # Get performance summary
        performance_summary = metrics_collector.get_performance_summary()
        
        return {
            "timestamp": time.time(),
            "system_status": "operational",
            "metrics": performance_summary
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/system")
async def get_system_metrics():
    """Get current system metrics snapshot."""
    try:
        system_metrics = await metrics_collector.collect_system_snapshot(field_service)
        
        return {
            "timestamp": system_metrics.timestamp,
            "total_fields": system_metrics.total_fields,
            "active_waves": system_metrics.active_waves,
            "evolution_time": system_metrics.evolution_time,
            "performance": {
                "evolution_step_duration_ms": system_metrics.evolution_step_duration * 1000,
                "wave_propagation_time_ms": system_metrics.wave_propagation_time * 1000,
                "memory_usage_mb": system_metrics.memory_usage_mb
            }
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/fields")
async def get_field_metrics():
    """Get detailed field metrics."""
    try:
        field_metrics = {}
        
        for field_id, metrics in metrics_collector.field_metrics.items():
            field_metrics[field_id] = {
                "creation_time": metrics.creation_time,
                "current_strength": metrics.current_strength,
                "resonance_frequency": metrics.resonance_frequency,
                "wave_interactions": metrics.wave_interactions,
                "resonance_amplifications": metrics.resonance_amplifications,
                "total_energy_received": metrics.total_energy_received
            }
        
        return {
            "field_count": len(field_metrics),
            "field_metrics": field_metrics,
            "summary": {
                "total_interactions": sum(m.wave_interactions for m in metrics_collector.field_metrics.values()),
                "total_resonance_events": sum(m.resonance_amplifications for m in metrics_collector.field_metrics.values()),
                "total_energy_in_system": sum(m.total_energy_received for m in metrics_collector.field_metrics.values())
            }
        }
    except Exception as e:
        logger.error(f"Error getting field metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/waves")
async def get_wave_metrics():
    """Get detailed wave metrics."""
    try:
        wave_metrics = {}
        
        for wave_id, metrics in metrics_collector.wave_metrics.items():
            wave_metrics[wave_id] = {
                "origin_id": metrics.origin_id,
                "creation_time": metrics.creation_time,
                "current_amplitude": metrics.current_amplitude,
                "current_radius": metrics.current_radius,
                "fields_visited": metrics.fields_visited,
                "resonance_events": metrics.resonance_events,
                "total_energy_transferred": metrics.total_energy_transferred
            }
        
        return {
            "wave_count": len(wave_metrics),
            "wave_metrics": wave_metrics,
            "summary": {
                "total_waves_created": metrics_collector.total_waves_created,
                "total_energy_transferred": sum(m.total_energy_transferred for m in metrics_collector.wave_metrics.values()),
                "total_resonance_events": sum(m.resonance_events for m in metrics_collector.wave_metrics.values())
            }
        }
    except Exception as e:
        logger.error(f"Error getting wave metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/export")
async def export_metrics(filepath: str = Query("cognitive_field_metrics.json", description="Export file path")):
    """Export all metrics to a JSON file."""
    try:
        metrics_collector.export_metrics(filepath)
        
        return {
            "status": "success",
            "message": f"Metrics exported to {filepath}",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/reset")
async def reset_metrics():
    """Reset all collected metrics."""
    try:
        metrics_collector.reset_metrics()
        
        return {
            "status": "success",
            "message": "All metrics have been reset",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evolution/step")
async def evolution_step(time_step: float = Query(0.1, description="Evolution time step")):
    """Manually trigger a field evolution step."""
    try:
        start_time = time.time()
        
        await field_service.evolve_fields(time_step)
        
        duration = time.time() - start_time
        
        return {
            "status": "success",
            "evolution_time": field_service.time,
            "time_step": time_step,
            "duration_ms": duration * 1000,
            "active_fields": len(field_service.fields),
            "active_waves": len(field_service.waves)
        }
    except Exception as e:
        logger.error(f"Error during evolution step: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 