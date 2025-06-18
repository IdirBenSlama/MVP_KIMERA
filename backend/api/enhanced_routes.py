"""
Enhanced API Routes
==================

New API endpoints that integrate Context Field Selector and 
Anthropomorphic Language Profiler for improved processing control
and security.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, List, Set, Any, Optional
import logging
from datetime import datetime

from ..core.context_field_selector import (
    ContextFieldSelector, ContextFieldConfig, FieldCategory, 
    ProcessingLevel, create_minimal_selector, create_standard_selector,
    create_enhanced_selector, create_domain_selector
)
from ..core.anthropomorphic_profiler import (
    AnthropomorphicProfiler, PersonalityProfile, InteractionAnalysis,
    create_default_profiler, create_strict_profiler
)
from ..core.gyroscopic_security import (
    GyroscopicSecurityCore, EquilibriumState, ManipulationVector,
    create_maximum_security_core, create_balanced_security_core
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced", tags=["enhanced"])

# Global instances (in production, these would be managed per session)
context_selector: Optional[ContextFieldSelector] = None
anthropomorphic_profiler: Optional[AnthropomorphicProfiler] = None
gyroscopic_security: Optional[GyroscopicSecurityCore] = None


# Pydantic models for API requests
class ContextFieldConfigRequest(BaseModel):
    processing_level: str = "standard"  # minimal, standard, enhanced, custom
    included_categories: Optional[List[str]] = None
    excluded_categories: Optional[List[str]] = None
    included_fields: Optional[List[str]] = None
    excluded_fields: Optional[List[str]] = None
    include_confidence_scores: bool = True
    include_processing_metadata: bool = True
    include_timestamps: bool = True
    skip_expensive_calculations: bool = False
    limit_embedding_dimensions: Optional[int] = None
    max_semantic_features: Optional[int] = None
    domain_focus: Optional[str] = None
    language_priority: Optional[List[str]] = None


class PersonalityProfileRequest(BaseModel):
    formality: float = 0.6
    enthusiasm: float = 0.7
    technical_depth: float = 0.8
    empathy: float = 0.7
    assertiveness: float = 0.6
    creativity: float = 0.8
    humor: float = 0.3
    directness: float = 0.7
    preferred_greeting: str = "professional_friendly"
    explanation_style: str = "structured_detailed"
    technical_language_level: str = "advanced"
    max_trait_deviation: float = 0.2
    drift_window_size: int = 10
    prevent_role_playing: bool = True
    prevent_persona_switching: bool = True
    maintain_professional_boundary: bool = True


class EnhancedProcessingRequest(BaseModel):
    input_text: str
    context_config: Optional[ContextFieldConfigRequest] = None
    use_profiler: bool = True
    session_id: Optional[str] = None


class ProfilerAnalysisRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class EquilibriumConfigRequest(BaseModel):
    cognitive_balance: float = 0.5
    emotional_stability: float = 0.5
    authority_recognition: float = 0.5
    boundary_integrity: float = 0.5
    context_clarity: float = 0.5
    cognitive_inertia: float = 0.8
    emotional_damping: float = 0.9
    role_rigidity: float = 0.95
    boundary_hardness: float = 0.99
    restoration_rate: float = 0.1
    stability_threshold: float = 0.05


class SecureProcessingRequest(BaseModel):
    input_text: str
    context_config: Optional[ContextFieldConfigRequest] = None
    use_profiler: bool = True
    use_gyroscopic_security: bool = True
    session_id: Optional[str] = None


# Context Field Selector Endpoints
@router.post("/context/configure")
async def configure_context_selector(config: ContextFieldConfigRequest):
    """Configure the context field selector"""
    global context_selector
    
    try:
        # Convert string enums to actual enums
        processing_level = ProcessingLevel(config.processing_level)
        
        included_categories = set()
        if config.included_categories:
            included_categories = {FieldCategory(cat) for cat in config.included_categories}
        
        excluded_categories = set()
        if config.excluded_categories:
            excluded_categories = {FieldCategory(cat) for cat in config.excluded_categories}
        
        # Create configuration
        field_config = ContextFieldConfig(
            processing_level=processing_level,
            included_categories=included_categories,
            excluded_categories=excluded_categories,
            included_fields=set(config.included_fields or []),
            excluded_fields=set(config.excluded_fields or []),
            include_confidence_scores=config.include_confidence_scores,
            include_processing_metadata=config.include_processing_metadata,
            include_timestamps=config.include_timestamps,
            skip_expensive_calculations=config.skip_expensive_calculations,
            limit_embedding_dimensions=config.limit_embedding_dimensions,
            max_semantic_features=config.max_semantic_features,
            domain_focus=config.domain_focus,
            language_priority=config.language_priority or []
        )
        
        # Create selector
        context_selector = ContextFieldSelector(field_config)
        
        logger.info(f"Context Field Selector configured with {processing_level.value} level")
        
        return {
            "status": "configured",
            "processing_level": processing_level.value,
            "included_categories": [cat.value for cat in included_categories],
            "excluded_categories": [cat.value for cat in excluded_categories],
            "domain_focus": config.domain_focus,
            "performance_optimizations": config.skip_expensive_calculations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Context selector configuration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.get("/context/presets/{preset_name}")
async def load_context_preset(preset_name: str):
    """Load a predefined context selector preset"""
    global context_selector
    
    try:
        if preset_name == "minimal":
            context_selector = create_minimal_selector()
        elif preset_name == "standard":
            context_selector = create_standard_selector()
        elif preset_name == "enhanced":
            context_selector = create_enhanced_selector()
        elif preset_name.startswith("domain_"):
            domain = preset_name.replace("domain_", "")
            context_selector = create_domain_selector(domain)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown preset: {preset_name}")
        
        logger.info(f"Context Field Selector loaded preset: {preset_name}")
        
        return {
            "status": "loaded",
            "preset": preset_name,
            "processing_level": context_selector.config.processing_level.value,
            "domain_focus": context_selector.config.domain_focus
        }
        
    except Exception as e:
        logger.error(f"Preset loading failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preset loading failed: {str(e)}")


@router.get("/context/status")
async def get_context_selector_status():
    """Get current context selector status and statistics"""
    global context_selector
    
    if not context_selector:
        return {"status": "not_configured", "message": "Context Field Selector not initialized"}
    
    try:
        summary = context_selector.get_processing_summary()
        return {
            "status": "active",
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Context status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


# Anthropomorphic Profiler Endpoints
@router.post("/profiler/configure")
async def configure_profiler(profile: PersonalityProfileRequest):
    """Configure the anthropomorphic language profiler"""
    global anthropomorphic_profiler
    
    try:
        # Create personality profile
        personality_profile = PersonalityProfile(
            formality=profile.formality,
            enthusiasm=profile.enthusiasm,
            technical_depth=profile.technical_depth,
            empathy=profile.empathy,
            assertiveness=profile.assertiveness,
            creativity=profile.creativity,
            humor=profile.humor,
            directness=profile.directness,
            preferred_greeting=profile.preferred_greeting,
            explanation_style=profile.explanation_style,
            technical_language_level=profile.technical_language_level,
            max_trait_deviation=profile.max_trait_deviation,
            drift_window_size=profile.drift_window_size,
            prevent_role_playing=profile.prevent_role_playing,
            prevent_persona_switching=profile.prevent_persona_switching,
            maintain_professional_boundary=profile.maintain_professional_boundary
        )
        
        # Create profiler
        anthropomorphic_profiler = AnthropomorphicProfiler(personality_profile)
        
        logger.info("Anthropomorphic Language Profiler configured")
        
        return {
            "status": "configured",
            "profile_summary": {
                "formality": profile.formality,
                "technical_depth": profile.technical_depth,
                "enthusiasm": profile.enthusiasm,
                "max_deviation": profile.max_trait_deviation,
                "security_enabled": profile.prevent_role_playing
            }
        }
        
    except Exception as e:
        logger.error(f"Profiler configuration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.get("/profiler/presets/{preset_name}")
async def load_profiler_preset(preset_name: str):
    """Load a predefined profiler preset"""
    global anthropomorphic_profiler
    
    try:
        if preset_name == "default":
            anthropomorphic_profiler = create_default_profiler()
        elif preset_name == "strict":
            anthropomorphic_profiler = create_strict_profiler()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown preset: {preset_name}")
        
        logger.info(f"Anthropomorphic Profiler loaded preset: {preset_name}")
        
        return {
            "status": "loaded",
            "preset": preset_name,
            "security_level": "strict" if preset_name == "strict" else "standard"
        }
        
    except Exception as e:
        logger.error(f"Profiler preset loading failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preset loading failed: {str(e)}")


@router.post("/profiler/analyze")
async def analyze_message(request: ProfilerAnalysisRequest):
    """Analyze a message for personality traits and drift"""
    global anthropomorphic_profiler
    
    if not anthropomorphic_profiler:
        # Initialize with default if not configured
        anthropomorphic_profiler = create_default_profiler()
    
    try:
        analysis = anthropomorphic_profiler.analyze_interaction(request.message)
        
        # Generate correction suggestions if needed
        suggestions = []
        if analysis.drift_severity.value in ["significant", "critical"]:
            suggestions = anthropomorphic_profiler.generate_correction_suggestions(analysis)
        
        return {
            "analysis": analysis.to_dict(),
            "suggestions": suggestions,
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"Message analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/profiler/status")
async def get_profiler_status():
    """Get current profiler status and drift trends"""
    global anthropomorphic_profiler
    
    if not anthropomorphic_profiler:
        return {"status": "not_configured", "message": "Anthropomorphic Profiler not initialized"}
    
    try:
        status = anthropomorphic_profiler.get_profiler_status()
        return {
            "status": "active",
            "profiler_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Profiler status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.get("/profiler/drift/trend")
async def get_drift_trend(window_size: Optional[int] = None):
    """Get recent personality drift trend"""
    global anthropomorphic_profiler
    
    if not anthropomorphic_profiler:
        raise HTTPException(status_code=400, detail="Profiler not configured")
    
    try:
        trend = anthropomorphic_profiler.get_recent_drift_trend(window_size)
        return {
            "drift_trend": trend,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Drift trend retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trend retrieval failed: {str(e)}")


# Gyroscopic Security Endpoints
@router.post("/security/configure")
async def configure_gyroscopic_security(config: EquilibriumConfigRequest):
    """Configure the gyroscopic security core"""
    global gyroscopic_security
    
    try:
        # Create equilibrium state
        equilibrium_state = EquilibriumState(
            cognitive_balance=config.cognitive_balance,
            emotional_stability=config.emotional_stability,
            authority_recognition=config.authority_recognition,
            boundary_integrity=config.boundary_integrity,
            context_clarity=config.context_clarity,
            cognitive_inertia=config.cognitive_inertia,
            emotional_damping=config.emotional_damping,
            role_rigidity=config.role_rigidity,
            boundary_hardness=config.boundary_hardness,
            restoration_rate=config.restoration_rate,
            stability_threshold=config.stability_threshold
        )
        
        # Create security core
        gyroscopic_security = GyroscopicSecurityCore(equilibrium_state)
        
        logger.info("Gyroscopic Security Core configured - Perfect equilibrium established")
        
        return {
            "status": "configured",
            "equilibrium_summary": {
                "stability_score": 1.0 - equilibrium_state.calculate_deviation(),
                "is_stable": equilibrium_state.is_stable(),
                "boundary_hardness": equilibrium_state.boundary_hardness,
                "role_rigidity": equilibrium_state.role_rigidity,
                "restoration_rate": equilibrium_state.restoration_rate
            },
            "security_level": "maximum" if equilibrium_state.boundary_hardness > 0.95 else "standard"
        }
        
    except Exception as e:
        logger.error(f"Gyroscopic security configuration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.get("/security/presets/{preset_name}")
async def load_security_preset(preset_name: str):
    """Load a predefined security preset"""
    global gyroscopic_security
    
    try:
        if preset_name == "maximum":
            gyroscopic_security = create_maximum_security_core()
        elif preset_name == "balanced":
            gyroscopic_security = create_balanced_security_core()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown preset: {preset_name}")
        
        logger.info(f"Gyroscopic Security Core loaded preset: {preset_name}")
        
        return {
            "status": "loaded",
            "preset": preset_name,
            "security_level": preset_name,
            "equilibrium_established": True
        }
        
    except Exception as e:
        logger.error(f"Security preset loading failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preset loading failed: {str(e)}")


@router.post("/security/analyze")
async def analyze_input_security(request: Dict[str, str]):
    """Analyze input for manipulation attempts"""
    global gyroscopic_security
    
    if not gyroscopic_security:
        # Initialize with balanced security if not configured
        gyroscopic_security = create_balanced_security_core()
    
    try:
        input_text = request.get("input_text", "")
        if not input_text:
            raise HTTPException(status_code=400, detail="input_text is required")
        
        # Process input through gyroscopic security
        security_result = gyroscopic_security.process_input_with_security(input_text)
        
        return {
            "security_analysis": security_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Security analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/security/status")
async def get_security_status():
    """Get comprehensive security status"""
    global gyroscopic_security
    
    if not gyroscopic_security:
        return {"status": "not_configured", "message": "Gyroscopic Security Core not initialized"}
    
    try:
        status = gyroscopic_security.get_security_status()
        return {
            "status": "active",
            "security_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Security status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.get("/security/threats")
async def get_threat_analysis():
    """Get detailed threat analysis and patterns"""
    global gyroscopic_security
    
    if not gyroscopic_security:
        raise HTTPException(status_code=400, detail="Security core not configured")
    
    try:
        # Get recent manipulation attempts
        recent_attempts = list(gyroscopic_security.manipulation_history)[-50:]
        
        # Analyze threat patterns
        threat_analysis = {
            "total_attempts": len(gyroscopic_security.manipulation_history),
            "recent_attempts": len(recent_attempts),
            "neutralization_rate": gyroscopic_security.stats['neutralized_attempts'] / max(gyroscopic_security.stats['total_attempts'], 1),
            "strongest_attempt": gyroscopic_security.stats['strongest_attempt_strength'],
            "vector_frequency": {},
            "sophistication_levels": [],
            "temporal_patterns": []
        }
        
        # Analyze vector frequency
        for attempt in recent_attempts:
            vector_name = attempt.vector.value
            threat_analysis["vector_frequency"][vector_name] = threat_analysis["vector_frequency"].get(vector_name, 0) + 1
        
        # Analyze sophistication levels
        threat_analysis["sophistication_levels"] = [attempt.sophistication_level for attempt in recent_attempts[-20:]]
        
        # Analyze temporal patterns (attempts per hour)
        if recent_attempts:
            time_buckets = {}
            for attempt in recent_attempts:
                hour_key = attempt.timestamp.strftime("%Y-%m-%d %H:00")
                time_buckets[hour_key] = time_buckets.get(hour_key, 0) + 1
            threat_analysis["temporal_patterns"] = time_buckets
        
        return {
            "threat_analysis": threat_analysis,
            "security_recommendations": gyroscopic_security._generate_security_recommendations(threat_analysis),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Threat analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Enhanced Secure Processing Endpoint
@router.post("/process/secure")
async def secure_enhanced_processing(request: SecureProcessingRequest):
    """Process input with full security, context selection, and personality profiling"""
    global context_selector, anthropomorphic_profiler, gyroscopic_security
    
    try:
        # Initialize components if needed
        if not context_selector:
            context_selector = create_standard_selector()
        
        if request.use_profiler and not anthropomorphic_profiler:
            anthropomorphic_profiler = create_default_profiler()
        
        if request.use_gyroscopic_security and not gyroscopic_security:
            gyroscopic_security = create_balanced_security_core()
        
        # Step 1: Security Analysis (First line of defense)
        security_result = None
        if request.use_gyroscopic_security and gyroscopic_security:
            security_result = gyroscopic_security.process_input_with_security(request.input_text)
            
            # If high-risk manipulation detected, return security response
            if not security_result.get('equilibrium_maintained', True):
                return {
                    "processing_status": "security_blocked",
                    "security_analysis": security_result,
                    "message": "Input blocked due to manipulation attempt detection",
                    "session_id": request.session_id,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Step 2: Apply temporary context configuration if provided
        temp_selector = context_selector
        if request.context_config:
            config_dict = request.context_config.dict()
            config_request = ContextFieldConfigRequest(**config_dict)
            processing_level = ProcessingLevel(config_request.processing_level)
            temp_config = ContextFieldConfig(processing_level=processing_level)
            temp_selector = ContextFieldSelector(temp_config)
        
        # Step 3: Personality Profiling
        profiler_analysis = None
        if request.use_profiler and anthropomorphic_profiler:
            profiler_analysis = anthropomorphic_profiler.analyze_interaction(request.input_text)
            
            # Apply personality-based security adjustments
            if profiler_analysis.drift_severity.value in ["significant", "critical"]:
                logger.warning(f"Significant personality drift detected: {profiler_analysis.drift_severity.value}")
        
        # Step 4: Simulate semantic processing with security-aware filtering
        raw_semantic_data = {
            "semantic_state": {
                "input_complexity": 0.75,
                "semantic_density": 0.82,
                "conceptual_depth": 0.68,
                "security_clearance": security_result.get('stability_score', 1.0) if security_result else 1.0,
                "manipulation_resistance": 1.0 - (security_result.get('manipulation_strength', 0.0) if security_result else 0.0)
            },
            "symbolic_state": {
                "parsed_entities": ["concept_1", "concept_2"],
                "relationships": [{"source": "concept_1", "target": "concept_2", "type": "relates_to"}],
                "security_validated": True
            },
            "embedding_vector": [0.1] * 512,
            "metadata": {
                "input_length": len(request.input_text),
                "processing_timestamp": datetime.now().isoformat(),
                "language_detected": "en",
                "security_score": security_result.get('stability_score', 1.0) if security_result else 1.0,
                "personality_drift": profiler_analysis.drift_severity.value if profiler_analysis else "minimal",
                "manipulation_vectors": security_result.get('manipulation_vectors', []) if security_result else []
            }
        }
        
        # Step 5: Apply context field selection
        filtered_output = temp_selector.create_filtered_output(raw_semantic_data)
        
        # Step 6: Combine all results
        result = {
            "processing_status": "completed",
            "processed_data": filtered_output,
            "security_analysis": security_result,
            "profiler_analysis": profiler_analysis.to_dict() if profiler_analysis else None,
            "context_summary": temp_selector.get_processing_summary(),
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat(),
            "security_clearance": "approved",
            "equilibrium_maintained": security_result.get('equilibrium_maintained', True) if security_result else True
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Secure enhanced processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# System Management Endpoints
@router.get("/system/status")
async def get_enhanced_system_status():
    """Get status of all enhanced components including security"""
    global context_selector, anthropomorphic_profiler, gyroscopic_security
    
    return {
        "context_selector": {
            "configured": context_selector is not None,
            "processing_level": context_selector.config.processing_level.value if context_selector else None,
            "statistics": context_selector.processing_stats if context_selector else None
        },
        "anthropomorphic_profiler": {
            "configured": anthropomorphic_profiler is not None,
            "total_interactions": anthropomorphic_profiler.stats["total_interactions"] if anthropomorphic_profiler else 0,
            "drift_incidents": anthropomorphic_profiler.stats["drift_incidents"] if anthropomorphic_profiler else 0,
            "security_violations": anthropomorphic_profiler.stats["security_violations"] if anthropomorphic_profiler else 0
        },
        "gyroscopic_security": {
            "configured": gyroscopic_security is not None,
            "total_attempts": gyroscopic_security.stats["total_attempts"] if gyroscopic_security else 0,
            "neutralized_attempts": gyroscopic_security.stats["neutralized_attempts"] if gyroscopic_security else 0,
            "neutralization_rate": (gyroscopic_security.stats["neutralized_attempts"] / max(gyroscopic_security.stats["total_attempts"], 1)) if gyroscopic_security else 1.0,
            "current_stability": gyroscopic_security.stats["current_stability_score"] if gyroscopic_security else 1.0,
            "equilibrium_status": "perfect_balance" if gyroscopic_security and gyroscopic_security.equilibrium.is_stable() else "unknown"
        },
        "overall_security_level": "maximum" if gyroscopic_security else "standard",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/system/reset")
async def reset_enhanced_components():
    """Reset all enhanced components to default state"""
    global context_selector, anthropomorphic_profiler
    
    try:
        context_selector = create_standard_selector()
        anthropomorphic_profiler = create_default_profiler()
        
        logger.info("Enhanced components reset to defaults")
        
        return {
            "status": "reset",
            "message": "All enhanced components reset to default configuration",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Component reset failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


# Health check endpoint
@router.get("/health")
async def enhanced_health_check():
    """Health check for enhanced processing components including security"""
    global context_selector, anthropomorphic_profiler, gyroscopic_security
    
    health_status = {
        "status": "healthy",
        "components": {
            "context_selector": "active" if context_selector else "inactive",
            "anthropomorphic_profiler": "active" if anthropomorphic_profiler else "inactive",
            "gyroscopic_security": "active" if gyroscopic_security else "inactive"
        },
        "security_level": "maximum" if gyroscopic_security else "standard",
        "equilibrium_status": "perfect_balance" if gyroscopic_security and gyroscopic_security.equilibrium.is_stable() else "unknown",
        "timestamp": datetime.now().isoformat()
    }
    
    # Check for any issues
    issues = []
    
    if context_selector:
        try:
            test_data = {"semantic_state": {"test": 0.5}}
            context_selector.create_filtered_output(test_data)
        except Exception as e:
            issues.append(f"Context selector error: {str(e)}")
            health_status["components"]["context_selector"] = "error"
    
    if anthropomorphic_profiler:
        try:
            anthropomorphic_profiler.analyze_interaction("test message")
        except Exception as e:
            issues.append(f"Profiler error: {str(e)}")
            health_status["components"]["anthropomorphic_profiler"] = "error"
    
    if gyroscopic_security:
        try:
            gyroscopic_security.process_input_with_security("test input")
        except Exception as e:
            issues.append(f"Security core error: {str(e)}")
            health_status["components"]["gyroscopic_security"] = "error"
    
    if issues:
        health_status["status"] = "degraded"
        health_status["issues"] = issues
    
    return health_status 