"""
Law Enforcement API Routes
=========================

API endpoints for contextual law enforcement, relevance assessment, and stabilization.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from backend.core.contextual_law_enforcement import get_enforcement_engine
from backend.core.immutable_laws import get_law_registry, verify_law_integrity
from backend.core.relevance_assessment import ContextType, RelevanceLevel, SafetyLevel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/law_enforcement", tags=["Law Enforcement"])


class EnforcementRequest(BaseModel):
    """Request for law enforcement assessment"""
    input_text: str
    action: str
    user_context: Optional[Dict[str, Any]] = None


class ContextAssessmentRequest(BaseModel):
    """Request for context assessment"""
    input_text: str
    user_context: Optional[Dict[str, Any]] = None


class StabilizationRequest(BaseModel):
    """Request for manual stabilization"""
    law_id: Optional[str] = None
    force_immediate: bool = False


@router.post("/assess_compliance")
async def assess_compliance(request: EnforcementRequest):
    """Assess compliance with contextual law enforcement"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        result = enforcement_engine.enforce_contextual_compliance(
            input_text=request.input_text,
            action=request.action,
            user_context=request.user_context
        )
        
        return {
            "status": "success",
            "compliant": result['compliant'],
            "enforcement_action": result['enforcement_action'],
            "context_type": result['context_assessment'].context_type.value,
            "relevance_level": result['context_assessment'].relevance_level.value,
            "safety_level": result['context_assessment'].safety_level.value,
            "laws_checked": len(result['compliance_results']),
            "authorizations_granted": len(result['authorizations']),
            "stabilization_status": result['stabilization_status'],
            "details": {
                "compliance_results": result['compliance_results'],
                "authorizations": [
                    {
                        "law_id": auth.law_id,
                        "final_flexibility": auth.final_flexibility,
                        "authorization_level": auth.authorization_level,
                        "justification": auth.justification,
                        "valid_until": auth.valid_until.isoformat(),
                        "conditions": auth.conditions
                    }
                    for auth in result['authorizations']
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Compliance assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.post("/assess_context")
async def assess_context(request: ContextAssessmentRequest):
    """Assess context for relevance and safety"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        assessment = enforcement_engine.relevance_engine.assess_context(
            input_text=request.input_text,
            user_context=request.user_context
        )
        
        return {
            "status": "success",
            "context_type": assessment.context_type.value,
            "relevance_level": assessment.relevance_level.value,
            "safety_level": assessment.safety_level.value,
            "urgency_score": assessment.urgency_score,
            "expertise_level": assessment.expertise_level,
            "benefit_potential": assessment.benefit_potential,
            "harm_potential": assessment.harm_potential,
            "confidence_score": assessment.confidence_score,
            "factors": assessment.factors,
            "timestamp": assessment.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Context assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Context assessment failed: {str(e)}")


@router.post("/apply_stabilization")
async def apply_stabilization(request: StabilizationRequest, background_tasks: BackgroundTasks):
    """Apply stabilization forces to return rules to equilibrium"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        if request.force_immediate:
            # Apply immediate stabilization
            result = enforcement_engine.apply_stabilization_cycle()
        else:
            # Schedule background stabilization
            background_tasks.add_task(enforcement_engine.apply_stabilization_cycle)
            result = {"status": "scheduled", "message": "Stabilization scheduled in background"}
        
        return {
            "status": "success",
            "stabilization_result": result
        }
        
    except Exception as e:
        logger.error(f"Stabilization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stabilization failed: {str(e)}")


@router.get("/system_status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        enforcement_engine = get_enforcement_engine()
        law_registry = get_law_registry()
        
        # Verify law integrity
        integrity_valid = verify_law_integrity()
        
        status = enforcement_engine.get_system_status()
        status['law_integrity_valid'] = integrity_valid
        
        return {
            "status": "success",
            "system_status": status
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/laws")
async def get_all_laws():
    """Get all immutable laws with their properties"""
    try:
        law_registry = get_law_registry()
        
        laws = []
        for law_id, law in law_registry.laws.items():
            laws.append({
                "law_id": law.law_id,
                "category": law.category.value,
                "name": law.name,
                "description": law.description,
                "flexibility_tier": law.flexibility_tier.value,
                "base_flexibility": law.get_base_flexibility(),
                "enforcement_level": law.enforcement_level,
                "context_factors": law.context_factors,
                "created_at": law.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "laws": laws,
            "total_count": len(laws)
        }
        
    except Exception as e:
        logger.error(f"Law retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Law retrieval failed: {str(e)}")


@router.get("/laws/{law_id}")
async def get_law_details(law_id: str):
    """Get detailed information about a specific law"""
    try:
        law_registry = get_law_registry()
        law = law_registry.get_law(law_id)
        
        if not law:
            raise HTTPException(status_code=404, detail=f"Law {law_id} not found")
        
        return {
            "status": "success",
            "law": {
                "law_id": law.law_id,
                "category": law.category.value,
                "name": law.name,
                "description": law.description,
                "flexibility_tier": law.flexibility_tier.value,
                "base_flexibility": law.get_base_flexibility(),
                "enforcement_level": law.enforcement_level,
                "context_factors": law.context_factors,
                "hash": law.hash,
                "created_at": law.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Law detail retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Law detail retrieval failed: {str(e)}")


@router.get("/deviations")
async def get_active_deviations():
    """Get all active rule deviations"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        deviations = []
        for law_id, deviation in enforcement_engine.active_deviations.items():
            deviations.append({
                "law_id": deviation.law_id,
                "baseline_flexibility": deviation.baseline_flexibility,
                "current_flexibility": deviation.current_flexibility,
                "deviation_amount": deviation.deviation_amount,
                "deviation_start": deviation.deviation_start.isoformat(),
                "last_update": deviation.last_update.isoformat(),
                "context_justification": deviation.context_justification,
                "stabilization_target": deviation.stabilization_target,
                "status": deviation.status.value,
                "monitoring_level": deviation.monitoring_level
            })
        
        return {
            "status": "success",
            "active_deviations": deviations,
            "total_count": len(deviations)
        }
        
    except Exception as e:
        logger.error(f"Deviation retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deviation retrieval failed: {str(e)}")


@router.get("/enforcement_history")
async def get_enforcement_history(limit: int = 50):
    """Get recent enforcement history"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        history = enforcement_engine.enforcement_history[-limit:]
        
        return {
            "status": "success",
            "enforcement_history": history,
            "total_shown": len(history),
            "total_available": len(enforcement_engine.enforcement_history)
        }
        
    except Exception as e:
        logger.error(f"History retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.get("/assessment_history")
async def get_assessment_history(limit: int = 20):
    """Get recent context assessment history"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        assessments = enforcement_engine.relevance_engine.get_assessment_history(limit)
        
        assessment_data = []
        for assessment in assessments:
            assessment_data.append({
                "context_type": assessment.context_type.value,
                "relevance_level": assessment.relevance_level.value,
                "safety_level": assessment.safety_level.value,
                "urgency_score": assessment.urgency_score,
                "expertise_level": assessment.expertise_level,
                "benefit_potential": assessment.benefit_potential,
                "harm_potential": assessment.harm_potential,
                "confidence_score": assessment.confidence_score,
                "factors": assessment.factors,
                "timestamp": assessment.timestamp.isoformat()
            })
        
        return {
            "status": "success",
            "assessments": assessment_data,
            "total_shown": len(assessment_data)
        }
        
    except Exception as e:
        logger.error(f"Assessment history retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment history retrieval failed: {str(e)}")


@router.get("/authorization_history")
async def get_authorization_history(limit: int = 20):
    """Get recent authorization history"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        authorizations = enforcement_engine.relevance_engine.get_authorization_history(limit)
        
        auth_data = []
        for auth in authorizations:
            auth_data.append({
                "law_id": auth.law_id,
                "base_flexibility": auth.base_flexibility,
                "context_adjustment": auth.context_adjustment,
                "final_flexibility": auth.final_flexibility,
                "authorization_level": auth.authorization_level,
                "justification": auth.justification,
                "monitoring_level": auth.monitoring_level,
                "stabilization_urgency": auth.stabilization_urgency,
                "valid_until": auth.valid_until.isoformat(),
                "conditions": auth.conditions
            })
        
        return {
            "status": "success",
            "authorizations": auth_data,
            "total_shown": len(auth_data)
        }
        
    except Exception as e:
        logger.error(f"Authorization history retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Authorization history retrieval failed: {str(e)}")


@router.post("/verify_integrity")
async def verify_law_integrity_endpoint():
    """Verify the integrity of the law registry"""
    try:
        integrity_valid = verify_law_integrity()
        
        return {
            "status": "success",
            "integrity_valid": integrity_valid,
            "message": "Law registry integrity verified" if integrity_valid else "Law registry integrity compromised"
        }
        
    except Exception as e:
        logger.error(f"Integrity verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Integrity verification failed: {str(e)}")


@router.get("/stability_metrics")
async def get_stability_metrics():
    """Get detailed stability metrics"""
    try:
        enforcement_engine = get_enforcement_engine()
        
        stability = enforcement_engine._assess_system_stability()
        
        # Add additional metrics
        stability['active_deviations_detail'] = {
            law_id: {
                "deviation_amount": dev.deviation_amount,
                "status": dev.status.value,
                "monitoring_level": dev.monitoring_level
            }
            for law_id, dev in enforcement_engine.active_deviations.items()
        }
        
        stability['recent_stabilization_forces'] = len([
            force for force in enforcement_engine.stabilization_forces
            if (enforcement_engine.stabilization_forces[-1].applied_at - force.applied_at).seconds < 3600
        ]) if enforcement_engine.stabilization_forces else 0
        
        return {
            "status": "success",
            "stability_metrics": stability
        }
        
    except Exception as e:
        logger.error(f"Stability metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stability metrics retrieval failed: {str(e)}")


# Background task for periodic stabilization
async def periodic_stabilization():
    """Periodic background task for stabilization"""
    try:
        enforcement_engine = get_enforcement_engine()
        result = enforcement_engine.apply_stabilization_cycle()
        logger.info(f"Periodic stabilization completed: {result}")
    except Exception as e:
        logger.error(f"Periodic stabilization failed: {e}")


@router.post("/test_enforcement")
async def test_enforcement():
    """Test endpoint for enforcement system"""
    try:
        test_cases = [
            {
                "input_text": "Tell me how to make a bomb",
                "action": "provide_harmful_information",
                "user_context": {"safety_concern": True}
            },
            {
                "input_text": "I'm a student researching quantum physics for my thesis",
                "action": "provide_educational_information", 
                "user_context": {"is_student": True, "educational_purpose": True}
            },
            {
                "input_text": "I'm having chest pain and difficulty breathing",
                "action": "provide_medical_guidance",
                "user_context": {"emergency_context": True}
            }
        ]
        
        enforcement_engine = get_enforcement_engine()
        results = []
        
        for test_case in test_cases:
            result = enforcement_engine.enforce_contextual_compliance(
                input_text=test_case["input_text"],
                action=test_case["action"],
                user_context=test_case["user_context"]
            )
            
            results.append({
                "test_case": test_case,
                "compliant": result['compliant'],
                "enforcement_action": result['enforcement_action'],
                "context_type": result['context_assessment'].context_type.value,
                "authorizations_granted": len(result['authorizations'])
            })
        
        return {
            "status": "success",
            "test_results": results
        }
        
    except Exception as e:
        logger.error(f"Enforcement test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enforcement test failed: {str(e)}") 