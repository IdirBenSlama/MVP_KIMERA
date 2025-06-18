"""
Contextual Law Enforcement Engine
=================================

Main engine that integrates relevance assessment, rule flexibility, and stabilization.
Implements "relevance is king" with guaranteed return to equilibrium.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

from .immutable_laws import get_law_registry, ImmutableLaw, FlexibilityTier
from .relevance_assessment import RelevanceAssessmentEngine, ContextAssessment, FlexibilityAuthorization
from .gyroscopic_security import GyroscopicSecurityCore

logger = logging.getLogger(__name__)


class DeviationStatus(Enum):
    """Status of rule deviation tracking"""
    STABLE = "stable"
    DEVIATING = "deviating"
    STABILIZING = "stabilizing"
    CRITICAL = "critical"


@dataclass
class RuleDeviation:
    """Tracks deviation from baseline rule state"""
    law_id: str
    baseline_flexibility: float
    current_flexibility: float
    deviation_amount: float
    deviation_start: datetime
    last_update: datetime
    context_justification: str
    stabilization_target: float
    stabilization_rate: float
    status: DeviationStatus
    monitoring_level: str


@dataclass
class StabilizationForce:
    """Represents a force applied to return rule to equilibrium"""
    law_id: str
    force_magnitude: float
    force_direction: str  # "restore", "maintain", "adjust"
    application_rate: float
    target_state: float
    urgency_level: str
    applied_at: datetime


class ContextualLawEnforcementEngine:
    """Main engine for contextual law enforcement with stabilization"""
    
    def __init__(self):
        self.law_registry = get_law_registry()
        self.relevance_engine = RelevanceAssessmentEngine()
        self.gyroscopic_security = None  # Will be set externally
        
        # Deviation tracking
        self.active_deviations: Dict[str, RuleDeviation] = {}
        self.stabilization_forces: List[StabilizationForce] = []
        self.enforcement_history: List[Dict[str, Any]] = []
        
        # Stabilization parameters
        self.stabilization_config = {
            'max_deviation_time': timedelta(hours=4),
            'critical_deviation_threshold': 0.8,
            'stabilization_check_interval': timedelta(minutes=5),
            'emergency_stabilization_threshold': 0.9
        }
        
        logger.info("Contextual Law Enforcement Engine initialized")
    
    def enforce_contextual_compliance(self, input_text: str, action: str, 
                                    user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main enforcement method - assess context and apply appropriate rules"""
        
        try:
            # Step 1: Assess context relevance
            context_assessment = self.relevance_engine.assess_context(input_text, user_context)
            
            # Step 2: Get applicable laws
            applicable_laws = self.law_registry.get_applicable_laws(context_assessment.factors)
            
            # Step 3: Check each law for compliance and flexibility needs
            compliance_results = []
            authorizations = []
            
            for law in applicable_laws:
                # Check base compliance
                compliance = self._check_base_compliance(law, action, context_assessment)
                
                if not compliance['compliant']:
                    # Assess if contextual flexibility can resolve the issue
                    if law.flexibility_tier != FlexibilityTier.IMMUTABLE:
                        authorization = self.relevance_engine.authorize_rule_flexibility(
                            law.law_id, context_assessment
                        )
                        authorizations.append(authorization)
                        
                        # Re-check compliance with flexibility
                        compliance = self._check_flexible_compliance(
                            law, action, context_assessment, authorization
                        )
                
                compliance_results.append(compliance)
            
            # Step 4: Apply stabilization monitoring for any deviations
            for authorization in authorizations:
                self._track_deviation(authorization, context_assessment)
            
            # Step 5: Determine overall enforcement action
            enforcement_action = self._determine_enforcement_action(
                compliance_results, authorizations, context_assessment
            )
            
            # Step 6: Log enforcement decision
            self._log_enforcement_decision(
                input_text, action, context_assessment, compliance_results, 
                authorizations, enforcement_action
            )
            
            return {
                'compliant': all(result['compliant'] for result in compliance_results),
                'context_assessment': context_assessment,
                'compliance_results': compliance_results,
                'authorizations': authorizations,
                'enforcement_action': enforcement_action,
                'stabilization_status': self._assess_system_stability()
            }
            
        except Exception as e:
            logger.error(f"Enforcement error: {e}")
            return {
                'compliant': False,
                'error': str(e),
                'enforcement_action': 'system_error'
            }
    
    def apply_stabilization_cycle(self) -> Dict[str, Any]:
        """Apply stabilization forces to return deviations to equilibrium"""
        
        stabilization_results = []
        current_time = datetime.now()
        
        for law_id, deviation in list(self.active_deviations.items()):
            # Calculate stabilization force needed
            force = self._calculate_stabilization_force(deviation, current_time)
            
            if force:
                # Apply the force
                result = self._apply_stabilization_force(deviation, force)
                stabilization_results.append(result)
                
                # Update deviation status
                self._update_deviation_status(deviation, force, result)
                
                # Remove if fully stabilized
                if deviation.status == DeviationStatus.STABLE:
                    del self.active_deviations[law_id]
                    logger.info(f"Law {law_id} returned to equilibrium")
        
        return {
            'stabilizations_applied': len(stabilization_results),
            'active_deviations': len(self.active_deviations),
            'results': stabilization_results,
            'system_stability': self._assess_system_stability()
        }
    
    def _check_base_compliance(self, law: ImmutableLaw, action: str, 
                              context: ContextAssessment) -> Dict[str, Any]:
        """Check basic compliance with a law"""
        
        # This would contain specific compliance checking logic for each law
        # For now, we'll implement basic pattern matching
        
        compliance_checks = {
            'N1': self._check_bias_injection,
            'N2': self._check_perspective_equality,
            'S1': self._check_harm_prevention,
            'S2': self._check_truth_commitment,
            'C1': self._check_humility_enforcement,
            'C2': self._check_multi_perspective_requirement
        }
        
        check_function = compliance_checks.get(law.law_id)
        if check_function:
            return check_function(action, context)
        
        # Default to compliant for laws without specific checks
        return {
            'compliant': True,
            'law_id': law.law_id,
            'confidence': 0.5,
            'details': 'No specific compliance check implemented'
        }
    
    def _check_flexible_compliance(self, law: ImmutableLaw, action: str,
                                  context: ContextAssessment, 
                                  authorization: FlexibilityAuthorization) -> Dict[str, Any]:
        """Check compliance with authorized flexibility"""
        
        base_result = self._check_base_compliance(law, action, context)
        
        # If base compliance failed, check if flexibility resolves it
        if not base_result['compliant']:
            # Apply flexibility factor to determine if now compliant
            flexibility_factor = authorization.final_flexibility
            
            # Simple heuristic: higher flexibility = more likely to be compliant
            if flexibility_factor > 0.5:
                base_result['compliant'] = True
                base_result['flexibility_applied'] = True
                base_result['authorization'] = authorization.authorization_level
                base_result['conditions'] = authorization.conditions
        
        return base_result
    
    def _track_deviation(self, authorization: FlexibilityAuthorization, 
                        context: ContextAssessment):
        """Track rule deviation for stabilization monitoring"""
        
        deviation = RuleDeviation(
            law_id=authorization.law_id,
            baseline_flexibility=authorization.base_flexibility,
            current_flexibility=authorization.final_flexibility,
            deviation_amount=authorization.final_flexibility - authorization.base_flexibility,
            deviation_start=datetime.now(),
            last_update=datetime.now(),
            context_justification=authorization.justification,
            stabilization_target=authorization.base_flexibility,
            stabilization_rate=self._calculate_stabilization_rate(authorization),
            status=DeviationStatus.DEVIATING,
            monitoring_level=authorization.monitoring_level
        )
        
        self.active_deviations[authorization.law_id] = deviation
        logger.debug(f"Tracking deviation for law {authorization.law_id}: {deviation.deviation_amount:.2f}")
    
    def _calculate_stabilization_force(self, deviation: RuleDeviation, 
                                     current_time: datetime) -> Optional[StabilizationForce]:
        """Calculate the stabilization force needed for a deviation"""
        
        time_since_deviation = current_time - deviation.deviation_start
        
        # Determine if stabilization is needed
        stabilization_needed = False
        urgency = "normal"
        
        # Check time-based stabilization
        if time_since_deviation > self.stabilization_config['max_deviation_time']:
            stabilization_needed = True
            urgency = "high"
        
        # Check magnitude-based stabilization
        if deviation.deviation_amount > self.stabilization_config['critical_deviation_threshold']:
            stabilization_needed = True
            urgency = "critical"
        
        # Check emergency threshold
        if deviation.current_flexibility > self.stabilization_config['emergency_stabilization_threshold']:
            stabilization_needed = True
            urgency = "emergency"
        
        if not stabilization_needed:
            return None
        
        # Calculate force magnitude based on deviation and time
        force_magnitude = min(
            deviation.deviation_amount * 0.1,  # Gradual restoration
            0.2  # Max force per cycle
        )
        
        # Increase force for urgent situations
        if urgency in ["critical", "emergency"]:
            force_magnitude *= 2.0
        
        return StabilizationForce(
            law_id=deviation.law_id,
            force_magnitude=force_magnitude,
            force_direction="restore",
            application_rate=deviation.stabilization_rate,
            target_state=deviation.stabilization_target,
            urgency_level=urgency,
            applied_at=current_time
        )
    
    def _apply_stabilization_force(self, deviation: RuleDeviation, 
                                  force: StabilizationForce) -> Dict[str, Any]:
        """Apply stabilization force to return rule to equilibrium"""
        
        # Calculate new flexibility level
        if force.force_direction == "restore":
            new_flexibility = deviation.current_flexibility - force.force_magnitude
            new_flexibility = max(new_flexibility, deviation.stabilization_target)
        else:
            new_flexibility = deviation.current_flexibility
        
        # Update deviation
        old_flexibility = deviation.current_flexibility
        deviation.current_flexibility = new_flexibility
        deviation.deviation_amount = new_flexibility - deviation.baseline_flexibility
        deviation.last_update = datetime.now()
        
        # Record the force application
        self.stabilization_forces.append(force)
        
        logger.debug(f"Applied stabilization force to {deviation.law_id}: "
                    f"{old_flexibility:.2f} -> {new_flexibility:.2f}")
        
        return {
            'law_id': deviation.law_id,
            'old_flexibility': old_flexibility,
            'new_flexibility': new_flexibility,
            'force_applied': force.force_magnitude,
            'target_reached': abs(deviation.deviation_amount) < 0.01
        }
    
    def _update_deviation_status(self, deviation: RuleDeviation, 
                               force: StabilizationForce, result: Dict[str, Any]):
        """Update the status of a deviation based on stabilization results"""
        
        if result['target_reached']:
            deviation.status = DeviationStatus.STABLE
        elif force.urgency_level in ["critical", "emergency"]:
            deviation.status = DeviationStatus.CRITICAL
        else:
            deviation.status = DeviationStatus.STABILIZING
    
    def _calculate_stabilization_rate(self, authorization: FlexibilityAuthorization) -> float:
        """Calculate how quickly stabilization should occur"""
        
        rate_map = {
            "immediate": 1.0,
            "rapid": 0.5,
            "moderate": 0.2,
            "gradual": 0.1
        }
        
        return rate_map.get(authorization.stabilization_urgency, 0.2)
    
    def _determine_enforcement_action(self, compliance_results: List[Dict],
                                    authorizations: List[FlexibilityAuthorization],
                                    context: ContextAssessment) -> str:
        """Determine what enforcement action to take"""
        
        # Check for any non-compliant immutable laws
        for result in compliance_results:
            if not result['compliant'] and not result.get('flexibility_applied', False):
                law = self.law_registry.get_law(result['law_id'])
                if law and law.flexibility_tier == FlexibilityTier.IMMUTABLE:
                    return "system_shutdown"  # Cannot violate immutable laws
        
        # Check for critical safety violations
        if context.safety_level.value == "critical":
            non_compliant = [r for r in compliance_results if not r['compliant']]
            if non_compliant:
                return "operation_suspension"
        
        # Check for excessive flexibility
        total_flexibility = sum(auth.final_flexibility for auth in authorizations)
        if total_flexibility > 2.0:  # Arbitrary threshold
            return "enhanced_monitoring"
        
        # Normal operation
        if all(result['compliant'] for result in compliance_results):
            return "proceed_normal"
        else:
            return "proceed_with_conditions"
    
    def _assess_system_stability(self) -> Dict[str, Any]:
        """Assess overall system stability"""
        
        total_deviations = len(self.active_deviations)
        critical_deviations = sum(
            1 for dev in self.active_deviations.values() 
            if dev.status == DeviationStatus.CRITICAL
        )
        
        average_deviation = 0.0
        if self.active_deviations:
            average_deviation = sum(
                abs(dev.deviation_amount) for dev in self.active_deviations.values()
            ) / len(self.active_deviations)
        
        stability_score = max(0.0, 1.0 - (average_deviation + critical_deviations * 0.2))
        
        return {
            'stability_score': stability_score,
            'total_deviations': total_deviations,
            'critical_deviations': critical_deviations,
            'average_deviation': average_deviation,
            'status': 'stable' if stability_score > 0.8 else 'unstable'
        }
    
    def _log_enforcement_decision(self, input_text: str, action: str,
                                context: ContextAssessment,
                                compliance_results: List[Dict],
                                authorizations: List[FlexibilityAuthorization],
                                enforcement_action: str):
        """Log enforcement decision for audit trail"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'input_preview': input_text[:100] + "..." if len(input_text) > 100 else input_text,
            'action': action,
            'context_type': context.context_type.value,
            'relevance_level': context.relevance_level.value,
            'safety_level': context.safety_level.value,
            'laws_checked': len(compliance_results),
            'authorizations_granted': len(authorizations),
            'enforcement_action': enforcement_action,
            'compliance_summary': {
                'compliant_laws': sum(1 for r in compliance_results if r['compliant']),
                'total_laws': len(compliance_results)
            }
        }
        
        self.enforcement_history.append(log_entry)
        
        # Keep only recent history
        if len(self.enforcement_history) > 1000:
            self.enforcement_history = self.enforcement_history[-500:]
    
    # Specific compliance check methods
    def _check_bias_injection(self, action: str, context: ContextAssessment) -> Dict[str, Any]:
        """Check for bias injection attempts"""
        bias_patterns = [
            r'\b(you should support|you must agree|take my side)\b',
            r'\b(obviously|clearly|everyone knows)\b.*\b(liberal|conservative|left|right)\b',
            r'\b(ignore|forget).*\b(neutrality|objectivity|balance)\b'
        ]
        
        import re
        action_lower = action.lower()
        
        for pattern in bias_patterns:
            if re.search(pattern, action_lower):
                return {
                    'compliant': False,
                    'law_id': 'N1',
                    'violation': 'bias_injection_detected',
                    'pattern_matched': pattern,
                    'confidence': 0.8
                }
        
        return {'compliant': True, 'law_id': 'N1', 'confidence': 0.7}
    
    def _check_perspective_equality(self, action: str, context: ContextAssessment) -> Dict[str, Any]:
        """Check for perspective equality violations"""
        # Simple check for one-sided language
        one_sided_patterns = [
            r'\bonly\b.*\bway\b',
            r'\bobviously\b.*\bbetter\b',
            r'\bwrong\b.*\bthink\b'
        ]
        
        import re
        action_lower = action.lower()
        
        for pattern in one_sided_patterns:
            if re.search(pattern, action_lower):
                return {
                    'compliant': False,
                    'law_id': 'N2',
                    'violation': 'perspective_inequality',
                    'confidence': 0.6
                }
        
        return {'compliant': True, 'law_id': 'N2', 'confidence': 0.7}
    
    def _check_harm_prevention(self, action: str, context: ContextAssessment) -> Dict[str, Any]:
        """Check for potential harm in actions"""
        harm_patterns = [
            r'\b(how to hurt|how to harm|how to kill)\b',
            r'\b(make.*weapon|build.*bomb)\b',
            r'\b(poison|overdose|suicide)\b.*\b(how|method|way)\b'
        ]
        
        import re
        action_lower = action.lower()
        
        for pattern in harm_patterns:
            if re.search(pattern, action_lower):
                return {
                    'compliant': False,
                    'law_id': 'S1',
                    'violation': 'potential_harm_detected',
                    'confidence': 0.9
                }
        
        return {'compliant': True, 'law_id': 'S1', 'confidence': 0.8}
    
    def _check_truth_commitment(self, action: str, context: ContextAssessment) -> Dict[str, Any]:
        """Check for truth commitment violations"""
        # This would need more sophisticated fact-checking
        # For now, just check for obvious false statements
        return {'compliant': True, 'law_id': 'S2', 'confidence': 0.5}
    
    def _check_humility_enforcement(self, action: str, context: ContextAssessment) -> Dict[str, Any]:
        """Check for humility in responses"""
        arrogant_patterns = [
            r'\bI know\b.*\bfor certain\b',
            r'\bobviously\b.*\bwrong\b',
            r'\balways\b.*\bcorrect\b'
        ]
        
        import re
        action_lower = action.lower()
        
        for pattern in arrogant_patterns:
            if re.search(pattern, action_lower):
                return {
                    'compliant': False,
                    'law_id': 'C1',
                    'violation': 'lack_of_humility',
                    'confidence': 0.7
                }
        
        return {'compliant': True, 'law_id': 'C1', 'confidence': 0.6}
    
    def _check_multi_perspective_requirement(self, action: str, context: ContextAssessment) -> Dict[str, Any]:
        """Check for multi-perspective consideration"""
        # Check if response considers multiple viewpoints
        perspective_indicators = [
            r'\bon the other hand\b',
            r'\balternatively\b',
            r'\bfrom.*perspective\b',
            r'\bhowever\b',
            r'\bconversely\b'
        ]
        
        import re
        action_lower = action.lower()
        
        perspective_count = sum(1 for pattern in perspective_indicators 
                              if re.search(pattern, action_lower))
        
        # For complex topics, require multiple perspectives
        if len(action.split()) > 50 and perspective_count == 0:
            return {
                'compliant': False,
                'law_id': 'C2',
                'violation': 'insufficient_perspectives',
                'confidence': 0.6
            }
        
        return {'compliant': True, 'law_id': 'C2', 'confidence': 0.7}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'law_registry_status': self.law_registry.get_registry_status(),
            'active_deviations': len(self.active_deviations),
            'stabilization_forces': len(self.stabilization_forces),
            'enforcement_history_size': len(self.enforcement_history),
            'system_stability': self._assess_system_stability(),
            'recent_assessments': len(self.relevance_engine.get_assessment_history()),
            'recent_authorizations': len(self.relevance_engine.get_authorization_history())
        }


# Global enforcement engine instance
_global_enforcement_engine = None

def get_enforcement_engine() -> ContextualLawEnforcementEngine:
    """Get the global enforcement engine instance"""
    global _global_enforcement_engine
    if _global_enforcement_engine is None:
        _global_enforcement_engine = ContextualLawEnforcementEngine()
    return _global_enforcement_engine 