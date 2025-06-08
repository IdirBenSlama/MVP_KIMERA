from __future__ import annotations
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime

from ..core.geoid import GeoidState
from ..core.scar import ScarRecord
from ..engines.contradiction_engine import ContradictionEngine, TensionGradient
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

def create_scar_from_tension(
    tension: TensionGradient,
    geoids_dict: Dict[str, GeoidState]
) -> ScarRecord:
    """Create a ScarRecord from a resolved tension."""

    geoid_a = geoids_dict[tension.geoid_a]
    geoid_b = geoids_dict[tension.geoid_b]

    pre_entropy = (geoid_a.calculate_entropy() + geoid_b.calculate_entropy()) / 2
    post_entropy = pre_entropy + 0.1  # Simulate entropy change after collapse

    return ScarRecord(
        scar_id=f"SCAR_{uuid.uuid4().hex[:8]}",
        geoids=[tension.geoid_a, tension.geoid_b],
        reason=f"Resolved '{tension.gradient_type}' tension.",
        timestamp=datetime.now().isoformat(),
        resolved_by="ContradictionEngine:Collapse",
        pre_entropy=pre_entropy,
        post_entropy=post_entropy,
        delta_entropy=post_entropy - pre_entropy,
        cls_angle=45.0,
        semantic_polarity=0.2,
        mutation_frequency=0.85,
    )

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
    try:
        for v in request.semantic_features.values():
            if not isinstance(v, (int, float)):
                raise ValueError("Semantic features must be numeric")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid semantic features: {exc}")

    geoid = GeoidState(
        geoid_id=geoid_id,
        semantic_state=request.semantic_features,
        symbolic_state=request.symbolic_content,
        metadata=request.metadata,
    )

    # Validate thermodynamic constraints for new geoid (no before state)
    kimera_system['thermodynamics_engine'].validate_transformation(
        None,
        geoid,
    )
    kimera_system['active_geoids'][geoid_id] = geoid
    return {
        'geoid_id': geoid_id,
        'geoid': geoid.to_dict(),
        'entropy': geoid.calculate_entropy(),
    }

@app.post("/process/contradictions", response_model=Dict[str, Any])
async def process_contradictions(request: ProcessContradictionRequest):
    """Execute the core contradiction detection and processing cycle
    based on DOC-205a specifications."""

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
    scars_created = 0
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

        scar_created = False
        if decision == 'collapse':
            scar = create_scar_from_tension(tension, kimera_system['active_geoids'])
            kimera_system['vault_manager'].insert_scar(scar)
            scars_created += 1
            scar_created = True

        results.append({
            'tension': {
                'geoids_involved': [tension.geoid_a, tension.geoid_b],
                'score': f"{tension.tension_score:.3f}",
                'type': tension.gradient_type
            },
            'pulse_strength': f"{pulse_strength:.3f}",
            'system_decision': decision,
            'scar_created': scar_created
        })

    if 'cycle_count' not in kimera_system['system_state']:
        kimera_system['system_state']['cycle_count'] = 0
    kimera_system['system_state']['cycle_count'] += 1

    return {
        'cycle': kimera_system['system_state']['cycle_count'],
        'contradictions_detected': len(tensions),
        'scars_created': scars_created,
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
