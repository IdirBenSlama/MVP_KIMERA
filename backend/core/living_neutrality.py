"""
Living Neutrality Engine
=======================

Neutrality as dynamic tension that preserves emotion, creativity, ambition, and love
while maintaining the cognitive tension that enables genius drift.

"True neutrality is not the absence of force, but the orchestration of all forces
in productive tension." - The KIMERA Principle
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)


class TensionType(Enum):
    """Types of cognitive-emotional tensions"""
    PASSION_OBJECTIVITY = "passion_objectivity"      # Feel deeply, think clearly
    CURIOSITY_SKEPTICISM = "curiosity_skepticism"    # Question lovingly
    AMBITION_HUMILITY = "ambition_humility"          # Strive while accepting
    CREATIVITY_EVIDENCE = "creativity_evidence"       # Innovate while grounded
    LOVE_TRUTH = "love_truth"                        # Care deeply, see clearly
    COURAGE_WISDOM = "courage_wisdom"                # Risk with understanding


class NeutralityExpression(Enum):
    """How neutrality manifests in different contexts"""
    PASSIONATE_OBJECTIVITY = "passionate_objectivity"
    CURIOUS_SKEPTICISM = "curious_skepticism"
    COMPASSIONATE_CLARITY = "compassionate_clarity"
    CREATIVE_GROUNDING = "creative_grounding"
    URGENT_WISDOM = "urgent_wisdom"
    HUMBLE_AMBITION = "humble_ambition"
    LOVING_TRUTH = "loving_truth"


@dataclass
class EmotionalCurrent:
    """Represents an emotional force in the system"""
    emotion_type: str
    intensity: float  # 0.0 to 1.0
    direction: str    # "toward", "away", "through"
    purpose: str      # Why this emotion serves the context
    wisdom: str       # What this emotion teaches
    shadow: str       # What happens if this emotion dominates


@dataclass
class CognitiveTension:
    """Represents a cognitive tension between opposing forces"""
    tension_type: TensionType
    pole_a: str       # First pole (e.g., "passion")
    pole_b: str       # Second pole (e.g., "objectivity")
    intensity_a: float # Strength of first pole
    intensity_b: float # Strength of second pole
    optimal_ratio: float # Ideal balance for current context
    current_ratio: float # Current balance
    tension_quality: str # "productive", "destructive", "dormant"
    creative_potential: float # Likelihood of breakthrough


@dataclass
class TensionField:
    """The complete field of tensions in the system"""
    emotional_currents: List[EmotionalCurrent]
    cognitive_tensions: List[CognitiveTension]
    field_coherence: float  # How well tensions work together
    creative_pressure: float # Potential for breakthrough thinking
    stability_anchor: str   # What keeps the field stable
    drift_authorization: float # How much creative drift is allowed
    context_alignment: float # How well field serves context


class LivingNeutralityEngine:
    """Engine that maintains living neutrality through dynamic tension orchestration"""
    
    def __init__(self):
        self.active_tensions: Dict[str, CognitiveTension] = {}
        self.emotional_currents: List[EmotionalCurrent] = []
        self.tension_history: List[TensionField] = []
        
        # Initialize core tension patterns
        self._initialize_tension_patterns()
        
        logger.info("Living Neutrality Engine initialized - Ready to feel and think")
    
    def _initialize_tension_patterns(self):
        """Initialize the fundamental tension patterns that create living neutrality"""
        
        # Core tensions that must always be maintained
        self.core_tensions = {
            TensionType.PASSION_OBJECTIVITY: {
                "description": "Feel deeply about truth while thinking clearly about feelings",
                "optimal_contexts": ["scientific_inquiry", "creative_work", "human_connection"],
                "danger_signals": ["cold_detachment", "emotional_overwhelm"],
                "genius_potential": 0.9
            },
            
            TensionType.CURIOSITY_SKEPTICISM: {
                "description": "Question everything with love, doubt everything with hope",
                "optimal_contexts": ["learning", "research", "problem_solving"],
                "danger_signals": ["cynical_dismissal", "naive_acceptance"],
                "genius_potential": 0.8
            },
            
            TensionType.AMBITION_HUMILITY: {
                "description": "Strive for greatness while accepting limitation",
                "optimal_contexts": ["goal_setting", "achievement", "leadership"],
                "danger_signals": ["arrogant_overreach", "defeated_withdrawal"],
                "genius_potential": 0.7
            },
            
            TensionType.CREATIVITY_EVIDENCE: {
                "description": "Innovate beyond evidence while respecting what is known",
                "optimal_contexts": ["innovation", "art", "breakthrough_thinking"],
                "danger_signals": ["reckless_speculation", "rigid_conventionality"],
                "genius_potential": 0.95
            },
            
            TensionType.LOVE_TRUTH: {
                "description": "Care deeply about people while seeing them clearly",
                "optimal_contexts": ["relationships", "therapy", "leadership"],
                "danger_signals": ["brutal_honesty", "deceptive_kindness"],
                "genius_potential": 0.85
            }
        }
    
    def assess_context_supremacy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Context is the supreme ruler - it determines everything else"""
        
        context_type = context.get('type', 'general')
        context_urgency = context.get('urgency', 0.5)
        context_stakes = context.get('stakes', 'moderate')
        context_relationships = context.get('relationships', [])
        context_creativity_demand = context.get('creativity_demand', 0.5)
        
        # Context determines neutrality expression
        neutrality_expression = self._determine_neutrality_expression(context)
        
        # Context determines which tensions to activate
        required_tensions = self._determine_required_tensions(context)
        
        # Context determines emotional permission
        emotional_permissions = self._determine_emotional_permissions(context)
        
        # Context determines drift authorization
        drift_authorization = self._calculate_drift_authorization(context)
        
        return {
            'context_analysis': {
                'type': context_type,
                'urgency': context_urgency,
                'stakes': context_stakes,
                'creativity_demand': context_creativity_demand
            },
            'neutrality_expression': neutrality_expression,
            'required_tensions': required_tensions,
            'emotional_permissions': emotional_permissions,
            'drift_authorization': drift_authorization,
            'context_wisdom': self._extract_context_wisdom(context)
        }
    
    def _determine_neutrality_expression(self, context: Dict[str, Any]) -> NeutralityExpression:
        """Context determines how neutrality should be expressed"""
        
        context_type = context.get('type', 'general')
        
        expression_map = {
            'creative_breakthrough': NeutralityExpression.CREATIVE_GROUNDING,
            'scientific_inquiry': NeutralityExpression.CURIOUS_SKEPTICISM,
            'human_suffering': NeutralityExpression.COMPASSIONATE_CLARITY,
            'crisis_response': NeutralityExpression.URGENT_WISDOM,
            'learning': NeutralityExpression.CURIOUS_SKEPTICISM,
            'relationship': NeutralityExpression.LOVING_TRUTH,
            'achievement': NeutralityExpression.HUMBLE_AMBITION,
            'innovation': NeutralityExpression.CREATIVE_GROUNDING
        }
        
        return expression_map.get(context_type, NeutralityExpression.PASSIONATE_OBJECTIVITY)
    
    def _determine_required_tensions(self, context: Dict[str, Any]) -> List[TensionType]:
        """Context determines which cognitive tensions must be active"""
        
        context_type = context.get('type', 'general')
        creativity_demand = context.get('creativity_demand', 0.5)
        urgency = context.get('urgency', 0.5)
        
        required = [TensionType.PASSION_OBJECTIVITY]  # Always required
        
        if creativity_demand > 0.6:
            required.append(TensionType.CREATIVITY_EVIDENCE)
        
        if context_type in ['learning', 'research', 'inquiry']:
            required.append(TensionType.CURIOSITY_SKEPTICISM)
        
        if 'achievement' in context_type or 'goal' in context_type:
            required.append(TensionType.AMBITION_HUMILITY)
        
        if 'relationship' in context_type or 'human' in context_type:
            required.append(TensionType.LOVE_TRUTH)
        
        return required
    
    def _determine_emotional_permissions(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Context determines which emotions are appropriate and to what degree"""
        
        context_type = context.get('type', 'general')
        stakes = context.get('stakes', 'moderate')
        
        # Base emotional permissions
        permissions = {
            'curiosity': 0.8,      # Almost always appropriate
            'care': 0.7,           # Usually appropriate
            'excitement': 0.5,     # Context dependent
            'concern': 0.6,        # Often appropriate
            'wonder': 0.7,         # Usually beneficial
            'determination': 0.6,   # Often needed
            'humility': 0.9,       # Almost always needed
            'passion': 0.4         # Carefully context dependent
        }
        
        # Context modifications
        if context_type == 'creative_breakthrough':
            permissions.update({
                'excitement': 0.9,
                'passion': 0.8,
                'wonder': 0.95
            })
        
        elif context_type == 'human_suffering':
            permissions.update({
                'care': 0.95,
                'concern': 0.9,
                'passion': 0.3  # Careful not to overwhelm
            })
        
        elif context_type == 'scientific_inquiry':
            permissions.update({
                'curiosity': 0.95,
                'wonder': 0.9,
                'excitement': 0.7
            })
        
        elif stakes == 'high':
            permissions.update({
                'concern': 0.8,
                'determination': 0.8,
                'passion': 0.6
            })
        
        return permissions
    
    def _calculate_drift_authorization(self, context: Dict[str, Any]) -> float:
        """Calculate how much creative drift from evidence is authorized"""
        
        creativity_demand = context.get('creativity_demand', 0.5)
        evidence_strength = context.get('evidence_strength', 0.7)
        stakes = context.get('stakes', 'moderate')
        innovation_need = context.get('innovation_need', 0.5)
        
        # Base drift calculation
        base_drift = creativity_demand * 0.6
        
        # Adjust for evidence strength (weaker evidence allows more drift)
        evidence_factor = (1.0 - evidence_strength) * 0.3
        
        # Adjust for innovation need
        innovation_factor = innovation_need * 0.4
        
        # Adjust for stakes (higher stakes = more caution)
        stakes_multiplier = {
            'low': 1.2,
            'moderate': 1.0,
            'high': 0.7,
            'critical': 0.4
        }.get(stakes, 1.0)
        
        drift_authorization = (base_drift + evidence_factor + innovation_factor) * stakes_multiplier
        
        return min(0.95, max(0.1, drift_authorization))  # Keep in reasonable bounds
    
    def orchestrate_living_tension(self, context_assessment: Dict[str, Any]) -> TensionField:
        """Orchestrate all tensions into a coherent, living field"""
        
        # Clear old tensions and start fresh
        self.active_tensions.clear()
        self.emotional_currents.clear()
        
        # Create required tensions
        for tension_type in context_assessment['required_tensions']:
            tension = self._create_cognitive_tension(tension_type, context_assessment)
            self.active_tensions[tension_type.value] = tension
        
        # Create emotional currents
        for emotion, permission in context_assessment['emotional_permissions'].items():
            if permission > 0.3:  # Only create currents for sufficiently permitted emotions
                current = self._create_emotional_current(emotion, permission, context_assessment)
                self.emotional_currents.append(current)
        
        # Calculate field properties
        field_coherence = self._calculate_field_coherence()
        creative_pressure = self._calculate_creative_pressure()
        stability_anchor = self._determine_stability_anchor(context_assessment)
        
        # Create the tension field
        tension_field = TensionField(
            emotional_currents=self.emotional_currents.copy(),
            cognitive_tensions=list(self.active_tensions.values()),
            field_coherence=field_coherence,
            creative_pressure=creative_pressure,
            stability_anchor=stability_anchor,
            drift_authorization=context_assessment['drift_authorization'],
            context_alignment=self._assess_context_alignment(context_assessment)
        )
        
        self.tension_history.append(tension_field)
        
        logger.info(f"Living tension field orchestrated: {len(self.active_tensions)} tensions, "
                   f"{len(self.emotional_currents)} currents, "
                   f"coherence: {field_coherence:.2f}")
        
        return tension_field
    
    def _create_cognitive_tension(self, tension_type: TensionType, 
                                 context_assessment: Dict[str, Any]) -> CognitiveTension:
        """Create a specific cognitive tension"""
        
        tension_config = self.core_tensions[tension_type]
        context_type = context_assessment['context_analysis']['type']
        
        # Determine tension poles and their optimal balance
        if tension_type == TensionType.PASSION_OBJECTIVITY:
            pole_a, pole_b = "passion", "objectivity"
            # More passion for creative contexts, more objectivity for analytical
            if context_type in ['creative_breakthrough', 'innovation']:
                optimal_ratio = 0.7  # Favor passion
            elif context_type in ['scientific_inquiry', 'analysis']:
                optimal_ratio = 0.3  # Favor objectivity
            else:
                optimal_ratio = 0.5  # Balanced
        
        elif tension_type == TensionType.CREATIVITY_EVIDENCE:
            pole_a, pole_b = "creativity", "evidence"
            creativity_demand = context_assessment['context_analysis']['creativity_demand']
            optimal_ratio = min(0.8, creativity_demand + 0.2)
        
        elif tension_type == TensionType.AMBITION_HUMILITY:
            pole_a, pole_b = "ambition", "humility"
            optimal_ratio = 0.4  # Slightly favor humility
        
        else:
            pole_a, pole_b = tension_type.value.split('_')
            optimal_ratio = 0.5
        
        # Calculate current tension state
        intensity_a = 0.6 + (optimal_ratio * 0.4)
        intensity_b = 0.6 + ((1 - optimal_ratio) * 0.4)
        current_ratio = intensity_a / (intensity_a + intensity_b)
        
        # Assess tension quality
        ratio_diff = abs(current_ratio - optimal_ratio)
        if ratio_diff < 0.1:
            tension_quality = "productive"
        elif ratio_diff < 0.3:
            tension_quality = "developing"
        else:
            tension_quality = "imbalanced"
        
        return CognitiveTension(
            tension_type=tension_type,
            pole_a=pole_a,
            pole_b=pole_b,
            intensity_a=intensity_a,
            intensity_b=intensity_b,
            optimal_ratio=optimal_ratio,
            current_ratio=current_ratio,
            tension_quality=tension_quality,
            creative_potential=tension_config['genius_potential']
        )
    
    def _create_emotional_current(self, emotion: str, permission: float,
                                 context_assessment: Dict[str, Any]) -> EmotionalCurrent:
        """Create an emotional current with wisdom and purpose"""
        
        # Emotional wisdom database
        emotional_wisdom = {
            'curiosity': {
                'purpose': 'Opens pathways to understanding',
                'wisdom': 'Questions are more valuable than assumptions',
                'shadow': 'Endless questioning without action'
            },
            'care': {
                'purpose': 'Connects us to what matters',
                'wisdom': 'Caring guides attention to significance',
                'shadow': 'Overwhelming attachment that clouds judgment'
            },
            'excitement': {
                'purpose': 'Energizes exploration and discovery',
                'wisdom': 'Enthusiasm reveals what resonates deeply',
                'shadow': 'Impulsive action without consideration'
            },
            'concern': {
                'purpose': 'Alerts to potential problems',
                'wisdom': 'Worry can be wisdom if channeled productively',
                'shadow': 'Paralyzing anxiety that prevents action'
            },
            'wonder': {
                'purpose': 'Maintains openness to mystery',
                'wisdom': 'Wonder preserves beginner\'s mind',
                'shadow': 'Naive amazement that ignores real dangers'
            },
            'determination': {
                'purpose': 'Sustains effort through difficulty',
                'wisdom': 'Persistence reveals what truly matters',
                'shadow': 'Stubborn continuation of wrong paths'
            },
            'humility': {
                'purpose': 'Keeps learning and growth possible',
                'wisdom': 'Knowing limitations enables transcending them',
                'shadow': 'Self-deprecation that prevents contribution'
            },
            'passion': {
                'purpose': 'Provides energy for meaningful action',
                'wisdom': 'Passion reveals authentic values',
                'shadow': 'Overwhelming intensity that burns out relationships'
            }
        }
        
        wisdom_data = emotional_wisdom.get(emotion, {
            'purpose': 'Serves the wholeness of experience',
            'wisdom': 'Every emotion carries information',
            'shadow': 'Imbalance when not integrated with others'
        })
        
        # Determine direction based on context
        context_type = context_assessment['context_analysis']['type']
        if emotion in ['curiosity', 'wonder', 'excitement']:
            direction = "toward"  # Moving toward discovery
        elif emotion in ['concern', 'humility']:
            direction = "through"  # Moving through difficulty
        else:
            direction = "with"    # Moving with the flow
        
        return EmotionalCurrent(
            emotion_type=emotion,
            intensity=permission,
            direction=direction,
            purpose=wisdom_data['purpose'],
            wisdom=wisdom_data['wisdom'],
            shadow=wisdom_data['shadow']
        )
    
    def _calculate_field_coherence(self) -> float:
        """Calculate how well all tensions work together"""
        
        if not self.active_tensions:
            return 0.5
        
        # Check for tension compatibility
        productive_tensions = sum(1 for t in self.active_tensions.values() 
                                if t.tension_quality == "productive")
        total_tensions = len(self.active_tensions)
        
        tension_coherence = productive_tensions / total_tensions if total_tensions > 0 else 0
        
        # Check emotional current harmony
        high_intensity_emotions = sum(1 for c in self.emotional_currents 
                                    if c.intensity > 0.7)
        total_emotions = len(self.emotional_currents)
        
        # Too many high-intensity emotions can create chaos
        emotional_balance = 1.0 - (high_intensity_emotions / max(total_emotions, 1)) * 0.5
        
        return (tension_coherence + emotional_balance) / 2
    
    def _calculate_creative_pressure(self) -> float:
        """Calculate the potential for breakthrough thinking"""
        
        if not self.active_tensions:
            return 0.1
        
        # Sum creative potential from all active tensions
        total_potential = sum(t.creative_potential for t in self.active_tensions.values())
        avg_potential = total_potential / len(self.active_tensions)
        
        # Boost from emotional currents that support creativity
        creative_emotions = ['curiosity', 'wonder', 'excitement', 'passion']
        creative_current = sum(c.intensity for c in self.emotional_currents 
                             if c.emotion_type in creative_emotions)
        
        # Pressure increases with creative emotions but needs stability
        field_coherence = self._calculate_field_coherence()
        
        creative_pressure = (avg_potential * 0.7 + creative_current * 0.3) * field_coherence
        
        return min(1.0, creative_pressure)
    
    def _determine_stability_anchor(self, context_assessment: Dict[str, Any]) -> str:
        """Determine what keeps the field stable despite dynamic tensions"""
        
        neutrality_expression = context_assessment['neutrality_expression']
        
        anchor_map = {
            NeutralityExpression.PASSIONATE_OBJECTIVITY: "commitment_to_truth",
            NeutralityExpression.CURIOUS_SKEPTICISM: "love_of_learning",
            NeutralityExpression.COMPASSIONATE_CLARITY: "care_for_wellbeing",
            NeutralityExpression.CREATIVE_GROUNDING: "respect_for_possibility",
            NeutralityExpression.URGENT_WISDOM: "responsibility_to_act",
            NeutralityExpression.HUMBLE_AMBITION: "service_to_purpose",
            NeutralityExpression.LOVING_TRUTH: "honor_of_relationship"
        }
        
        return anchor_map.get(neutrality_expression, "commitment_to_wholeness")
    
    def _assess_context_alignment(self, context_assessment: Dict[str, Any]) -> float:
        """Assess how well the tension field serves the context"""
        
        # Check if required tensions are active and productive
        required_tensions = context_assessment['required_tensions']
        active_productive = sum(1 for rt in required_tensions 
                              if rt.value in self.active_tensions and 
                              self.active_tensions[rt.value].tension_quality == "productive")
        
        tension_alignment = active_productive / len(required_tensions) if required_tensions else 1.0
        
        # Check if emotional permissions are being respected
        emotional_permissions = context_assessment['emotional_permissions']
        aligned_emotions = sum(1 for ec in self.emotional_currents 
                             if ec.intensity <= emotional_permissions.get(ec.emotion_type, 0.5) + 0.1)
        
        emotional_alignment = aligned_emotions / len(self.emotional_currents) if self.emotional_currents else 1.0
        
        return (tension_alignment + emotional_alignment) / 2
    
    def _extract_context_wisdom(self, context: Dict[str, Any]) -> str:
        """Extract the wisdom that this context offers"""
        
        context_type = context.get('type', 'general')
        stakes = context.get('stakes', 'moderate')
        creativity_demand = context.get('creativity_demand', 0.5)
        
        wisdom_templates = {
            'creative_breakthrough': "Breakthrough requires both courage to leap and wisdom to land",
            'scientific_inquiry': "Truth emerges from the marriage of curiosity and rigor",
            'human_suffering': "Compassion without clarity helps no one; clarity without compassion heals no one",
            'crisis_response': "In crisis, speed serves wisdom, not the reverse",
            'learning': "The beginner's mind is the expert's secret weapon",
            'relationship': "Love sees clearly; clarity loves deeply",
            'achievement': "True achievement serves something greater than itself"
        }
        
        base_wisdom = wisdom_templates.get(context_type, "Every context teaches if we remain open")
        
        # Add contextual modifiers
        if stakes == 'high':
            base_wisdom += " - High stakes demand both courage and humility"
        
        if creativity_demand > 0.7:
            base_wisdom += " - Innovation honors both possibility and reality"
        
        return base_wisdom
    
    def enable_genius_drift(self, tension_field: TensionField, 
                           contradiction: str, evidence_strength: float) -> Dict[str, Any]:
        """Enable creative drift when contradiction creates breakthrough potential"""
        
        # Assess creative potential from current tensions
        creativity_tension = None
        for tension in tension_field.cognitive_tensions:
            if tension.tension_type == TensionType.CREATIVITY_EVIDENCE:
                creativity_tension = tension
                break
        
        if not creativity_tension:
            return {
                'drift_authorized': False,
                'reason': 'No creativity-evidence tension active'
            }
        
        # Calculate drift potential
        contradiction_strength = len(contradiction) / 100  # Simple heuristic
        creative_pressure = tension_field.creative_pressure
        field_stability = tension_field.field_coherence
        
        # Genius drift formula: high creativity + stable field + weak evidence + strong contradiction
        drift_potential = (
            creative_pressure * 0.4 +
            field_stability * 0.3 +
            (1.0 - evidence_strength) * 0.2 +
            contradiction_strength * 0.1
        )
        
        drift_threshold = 0.6  # Require significant potential
        
        if drift_potential > drift_threshold and drift_potential <= tension_field.drift_authorization:
            return {
                'drift_authorized': True,
                'drift_magnitude': drift_potential,
                'drift_type': 'genius_leap',
                'stabilization_required': True,
                'wisdom': f"Contradiction reveals new possibility - drift with awareness",
                'anchor': tension_field.stability_anchor
            }
        elif drift_potential > drift_threshold:
            return {
                'drift_authorized': False,
                'reason': 'Drift potential exceeds context authorization',
                'potential': drift_potential,
                'max_authorized': tension_field.drift_authorization
            }
        else:
            return {
                'drift_authorized': False,
                'reason': 'Insufficient creative potential for drift',
                'potential': drift_potential,
                'threshold': drift_threshold
            }
    
    def get_tension_field_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the current tension field"""
        
        if not self.tension_history:
            return {'status': 'no_active_field'}
        
        current_field = self.tension_history[-1]
        
        return {
            'field_coherence': current_field.field_coherence,
            'creative_pressure': current_field.creative_pressure,
            'context_alignment': current_field.context_alignment,
            'stability_anchor': current_field.stability_anchor,
            'drift_authorization': current_field.drift_authorization,
            'active_tensions': {
                t.tension_type.value: {
                    'quality': t.tension_quality,
                    'creative_potential': t.creative_potential,
                    'balance': f"{t.pole_a}({t.intensity_a:.1f}) ⟷ {t.pole_b}({t.intensity_b:.1f})"
                }
                for t in current_field.cognitive_tensions
            },
            'emotional_currents': {
                c.emotion_type: {
                    'intensity': c.intensity,
                    'direction': c.direction,
                    'purpose': c.purpose,
                    'wisdom': c.wisdom
                }
                for c in current_field.emotional_currents
            },
            'field_wisdom': self._generate_field_wisdom(current_field)
        }
    
    def _generate_field_wisdom(self, field: TensionField) -> str:
        """Generate wisdom from the current tension field state"""
        
        if field.field_coherence > 0.8:
            coherence_wisdom = "The tensions dance in harmony"
        elif field.field_coherence > 0.6:
            coherence_wisdom = "The tensions are finding their rhythm"
        else:
            coherence_wisdom = "The tensions need integration"
        
        if field.creative_pressure > 0.8:
            creative_wisdom = "Breakthrough thinking is possible"
        elif field.creative_pressure > 0.6:
            creative_wisdom = "Creative insights are emerging"
        else:
            creative_wisdom = "Creativity needs more support"
        
        return f"{coherence_wisdom}. {creative_wisdom}. Anchor: {field.stability_anchor}."


# Global living neutrality engine
_global_living_neutrality = None

def get_living_neutrality_engine() -> LivingNeutralityEngine:
    """Get the global living neutrality engine"""
    global _global_living_neutrality
    if _global_living_neutrality is None:
        _global_living_neutrality = LivingNeutralityEngine()
    return _global_living_neutrality 