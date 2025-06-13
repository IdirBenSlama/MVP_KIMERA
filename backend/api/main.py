from __future__ import annotations
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from pydantic import BaseModel
import uuid
from datetime import datetime
import os

from ..core.geoid import GeoidState
from ..core.scar import ScarRecord
from ..core.models import LinguisticGeoid
from ..core.embedding_utils import encode_text, extract_semantic_features, initialize_embedding_model, get_embedding_model
from ..engines.contradiction_engine import ContradictionEngine, TensionGradient
from ..engines.thermodynamics import SemanticThermodynamicsEngine
from ..engines.asm import AxisStabilityMonitor
from ..engines.spde import SPDE
from ..engines.kccl import KimeraCognitiveCycle
from ..engines.meta_insight import MetaInsightEngine
from ..vault.vault_manager import VaultManager
from ..vault.database import SessionLocal, GeoidDB, ScarDB, engine
from ..engines.background_jobs import start_background_jobs, stop_background_jobs
from ..engines.clip_service import clip_service
from ..linguistic.echoform import parse_echoform
from .middleware import icw_middleware
from .monitoring_routes import router as monitoring_router
import numpy as np
from scipy.spatial.distance import cosine

app = FastAPI(title="KIMERA SWM MVP API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="static/images"), name="images")
app.middleware("http")(icw_middleware)

# Include monitoring routes
app.include_router(monitoring_router)

kimera_system = {
    'contradiction_engine': ContradictionEngine(tension_threshold=0.5),
    'thermodynamics_engine': SemanticThermodynamicsEngine(),
    'vault_manager': VaultManager(),
    'spde_engine': SPDE(),
    'cognitive_cycle': KimeraCognitiveCycle(),
    'meta_insight_engine': MetaInsightEngine(),
    'active_geoids': {},
    'system_state': {'cycle_count': 0},
    'recent_insights': [],  # rolling list to feed MetaInsightEngine
    'embedding_model': None
}


@app.on_event("startup")
def startup_event():
    """Initializes the embedding model and background jobs on startup."""
    kimera_system['embedding_model'] = initialize_embedding_model()
    if os.getenv("ENABLE_JOBS", "1") != "0":
        start_background_jobs(encode_text)


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

    embedding_model = get_embedding_model()
    vector = embedding_model.encode(scar_summary_text).tolist()
    return scar, vector


class CreateGeoidRequest(BaseModel):
    semantic_features: Dict[str, float] | None = None
    symbolic_content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    echoform_text: str | None = None


class ProcessContradictionRequest(BaseModel):
    trigger_geoid_id: str
    search_limit: int = 5
    force_collapse: bool = False  # Optional flag for future use


@app.post("/geoids")
async def create_geoid(request: CreateGeoidRequest):
    geoid_id = f"GEOID_{uuid.uuid4().hex[:8]}"
    
    semantic_state = {}
    embedding_vector = []
    symbolic_state = dict(request.symbolic_content)

    if request.echoform_text:
        # Path 1: Geoid created from raw text
        text = request.echoform_text
        try:
            symbolic_state["echoform"] = parse_echoform(text)
            semantic_state = extract_semantic_features(text)
            embedding_model = get_embedding_model()
            embedding_vector = embedding_model.encode(text).tolist()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid EchoForm: {exc}")
    
    elif request.semantic_features:
        # Path 2: Geoid created from pre-defined features
        try:
            for v in request.semantic_features.values():
                if not isinstance(v, (int, float)):
                    raise ValueError("Semantic features must be numeric")
            semantic_state = request.semantic_features
            # Create a text representation for embedding
            semantic_text = " ".join([f"{k}:{v:.2f}" for k, v in semantic_state.items()])
            embedding_model = get_embedding_model()
            embedding_vector = embedding_model.encode(semantic_text).tolist()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid semantic features: {exc}")
    
    else:
        raise HTTPException(status_code=400, detail="Either 'echoform_text' or 'semantic_features' must be provided.")

    geoid = GeoidState(
        geoid_id=geoid_id,
        semantic_state=semantic_state,
        symbolic_state=symbolic_state,
        embedding_vector=embedding_vector,
        metadata=request.metadata,
    )

    # --- VECTOR PERSISTENCE ---
    with SessionLocal() as db:
        geoid_db = GeoidDB(
            geoid_id=geoid.geoid_id,
            symbolic_state=geoid.symbolic_state,
            metadata_json=geoid.metadata,
            semantic_state_json=geoid.semantic_state,
            semantic_vector=geoid.embedding_vector,
        )
        db.add(geoid_db)
        db.commit()
        db.refresh(geoid_db)

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

    with SessionLocal() as db:
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

    return {
        "message": "Geoid created from image",
        "geoid_id": geoid_id,
        "geoid_db": geoid_db_entry.geoid_id,
    }


@app.post("/process/contradictions", response_model=Dict[str, Any])
async def process_contradictions(body: ProcessContradictionRequest, request: Request):
    """Autonomously discover contradictions for a trigger Geoid."""

    with SessionLocal() as db:

        # Use Axis Stability Monitor for global metrics
        asm = AxisStabilityMonitor(db)
        stability_metrics = asm.get_stability_metrics()
        profile = getattr(request.state, "kimera_profile", {})

        trigger_db = db.query(GeoidDB).filter(GeoidDB.geoid_id == body.trigger_geoid_id).first()
        if not trigger_db:
            raise HTTPException(status_code=404, detail="Trigger Geoid not found")

        trigger_vector = trigger_db.semantic_vector

        if engine.url.drivername.startswith("postgresql"):
            similar_db = (
                db.query(GeoidDB)
                .filter(GeoidDB.geoid_id != body.trigger_geoid_id)
                .order_by(GeoidDB.semantic_vector.l2_distance(trigger_vector))
                .limit(body.search_limit)
                .all()
            )
        else:
            similar_db = (
                db.query(GeoidDB)
                .filter(GeoidDB.geoid_id != body.trigger_geoid_id)
                .limit(body.search_limit)
                .all()
            )

    def to_state(row: GeoidDB) -> GeoidState:
        return GeoidState(
            geoid_id=row.geoid_id,
            semantic_state=row.semantic_state_json or {},
            symbolic_state=row.symbolic_state or {},
            embedding_vector=row.semantic_vector or [],
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
        query_vector = encode_text(current_summary)
        with SessionLocal() as db:
            if engine.url.drivername.startswith("postgresql"):
                past_scars = (
                    db.query(ScarDB)
                    .order_by(ScarDB.scar_vector.l2_distance(query_vector))
                    .limit(3)
                    .all()
                )
            else:
                past_scars = db.query(ScarDB).limit(3).all()

        if past_scars:
            avg_entropy = sum(s.delta_entropy for s in past_scars) / len(past_scars)
            if avg_entropy > 0.2:
                metrics['vault_resonance'] += 0.2

        decision = contradiction_engine.decide_collapse_or_surge(
            pulse_strength, metrics, profile
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


@app.post("/vaults/rebalance")
async def rebalance_vaults(by_weight: bool = False):
    """Manually trigger vault rebalancing."""
    vault_manager = kimera_system['vault_manager']
    moved = vault_manager.rebalance_vaults(by_weight=by_weight)
    return {"moved_scars": moved}


@app.get("/geoids/{geoid_id}/speak", response_model=LinguisticGeoid)
async def speak_geoid(geoid_id: str):
    with SessionLocal() as db:
        geoid_db = db.query(GeoidDB).filter(GeoidDB.geoid_id == geoid_id).first()
        if not geoid_db:
            raise HTTPException(status_code=404, detail="Geoid not found")

        asm = AxisStabilityMonitor(db)
        stability = asm.get_stability_metrics()["semantic_cohesion"]
        if stability < 0.7:
            raise HTTPException(status_code=409, detail="Concept is currently unstable.")

        supporting_scars = (
            db.query(ScarDB)
            .filter(ScarDB.geoids.contains([geoid_id]))
            .limit(3)
            .all()
        )

    primary_statement = (
        f"Based on available data, the concept '{geoid_id}' represents: {geoid_db.symbolic_state}"
    )

    response = LinguisticGeoid(
        primary_statement=primary_statement,
        confidence_score=stability,
        source_geoid_id=geoid_id,
        supporting_scars=[scar.__dict__ for scar in supporting_scars],
        explanation_lineage=f"This concept is supported by {len(supporting_scars)} resolved contradictions."
    )
    return response


@app.get("/geoids/search")
async def search_geoids(query: str, limit: int = 5):
    """Find geoids semantically similar to a query string."""
    query_vector = encode_text(query)
    with SessionLocal() as db:
        if engine.url.drivername.startswith("postgresql"):
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
    return {"query": query, "similar_geoids": similar}


@app.get("/scars/search")
async def search_scars(query: str, limit: int = 3):
    """Find scars semantically similar to a query describing a contradiction."""
    query_vector = encode_text(query)
    with SessionLocal() as db:
        if engine.url.drivername.startswith("postgresql"):
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


@app.post("/system/cycle")
async def trigger_cycle():
    """Run one cognitive cycle."""
    status = kimera_system['cognitive_cycle'].run_cycle(kimera_system)
    cycle_stats = kimera_system['system_state'].get('last_cycle', {})
    return {
        'status': status,
        'cycle_count': kimera_system['system_state']['cycle_count'],
        'contradictions_detected': cycle_stats.get('contradictions_detected', 0),
        'scars_created': cycle_stats.get('scars_created', 0),
        'entropy_before_diffusion': cycle_stats.get('entropy_before_diffusion', 0.0),
        'entropy_after_diffusion': cycle_stats.get('entropy_after_diffusion', 0.0),
        'entropy_delta': cycle_stats.get('entropy_delta', 0.0),
    }


@app.get("/system/stability")
async def get_system_stability():
    """Return global stability metrics from the Axis Stability Monitor."""
    with SessionLocal() as db:
        asm = AxisStabilityMonitor(db)
        metrics = asm.get_stability_metrics()
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

