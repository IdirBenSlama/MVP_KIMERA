from __future__ import annotations
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
from pydantic import BaseModel
import uuid
from datetime import datetime
import os

from ..core.geoid import GeoidState
from ..core.scar import ScarRecord
from ..core.constants import EMBEDDING_DIM
from ..engines.contradiction_engine import ContradictionEngine, TensionGradient
from ..engines.thermodynamics import SemanticThermodynamicsEngine
from ..engines.asm import AxisStabilityMonitor
from ..vault.vault_manager import VaultManager
from ..vault.database import SessionLocal, GeoidDB, ScarDB
from ..engines.background_jobs import start_background_jobs, stop_background_jobs
from ..engines.clip_service import clip_service
import hashlib
import numpy as np

class _DummyTransformer:
    def encode(self, text: str):
        h = hashlib.sha256(text.encode()).digest()
        vec = np.frombuffer(h, dtype=np.uint8).astype(float)
        reps = (EMBEDDING_DIM + len(vec) - 1) // len(vec)
        return np.tile(vec, reps)[:EMBEDDING_DIM] / 255.0

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - allow tests without heavy deps
    SentenceTransformer = None  # type: ignore

_fallback_model = _DummyTransformer()
from scipy.spatial.distance import cosine

app = FastAPI(title="KIMERA SWM MVP API", version="0.1.0")
app.mount("/images", StaticFiles(directory="static/images"), name="images")

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


@app.on_event("startup")
def _startup_background_jobs() -> None:
    start_background_jobs(embedding_model.encode)


@app.on_event("shutdown")
def _shutdown_background_jobs() -> None:
    stop_background_jobs()


def create_scar_from_tension(
    tension: TensionGradient,
    geoids_dict: Dict[str, GeoidState]
) -> tuple[ScarRecord, list[float]]:
    """Create a ScarRecord from a resolved tension with real metrics."""

    geoid_a = geoids_dict[tension.geoid_a]
    geoid_b = geoids_dict[tension.geoid_b]

    pre_entropy = (geoid_a.calculate_entropy() + geoid_b.calculate_entropy()) / 2
    post_entropy = pre_entropy + 0.1

    all_features = set(geoid_a.semantic_state.keys()) | set(geoid_b.semantic_state.keys())
    vec_a = [geoid_a.semantic_state.get(f, 0.0) for f in all_features]
    vec_b = [geoid_b.semantic_state.get(f, 0.0) for f in all_features]
    cls_angle_proxy = cosine(vec_a, vec_b) if any(vec_a) and any(vec_b) else 0.0

    scar = ScarRecord(
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

    geoid_a_summary = " ".join(geoid_a.semantic_state.keys())
    geoid_b_summary = " ".join(geoid_b.semantic_state.keys())
    scar_summary_text = (
        f"Contradiction between '{geoid_a_summary}' and '{geoid_b_summary}'"
    )

    vector = embedding_model.encode(scar_summary_text).tolist()
    return scar, vector


class CreateGeoidRequest(BaseModel):
    semantic_features: Dict[str, float]
    symbolic_content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class ProcessContradictionRequest(BaseModel):
    trigger_geoid_id: str
    search_limit: int = 5
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
        semantic_state_json=geoid.semantic_state,
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


@app.post("/geoids/from_image", response_model=Dict[str, Any])
async def create_geoid_from_image(file: UploadFile = File(...)):
    """Create a Geoid from an uploaded image using CLIP embeddings."""
    image_bytes = await file.read()
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify it's a valid image
        image = Image.open(io.BytesIO(image_bytes))  # Reopen after verify
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    vector = clip_service.get_image_embedding(image)

    geoid_id = f"GEOID_IMG_{uuid.uuid4().hex[:8]}"
    ext = os.path.splitext(file.filename)[1] or ".bin"
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    geoid = GeoidState(
        geoid_id=geoid_id,
        symbolic_state={'type': 'image', 'filename': file.filename},
        metadata={'image_uri': f"/images/{unique_filename}"},
    )

    db = SessionLocal()
    try:
        geoid_db_entry = GeoidDB(
            geoid_id=geoid.geoid_id,
            symbolic_state=geoid.symbolic_state,
            metadata_json=geoid.metadata,
            semantic_state_json={},
            semantic_vector=vector.tolist(),
        )
        db.add(geoid_db_entry)
        db.commit()
        db.refresh(geoid_db_entry)

        os.makedirs("static/images", exist_ok=True)
        with open(f"static/images/{unique_filename}", "wb") as buffer:
            buffer.write(image_bytes)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {
        "message": "Geoid created from image",
        "geoid_id": geoid_id,
        "geoid_db": geoid_db_entry.geoid_id,
    }


@app.post("/process/contradictions", response_model=Dict[str, Any])
async def process_contradictions(request: ProcessContradictionRequest):
    """Autonomously discover contradictions for a trigger Geoid."""

    db = SessionLocal()

    # Use Axis Stability Monitor for global metrics
    asm = AxisStabilityMonitor(db)
    stability_metrics = asm.get_stability_metrics()

    trigger_db = db.query(GeoidDB).filter(GeoidDB.geoid_id == request.trigger_geoid_id).first()
    if not trigger_db:
        db.close()
        raise HTTPException(status_code=404, detail="Trigger Geoid not found")

    trigger_vector = trigger_db.semantic_vector

    if kimera_system['vault_manager'].db.bind.url.drivername.startswith("postgresql"):
        similar_db = (
            db.query(GeoidDB)
            .filter(GeoidDB.geoid_id != request.trigger_geoid_id)
            .order_by(GeoidDB.semantic_vector.l2_distance(trigger_vector))
            .limit(request.search_limit)
            .all()
        )
    else:
        similar_db = (
            db.query(GeoidDB)
            .filter(GeoidDB.geoid_id != request.trigger_geoid_id)
            .limit(request.search_limit)
            .all()
        )
    db.close()

    def to_state(row: GeoidDB) -> GeoidState:
        return GeoidState(
            geoid_id=row.geoid_id,
            semantic_state=row.semantic_state_json or {},
            symbolic_state=row.symbolic_state or {},
            metadata=row.metadata_json or {},
        )

    target_geoids: List[GeoidState] = []
    target_geoids.append(to_state(trigger_db))
    target_geoids.extend([to_state(r) for r in similar_db])
    geoids_dict = {g.geoid_id: g for g in target_geoids}

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
            tension, geoids_dict
        )

        metrics = stability_metrics.copy()

        # --- Scar Resonance: consult similar scars ---
        current_summary = f"Tension between {tension.geoid_a} and {tension.geoid_b}"
        query_vector = embedding_model.encode(current_summary).tolist()
        db = SessionLocal()
        if kimera_system['vault_manager'].db.bind.url.drivername.startswith("postgresql"):
            past_scars = (
                db.query(ScarDB)
                .order_by(ScarDB.scar_vector.l2_distance(query_vector))
                .limit(3)
                .all()
            )
        else:
            past_scars = db.query(ScarDB).limit(3).all()
        db.close()

        if past_scars:
            avg_entropy = sum(s.delta_entropy for s in past_scars) / len(past_scars)
            if avg_entropy > 0.2:
                metrics['vault_resonance'] += 0.2

        decision = contradiction_engine.decide_collapse_or_surge(
            pulse_strength, metrics
        )

        scar_created = False
        if decision == 'collapse':
            scar, vector = create_scar_from_tension(tension, geoids_dict)
            kimera_system['vault_manager'].insert_scar(scar, vector)
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
        results = db.query(GeoidDB).limit(limit).all()
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


@app.get("/scars/search")
async def search_scars(query: str, limit: int = 3):
    """Find scars semantically similar to a query describing a contradiction."""
    query_vector = embedding_model.encode(query).tolist()
    db = SessionLocal()
    if kimera_system['vault_manager'].db.bind.url.drivername.startswith("postgresql"):
        results = (
            db.query(ScarDB)
            .order_by(ScarDB.scar_vector.l2_distance(query_vector))
            .limit(limit)
            .all()
        )
    else:
        results = db.query(ScarDB).limit(limit).all()
    now = datetime.utcnow()
    similar = []
    for r in results:
        r.last_accessed = now
        r.weight += 1.0
        similar.append(
            {
                'scar_id': r.scar_id,
                'reason': r.reason,
                'delta_entropy': r.delta_entropy,
            }
        )
    db.commit()
    db.close()
    return {"query": query, "similar_scars": similar}

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


@app.get("/system/stability")
async def get_system_stability():
    """Return global stability metrics from the Axis Stability Monitor."""
    db = SessionLocal()
    asm = AxisStabilityMonitor(db)
    metrics = asm.get_stability_metrics()
    db.close()
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
