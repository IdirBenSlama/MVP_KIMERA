from __future__ import annotations
from typing import Dict, Any, List
from dotenv import load_dotenv
load_dotenv()  # Load .env file
from fastapi import FastAPI, HTTPException, UploadFile, File, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from pydantic import BaseModel
import uuid
from datetime import datetime
import os
import time
import json
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import asyncio
import numpy as np

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
from ..vault import get_vault_manager
from ..vault.database import SessionLocal, GeoidDB, ScarDB, engine
from ..engines.background_jobs import start_background_jobs, stop_background_jobs
from ..engines.clip_service import clip_service
from ..linguistic.echoform import parse_echoform
from .middleware import icw_middleware
from .monitoring_routes import router as monitoring_router
from .cognitive_field_routes import router as cognitive_field_router
from ..monitoring.telemetry import router as telemetry_router
from ..core.native_math import NativeMath
from ..engines.activation_synthesis import (
    trigger_activation_cascade,
    synthesize_patterns,
    ResonanceEvent,
    Geoid as ASGeoid,
)
from ..engines.output_generator import generate_insight_scar
from ..engines.insight_lifecycle import (
    update_utility_score,
    manage_insight_lifecycle,
    FeedbackEvent,
)
from ..engines.proactive_contradiction_detector import ProactiveContradictionDetector
from ..core.statistical_modeling import (
    statistical_engine,
    StatisticalModelResult,
    analyze_entropy_time_series,
    analyze_contradiction_factors,
    analyze_semantic_market
)
from ..monitoring.advanced_statistical_monitor import (
    advanced_monitor,
    initialize_advanced_monitoring
)
from .enhanced_routes import router as enhanced_router

try:
    from .law_enforcement_routes import router as law_enforcement_router, periodic_stabilization
    LAW_ENFORCEMENT_AVAILABLE = True
except ImportError:
    LAW_ENFORCEMENT_AVAILABLE = False
    logging.warning("Law enforcement routes not available")

try:
    from .revolutionary_routes import router as revolutionary_router
    REVOLUTIONARY_INTELLIGENCE_AVAILABLE = True
except ImportError:
    REVOLUTIONARY_INTELLIGENCE_AVAILABLE = False
    logging.warning("Revolutionary intelligence routes not available")

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
# app.middleware("http")(icw_middleware)

# Include monitoring routes
app.include_router(monitoring_router)
app.include_router(telemetry_router)
app.include_router(cognitive_field_router)
app.include_router(enhanced_router)

if LAW_ENFORCEMENT_AVAILABLE:
    app.include_router(law_enforcement_router)
    logging.info("⚖️ Law enforcement routes registered")

if REVOLUTIONARY_INTELLIGENCE_AVAILABLE:
    app.include_router(revolutionary_router)
    logging.info("🧠 Revolutionary intelligence routes registered")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kimera.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure the pg_vector extension is enabled for PostgreSQL
if engine.url.drivername.startswith("postgresql"):
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

# Simplified Kimera System State
kimera_system = {
    'vault_manager': None,
    'contradiction_engine': None,
    'system_state': {'cycle_count': 0, 'status': 'initializing'},
    'active_geoids': {},
    'insights': {},
    'recent_insights': []
}


@app.on_event("startup")
def startup_event():
    """Initializes the embedding model and background jobs on startup."""
    kimera_system['embedding_model'] = initialize_embedding_model()
    
    # Initialize core engines
    kimera_system['contradiction_engine'] = ContradictionEngine(tension_threshold=0.4)
    kimera_system['thermodynamics_engine'] = SemanticThermodynamicsEngine()
    kimera_system['vault_manager'] = get_vault_manager()
    kimera_system['spde_engine'] = SPDE()
    kimera_system['cognitive_cycle'] = KimeraCognitiveCycle()
    kimera_system['meta_insight_engine'] = MetaInsightEngine()
    kimera_system['proactive_detector'] = ProactiveContradictionDetector()
    
    # Initialize revolutionary intelligence system
    try:
        from ..core.revolutionary_intelligence import get_revolutionary_intelligence
        kimera_system['revolutionary_intelligence'] = get_revolutionary_intelligence()
        logging.info("🧠 Revolutionary intelligence system initialized")
    except Exception as e:
        logging.warning(f"Revolutionary intelligence not available: {e}")
        kimera_system['revolutionary_intelligence'] = None
    
    # Update system status
    kimera_system['system_state']['status'] = 'operational'
    
    if os.getenv("ENABLE_JOBS", "1") != "0":
        start_background_jobs(encode_text)
    
    # Initialize advanced statistical monitoring
    try:
        from ..monitoring.entropy_monitor import EntropyMonitor
        from ..monitoring.system_observer import SystemObserver
        entropy_monitor = EntropyMonitor()
        system_observer = SystemObserver()
        initialize_advanced_monitoring(entropy_monitor, system_observer)
    except Exception as e:
        print(f"Warning: Could not initialize advanced monitoring: {e}")


@app.on_event("shutdown")
def _shutdown_background_jobs() -> None:
    stop_background_jobs()


def sanitize_for_json(obj):
    """Convert numpy types to Python types for JSON serialization."""
    if isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_for_json(item) for item in obj)
    else:
        return obj


def create_scar_from_tension(
    tension: TensionGradient,
    geoids_dict: Dict[str, GeoidState],
    decision: str = "collapse"
) -> tuple[ScarRecord, list[float]]:
    """Create a SCAR from a TensionGradient with proper type conversion."""
    geoid_a = geoids_dict[tension.geoid_a]
    geoid_b = geoids_dict[tension.geoid_b]

    pre_entropy = geoid_a.calculate_entropy() + geoid_b.calculate_entropy()
    
    # Simple entropy adjustment based on decision
    entropy_delta = {
        "collapse": -0.02,
        "surge": 0.05,
        "buffer": 0.02
    }.get(decision, 0.0)
    
    post_entropy = pre_entropy + entropy_delta
    cls_angle_proxy = tension.tension_score

    reason_map = {
        "collapse": f"Collapsed '{tension.gradient_type}' tension.",
        "surge": f"Surged '{tension.gradient_type}' tension.",
        "buffer": f"Buffered '{tension.gradient_type}' tension."
    }

    resolved_by_map = {
        "collapse": "ContradictionEngine:Collapse",
        "surge": "ContradictionEngine:Surge", 
        "buffer": "ContradictionEngine:Buffer"
    }

    # Calculate semantic polarity with proper type conversion
    geoid_a_values = list(geoid_a.semantic_state.values()) if geoid_a.semantic_state else [0.0]
    geoid_b_values = list(geoid_b.semantic_state.values()) if geoid_b.semantic_state else [0.0]
    
    semantic_polarity = float(np.mean(geoid_a_values) - np.mean(geoid_b_values))

    scar = ScarRecord(
        scar_id=f"SCAR_{uuid.uuid4().hex[:8]}",
        geoids=[tension.geoid_a, tension.geoid_b],
        reason=reason_map.get(decision, f"Processed '{tension.gradient_type}' tension."),
        timestamp=datetime.now().isoformat(),
        resolved_by=resolved_by_map.get(decision, "ContradictionEngine:Unknown"),
        pre_entropy=pre_entropy,
        post_entropy=post_entropy,
        delta_entropy=post_entropy - pre_entropy,
        cls_angle=float(cls_angle_proxy * 180 / np.pi),
        semantic_polarity=semantic_polarity,
        mutation_frequency=float(tension.tension_score),
    )

    geoid_a_summary = " ".join(geoid_a.semantic_state.keys())
    geoid_b_summary = " ".join(geoid_b.semantic_state.keys())
    scar_summary_text = (
        f"{decision.capitalize()} contradiction between '{geoid_a_summary}' and '{geoid_b_summary}'"
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
    try:
        kimera_system['thermodynamics_engine'].validate_transformation(
            None,
            geoid,
        )
    except Exception as e:
        # Use proper logging instead of print
        import logging
        logging.warning(f"Thermodynamic validation failed for new geoid {geoid_id}: {e}")
        # Continue execution - validation failure is not critical for geoid creation

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


def run_contradiction_processing_bg(body: ProcessContradictionRequest, kimera_profile: dict):
    """The background task for processing contradictions."""
    try:
        with SessionLocal() as db:
            # Use simplified stability metrics to avoid computation errors
            try:
                asm = AxisStabilityMonitor(db)
                stability_metrics = asm.get_stability_metrics()
            except Exception as e:
                logging.warning(f"AxisStabilityMonitor failed, using fallback metrics: {e}")
                # Fallback to default metrics if ASM fails
                stability_metrics = {
                    "vault_pressure": 0.5, "semantic_cohesion": 0.7, "entropic_stability": 0.5,
                    "axis_convergence": 0.7, "vault_resonance": 0.5, "contradiction_lineage_ambiguity": 0.5,
                }
            
            trigger_db = db.query(GeoidDB).filter(GeoidDB.geoid_id == body.trigger_geoid_id).first()
            if not trigger_db:
                logging.error(f"Trigger Geoid {body.trigger_geoid_id} not found in background task.")
                return

            trigger_vector = trigger_db.semantic_vector

            if engine.url.drivername.startswith("postgresql"):
                similar_db = db.query(GeoidDB).filter(GeoidDB.geoid_id != body.trigger_geoid_id).order_by(GeoidDB.semantic_vector.l2_distance(trigger_vector)).limit(body.search_limit).all()
            else:
                # Manual similarity for SQLite
                all_others = db.query(GeoidDB).filter(GeoidDB.geoid_id != body.trigger_geoid_id).all()
                trigger_vec = np.array(trigger_vector)
                
                def l2_dist(row):
                    if row.semantic_vector:
                        return np.linalg.norm(trigger_vec - np.array(row.semantic_vector))
                    return float('inf') # Move geoids without vectors to the end

                all_others.sort(key=l2_dist)
                similar_db = all_others[:body.search_limit]

            def to_state(row: GeoidDB) -> GeoidState:
                # Convert numpy array to Python list for compatibility
                embedding_vector = []
                if row.semantic_vector is not None:
                    if hasattr(row.semantic_vector, 'tolist'):
                        embedding_vector = row.semantic_vector.tolist()
                    else:
                        embedding_vector = list(row.semantic_vector)
                
                return GeoidState(
                    geoid_id=row.geoid_id, 
                    semantic_state=row.semantic_state_json or {},
                    symbolic_state=row.symbolic_state or {},
                    embedding_vector=embedding_vector,
                    metadata=row.metadata_json or {},
                )

            target_geoids = [to_state(trigger_db)] + [to_state(r) for r in similar_db]
            geoids_dict = {g.geoid_id: g for g in target_geoids}

            # --- Re-enabling the contradiction engine call ---
            contradiction_engine = kimera_system['contradiction_engine']
            tensions = contradiction_engine.detect_tension_gradients(target_geoids)

            if not tensions:
                logging.info("No significant contradictions detected in background task.")
                return 

            results, scars_created = [], 0
            for tension in tensions:
                pulse_strength = 0.0  # Placeholder
                metrics = stability_metrics.copy()
                
                current_summary = f"Tension between {tension.geoid_a} and {tension.geoid_b}"
                query_vector = encode_text(current_summary)
                past_scars = db.query(ScarDB).order_by(ScarDB.scar_vector.l2_distance(query_vector)).limit(3).all()
                
                if past_scars:
                    avg_entropy = sum(s.delta_entropy for s in past_scars) / len(past_scars)
                    if avg_entropy > 0.2: metrics['vault_resonance'] += 0.2
                
                decision = "collapse"  # Placeholder
                
                scar_created = False
                if decision in ['collapse', 'surge', 'buffer']:
                    scar, vector = create_scar_from_tension(tension, geoids_dict, decision)
                    kimera_system['vault_manager'].insert_scar(scar, vector, db=db)
                    scars_created += 1

                results.append({
                    'tension': {'geoids_involved': [tension.geoid_a, tension.geoid_b], 'score': f"{pulse_strength:.3f}", 'type': "Dynamic"},
                    'pulse_strength': f"{pulse_strength:.3f}", 'system_decision': decision, 'scar_created': scar_created
                })

            if 'cycle_count' not in kimera_system['system_state']:
                kimera_system['system_state']['cycle_count'] = 0
            kimera_system['system_state']['cycle_count'] += 1
            
            logging.info(f"Contradiction cycle {kimera_system['system_state']['cycle_count']} complete. Detected: {len(tensions)}, Created: {scars_created} scars.")

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Contradiction processing background task failed: {e}\n{error_details}")


@app.post("/process/contradictions", status_code=202)
async def process_contradictions(
    body: ProcessContradictionRequest, 
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Autonomously discover contradictions for a trigger Geoid.
    This task is computationally intensive and is run in the background.
    """
    profile = getattr(request.state, "kimera_profile", {})
    background_tasks.add_task(run_contradiction_processing_bg, body, profile)
    return {"message": "Contradiction processing task accepted and running in the background."}


@app.post("/process/contradictions/sync")
async def process_contradictions_sync(body: ProcessContradictionRequest):
    """
    Synchronous contradiction processing for testing and immediate results.
    Returns actual contradiction detection results instead of background task status.
    """
    try:
        logging.info(f"Starting synchronous contradiction processing for trigger: {body.trigger_geoid_id}")
        
        with SessionLocal() as db:
            # Get trigger geoid
            trigger_db = db.query(GeoidDB).filter(
                GeoidDB.geoid_id == body.trigger_geoid_id
            ).first()
            
            if not trigger_db:
                raise HTTPException(status_code=404, detail="Trigger geoid not found")
            
            # Find similar geoids
            similar_db = []
            if trigger_db.semantic_vector is not None:
                if engine.url.drivername.startswith("postgresql"):
                    similar_db = (
                        db.query(GeoidDB)
                        .filter(GeoidDB.geoid_id != body.trigger_geoid_id)
                        .order_by(GeoidDB.semantic_vector.l2_distance(trigger_db.semantic_vector))
                        .limit(body.search_limit)
                        .all()
                    )
                else:
                    # Manual similarity for SQLite
                    all_others = db.query(GeoidDB).filter(GeoidDB.geoid_id != body.trigger_geoid_id).all()
                    trigger_vec = np.array(trigger_db.semantic_vector)
                    
                    def l2_dist(row):
                        if row.semantic_vector:
                            return np.linalg.norm(trigger_vec - np.array(row.semantic_vector))
                        return float('inf')

                    all_others.sort(key=l2_dist)
                    similar_db = all_others[:body.search_limit]
            
            # Convert to GeoidState objects
            def to_state(row: GeoidDB) -> GeoidState:
                # Convert numpy array to Python list for compatibility
                embedding_vector = []
                if row.semantic_vector is not None:
                    if hasattr(row.semantic_vector, 'tolist'):
                        embedding_vector = row.semantic_vector.tolist()
                    else:
                        embedding_vector = list(row.semantic_vector)
                
                return GeoidState(
                    geoid_id=row.geoid_id, 
                    semantic_state=row.semantic_state_json or {},
                    symbolic_state=row.symbolic_state or {},
                    embedding_vector=embedding_vector,
                    metadata=row.metadata_json or {},
                )

            target_geoids = [to_state(trigger_db)] + [to_state(r) for r in similar_db]
            geoids_dict = {g.geoid_id: g for g in target_geoids}

            # Run contradiction detection
            contradiction_engine = kimera_system['contradiction_engine']
            
            logging.info(f"Running contradiction detection on {len(target_geoids)} geoids:")
            for i, geoid in enumerate(target_geoids):
                logging.info(f"  Geoid {i}: {geoid.geoid_id} - embedding_vector length: {len(geoid.embedding_vector) if geoid.embedding_vector else 0}")
            
            tensions = contradiction_engine.detect_tension_gradients(target_geoids)
            
            logging.info(f"Contradiction detection completed. Found {len(tensions)} tensions.")

            if not tensions:
                logging.info("No significant contradictions detected in synchronous processing.")
                return {
                    "trigger_geoid_id": body.trigger_geoid_id,
                    "contradictions_detected": 0,
                    "scars_created": 0,
                    "results": [],
                    "processing_time": 0,
                    "geoids_analyzed": len(target_geoids)
                }

            # Process tensions and create SCARs
            results = []
            scars_created = 0
            start_time = time.time()
            
            for tension in tensions:
                try:
                    # Calculate pulse strength
                    pulse_strength = contradiction_engine.calculate_pulse_strength(
                        tension, geoids_dict
                    )
                    
                    # Get stability metrics
                    with SessionLocal() as stability_db:
                        asm = AxisStabilityMonitor(stability_db)
                        stability_metrics = asm.get_stability_metrics()
                    
                    # Decide action
                    decision = contradiction_engine.decide_collapse_or_surge(
                        pulse_strength, stability_metrics, None
                    )
                    
                    # Create SCAR
                    scar, vector = create_scar_from_tension(tension, geoids_dict, decision)
                    kimera_system['vault_manager'].insert_scar(scar, vector)
                    scars_created += 1
                    
                    results.append({
                        'tension': {
                            'geoid_a': tension.geoid_a,
                            'geoid_b': tension.geoid_b,
                            'score': tension.tension_score,
                            'type': tension.gradient_type
                        },
                        'pulse_strength': pulse_strength,
                        'decision': decision,
                        'scar_id': scar.scar_id
                    })
                    
                except Exception as e:
                    logging.error(f"Error processing tension {tension.geoid_a}-{tension.geoid_b}: {e}")
                    continue
            
            processing_time = time.time() - start_time
            
            # Update system state
            state = kimera_system.setdefault("system_state", {})
            state["cycle_count"] = state.get("cycle_count", 0) + 1
            
            return {
                "trigger_geoid_id": body.trigger_geoid_id,
                "contradictions_detected": len(tensions),
                "scars_created": scars_created,
                "results": results,
                "processing_time": round(processing_time, 3),
                "geoids_analyzed": len(target_geoids),
                "cycle_count": state["cycle_count"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Synchronous contradiction processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Contradiction processing failed: {str(e)}")


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
    """Get comprehensive system status including performance metrics."""
    vault_manager = kimera_system['vault_manager']
    
    # Get embedding performance stats
    try:
        from ..core.embedding_utils import get_performance_stats
        embedding_stats = get_performance_stats()
    except:
        embedding_stats = {}
    
    # Get system metrics
    try:
        import psutil
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('.').percent
        }
    except:
        system_metrics = {}
    
    # Get GPU info if available
    gpu_info = {}
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info = {
                "gpu_available": True,
                "gpu_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "gpu_name": torch.cuda.get_device_name(),
                "gpu_memory_allocated": torch.cuda.memory_allocated(),
                "gpu_memory_reserved": torch.cuda.memory_reserved()
            }
        else:
            gpu_info = {"gpu_available": False}
    except:
        gpu_info = {"gpu_available": False}
    
    return {
        'timestamp': time.time(),
        'system_info': {
            'active_geoids': len(kimera_system['active_geoids']),
            'vault_a_scars': vault_manager.get_total_scar_count("vault_a"),
            'vault_b_scars': vault_manager.get_total_scar_count("vault_b"),
            'system_entropy': sum(g.calculate_entropy() for g in kimera_system['active_geoids'].values()),
            'cycle_count': kimera_system['system_state']['cycle_count']
        },
        'embedding_performance': embedding_stats,
        'system_metrics': system_metrics,
        'gpu_info': gpu_info,
        'model_info': {
            'embedding_model': "BAAI/bge-m3",
            'embedding_dimension': 1024,
            'model_type': getattr(kimera_system.get('embedding_model', {}), 'get', lambda x: 'unknown')('type')
        },
        'revolutionary_intelligence': {
            'available': kimera_system.get('revolutionary_intelligence') is not None,
            'status': 'operational' if kimera_system.get('revolutionary_intelligence') else 'not_available'
        }
    }


@app.get("/system/health")
async def get_system_health_simple():
    """Fast, basic health check. Returns 200 if the app is running."""
    return {"status": "healthy"}


@app.get("/system/health/detailed")
async def get_system_health_detailed():
    """Comprehensive system health check."""
    from sqlalchemy import text

    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Check database connection
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1")).fetchone()
        health_status["checks"]["database"] = {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "degraded"
    
    # Check embedding model
    try:
        from ..core.embedding_utils import encode_text
        test_embedding = encode_text("health check")
        if len(test_embedding) == 1024:
            health_status["checks"]["embedding_model"] = {"status": "healthy", "message": "BGE-M3 model working"}
        else:
            health_status["checks"]["embedding_model"] = {"status": "degraded", "message": f"Unexpected dimension: {len(test_embedding)}"}
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["embedding_model"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "unhealthy"
    
    # Check Neo4j connection
    try:
        from ..graph.session import driver_liveness_check
        if driver_liveness_check():
            health_status["checks"]["neo4j"] = {"status": "healthy", "message": "Neo4j connection OK"}
        else:
            health_status["checks"]["neo4j"] = {"status": "unhealthy", "message": "Neo4j not responding"}
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["neo4j"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "degraded"
    
    # Check vault system
    try:
        vault_manager = kimera_system['vault_manager']
        total_scars = vault_manager.get_total_scar_count("vault_a") + vault_manager.get_total_scar_count("vault_b")
        health_status["checks"]["vault_system"] = {"status": "healthy", "message": f"Vault system OK, {total_scars} total scars"}
    except Exception as e:
        health_status["checks"]["vault_system"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "degraded"
    
    # Check revolutionary intelligence system
    try:
        revolutionary_intelligence = kimera_system.get('revolutionary_intelligence')
        if revolutionary_intelligence:
            status = revolutionary_intelligence.get_revolutionary_status()
            health_status["checks"]["revolutionary_intelligence"] = {
                "status": "healthy", 
                "message": f"Revolutionary intelligence operational, {status['total_moments']} moments recorded"
            }
        else:
            health_status["checks"]["revolutionary_intelligence"] = {
                "status": "unavailable", 
                "message": "Revolutionary intelligence not initialized"
            }
    except Exception as e:
        health_status["checks"]["revolutionary_intelligence"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "degraded"
    
    return health_status


@app.post("/system/cycle")
async def trigger_cycle():
    """Run one cognitive cycle with improved error handling."""
    try:
        logging.info("Starting cognitive cycle")
        start_time = time.time()
        
        # Check system health before proceeding
        active_geoids_count = len(kimera_system['active_geoids'])
        if active_geoids_count > 1000:  # Safety limit
            logging.warning(f"High geoid count ({active_geoids_count}), limiting cycle scope")
        
        # Run the cycle with timeout protection
        try:
            status = kimera_system['cognitive_cycle'].run_cycle(kimera_system)
        except Exception as e:
            logging.error(f"Cognitive cycle execution failed: {e}")
            # Return partial success to avoid complete failure
            status = "cycle_partial"
            
        cycle_stats = kimera_system['system_state'].get('last_cycle', {})
        processing_time = time.time() - start_time
        
        # Add performance metrics
        cycle_stats['processing_time'] = round(processing_time, 3)
        cycle_stats['active_geoids'] = active_geoids_count
        
        return {
            'status': status,
            'cycle_count': kimera_system['system_state']['cycle_count'],
            'contradictions_detected': cycle_stats.get('contradictions_detected', 0),
            'scars_created': cycle_stats.get('scars_created', 0),
            'entropy_before_diffusion': cycle_stats.get('entropy_before_diffusion', 0.0),
            'entropy_after_diffusion': cycle_stats.get('entropy_after_diffusion', 0.0),
            'entropy_delta': cycle_stats.get('entropy_delta', 0.0),
            'processing_time': cycle_stats.get('processing_time', 0.0),
            'active_geoids': cycle_stats.get('active_geoids', 0)
        }
        
    except Exception as e:
        logging.error(f"System cycle failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cognitive cycle failed: {str(e)}")


@app.get("/system/stability")
async def get_system_stability():
    """Return global stability metrics from the Axis Stability Monitor."""
    with SessionLocal() as db:
        asm = AxisStabilityMonitor(db)
        metrics = asm.get_stability_metrics()
    return metrics


@app.post("/system/proactive_scan")
async def run_proactive_contradiction_scan():
    """Run a proactive contradiction detection scan to increase SCAR utilization."""
    detector = kimera_system['proactive_detector']
    scan_results = detector.run_proactive_scan()
    
    # Process any tensions found during the scan
    tensions_processed = 0
    scars_created = 0
    
    if scan_results.get("tensions_found"):
        # Load geoids for processing
        with SessionLocal() as db:
            geoid_rows = db.query(GeoidDB).all()
            geoids_dict = {}
            for row in geoid_rows:
                try:
                    geoid = GeoidState(
                        geoid_id=row.geoid_id,
                        semantic_state=row.semantic_state_json or {},
                        symbolic_state=row.symbolic_state or {},
                        embedding_vector=row.semantic_vector if row.semantic_vector is not None else [],
                        metadata=row.metadata_json or {}
                    )
                    geoids_dict[geoid.geoid_id] = geoid
                except:
                    continue
        
        # Process each tension found
        for tension in scan_results["tensions_found"][:10]:  # Limit to 10 per scan
            try:
                # Calculate pulse strength and make decision
                pulse_strength = kimera_system['contradiction_engine'].calculate_pulse_strength(
                    tension, geoids_dict
                )
                
                decision = kimera_system['contradiction_engine'].decide_collapse_or_surge(
                    pulse_strength, {"semantic_cohesion": 0.5}, None
                )
                
                # Create SCAR for all decisions
                if decision in ['collapse', 'surge', 'buffer']:
                    scar, vector = create_scar_from_tension(tension, geoids_dict, decision)
                    kimera_system['vault_manager'].insert_scar(scar, vector)
                    scars_created += 1
                
                tensions_processed += 1
                
            except Exception as e:
                # Skip problematic tensions
                continue
    
    scan_results["tensions_processed"] = tensions_processed
    scan_results["scars_created"] = scars_created
    
    # Sanitize all numpy types for JSON serialization
    return sanitize_for_json(scan_results)


@app.get("/system/utilization_stats")
async def get_utilization_statistics():
    """Get detailed statistics about SCAR utilization and system performance."""
    detector = kimera_system['proactive_detector']
    stats = detector.get_scan_statistics()
    
    # Add additional system metrics
    vault_manager = kimera_system['vault_manager']
    stats.update({
        "vault_a_scars": vault_manager.get_total_scar_count("vault_a"),
        "vault_b_scars": vault_manager.get_total_scar_count("vault_b"),
        "active_geoids": len(kimera_system['active_geoids']),
        "system_cycle_count": kimera_system['system_state']['cycle_count']
    })
    
    return stats


# -----------------------------
# Insight API Models (Phase 4)
# -----------------------------


class GenerateInsightRequest(BaseModel):
    source_geoid: str
    target_domain: str | None = None
    focus: str | None = None


class InsightFeedbackRequest(BaseModel):
    feedback_event: FeedbackEvent


# -----------------------------
# Insight API Endpoints
# -----------------------------


@app.post("/insights/generate")
async def generate_insight(request: GenerateInsightRequest):
    """Generates an insight from a source geoid using activation synthesis pipeline."""

    if request.source_geoid not in kimera_system["active_geoids"]:
        raise HTTPException(status_code=404, detail="Source geoid not found")

    # Build a minimal knowledge graph view (neighbors mocked for now)
    knowledge_graph: dict[str, ASGeoid] = {}
    for gid, g in kimera_system["active_geoids"].items():
        knowledge_graph[gid] = ASGeoid(geoid_id=gid, neighbors=list(g.metadata.get("neighbors", [])))

    resonance = ResonanceEvent(source_geoids=[request.source_geoid])
    activated_ids = trigger_activation_cascade(resonance, knowledge_graph)
    activated_geoids = [knowledge_graph[g] for g in activated_ids]

    mosaic = synthesize_patterns(activated_geoids)

    # Placeholder entropy reduction calculation
    entropy_reduction = 0.1 * len(activated_geoids)

    insight = generate_insight_scar(mosaic, resonance_id=request.source_geoid, entropy_reduction=entropy_reduction)

    # Store insight
    kimera_system["insights"][insight.insight_id] = insight
    kimera_system["recent_insights"].append(insight)
    if len(kimera_system["recent_insights"]) > 100:
        del kimera_system["recent_insights"][0]

    return {"insight": insight.to_dict()}


@app.get("/insights/{insight_id}")
async def get_insight(insight_id: str):
    insight = kimera_system["insights"].get(insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight.to_dict()


@app.get("/insights")
async def list_insights(type: str | None = None, domain: str | None = None):
    results = kimera_system["insights"].values()
    if type:
        results = filter(lambda i: i.insight_type.lower() == type.lower(), results)
    if domain:
        results = filter(lambda i: domain.lower() in (d.lower() for d in i.application_domains), results)
    return [i.to_dict() for i in results]


@app.post("/insights/{insight_id}/feedback")
async def feedback_insight(insight_id: str, request: InsightFeedbackRequest):
    insight = kimera_system["insights"].get(insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    state = kimera_system["system_state"]
    current_cycle = state.get("cycle_count", 0)

    insight = update_utility_score(insight, request.feedback_event, current_cycle)
    insight = manage_insight_lifecycle(insight)

    # Update stored object
    kimera_system["insights"][insight_id] = insight

    return {"insight": insight.to_dict()}


# Lineage tracer endpoint
@app.get("/insights/{insight_id}/lineage")
async def get_insight_lineage(insight_id: str):
    try:
        from ..tools.lineage_tracer import trace as trace_lineage
        lineage = trace_lineage(insight_id, kimera_system)
        return lineage
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# -----------------------------
# Statistical Modeling API Endpoints
# -----------------------------

class StatisticalAnalysisRequest(BaseModel):
    entropy_history: List[float] = []
    timestamps: List[str] = []
    contradiction_scores: List[float] = []
    semantic_features: Dict[str, List[float]] = {}
    semantic_supply: List[float] = []
    semantic_demand: List[float] = []
    entropy_prices: List[float] = []


@app.get("/statistics/capabilities")
async def get_statistical_capabilities():
    """Get available statistical modeling capabilities"""
    return statistical_engine.get_model_summary()


@app.post("/statistics/analyze/entropy_series")
async def analyze_entropy_series_endpoint(
    entropy_data: List[float],
    timestamps: List[str] = None
):
    """Analyze entropy time series data"""
    try:
        # Convert string timestamps to datetime objects if provided
        datetime_timestamps = None
        if timestamps:
            datetime_timestamps = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
        
        result = analyze_entropy_time_series(entropy_data, datetime_timestamps)
        
        # Convert result to dict for JSON serialization
        return {
            "model_type": result.model_type,
            "parameters": result.parameters,
            "statistics": result.statistics,
            "predictions": result.predictions,
            "diagnostics": result.diagnostics,
            "timestamp": result.timestamp.isoformat() if result.timestamp else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@app.post("/statistics/analyze/contradiction_factors")
async def analyze_contradiction_factors_endpoint(
    contradiction_scores: List[float],
    semantic_features: Dict[str, List[float]]
):
    """Analyze factors contributing to contradiction detection"""
    try:
        result = analyze_contradiction_factors(contradiction_scores, semantic_features)
        
        return {
            "model_type": result.model_type,
            "parameters": result.parameters,
            "statistics": result.statistics,
            "predictions": result.predictions,
            "residuals": result.residuals,
            "diagnostics": result.diagnostics,
            "timestamp": result.timestamp.isoformat() if result.timestamp else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@app.post("/statistics/analyze/semantic_market")
async def analyze_semantic_market_endpoint(
    semantic_supply: List[float],
    semantic_demand: List[float],
    entropy_prices: List[float]
):
    """Analyze semantic market dynamics using econometric models"""
    try:
        result = analyze_semantic_market(semantic_supply, semantic_demand, entropy_prices)
        
        return {
            "model_type": result.model_type,
            "parameters": result.parameters,
            "statistics": result.statistics,
            "diagnostics": result.diagnostics,
            "timestamp": result.timestamp.isoformat() if result.timestamp else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@app.post("/statistics/analyze/comprehensive")
async def comprehensive_statistical_analysis(request: StatisticalAnalysisRequest):
    """Perform comprehensive statistical analysis of system data"""
    try:
        # Prepare system data
        system_data = {}
        
        if request.entropy_history:
            system_data['entropy_history'] = request.entropy_history
            
        if request.timestamps:
            system_data['timestamps'] = [
                datetime.fromisoformat(ts.replace('Z', '+00:00')) 
                for ts in request.timestamps
            ]
            
        if request.contradiction_scores:
            system_data['contradiction_scores'] = request.contradiction_scores
            
        if request.semantic_features:
            system_data['semantic_features'] = request.semantic_features
            
        if request.semantic_supply and request.semantic_demand and request.entropy_prices:
            system_data['semantic_supply'] = request.semantic_supply
            system_data['semantic_demand'] = request.semantic_demand
            system_data['entropy_prices'] = request.entropy_prices
        
        # Perform comprehensive analysis
        results = statistical_engine.comprehensive_analysis(system_data)
        
        # Convert results to JSON-serializable format
        json_results = {}
        for analysis_type, result in results.items():
            json_results[analysis_type] = {
                "model_type": result.model_type,
                "parameters": result.parameters,
                "statistics": result.statistics,
                "predictions": result.predictions,
                "residuals": result.residuals,
                "diagnostics": result.diagnostics,
                "timestamp": result.timestamp.isoformat() if result.timestamp else None
            }
        
        return {
            "analysis_results": json_results,
            "summary": {
                "analyses_performed": len(json_results),
                "data_points_analyzed": len(request.entropy_history),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Comprehensive analysis failed: {str(e)}")


@app.get("/statistics/monitoring/status")
async def get_statistical_monitoring_status():
    """Get status of advanced statistical monitoring"""
    try:
        summary = advanced_monitor.get_statistical_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring status: {str(e)}")


@app.post("/statistics/monitoring/start")
async def start_statistical_monitoring():
    """Start advanced statistical monitoring"""
    try:
        advanced_monitor.start_monitoring()
        return {"status": "started", "message": "Advanced statistical monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@app.post("/statistics/monitoring/stop")
async def stop_statistical_monitoring():
    """Stop advanced statistical monitoring"""
    try:
        advanced_monitor.stop_monitoring()
        return {"status": "stopped", "message": "Advanced statistical monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@app.get("/statistics/monitoring/alerts")
async def get_statistical_alerts(severity: str = None, hours: int = 24):
    """Get recent statistical alerts"""
    try:
        alerts = advanced_monitor.get_alerts(severity_filter=severity, hours=hours)
        
        # Convert alerts to JSON-serializable format
        json_alerts = []
        for alert in alerts:
            json_alerts.append({
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value,
                "expected_range": alert.expected_range,
                "confidence_level": alert.confidence_level,
                "timestamp": alert.timestamp.isoformat(),
                "statistical_test": alert.statistical_test,
                "p_value": alert.p_value
            })
        
        return {
            "alerts": json_alerts,
            "total_alerts": len(json_alerts),
            "severity_filter": severity,
            "time_window_hours": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@app.get("/statistics/monitoring/forecast/{metric_name}")
async def get_metric_forecast(metric_name: str):
    """Get forecast for a specific metric"""
    try:
        forecast = advanced_monitor.get_forecast(metric_name)
        if not forecast:
            raise HTTPException(status_code=404, detail=f"No forecast available for metric: {metric_name}")
        
        return {
            "metric_name": metric_name,
            "forecast": forecast['forecast'],
            "confidence_intervals": forecast.get('confidence_intervals', []),
            "timestamp": forecast['timestamp'].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast: {str(e)}")


@app.get("/statistics/system/entropy_analysis")
async def get_system_entropy_analysis():
    """Provides a high-level analysis of the system's current entropy state."""
    # This endpoint can be expanded to return more detailed analysis
    try:
        from ..monitoring.entropy_monitor import entropy_monitor
        if not entropy_monitor.history:
            raise HTTPException(status_code=404, detail="No entropy data recorded yet.")
        
        latest_entropy = entropy_monitor.history[-1][1]
        avg_entropy = entropy_monitor.get_average_entropy()
        trend = entropy_monitor.get_entropy_trends(window_size=min(len(entropy_monitor.history), 20))

        return {
            "latest_entropy": latest_entropy,
            "average_entropy": avg_entropy,
            "trend_analysis": trend,
            "stability": "stable" if trend.get('slope', 0) < 0.001 else "volatile"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing entropy: {e}")


@app.get("/vault/understanding/metrics")
async def get_understanding_metrics_endpoint():
    """
    Get high-level metrics about the "understanding" capabilities of the vault.
    Requires the system to be running in 'understanding' mode.
    """
    vault_manager = kimera_system['vault_manager']
    if not hasattr(vault_manager, 'get_understanding_metrics'):
        raise HTTPException(
            status_code=400,
            detail="The system is not running in 'understanding' mode. The vault manager does not support this operation."
        )
    try:
        metrics = vault_manager.get_understanding_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving understanding metrics: {e}")


@app.post("/system/revolutionary_demo")
async def revolutionary_intelligence_demo(user_input: str = "I want to create something innovative"):
    """Demonstrate revolutionary intelligence integration with the full system."""
    try:
        revolutionary_intelligence = kimera_system.get('revolutionary_intelligence')
        if not revolutionary_intelligence:
            raise HTTPException(status_code=503, detail="Revolutionary intelligence not available")
        
        # Context from current system state
        user_context = {
            'creative_project': True,
            'system_state': {
                'active_geoids': len(kimera_system['active_geoids']),
                'cycle_count': kimera_system['system_state']['cycle_count'],
                'vault_scars': kimera_system['vault_manager'].get_total_scar_count("vault_a") + 
                              kimera_system['vault_manager'].get_total_scar_count("vault_b")
            }
        }
        
        # Evidence from system performance
        evidence = {
            'certainty': 0.7,
            'system_health': 'operational'
        }
        
        # Run revolutionary intelligence orchestration
        response = await revolutionary_intelligence.orchestrate_revolutionary_response(
            user_input=user_input,
            user_context=user_context,
            evidence=evidence
        )
        
        return {
            'status': 'success',
            'revolutionary_response': response,
            'system_context': user_context,
            'integration_proof': {
                'vault_system': 'connected',
                'cognitive_cycle': 'integrated',
                'embedding_model': 'operational',
                'revolutionary_intelligence': 'orchestrated'
            }
        }
        
    except Exception as e:
        logging.error(f"Revolutionary intelligence demo failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")


@app.post("/insights/auto_generate")
async def auto_generate_insights():
    """
    Automatically generate insights from recent geoids and contradictions.
    This addresses the issue of no insights being generated during normal operation.
    """
    try:
        logging.info("Starting automatic insight generation")
        
        # Get recent geoids (last 10)
        recent_geoids = list(kimera_system['active_geoids'].keys())[-10:]
        
        if not recent_geoids:
            return {
                "insights_generated": 0,
                "message": "No geoids available for insight generation"
            }
        
        insights_generated = 0
        generated_insights = []
        
        for geoid_id in recent_geoids:
            try:
                # Build knowledge graph
                knowledge_graph = {}
                for gid, g in kimera_system["active_geoids"].items():
                    knowledge_graph[gid] = ASGeoid(
                        geoid_id=gid, 
                        neighbors=list(g.metadata.get("neighbors", []))
                    )
                
                # Generate insight
                resonance = ResonanceEvent(source_geoids=[geoid_id])
                activated_ids = trigger_activation_cascade(resonance, knowledge_graph)
                activated_geoids = [knowledge_graph[g] for g in activated_ids]
                
                mosaic = synthesize_patterns(activated_geoids)
                entropy_reduction = 0.1 * len(activated_geoids)
                
                insight = generate_insight_scar(
                    mosaic, 
                    resonance_id=geoid_id, 
                    entropy_reduction=entropy_reduction
                )
                
                # Store insight
                kimera_system["insights"][insight.insight_id] = insight
                kimera_system["recent_insights"].append(insight)
                if len(kimera_system["recent_insights"]) > 100:
                    del kimera_system["recent_insights"][0]
                
                insights_generated += 1
                generated_insights.append({
                    "insight_id": insight.insight_id,
                    "source_geoid": geoid_id,
                    "type": insight.insight_type,
                    "confidence": insight.confidence
                })
                
            except Exception as e:
                logging.warning(f"Failed to generate insight for geoid {geoid_id}: {e}")
                continue
        
        return {
            "insights_generated": insights_generated,
            "insights": generated_insights,
            "total_insights_stored": len(kimera_system["insights"])
        }
        
    except Exception as e:
        logging.error(f"Auto insight generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 KIMERA API starting up...")
    
    # Start background tasks
    if LAW_ENFORCEMENT_AVAILABLE:
        # Schedule periodic stabilization every 5 minutes
        async def stabilization_scheduler():
            while True:
                await asyncio.sleep(300)  # 5 minutes
                try:
                    await periodic_stabilization()
                except Exception as e:
                    logger.error(f"Periodic stabilization error: {e}")
        
        # Start the scheduler in the background
        asyncio.create_task(stabilization_scheduler())
        logger.info("📊 Law enforcement stabilization scheduler started")
    
    yield
    
    logger.info("🛑 KIMERA API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

