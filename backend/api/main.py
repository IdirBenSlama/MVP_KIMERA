from __future__ import annotations
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from ..core.geoid import GeoidState
from ..engines.contradiction_engine import ContradictionEngine
from ..engines.thermodynamics import SemanticThermodynamicsEngine
from ..vault.vault_manager import VaultManager

app = FastAPI(title="KIMERA SWM MVP API", version="0.1.0")

kimera_system = {
    'contradiction_engine': ContradictionEngine(),
    'thermodynamics_engine': SemanticThermodynamicsEngine(),
    'vault_manager': VaultManager(),
    'active_geoids': {},
    'system_state': {'cycle_count': 0}
}

class CreateGeoidRequest(BaseModel):
    semantic_features: Dict[str, float]
    symbolic_content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class ProcessContradictionRequest(BaseModel):
    geoid_ids: List[str]
    force_collapse: bool = False  # Optional flag for future use

@app.post("/geoids")
async def create_geoid(request: CreateGeoidRequest):
    geoid_id = f"GEOID_{uuid.uuid4().hex[:8]}"
    geoid = GeoidState(
        geoid_id=geoid_id,
        semantic_state=request.semantic_features,
        symbolic_state=request.symbolic_content,
        metadata=request.metadata,
    )

    kimera_system['thermodynamics_engine'].validate_transformation(GeoidState(geoid_id="temp"), geoid)
    kimera_system['active_geoids'][geoid_id] = geoid
    return {
        'geoid_id': geoid_id,
        'geoid': geoid.to_dict(),
        'entropy': geoid.calculate_entropy(),
    }

@app.post("/process/contradictions", response_model=Dict[str, Any])
async def process_contradictions(request: ProcessContradictionRequest):
    """Execute the core contradiction detection and processing cycle"""

    # 1. Fetch the target Geoids from the active system state
    target_geoids = [
        kimera_system['active_geoids'][gid]
        for gid in request.geoid_ids
        if gid in kimera_system['active_geoids']
    ]

    if len(target_geoids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Contradiction detection requires at least two valid Geoid IDs."
        )

    # 2. Run the Contradiction Engine
    contradiction_engine = kimera_system['contradiction_engine']
    tensions = contradiction_engine.detect_tension_gradients(target_geoids)

    if not tensions:
        return {"status": "complete", "message": "No significant contradictions detected."}

    # 3. Analyze each detected tension
    results = []
    for tension in tensions:
        pulse_strength = contradiction_engine.calculate_pulse_strength(
            tension, kimera_system['active_geoids']
        )

        stability_metrics = {
            'axis_convergence': 0.8,
            'vault_resonance': 0.7,
            'contradiction_lineage_ambiguity': 0.3
        }

        decision = contradiction_engine.decide_collapse_or_surge(
            pulse_strength, stability_metrics
        )

        results.append({
            'tension': {
                'geoids_involved': [tension.geoid_a, tension.geoid_b],
                'score': f"{tension.tension_score:.3f}",
                'type': tension.gradient_type
            },
            'pulse_strength': f"{pulse_strength:.3f}",
            'system_decision': decision
        })

    kimera_system['system_state']['cycle_count'] += 1

    return {
        'cycle': kimera_system['system_state']['cycle_count'],
        'contradictions_detected': len(tensions),
        'analysis_results': results
    }

@app.get("/system/status")
async def get_system_status():
    return {
        'active_geoids': len(kimera_system['active_geoids']),
        'vault_a_scars': len(kimera_system['vault_manager'].vault_a),
        'vault_b_scars': len(kimera_system['vault_manager'].vault_b),
        'system_entropy': sum(g.calculate_entropy() for g in kimera_system['active_geoids'].values()),
        'cycle_count': kimera_system['system_state']['cycle_count']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
