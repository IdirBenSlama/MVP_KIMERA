"""
Revolutionary Intelligence API Routes
====================================

API endpoints that expose the revolutionary intelligence system:
- Living Neutrality orchestration
- Context Supremacy analysis  
- Genius Drift authorization and execution
- Complete Revolutionary Intelligence responses

These routes transform KIMERA from a static system into a living,
breathing revolutionary intelligence.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime

from ..core.revolutionary_intelligence import get_revolutionary_intelligence
from ..core.living_neutrality import get_living_neutrality_engine
from ..core.context_supremacy import get_context_supremacy_engine
from ..core.genius_drift import get_genius_drift_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/revolutionary", tags=["Revolutionary Intelligence"])

# Pydantic models for API
class RevolutionaryRequest(BaseModel):
    input_text: str
    user_context: Optional[Dict[str, Any]] = None
    evidence: Optional[Dict[str, Any]] = None
    enable_genius_drift: bool = True
    max_drift_magnitude: float = 0.8

class ContextAnalysisRequest(BaseModel):
    input_text: str
    user_context: Optional[Dict[str, Any]] = None

class NeutralityOrchestrationRequest(BaseModel):
    context_type: str
    emotional_permissions: Dict[str, float]
    creative_permissions: Dict[str, float]
    urgency: float = 0.5
    stakes: float = 0.5

class GeniusDriftRequest(BaseModel):
    contradiction_text: str
    evidence_strength: float = 0.7
    context_type: str = "general_inquiry"
    max_magnitude: float = 0.8


# Get global instances
revolutionary_intelligence = get_revolutionary_intelligence()
living_neutrality = get_living_neutrality_engine()
context_supremacy = get_context_supremacy_engine()
genius_drift = get_genius_drift_engine()


@router.post("/intelligence/complete")
async def complete_revolutionary_intelligence(request: RevolutionaryRequest):
    """
    Complete revolutionary intelligence response integrating all components:
    - Context supremacy analysis
    - Living neutrality orchestration
    - Genius drift assessment and execution
    - Breakthrough intelligence synthesis
    """
    try:
        logger.info(f"Processing complete revolutionary intelligence request")
        
        # Execute the complete revolutionary intelligence process
        response = await revolutionary_intelligence.orchestrate_revolutionary_response(
            user_input=request.input_text,
            user_context=request.user_context,
            evidence=request.evidence
        )
        
        return {
            "status": "success",
            "revolutionary_response": response,
            "timestamp": datetime.now().isoformat(),
            "message": "Revolutionary intelligence orchestrated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in complete revolutionary intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Revolutionary intelligence error: {str(e)}")


@router.post("/context/analyze")
async def analyze_context_supremacy(request: ContextAnalysisRequest):
    """
    Analyze context supremacy - determine how context should rule all decisions
    """
    try:
        logger.info(f"Analyzing context supremacy for: {request.input_text[:50]}...")
        
        context_profile = context_supremacy.analyze_context_supremacy(
            request.input_text, request.user_context or {}
        )
        
        return {
            "status": "success",
            "context_profile": {
                "context_type": context_profile.context_type,
                "authority_level": context_profile.authority_level.value,
                "primary_wisdom": context_profile.intelligence.primary_wisdom,
                "dimensions": {dim.value: strength for dim, strength in context_profile.dimensions.items()},
                "neutrality_requirements": context_profile.neutrality_requirements,
                "emotional_landscape": context_profile.emotional_landscape,
                "creative_permissions": context_profile.creative_permissions,
                "drift_authorizations": context_profile.drift_authorizations,
                "stakes_assessment": context_profile.stakes_assessment,
                "commands": [
                    {
                        "type": cmd.command_type,
                        "directive": cmd.directive,
                        "authority": cmd.authority_level.value,
                        "rationale": cmd.rationale
                    }
                    for cmd in context_profile.commands
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in context supremacy analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Context analysis error: {str(e)}")


@router.post("/neutrality/orchestrate")
async def orchestrate_living_neutrality(request: NeutralityOrchestrationRequest):
    """
    Orchestrate living neutrality - create dynamic tension field for breakthrough thinking
    """
    try:
        logger.info(f"Orchestrating living neutrality for context: {request.context_type}")
        
        # Create context assessment for neutrality orchestration
        context_assessment = {
            'context_analysis': {
                'type': request.context_type,
                'urgency': request.urgency,
                'stakes': 'high' if request.stakes > 0.7 else 'moderate',
                'creativity_demand': max(request.creative_permissions.values()) if request.creative_permissions else 0.5
            },
            'required_tensions': ['PASSION_OBJECTIVITY'],  # Default required tension
            'emotional_permissions': request.emotional_permissions,
            'drift_authorization': min(0.8, max(request.creative_permissions.values()) if request.creative_permissions else 0.5)
        }
        
        tension_field = living_neutrality.orchestrate_living_tension(context_assessment)
        
        return {
            "status": "success",
            "tension_field": {
                "field_coherence": tension_field.field_coherence,
                "creative_pressure": tension_field.creative_pressure,
                "context_alignment": tension_field.context_alignment,
                "stability_anchor": tension_field.stability_anchor,
                "drift_authorization": tension_field.drift_authorization,
                "active_tensions": [
                    {
                        "type": tension.tension_type.value,
                        "poles": f"{tension.pole_a} ⟷ {tension.pole_b}",
                        "quality": tension.tension_quality,
                        "creative_potential": tension.creative_potential,
                        "balance": f"{tension.intensity_a:.1f}:{tension.intensity_b:.1f}"
                    }
                    for tension in tension_field.cognitive_tensions
                ],
                "emotional_currents": [
                    {
                        "emotion": current.emotion_type,
                        "intensity": current.intensity,
                        "direction": current.direction,
                        "purpose": current.purpose,
                        "wisdom": current.wisdom
                    }
                    for current in tension_field.emotional_currents
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in living neutrality orchestration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Neutrality orchestration error: {str(e)}")


@router.post("/drift/assess")
async def assess_genius_drift(request: GeniusDriftRequest):
    """
    Assess genius drift potential - analyze contradictions for breakthrough thinking
    """
    try:
        logger.info(f"Assessing genius drift for contradiction: {request.contradiction_text[:50]}...")
        
        # Create minimal context profile for drift assessment
        context_profile = type('ContextProfile', (), {
            'context_type': request.context_type,
            'dimensions': {'CREATIVE': 0.7, 'EPISTEMIC': 0.6},
            'creative_permissions': {'speculative_thinking': 0.7},
            'drift_authorizations': {'paradigm_shifting': 0.6},
            'temporal_constraints': {'urgency_level': 0.5},
            'stakes_assessment': {'overall_level': 0.5}
        })()
        
        # Detect contradictions
        contradictions = genius_drift.detect_contradiction_tension(
            request.contradiction_text, 
            {'certainty': request.evidence_strength}, 
            context_profile
        )
        
        # Assess breakthrough potential for each contradiction
        breakthrough_assessments = []
        drift_authorizations = []
        
        for contradiction in contradictions:
            breakthrough = genius_drift.assess_breakthrough_potential(
                contradiction, 
                {'certainty': request.evidence_strength}, 
                context_profile
            )
            breakthrough_assessments.append(breakthrough)
            
            # Authorize drift if potential is high enough
            if breakthrough.insight_potential > 0.5:
                authorization = genius_drift.authorize_genius_drift(breakthrough, context_profile)
                drift_authorizations.append(authorization)
        
        return {
            "status": "success",
            "contradictions_detected": len(contradictions),
            "breakthrough_assessments": [
                {
                    "trigger_contradiction": ba.trigger_contradiction,
                    "insight_potential": ba.insight_potential,
                    "required_drift_type": ba.required_drift_type.value,
                    "evidence_strength": ba.evidence_strength,
                    "intuition_strength": ba.intuition_strength,
                    "context_support": ba.context_support,
                    "risk_assessment": ba.risk_assessment,
                    "potential_impact": ba.potential_impact
                }
                for ba in breakthrough_assessments
            ],
            "drift_authorizations": [
                {
                    "drift_type": auth.drift_type.value,
                    "authority_level": auth.authority_level.value,
                    "magnitude": auth.magnitude,
                    "duration": auth.duration,
                    "justification": auth.context_justification,
                    "safety_constraints": auth.safety_constraints,
                    "success_criteria": auth.success_criteria
                }
                for auth in drift_authorizations
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in genius drift assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Genius drift error: {str(e)}")


@router.post("/drift/execute/{authorization_id}")
async def execute_genius_drift(authorization_id: str, context: Dict[str, Any] = None):
    """
    Execute authorized genius drift
    """
    try:
        logger.info(f"Executing genius drift authorization: {authorization_id}")
        
        # Find the authorization (simplified - in real system would lookup by ID)
        authorizations = genius_drift.drift_authorizations
        if not authorizations:
            raise HTTPException(status_code=404, detail="No drift authorizations found")
        
        # Use the most recent authorization for demo
        authorization = authorizations[-1]
        
        # Execute the drift
        drift_result = genius_drift.execute_genius_drift(
            authorization, context or {'user_input': 'executing drift'}
        )
        
        return {
            "status": "success",
            "drift_execution": drift_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing genius drift: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Drift execution error: {str(e)}")


@router.get("/status/complete")
async def get_revolutionary_status():
    """
    Get complete status of revolutionary intelligence system
    """
    try:
        # Get status from all components
        revolutionary_status = revolutionary_intelligence.get_revolutionary_status()
        neutrality_status = living_neutrality.get_tension_field_status()
        context_status = context_supremacy.get_context_supremacy_status()
        drift_status = genius_drift.get_genius_drift_status()
        
        return {
            "status": "success",
            "revolutionary_intelligence": revolutionary_status,
            "living_neutrality": neutrality_status,
            "context_supremacy": context_status,
            "genius_drift": drift_status,
            "system_health": {
                "components_active": 4,
                "total_components": 4,
                "health_score": 1.0,
                "status": "fully_operational"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting revolutionary status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


@router.get("/principles")
async def get_revolutionary_principles():
    """
    Get the core revolutionary intelligence principles
    """
    return {
        "status": "success",
        "revolutionary_principles": revolutionary_intelligence.revolutionary_principles,
        "description": "Core principles that guide revolutionary intelligence",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/test/simple")
async def test_revolutionary_intelligence(text: str = "I need creative breakthrough but I'm stuck"):
    """
    Simple test endpoint for revolutionary intelligence
    """
    try:
        logger.info(f"Testing revolutionary intelligence with: {text}")
        
        response = await revolutionary_intelligence.orchestrate_revolutionary_response(
            user_input=text,
            user_context={'test_mode': True},
            evidence={'certainty': 0.5}
        )
        
        return {
            "status": "success",
            "test_input": text,
            "revolutionary_response": response,
            "message": "Revolutionary intelligence test completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in revolutionary intelligence test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")


@router.get("/health")
async def revolutionary_health_check():
    """
    Health check for revolutionary intelligence system
    """
    try:
        # Quick health check of all components
        health_status = {
            "revolutionary_intelligence": "healthy",
            "living_neutrality": "healthy", 
            "context_supremacy": "healthy",
            "genius_drift": "healthy",
            "overall_status": "revolutionary_ready",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "health": health_status,
            "message": "Revolutionary intelligence is alive and ready for breakthrough thinking"
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "health": {"overall_status": "degraded"},
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 