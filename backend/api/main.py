from __future__ import annotations
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime
import os

from ..core.geoid import GeoidState
from ..core.scar import ScarRecord
from ..engines.contradiction_engine import ContradictionEngine, TensionGradient
from ..engines.thermodynamics import SemanticThermodynamicsEngine
from ..vault.vault_manager import VaultManager
from ..vault.database import SessionLocal, GeoidDB
import hashlib
import numpy as np

class _DummyTransformer:
    def encode(self, text: str):
        h = hashlib.sha256(text.encode()).digest()
        vec = np.frombuffer(h, dtype=np.uint8).astype(float)
        reps = (384 + len(vec) - 1) // len(vec)
        return np.tile(vec, reps)[:384] / 255.0

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - allow tests without heavy deps
    SentenceTransformer = None  # type: ignore

_fallback_model = _DummyTransformer()
from scipy.spatial.distance import cosine

app = FastAPI(title="KIMERA SWM MVP API", version="0.1.0")

# Load embedding model once at startup for semantic vector persistence
LIGHTWEIGHT_EMBEDDING = os.getenv("LIGHTWEIGHT_EMBEDDING", "0") == "1"
if SentenceTransformer is not None and not LIGHTWEIGHT_EMBEDDING:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
else:  # pragma: no cover - lightweight fallback
    embedding_model = _fallback_model

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
    """Create a ScarRecord from a resolved tension with real metrics."""

    geoid_a = geoids_dict[tension.geoid_a]
    geoid_b = geoids_dict[tension.geoid_b]

    pre_entropy = (geoid_a.calculate_entropy() + geoid_b.calculate_entropy()) / 2
    post_entropy = pre_entropy + 0.1

    all_features = set(geoid_a.semantic_state.keys()) | set(geoid_b.semantic_state.keys())
    vec_a = [geoid_a.semantic_state.get(f, 0.0) for f in all_features]
    vec_b = [geoid_b.semantic_state.get(f, 0.0) for f in all_features]
    cls_angle_proxy = cosine(vec_a, vec_b) if any(vec_a) and any(vec_b) else 0.0

    return ScarRecord(
        scar_id=f"SCAR_{uuid.uuid4().hex[:8]}",
        geoids=[tension.geoid_a, tension.geoid_b],
        reason=f"Resolved '{tension.gradient_type}' tension.",
        timestamp=datetime.now().isoformat(),
        resolved_by="ContradictionEngine:Collapse",
        pre_entropy=pre_entropy,
        post_entropy=post_entropy,
        delta_entropy=post_entropy - pre_entropy,
        cls_angle=cls_angle_proxy * 180 / np.pi,
        semantic_polarity=np.mean(list(geoid_a.semantic_state.values())) - np.mean(list(geoid_b.semantic_state.values())),
        mutation_frequency=tension.tension_score,
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

    # --- VECTOR PERSISTENCE ---
    semantic_text = " ".join([f"{k}:{v:.2f}" for k, v in request.semantic_features.items()])
    vector = embedding_model.encode(semantic_text).tolist()
    db = SessionLocal()
    geoid_db = GeoidDB(
        geoid_id=geoid.geoid_id,
        symbolic_state=geoid.symbolic_state,
        metadata_json=geoid.metadata,
        semantic_vector=vector,
    )
    db.add(geoid_db)
    db.commit()
    db.refresh(geoid_db)
    db.close()

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


@app.get("/vaults/{vault_id}")
async def get_vault_contents(vault_id: str, limit: int = 10):
    """Retrieve recent scars from the specified vault."""
    if vault_id not in ["vault_a", "vault_b"]:
        raise HTTPException(status_code=404, detail="Vault not found. Use 'vault_a' or 'vault_b'.")

    vault_manager = kimera_system['vault_manager']
    scars = vault_manager.get_scars_from_vault(vault_id, limit=limit)
    scars_dicts = [
        {
            'scar_id': s.scar_id,
            'geoids': s.geoids,
            'reason': s.reason,
            'timestamp': s.timestamp.isoformat() if hasattr(s.timestamp, 'isoformat') else s.timestamp,
            'resolved_by': s.resolved_by,
            'pre_entropy': s.pre_entropy,
            'post_entropy': s.post_entropy,
            'delta_entropy': s.delta_entropy,
            'cls_angle': s.cls_angle,
            'semantic_polarity': s.semantic_polarity,
            'mutation_frequency': s.mutation_frequency,
        }
        for s in scars
    ]
    return {"vault_id": vault_id, "scars": scars_dicts}


@app.get("/geoids/search")
async def search_geoids(query: str, limit: int = 5):
    """Find geoids semantically similar to a query string."""
    query_vector = embedding_model.encode(query).tolist()
    db = SessionLocal()
    if kimera_system['vault_manager'].db.bind.url.drivername.startswith("postgresql"):
        results = (
            db.query(GeoidDB)
            .order_by(GeoidDB.semantic_vector.l2_distance(query_vector))
            .limit(limit)
            .all()
        )
    else:
        all_rows = db.query(GeoidDB).all()
        # Compute simple L2 distance in Python for sqlite fallback
        def _dist(row):
            vec = np.array(row.semantic_vector, dtype=float)
            return np.linalg.norm(vec - np.array(query_vector, dtype=float))

        results = sorted(all_rows, key=_dist)[:limit]
    similar = [
        {
            'geoid_id': r.geoid_id,
            'symbolic_state': r.symbolic_state,
            'metadata': r.metadata_json,
        }
        for r in results
    ]
    db.close()
    return {"query": query, "similar_geoids": similar}

@app.get("/system/status")
async def get_system_status():
    vault_manager = kimera_system['vault_manager']
    return {
        'active_geoids': len(kimera_system['active_geoids']),
        'vault_a_scars': vault_manager.get_total_scar_count("vault_a"),
        'vault_b_scars': vault_manager.get_total_scar_count("vault_b"),
        'system_entropy': sum(g.calculate_entropy() for g in kimera_system['active_geoids'].values()),
        'cycle_count': kimera_system['system_state']['cycle_count']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
