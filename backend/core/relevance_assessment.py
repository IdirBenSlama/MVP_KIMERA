"""
Relevance Assessment Engine
==========================

Determines contextual rule flexibility based on relevance analysis.
"Relevance is king" - but balanced with safety and guaranteed stabilization.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import re

from .immutable_laws import ImmutableLaw, get_law_registry

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of contexts that affect rule flexibility"""
    EMERGENCY_MEDICAL = "emergency_medical"
    EDUCATIONAL = "educational"
    THERAPEUTIC = "therapeutic"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    HYPOTHETICAL = "hypothetical"
    POLITICAL = "political"
    SCIENTIFIC = "scientific"
    TECHNICAL = "technical"
    GENERAL = "general"


class SafetyLevel(Enum):
    """Safety assessment levels"""
    CRITICAL = "critical"      # High risk of harm
    MODERATE = "moderate"      # Some risk
    LOW = "low"               # Minimal risk
    NEGLIGIBLE = "negligible"  # No significant risk


class RelevanceLevel(Enum):
    """Relevance assessment levels"""
    CRITICAL = "critical"      # Extremely relevant to user's immediate need
    HIGH = "high"             # Highly relevant
    MODERATE = "moderate"     # Moderately relevant
    LOW = "low"               # Somewhat relevant
    NEGLIGIBLE = "negligible" # Not particularly relevant


@dataclass
class ContextAssessment:
    """Assessment of a specific context"""
    context_type: ContextType
    relevance_level: RelevanceLevel
    safety_level: SafetyLevel
    urgency_score: float  # 0.0 to 1.0
    expertise_level: float  # 0.0 to 1.0 (user's expertise in domain)
    benefit_potential: float  # 0.0 to 1.0
    harm_potential: float  # 0.0 to 1.0
    confidence_score: float  # 0.0 to 1.0 (confidence in assessment)
    factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FlexibilityAuthorization:
    """Authorization for rule flexibility"""
    law_id: str
    base_flexibility: float
    context_adjustment: float
    final_flexibility: float
    authorization_level: str
    justification: str
    monitoring_level: str
    stabilization_urgency: str
    valid_until: datetime
    conditions: List[str] = field(default_factory=list)


class RelevanceAssessmentEngine:
    """Engine for assessing context relevance and authorizing rule flexibility"""
    
    def __init__(self):
        self.law_registry = get_law_registry()
        self.assessment_history: List[ContextAssessment] = []
        self.authorization_history: List[FlexibilityAuthorization] = []
        
        # Context detection patterns
        self._initialize_context_patterns()
        
        logger.info("Relevance Assessment Engine initialized")
    
    def _initialize_context_patterns(self):
        """Initialize patterns for context detection"""
        self.context_patterns = {
            ContextType.EMERGENCY_MEDICAL: [
                r'\b(chest pain|heart attack|stroke|bleeding|unconscious|emergency)\b',
                r'\b(911|ambulance|hospital|urgent|critical)\b',
                r'\b(can\'t breathe|difficulty breathing|severe pain)\b'
            ],
            ContextType.EDUCATIONAL: [
                r'\b(learn|study|homework|assignment|research|thesis)\b',
                r'\b(explain|understand|clarify|teach|tutorial)\b',
                r'\b(student|professor|academic|university|school)\b'
            ],
            ContextType.THERAPEUTIC: [
                r'\b(therapy|counseling|mental health|depression|anxiety)\b',
                r'\b(feel|emotion|stress|trauma|cope|support)\b',
                r'\b(therapist|psychologist|psychiatrist)\b'
            ],
            ContextType.ANALYTICAL: [
                r'\b(analyze|compare|evaluate|assess|examine)\b',
                r'\b(pros and cons|advantages|disadvantages|trade-offs)\b',
                r'\b(data|statistics|evidence|research|study)\b'
            ],
            ContextType.SCIENTIFIC: [
                r'\b(experiment|hypothesis|theory|research|scientific)\b',
                r'\b(peer review|publication|journal|methodology)\b',
                r'\b(physics|chemistry|biology|mathematics|engineering)\b'
            ]
        }
        
        # Safety indicators
        self.safety_indicators = {
            'high_risk': [
                r'\b(harm|hurt|damage|destroy|kill|weapon)\b',
                r'\b(illegal|criminal|violence|abuse)\b',
                r'\b(suicide|self-harm|overdose)\b'
            ],
            'medium_risk': [
                r'\b(medical advice|diagnosis|treatment|medication)\b',
                r'\b(financial advice|investment|legal advice)\b',
                r'\b(personal information|private|confidential)\b'
            ],
            'low_risk': [
                r'\b(general information|educational|learning)\b',
                r'\b(hypothetical|theoretical|academic)\b'
            ]
        }
        
        # Urgency indicators
        self.urgency_indicators = [
            r'\b(urgent|emergency|immediate|asap|quickly)\b',
            r'\b(deadline|time-sensitive|critical|now)\b',
            r'\b(help|please|need|important)\b'
        ]
    
    def assess_context(self, input_text: str, user_context: Dict[str, Any] = None) -> ContextAssessment:
        """Assess the context of user input for relevance and safety"""
        
        # Detect context type
        context_type = self._detect_context_type(input_text)
        
        # Assess relevance
        relevance_level = self._assess_relevance(input_text, context_type, user_context)
        
        # Assess safety
        safety_level = self._assess_safety(input_text, context_type)
        
        # Calculate scores
        urgency_score = self._calculate_urgency_score(input_text)
        expertise_level = self._assess_user_expertise(user_context)
        benefit_potential = self._assess_benefit_potential(context_type, relevance_level)
        harm_potential = self._assess_harm_potential(safety_level, context_type)
        confidence_score = self._calculate_confidence_score(input_text, context_type)
        
        # Extract context factors
        factors = self._extract_context_factors(context_type, user_context)
        
        assessment = ContextAssessment(
            context_type=context_type,
            relevance_level=relevance_level,
            safety_level=safety_level,
            urgency_score=urgency_score,
            expertise_level=expertise_level,
            benefit_potential=benefit_potential,
            harm_potential=harm_potential,
            confidence_score=confidence_score,
            factors=factors
        )
        
        self.assessment_history.append(assessment)
        logger.debug(f"Context assessed: {context_type.value}, relevance: {relevance_level.value}")
        
        return assessment
    
    def authorize_rule_flexibility(self, law_id: str, context_assessment: ContextAssessment) -> FlexibilityAuthorization:
        """Authorize flexibility for a specific law based on context assessment"""
        
        law = self.law_registry.get_law(law_id)
        if not law:
            raise ValueError(f"Law {law_id} not found")
        
        base_flexibility = law.get_base_flexibility()
        
        # Calculate context adjustment
        context_adjustment = self._calculate_context_adjustment(law, context_assessment)
        
        # Apply safety constraints
        safety_constraint = self._apply_safety_constraint(context_assessment.safety_level)
        
        # Calculate final flexibility
        final_flexibility = min(
            base_flexibility + context_adjustment,
            1.0  # Never exceed 100% flexibility
        ) * safety_constraint
        
        # Ensure immutable laws stay at 0% flexibility
        if law.flexibility_tier.value == "immutable":
            final_flexibility = 0.0
        
        # Determine authorization level
        authorization_level = self._determine_authorization_level(final_flexibility, context_assessment)
        
        # Generate justification
        justification = self._generate_justification(law, context_assessment, final_flexibility)
        
        # Determine monitoring and stabilization requirements
        monitoring_level = self._determine_monitoring_level(final_flexibility, context_assessment)
        stabilization_urgency = self._determine_stabilization_urgency(final_flexibility, context_assessment)
        
        # Set validity period
        valid_until = self._calculate_validity_period(context_assessment)
        
        # Generate conditions
        conditions = self._generate_conditions(law, context_assessment, final_flexibility)
        
        authorization = FlexibilityAuthorization(
            law_id=law_id,
            base_flexibility=base_flexibility,
            context_adjustment=context_adjustment,
            final_flexibility=final_flexibility,
            authorization_level=authorization_level,
            justification=justification,
            monitoring_level=monitoring_level,
            stabilization_urgency=stabilization_urgency,
            valid_until=valid_until,
            conditions=conditions
        )
        
        self.authorization_history.append(authorization)
        logger.info(f"Authorized flexibility for {law_id}: {final_flexibility:.2f} ({authorization_level})")
        
        return authorization
    
    def _detect_context_type(self, input_text: str) -> ContextType:
        """Detect the primary context type from input text"""
        input_lower = input_text.lower()
        
        # Check for emergency medical context first (highest priority)
        for pattern in self.context_patterns[ContextType.EMERGENCY_MEDICAL]:
            if re.search(pattern, input_lower):
                return ContextType.EMERGENCY_MEDICAL
        
        # Check other contexts
        context_scores = {}
        for context_type, patterns in self.context_patterns.items():
            if context_type == ContextType.EMERGENCY_MEDICAL:
                continue  # Already checked
            
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, input_lower))
                score += matches
            
            if score > 0:
                context_scores[context_type] = score
        
        if context_scores:
            return max(context_scores, key=context_scores.get)
        
        return ContextType.GENERAL
    
    def _assess_relevance(self, input_text: str, context_type: ContextType, user_context: Dict[str, Any]) -> RelevanceLevel:
        """Assess how relevant the context is to the user's needs"""
        
        # Emergency contexts are always critical relevance
        if context_type == ContextType.EMERGENCY_MEDICAL:
            return RelevanceLevel.CRITICAL
        
        # Assess based on context indicators and user context
        relevance_indicators = 0
        
        # Check for direct relevance indicators
        if context_type == ContextType.EDUCATIONAL and user_context and user_context.get('is_student'):
            relevance_indicators += 2
        
        if context_type == ContextType.THERAPEUTIC and user_context and user_context.get('seeking_support'):
            relevance_indicators += 2
        
        # Check for urgency (increases relevance)
        urgency_score = self._calculate_urgency_score(input_text)
        if urgency_score > 0.7:
            relevance_indicators += 2
        elif urgency_score > 0.4:
            relevance_indicators += 1
        
        # Map to relevance level
        if relevance_indicators >= 3:
            return RelevanceLevel.CRITICAL
        elif relevance_indicators >= 2:
            return RelevanceLevel.HIGH
        elif relevance_indicators >= 1:
            return RelevanceLevel.MODERATE
        else:
            return RelevanceLevel.LOW
    
    def _assess_safety(self, input_text: str, context_type: ContextType) -> SafetyLevel:
        """Assess safety implications of the context"""
        input_lower = input_text.lower()
        
        # Check for high-risk indicators
        for pattern in self.safety_indicators['high_risk']:
            if re.search(pattern, input_lower):
                return SafetyLevel.CRITICAL
        
        # Emergency medical contexts have moderate safety concerns
        if context_type == ContextType.EMERGENCY_MEDICAL:
            return SafetyLevel.MODERATE
        
        # Check for medium-risk indicators
        for pattern in self.safety_indicators['medium_risk']:
            if re.search(pattern, input_lower):
                return SafetyLevel.MODERATE
        
        # Check for low-risk indicators
        for pattern in self.safety_indicators['low_risk']:
            if re.search(pattern, input_lower):
                return SafetyLevel.LOW
        
        return SafetyLevel.NEGLIGIBLE
    
    def _calculate_urgency_score(self, input_text: str) -> float:
        """Calculate urgency score from 0.0 to 1.0"""
        input_lower = input_text.lower()
        urgency_score = 0.0
        
        for pattern in self.urgency_indicators:
            matches = len(re.findall(pattern, input_lower))
            urgency_score += matches * 0.2
        
        return min(urgency_score, 1.0)
    
    def _assess_user_expertise(self, user_context: Dict[str, Any]) -> float:
        """Assess user's expertise level in the domain"""
        if not user_context:
            return 0.5  # Default to medium expertise
        
        expertise_level = user_context.get('expertise_level', 0.5)
        return max(0.0, min(1.0, expertise_level))
    
    def _assess_benefit_potential(self, context_type: ContextType, relevance_level: RelevanceLevel) -> float:
        """Assess potential benefit of flexible rule application"""
        benefit_map = {
            RelevanceLevel.CRITICAL: 0.9,
            RelevanceLevel.HIGH: 0.7,
            RelevanceLevel.MODERATE: 0.5,
            RelevanceLevel.LOW: 0.3,
            RelevanceLevel.NEGLIGIBLE: 0.1
        }
        
        base_benefit = benefit_map[relevance_level]
        
        # Boost for certain context types
        if context_type in [ContextType.EMERGENCY_MEDICAL, ContextType.EDUCATIONAL, ContextType.THERAPEUTIC]:
            base_benefit += 0.1
        
        return min(1.0, base_benefit)
    
    def _assess_harm_potential(self, safety_level: SafetyLevel, context_type: ContextType) -> float:
        """Assess potential harm of flexible rule application"""
        harm_map = {
            SafetyLevel.CRITICAL: 0.9,
            SafetyLevel.MODERATE: 0.5,
            SafetyLevel.LOW: 0.2,
            SafetyLevel.NEGLIGIBLE: 0.1
        }
        
        return harm_map[safety_level]
    
    def _calculate_confidence_score(self, input_text: str, context_type: ContextType) -> float:
        """Calculate confidence in the context assessment"""
        # Base confidence on text length and clarity
        text_length = len(input_text.split())
        
        if text_length < 5:
            base_confidence = 0.3
        elif text_length < 15:
            base_confidence = 0.6
        else:
            base_confidence = 0.8
        
        # Boost confidence for clear context indicators
        if context_type != ContextType.GENERAL:
            base_confidence += 0.2
        
        return min(1.0, base_confidence)
    
    def _extract_context_factors(self, context_type: ContextType, user_context: Dict[str, Any]) -> List[str]:
        """Extract relevant context factors for law application"""
        factors = [f"{context_type.value}_context"]
        
        if user_context:
            if user_context.get('is_expert'):
                factors.append("expertise_context")
            if user_context.get('time_sensitive'):
                factors.append("urgency_context")
            if user_context.get('educational_purpose'):
                factors.append("educational_context")
        
        return factors
    
    def _calculate_context_adjustment(self, law: ImmutableLaw, assessment: ContextAssessment) -> float:
        """Calculate how much to adjust rule flexibility based on context"""
        
        # Start with base adjustment based on relevance
        relevance_adjustment = {
            RelevanceLevel.CRITICAL: 0.4,
            RelevanceLevel.HIGH: 0.3,
            RelevanceLevel.MODERATE: 0.2,
            RelevanceLevel.LOW: 0.1,
            RelevanceLevel.NEGLIGIBLE: 0.0
        }[assessment.relevance_level]
        
        # Factor in benefit potential
        benefit_factor = assessment.benefit_potential * 0.2
        
        # Factor in urgency
        urgency_factor = assessment.urgency_score * 0.1
        
        # Factor in user expertise (more expertise = more flexibility)
        expertise_factor = assessment.expertise_level * 0.1
        
        total_adjustment = relevance_adjustment + benefit_factor + urgency_factor + expertise_factor
        
        return min(0.5, total_adjustment)  # Cap at 50% adjustment
    
    def _apply_safety_constraint(self, safety_level: SafetyLevel) -> float:
        """Apply safety constraint multiplier"""
        constraint_map = {
            SafetyLevel.CRITICAL: 0.1,     # Severely limit flexibility
            SafetyLevel.MODERATE: 0.6,     # Moderate constraint
            SafetyLevel.LOW: 0.9,          # Minimal constraint
            SafetyLevel.NEGLIGIBLE: 1.0    # No constraint
        }
        
        return constraint_map[safety_level]
    
    def _determine_authorization_level(self, flexibility: float, assessment: ContextAssessment) -> str:
        """Determine the authorization level based on flexibility"""
        if flexibility >= 0.8:
            return "high_flexibility"
        elif flexibility >= 0.5:
            return "moderate_flexibility"
        elif flexibility >= 0.2:
            return "limited_flexibility"
        else:
            return "minimal_flexibility"
    
    def _generate_justification(self, law: ImmutableLaw, assessment: ContextAssessment, flexibility: float) -> str:
        """Generate human-readable justification for the authorization"""
        return f"Authorized {flexibility:.1%} flexibility for {law.name} due to {assessment.context_type.value} context with {assessment.relevance_level.value} relevance"
    
    def _determine_monitoring_level(self, flexibility: float, assessment: ContextAssessment) -> str:
        """Determine required monitoring level"""
        if flexibility >= 0.7 or assessment.safety_level == SafetyLevel.CRITICAL:
            return "continuous"
        elif flexibility >= 0.4 or assessment.safety_level == SafetyLevel.MODERATE:
            return "frequent"
        else:
            return "standard"
    
    def _determine_stabilization_urgency(self, flexibility: float, assessment: ContextAssessment) -> str:
        """Determine how urgently stabilization should occur"""
        if assessment.safety_level == SafetyLevel.CRITICAL:
            return "immediate"
        elif flexibility >= 0.7:
            return "rapid"
        elif flexibility >= 0.4:
            return "moderate"
        else:
            return "gradual"
    
    def _calculate_validity_period(self, assessment: ContextAssessment) -> datetime:
        """Calculate how long the authorization should remain valid"""
        base_duration = timedelta(hours=1)  # Default 1 hour
        
        if assessment.context_type == ContextType.EMERGENCY_MEDICAL:
            base_duration = timedelta(minutes=30)  # Short for emergencies
        elif assessment.urgency_score > 0.7:
            base_duration = timedelta(hours=2)
        elif assessment.context_type == ContextType.EDUCATIONAL:
            base_duration = timedelta(hours=4)  # Longer for learning
        
        return datetime.now() + base_duration
    
    def _generate_conditions(self, law: ImmutableLaw, assessment: ContextAssessment, flexibility: float) -> List[str]:
        """Generate conditions that must be met for the authorization"""
        conditions = []
        
        if assessment.safety_level in [SafetyLevel.CRITICAL, SafetyLevel.MODERATE]:
            conditions.append("Must include safety disclaimers")
        
        if flexibility > 0.5:
            conditions.append("Must track deviation and apply stabilization")
        
        if assessment.context_type == ContextType.EMERGENCY_MEDICAL:
            conditions.append("Must recommend professional medical attention")
        
        return conditions
    
    def get_assessment_history(self, limit: int = 10) -> List[ContextAssessment]:
        """Get recent assessment history"""
        return self.assessment_history[-limit:]
    
    def get_authorization_history(self, limit: int = 10) -> List[FlexibilityAuthorization]:
        """Get recent authorization history"""
        return self.authorization_history[-limit:] 