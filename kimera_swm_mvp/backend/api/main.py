from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid

from ..core.geoid import GeoidState
from ..engines.contradiction_engine import ContradictionEngine
from ..engines.thermodynamics import SemanticThermodynamicsEngine
from ..vault.vault_manager import VaultManager
from ..engines.kccl import KimeraCognitiveCycle

app = FastAPI(title="KIMERA SWM MVP API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize core systems
kimera_system = {
    'contradiction_engine': ContradictionEngine(),
    'thermodynamics_engine': SemanticThermodynamicsEngine(),
    'vault_manager': VaultManager(),
    'cognitive_cycle': KimeraCognitiveCycle(),
    'active_geoids': {},
    'system_state': {'cycle_count': 0}
}

class CreateGeoidRequest(BaseModel):
    semantic_features: Dict[str, float]
    symbolic_content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class ProcessContradictionRequest(BaseModel):
    geoid_ids: List[str]
    force_collapse: bool = False

@app.post("/geoids", response_model=Dict[str, Any])
async def create_geoid(request: CreateGeoidRequest):
    """Create new Geoid following DOC-201 specification"""
    geoid_id = f"GEOID_{uuid.uuid4().hex[:8]}"

    geoid = GeoidState(
        geoid_id=geoid_id,
        semantic_state=request.semantic_features,
        symbolic_state=request.symbolic_content,
        metadata=request.metadata
    )

    # Validate thermodynamic constraints
    kimera_system['thermodynamics_engine'].validate_transformation(
        GeoidState(geoid_id="dummy", semantic_state={}),
        geoid,
    )

    kimera_system['active_geoids'][geoid_id] = geoid

    return {
        'geoid_id': geoid_id,
        'status': 'created',
        'entropy': geoid.calculate_entropy(),
        'geoid': geoid.to_dict()
    }

@app.post("/process/contradictions")
async def process_contradictions(request: ProcessContradictionRequest):
    """Execute contradiction detection and processing"""

    # Get specified geoids
    target_geoids = [
        kimera_system['active_geoids'][gid]
        for gid in request.geoid_ids
        if gid in kimera_system['active_geoids']
    ]

    if len(target_geoids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 geoids for contradiction detection")

    # Run contradiction detection
    tensions = kimera_system['contradiction_engine'].detect_tension_gradients(target_geoids)

    results = []
    for tension in tensions:
        pulse_strength = kimera_system['contradiction_engine'].calculate_pulse_strength(
            tension, kimera_system['active_geoids']
        )

        stability_metrics = {
            'axis_convergence': 0.8,  # Mock values for MVP
            'vault_resonance': 0.7,
            'contradiction_lineage_ambiguity': 0.3
        }

        decision = kimera_system['contradiction_engine'].decide_collapse_or_surge(
            pulse_strength, stability_metrics
        )

        results.append({
            'tension': {
                'geoid_a': tension.geoid_a,
                'geoid_b': tension.geoid_b,
                'score': tension.tension_score,
                'type': tension.gradient_type
            },
            'pulse_strength': pulse_strength,
            'decision': decision
        })

    return {
        'cycle': kimera_system['system_state']['cycle_count'],
        'contradictions_detected': len(tensions),
        'results': results
    }

@app.get("/system/status")
async def get_system_status():
    """Get current KIMERA system status"""
    return {
        'active_geoids': len(kimera_system['active_geoids']),
        'vault_a_scars': len(kimera_system['vault_manager'].vault_a),
        'vault_b_scars': len(kimera_system['vault_manager'].vault_b),
        'cycle_count': kimera_system['system_state']['cycle_count'],
        'system_entropy': sum(g.calculate_entropy() for g in kimera_system['active_geoids'].values())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
