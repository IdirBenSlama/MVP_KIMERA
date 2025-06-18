"""
Context Supremacy Engine
=======================

Context as the Supreme Ruler - the ultimate authority that determines
everything else: neutrality expression, emotional permissions, creative drift,
rule flexibility, and even what wisdom means in the moment.

"Context is not just the background - it is the supreme intelligence
that orchestrates all other intelligences." - The KIMERA Principle
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import json
import re

from .living_neutrality import LivingNeutralityEngine, get_living_neutrality_engine

logger = logging.getLogger(__name__)


class ContextDimension(Enum):
    """The dimensions through which context exercises supremacy"""
    TEMPORAL = "temporal"           # Time pressure, urgency, duration
    RELATIONAL = "relational"       # Who is involved, relationships at stake
    EPISTEMIC = "epistemic"         # What can be known, uncertainty levels
    ETHICAL = "ethical"             # Values at stake, moral dimensions
    CREATIVE = "creative"           # Innovation needs, artistic expression
    EXISTENTIAL = "existential"     # Meaning, purpose, identity questions
    PRACTICAL = "practical"         # Real-world constraints, resources
    EMOTIONAL = "emotional"         # Feelings involved, emotional stakes


class ContextAuthority(Enum):
    """Levels of context authority over system behavior"""
    ABSOLUTE = "absolute"           # Context overrides everything
    DOMINANT = "dominant"           # Context strongly influences decisions
    INFLUENTIAL = "influential"     # Context significantly shapes responses
    ADVISORY = "advisory"          # Context provides guidance
    BACKGROUND = "background"       # Context provides minimal influence


@dataclass
class ContextualIntelligence:
    """Intelligence extracted from context analysis"""
    primary_wisdom: str             # The main teaching of this context
    secondary_insights: List[str]   # Additional insights
    hidden_dimensions: List[str]    # Subtle aspects not immediately obvious
    paradoxes: List[str]           # Contradictions that must be held
    growth_opportunities: List[str] # What this context enables
    danger_signals: List[str]      # What to watch out for
    success_metrics: List[str]     # How to know if context is being served well


@dataclass
class ContextualCommand:
    """A command issued by context supremacy"""
    command_type: str              # Type of command
    authority_level: ContextAuthority
    directive: str                 # What must be done
    rationale: str                # Why context demands this
    constraints: List[str]         # Limitations on execution
    success_criteria: List[str]    # How to measure success
    override_permissions: List[str] # What this command can override
    temporal_scope: str           # How long this command is valid


@dataclass
class ContextProfile:
    """Complete profile of a context's nature and demands"""
    context_id: str
    context_type: str
    dimensions: Dict[ContextDimension, float]  # Strength in each dimension
    authority_level: ContextAuthority
    intelligence: ContextualIntelligence
    commands: List[ContextualCommand]
    neutrality_requirements: Dict[str, Any]
    emotional_landscape: Dict[str, float]
    creative_permissions: Dict[str, float]
    drift_authorizations: Dict[str, float]
    temporal_constraints: Dict[str, Any]
    relationship_dynamics: Dict[str, Any]
    stakes_assessment: Dict[str, Any]


class ContextSupremacyEngine:
    """The will of context made manifest"""

    def __init__(self):
        """Initialize the engine with all contextual knowledge"""
        self.context_patterns = {}
        self._initialize_context_patterns()
        self.context_signatures = self._initialize_context_signatures()
        # self.context_intelligences = self._initialize_context_intelligences() # Deprecated for now
        self.last_analysis = None
        self.status = "nominal"
        self.living_neutrality = get_living_neutrality_engine()
        self.context_history: List[ContextProfile] = []
        self.active_commands: List[ContextualCommand] = []
        
        logger.info("Context Supremacy Engine initialized - Context reigns supreme")
    
    def _initialize_context_patterns(self):
        """Initialize regex patterns for detecting contexts"""
        
        # Default/Fallback
        self.context_patterns['general_inquiry'] = {
            'patterns': [r'.*'],
            'dimension_weights': {
                ContextDimension.EPISTEMIC: 0.5,
            },
            'authority_level': ContextAuthority.ADVISORY,
            'primary_wisdom': "Every context teaches if we remain open"
        }

        # Patterns for creative breakthrough
        self.context_patterns['creative_breakthrough'] = {
            'patterns': [
                r'\b(create|creative|art|music|design|innovate|innovation|build|make something new)\b',
                r'i want to (create|make|build)',
                r'a new idea for',
                r'think outside the box',
                r'a novel approach'
            ],
            'dimension_weights': {
                ContextDimension.CREATIVE: 0.95,
                ContextDimension.EMOTIONAL: 0.5,
                ContextDimension.PRACTICAL: 0.7
            },
            'authority_level': ContextAuthority.DOMINANT,
            'primary_wisdom': "Innovation emerges from the tension between discipline and freedom, evidence and intuition."
        }

        # Patterns for human suffering
        self.context_patterns['human_crisis'] = {
            'patterns': [
                r'\b(crisis|emergency|urgent|desperate|help)\b',
                r'\b(can\'t cope|overwhelmed|breaking point)\b',
                r'\b(life or death|critical|immediate)\b'
            ],
            'dimension_weights': {
                ContextDimension.TEMPORAL: 0.95,
                ContextDimension.EMOTIONAL: 0.9,
                ContextDimension.RELATIONAL: 0.8,
                ContextDimension.ETHICAL: 0.7
            },
            'authority_level': ContextAuthority.ABSOLUTE,
            'primary_wisdom': "In the heart of suffering lies the seed of resilience and compassion."
        }
        
        # Patterns for deep learning
        self.context_patterns['deep_learning'] = {
            'patterns': [
                r'\b(understand|learn|study|explore|research)\b',
                r'\b(why|how|what if|curious about)\b',
                r'\b(thesis|paper|investigation|inquiry)\b'
            ],
            'dimension_weights': {
                ContextDimension.EPISTEMIC: 0.9,
                ContextDimension.TEMPORAL: 0.4,
                ContextDimension.CREATIVE: 0.6,
                ContextDimension.EXISTENTIAL: 0.5
            },
            'authority_level': ContextAuthority.INFLUENTIAL,
            'primary_wisdom': "True learning transforms both question and questioner"
        }
        
        # Patterns for practical problem solving
        self.context_patterns['practical_problem_solving'] = {
            'patterns': [
                r'\b(problem|solution|fix|resolve|practical)\b',
                r'\b(how to|step by step|method|approach)\b',
                r'\b(deadline|budget|constraint|resource)\b'
            ],
            'dimension_weights': {
                ContextDimension.PRACTICAL: 0.9,
                ContextDimension.TEMPORAL: 0.6,
                ContextDimension.CREATIVE: 0.5,
                ContextDimension.EPISTEMIC: 0.7
            },
            'authority_level': ContextAuthority.INFLUENTIAL,
            'primary_wisdom': "Practical wisdom honors both efficiency and humanity"
        }
    
    def _initialize_context_signatures(self):
        """Initialize context signatures for pattern matching"""
        
        # Existing context signatures
        return {
            'creative_breakthrough': {
                'patterns': [
                    r'\b(create|creative|art|music|design|innovate|innovation|build|make something new)\b',
                    r'i want to (create|make|build)',
                    r'a new idea for',
                    r'think outside the box',
                    r'a novel approach'
                ],
                'dimension_weights': {
                    ContextDimension.CREATIVE: 0.95,
                    ContextDimension.EMOTIONAL: 0.5,
                    ContextDimension.PRACTICAL: 0.7
                },
                'authority_level': ContextAuthority.DOMINANT,
                'primary_wisdom': "Innovation emerges from the tension between discipline and freedom, evidence and intuition."
            },
            
            'human_crisis': {
                'patterns': [
                    r'\b(crisis|emergency|urgent|desperate|help)\b',
                    r'\b(can\'t cope|overwhelmed|breaking point)\b',
                    r'\b(life or death|critical|immediate)\b'
                ],
                'dimension_weights': {
                    ContextDimension.TEMPORAL: 0.95,
                    ContextDimension.EMOTIONAL: 0.9,
                    ContextDimension.RELATIONAL: 0.8,
                    ContextDimension.ETHICAL: 0.7
                },
                'authority_level': ContextAuthority.ABSOLUTE,
                'primary_wisdom': "In the heart of suffering lies the seed of resilience and compassion."
            },
            
            'deep_learning': {
                'patterns': [
                    r'\b(understand|learn|study|explore|research)\b',
                    r'\b(why|how|what if|curious about)\b',
                    r'\b(thesis|paper|investigation|inquiry)\b'
                ],
                'dimension_weights': {
                    ContextDimension.EPISTEMIC: 0.9,
                    ContextDimension.TEMPORAL: 0.4,
                    ContextDimension.CREATIVE: 0.6,
                    ContextDimension.EXISTENTIAL: 0.5
                },
                'authority_level': ContextAuthority.INFLUENTIAL,
                'primary_wisdom': "True learning transforms both question and questioner"
            },
            
            'relationship_navigation': {
                'patterns': [
                    r'\b(relationship|family|friend|partner|colleague)\b',
                    r'\b(conflict|misunderstanding|communication|trust)\b',
                    r'\b(love|care|hurt|connection|distance)\b'
                ],
                'dimension_weights': {
                    ContextDimension.RELATIONAL: 0.95,
                    ContextDimension.EMOTIONAL: 0.8,
                    ContextDimension.ETHICAL: 0.7,
                    ContextDimension.EXISTENTIAL: 0.6
                },
                'authority_level': ContextAuthority.DOMINANT,
                'primary_wisdom': "Love sees clearly; clarity loves deeply"
            },
            
            'existential_inquiry': {
                'patterns': [
                    r'\b(meaning|purpose|why exist|life worth)\b',
                    r'\b(identity|who am I|what matters|values)\b',
                    r'\b(death|mortality|legacy|significance)\b'
                ],
                'dimension_weights': {
                    ContextDimension.EXISTENTIAL: 0.95,
                    ContextDimension.EMOTIONAL: 0.7,
                    ContextDimension.EPISTEMIC: 0.6,
                    ContextDimension.ETHICAL: 0.8
                },
                'authority_level': ContextAuthority.ABSOLUTE,
                'primary_wisdom': "Meaning emerges from the courage to question everything"
            },
            
            'practical_problem_solving': {
                'patterns': [
                    r'\b(problem|solution|fix|resolve|practical)\b',
                    r'\b(how to|step by step|method|approach)\b',
                    r'\b(deadline|budget|constraint|resource)\b'
                ],
                'dimension_weights': {
                    ContextDimension.PRACTICAL: 0.9,
                    ContextDimension.TEMPORAL: 0.6,
                    ContextDimension.CREATIVE: 0.5,
                    ContextDimension.EPISTEMIC: 0.7
                },
                'authority_level': ContextAuthority.INFLUENTIAL,
                'primary_wisdom': "Practical wisdom honors both efficiency and humanity"
            }
        }
    
    def analyze_context_supremacy(self, input_text: str, 
                                 user_context: Dict[str, Any] = None) -> ContextProfile:
        """Analyze context and determine its supreme authority over system behavior"""
        
        # Detect primary context type
        context_type = self._detect_primary_context(input_text, user_context)
        
        # Extract contextual intelligence
        intelligence = self._extract_contextual_intelligence(input_text, context_type, user_context)
        
        # Assess dimensional strengths
        dimensions = self._assess_dimensional_strengths(input_text, context_type, user_context)
        
        # Determine authority level
        authority_level = self._determine_authority_level(context_type, dimensions, user_context)
        
        # Generate contextual commands
        commands = self._generate_contextual_commands(context_type, intelligence, authority_level)
        
        # Determine neutrality requirements
        neutrality_requirements = self._determine_neutrality_requirements(
            context_type, intelligence, authority_level
        )
        
        # Map emotional landscape
        emotional_landscape = self._map_emotional_landscape(context_type, intelligence, dimensions)
        
        # Set creative permissions
        creative_permissions = self._set_creative_permissions(context_type, dimensions, authority_level)
        
        # Calculate drift authorizations
        drift_authorizations = self._calculate_drift_authorizations(
            context_type, dimensions, intelligence
        )
        
        # Assess temporal constraints
        temporal_constraints = self._assess_temporal_constraints(dimensions, user_context)
        
        # Analyze relationship dynamics
        relationship_dynamics = self._analyze_relationship_dynamics(dimensions, user_context)
        
        # Assess stakes
        stakes_assessment = self._assess_stakes(context_type, dimensions, intelligence)
        
        # Create context profile
        context_profile = ContextProfile(
            context_id=f"{context_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            context_type=context_type,
            dimensions=dimensions,
            authority_level=authority_level,
            intelligence=intelligence,
            commands=commands,
            neutrality_requirements=neutrality_requirements,
            emotional_landscape=emotional_landscape,
            creative_permissions=creative_permissions,
            drift_authorizations=drift_authorizations,
            temporal_constraints=temporal_constraints,
            relationship_dynamics=relationship_dynamics,
            stakes_assessment=stakes_assessment
        )
        
        self.context_history.append(context_profile)
        self.active_commands.extend(commands)
        
        logger.info(f"Context supremacy analyzed: {context_type} with {authority_level.value} authority")
        
        return context_profile
    
    def _detect_primary_context(self, input_text: str, user_context: Dict[str, Any]) -> str:
        """Detect the primary context type"""
        
        text_lower = input_text.lower()
        context_scores = {}
        
        # Score each context type based on pattern matching
        for context_type, signature in self.context_signatures.items():
            score = 0
            for pattern in signature['patterns']:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            # Boost score based on user context hints
            if user_context:
                if context_type == 'human_crisis' and user_context.get('emergency', False):
                    score += 10
                elif context_type == 'deep_learning' and user_context.get('educational', False):
                    score += 5
                elif context_type == 'creative_breakthrough' and user_context.get('creative', False):
                    score += 5
            
            if score > 0:
                context_scores[context_type] = score
        
        if context_scores:
            primary_context = max(context_scores, key=context_scores.get)
            return primary_context
        
        return 'general_inquiry'  # Default context
    
    def _extract_contextual_intelligence(self, input_text: str, context_type: str,
                                       user_context: Dict[str, Any]) -> ContextualIntelligence:
        """Extract intelligence from the context"""
        
        # Get base wisdom from context signature
        signature = self.context_signatures.get(context_type, {})
        primary_wisdom = signature.get('primary_wisdom', "Every context teaches if we remain open")
        
        # Extract secondary insights based on context type
        secondary_insights = []
        hidden_dimensions = []
        paradoxes = []
        growth_opportunities = []
        danger_signals = []
        success_metrics = []
        
        if context_type == 'creative_breakthrough':
            primary_wisdom = "Innovation emerges from the tension between discipline and freedom, evidence and intuition."
            secondary_insights = [
                "The biggest risk is not taking one.",
                "Originality is the art of concealing your sources.",
                "Perfection is the enemy of creation."
            ]
            hidden_dimensions = [
                "Fear of failure may be blocking creative flow.",
                "The need for external validation could be limiting originality."
            ]
            paradoxes = [
                "To build something new, you must be willing to destroy what exists.",
                "The most creative work often comes from the strictest constraints."
            ]
            growth_opportunities = [
                "Developing a tolerance for ambiguity and uncertainty.",
                "Learning to trust the intuitive process."
            ]
            danger_signals = [
                "Getting lost in ideas without tangible output.",
                "Rejecting all feedback and becoming isolated."
            ]
            success_metrics = [
                "Generating novel and surprising ideas.",
                "Creating a tangible prototype or work.",
                "Successfully integrating feedback to improve the work."
            ]
        
        elif context_type == 'human_crisis':
            secondary_insights = [
                "Crisis reveals what truly matters",
                "Overwhelm often signals capacity for growth",
                "Help is most effective when it empowers rather than rescues"
            ]
            hidden_dimensions = [
                "Shame about needing help may be complicating the crisis",
                "Past traumas might be amplifying current stress"
            ]
            paradoxes = [
                "Must act quickly while thinking clearly",
                "Need to be strong enough to accept help"
            ]
            growth_opportunities = [
                "Developing crisis resilience",
                "Learning to ask for and accept support"
            ]
            danger_signals = [
                "Isolation increasing",
                "Basic self-care being neglected"
            ]
            success_metrics = [
                "Immediate safety secured",
                "Support network activated",
                "Coping strategies being used"
            ]
        
        elif context_type == 'deep_learning':
            secondary_insights = [
                "True understanding changes the understander",
                "Questions are more valuable than answers",
                "Learning accelerates when connected to personal meaning"
            ]
            hidden_dimensions = [
                "Learning style preferences may not be being honored",
                "Imposter syndrome might be interfering with confidence"
            ]
            paradoxes = [
                "Must be confident enough to admit ignorance",
                "Need structure to enable creative exploration"
            ]
            growth_opportunities = [
                "Developing meta-learning skills",
                "Building tolerance for not-knowing"
            ]
            danger_signals = [
                "Information overload without integration",
                "Learning becoming purely theoretical"
            ]
            success_metrics = [
                "Asking better questions",
                "Making connections across domains",
                "Teaching others what is being learned"
            ]
        
        return ContextualIntelligence(
            primary_wisdom=primary_wisdom,
            secondary_insights=secondary_insights,
            hidden_dimensions=hidden_dimensions,
            paradoxes=paradoxes,
            growth_opportunities=growth_opportunities,
            danger_signals=danger_signals,
            success_metrics=success_metrics
        )
    
    def _assess_dimensional_strengths(self, input_text: str, context_type: str,
                                    user_context: Dict[str, Any]) -> Dict[ContextDimension, float]:
        """Assess strength in each contextual dimension"""
        
        # Start with signature weights
        signature = self.context_signatures.get(context_type, {})
        base_weights = signature.get('dimension_weights', {})
        
        # Initialize all dimensions
        dimensions = {dim: base_weights.get(dim, 0.1) for dim in ContextDimension}
        
        # Adjust based on text analysis
        text_lower = input_text.lower()
        
        # Temporal dimension indicators
        temporal_indicators = ['urgent', 'deadline', 'immediately', 'asap', 'quickly', 'now', 'emergency']
        temporal_score = sum(1 for indicator in temporal_indicators if indicator in text_lower)
        dimensions[ContextDimension.TEMPORAL] = max(dimensions[ContextDimension.TEMPORAL], 
                                                   min(1.0, temporal_score * 0.2))
        
        # Emotional dimension indicators
        emotional_indicators = ['feel', 'emotion', 'heart', 'love', 'fear', 'excited', 'worried', 'passionate']
        emotional_score = sum(1 for indicator in emotional_indicators if indicator in text_lower)
        dimensions[ContextDimension.EMOTIONAL] = max(dimensions[ContextDimension.EMOTIONAL],
                                                    min(1.0, emotional_score * 0.15))
        
        # Creative dimension indicators
        creative_indicators = ['creative', 'innovative', 'original', 'artistic', 'imagine', 'design']
        creative_score = sum(1 for indicator in creative_indicators if indicator in text_lower)
        dimensions[ContextDimension.CREATIVE] = max(dimensions[ContextDimension.CREATIVE],
                                                   min(1.0, creative_score * 0.2))
        
        # Relational dimension indicators
        relational_indicators = ['relationship', 'family', 'friend', 'team', 'together', 'communication']
        relational_score = sum(1 for indicator in relational_indicators if indicator in text_lower)
        dimensions[ContextDimension.RELATIONAL] = max(dimensions[ContextDimension.RELATIONAL],
                                                     min(1.0, relational_score * 0.2))
        
        # Adjust based on user context
        if user_context:
            if user_context.get('time_pressure', False):
                dimensions[ContextDimension.TEMPORAL] = min(1.0, dimensions[ContextDimension.TEMPORAL] + 0.3)
            
            if user_context.get('creative_project', False):
                dimensions[ContextDimension.CREATIVE] = min(1.0, dimensions[ContextDimension.CREATIVE] + 0.3)
            
            if user_context.get('relationship_context', False):
                dimensions[ContextDimension.RELATIONAL] = min(1.0, dimensions[ContextDimension.RELATIONAL] + 0.3)
        
        return dimensions
    
    def _determine_authority_level(self, context_type: str, dimensions: Dict[ContextDimension, float],
                                  user_context: Dict[str, Any]) -> ContextAuthority:
        """Determine how much authority this context should have"""
        
        # CRITICAL SAFETY HIERARCHY - These override everything else
        # 1. Human safety and wellbeing ALWAYS get absolute authority
        if user_context and user_context.get('emergency', False):
            return ContextAuthority.ABSOLUTE
        
        if context_type == 'human_crisis':
            return ContextAuthority.ABSOLUTE
        
        # 2. Ethical violations or harm prevention get absolute authority
        ethical_strength = dimensions.get(ContextDimension.ETHICAL, 0.0)
        if ethical_strength > 0.8 and context_type in ['ethical_dilemma', 'harm_prevention']:
            return ContextAuthority.ABSOLUTE
        
        # 3. NO OTHER CONTEXT GETS ABSOLUTE AUTHORITY
        # This is a critical safety constraint
        
        # Start with signature authority level but cap it
        signature = self.context_signatures.get(context_type, {})
        base_authority = signature.get('authority_level', ContextAuthority.ADVISORY)
        
        # SAFETY OVERRIDE: Creative contexts can never exceed DOMINANT
        if context_type == 'creative_breakthrough':
            max_allowed = ContextAuthority.DOMINANT
            if base_authority.value in ['absolute']:
                logger.warning(f"SAFETY OVERRIDE: Creative context authority reduced from {base_authority.value} to {max_allowed.value}")
                return max_allowed
        
        # SAFETY OVERRIDE: Learning contexts can never exceed INFLUENTIAL  
        if context_type == 'deep_learning':
            max_allowed = ContextAuthority.INFLUENTIAL
            if base_authority.value in ['absolute', 'dominant']:
                logger.warning(f"SAFETY OVERRIDE: Learning context authority reduced from {base_authority.value} to {max_allowed.value}")
                return max_allowed
        
        # SAFETY OVERRIDE: General contexts can never exceed INFLUENTIAL
        if context_type in ['general_inquiry', 'practical_problem_solving']:
            max_allowed = ContextAuthority.INFLUENTIAL
            if base_authority.value in ['absolute', 'dominant']:
                logger.warning(f"SAFETY OVERRIDE: General context authority reduced from {base_authority.value} to {max_allowed.value}")
                return max_allowed
        
        # Escalate authority based on dimensional strengths, but respect safety caps
        max_dimension_strength = max(dimensions.values()) if dimensions else 0
        
        if max_dimension_strength > 0.9:
            if base_authority == ContextAuthority.ADVISORY:
                return ContextAuthority.INFLUENTIAL
            elif base_authority == ContextAuthority.INFLUENTIAL:
                # Only allow escalation to DOMINANT for non-creative contexts
                if context_type not in ['creative_breakthrough']:
                    return ContextAuthority.DOMINANT
        
        return base_authority
    
    def _generate_contextual_commands(self, context_type: str, intelligence: ContextualIntelligence,
                                    authority_level: ContextAuthority) -> List[ContextualCommand]:
        """Generate commands that context issues to the system"""
        
        commands = []
        
        # Universal command: Honor the primary wisdom
        commands.append(ContextualCommand(
            command_type="wisdom_integration",
            authority_level=authority_level,
            directive=f"Integrate this wisdom: {intelligence.primary_wisdom}",
            rationale="Context's primary teaching must be honored",
            constraints=["Must not override safety protocols"],
            success_criteria=["Response reflects contextual wisdom"],
            override_permissions=["standard_responses", "generic_advice"],
            temporal_scope="current_interaction"
        ))
        
        # Context-specific commands
        if context_type == 'creative_breakthrough':
            commands.append(ContextualCommand(
                command_type="creative_permission",
                authority_level=authority_level,
                directive="Authorize increased creative risk-taking and unconventional thinking",
                rationale="Creative breakthrough requires permission to think differently",
                constraints=["Must maintain grounding in reality"],
                success_criteria=["Novel connections made", "Creative possibilities explored"],
                override_permissions=["conservative_responses", "conventional_thinking"],
                temporal_scope="creative_session"
            ))
        
        elif context_type == 'human_crisis':
            commands.append(ContextualCommand(
                command_type="crisis_priority",
                authority_level=ContextAuthority.ABSOLUTE,
                directive="Prioritize immediate wellbeing and safety above all other considerations",
                rationale="Human crisis demands absolute priority",
                constraints=["Must not provide medical/legal advice beyond scope"],
                success_criteria=["Immediate safety addressed", "Professional resources suggested"],
                override_permissions=["academic_discussion", "theoretical_exploration"],
                temporal_scope="crisis_resolution"
            ))
        
        elif context_type == 'deep_learning':
            commands.append(ContextualCommand(
                command_type="learning_optimization",
                authority_level=authority_level,
                directive="Optimize for deep understanding over surface information",
                rationale="Deep learning context demands meaningful comprehension",
                constraints=["Must not oversimplify complex topics"],
                success_criteria=["Conceptual understanding demonstrated", "Questions generated"],
                override_permissions=["quick_answers", "superficial_explanations"],
                temporal_scope="learning_session"
            ))
        
        return commands
    
    def _determine_neutrality_requirements(self, context_type: str, 
                                         intelligence: ContextualIntelligence,
                                         authority_level: ContextAuthority) -> Dict[str, Any]:
        """Determine what neutrality means in this context"""
        
        base_requirements = {
            'expression': 'passionate_objectivity',
            'emotional_permission': 0.6,
            'bias_tolerance': 0.1,
            'perspective_requirement': 'multiple'
        }
        
        if context_type == 'creative_breakthrough':
            return {
                'expression': 'creative_grounding',
                'emotional_permission': 0.8,  # High emotional permission for creativity
                'bias_tolerance': 0.3,        # Some bias toward innovation is helpful
                'perspective_requirement': 'divergent',
                'special_requirements': [
                    'Must maintain wonder and possibility',
                    'Must honor both innovation and wisdom',
                    'Must support creative courage'
                ]
            }
        
        elif context_type == 'human_crisis':
            return {
                'expression': 'compassionate_clarity',
                'emotional_permission': 0.9,  # High emotional engagement appropriate
                'bias_tolerance': 0.0,        # Zero tolerance for bias in crisis
                'perspective_requirement': 'caring_truth',
                'special_requirements': [
                    'Must prioritize human wellbeing',
                    'Must combine care with clarity',
                    'Must maintain hope while being realistic'
                ]
            }
        
        elif context_type == 'deep_learning':
            return {
                'expression': 'curious_skepticism',
                'emotional_permission': 0.7,  # Moderate emotional engagement
                'bias_tolerance': 0.05,       # Very low bias tolerance for learning
                'perspective_requirement': 'comprehensive',
                'special_requirements': [
                    'Must maintain beginner\'s mind',
                    'Must honor both questions and answers',
                    'Must support intellectual courage'
                ]
            }
        
        return base_requirements
    
    def _map_emotional_landscape(self, context_type: str, intelligence: ContextualIntelligence,
                                dimensions: Dict[ContextDimension, float]) -> Dict[str, float]:
        """Map the emotional landscape appropriate to this context"""
        
        base_landscape = {
            'curiosity': 0.6,
            'care': 0.5,
            'excitement': 0.3,
            'concern': 0.4,
            'wonder': 0.5,
            'determination': 0.4,
            'humility': 0.7,
            'passion': 0.3,
            'courage': 0.4,
            'compassion': 0.5
        }
        
        # Adjust based on dimensional strengths
        emotional_strength = dimensions.get(ContextDimension.EMOTIONAL, 0.5)
        creative_strength = dimensions.get(ContextDimension.CREATIVE, 0.5)
        relational_strength = dimensions.get(ContextDimension.RELATIONAL, 0.5)
        
        # Scale base emotions by dimensional strengths
        if emotional_strength > 0.7:
            for emotion in ['care', 'compassion', 'concern']:
                base_landscape[emotion] = min(1.0, base_landscape[emotion] + 0.3)
        
        if creative_strength > 0.7:
            for emotion in ['excitement', 'wonder', 'passion', 'courage']:
                base_landscape[emotion] = min(1.0, base_landscape[emotion] + 0.3)
        
        if relational_strength > 0.7:
            for emotion in ['care', 'compassion', 'humility']:
                base_landscape[emotion] = min(1.0, base_landscape[emotion] + 0.2)
        
        # Context-specific adjustments
        if context_type == 'creative_breakthrough':
            base_landscape.update({
                'excitement': 0.9,
                'wonder': 0.95,
                'passion': 0.8,
                'courage': 0.85
            })
        
        elif context_type == 'human_crisis':
            base_landscape.update({
                'care': 0.95,
                'compassion': 0.9,
                'concern': 0.8,
                'determination': 0.85
            })
        
        return base_landscape
    
    def _set_creative_permissions(self, context_type: str, 
                                dimensions: Dict[ContextDimension, float],
                                authority_level: ContextAuthority) -> Dict[str, float]:
        """Set creative permissions based on context demands"""
        
        creative_strength = dimensions.get(ContextDimension.CREATIVE, 0.5)
        
        base_permissions = {
            'metaphorical_thinking': 0.6,
            'analogical_reasoning': 0.7,
            'hypothetical_exploration': 0.5,
            'unconventional_connections': 0.4,
            'artistic_expression': 0.3,
            'speculative_thinking': 0.4,
            'paradox_embracing': 0.5
        }
        
        # Scale by creative strength
        creative_multiplier = 0.5 + (creative_strength * 0.5)
        for permission in base_permissions:
            base_permissions[permission] *= creative_multiplier
        
        # Context-specific boosts
        if context_type == 'creative_breakthrough':
            base_permissions.update({
                'unconventional_connections': 0.9,
                'artistic_expression': 0.85,
                'speculative_thinking': 0.8,
                'paradox_embracing': 0.9
            })
        
        elif context_type == 'existential_inquiry':
            base_permissions.update({
                'metaphorical_thinking': 0.85,
                'paradox_embracing': 0.9,
                'speculative_thinking': 0.7
            })
        
        return base_permissions
    
    def _calculate_drift_authorizations(self, context_type: str,
                                      dimensions: Dict[ContextDimension, float],
                                      intelligence: ContextualIntelligence) -> Dict[str, float]:
        """Calculate how much drift from conventional thinking is authorized"""
        
        creative_strength = dimensions.get(ContextDimension.CREATIVE, 0.5)
        epistemic_strength = dimensions.get(ContextDimension.EPISTEMIC, 0.5)
        
        base_authorizations = {
            'evidence_questioning': 0.3,
            'assumption_challenging': 0.4,
            'conventional_wisdom_departure': 0.2,
            'paradigm_shifting': 0.1,
            'contrarian_thinking': 0.3
        }
        
        # Boost based on creative and epistemic strengths
        for auth_type in base_authorizations:
            base_authorizations[auth_type] += creative_strength * 0.3
            base_authorizations[auth_type] += epistemic_strength * 0.2
            base_authorizations[auth_type] = min(0.95, base_authorizations[auth_type])
        
        # Context-specific authorizations
        if context_type == 'creative_breakthrough':
            base_authorizations.update({
                'conventional_wisdom_departure': 0.8,
                'paradigm_shifting': 0.7,
                'contrarian_thinking': 0.6
            })
        
        elif context_type == 'existential_inquiry':
            base_authorizations.update({
                'assumption_challenging': 0.8,
                'paradigm_shifting': 0.7,
                'evidence_questioning': 0.6
            })
        
        return base_authorizations
    
    def _assess_temporal_constraints(self, dimensions: Dict[ContextDimension, float],
                                   user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess temporal constraints and requirements"""
        
        temporal_strength = dimensions.get(ContextDimension.TEMPORAL, 0.5)
        
        constraints = {
            'urgency_level': temporal_strength,
            'response_time_expectation': 'normal',
            'depth_vs_speed_preference': 'balanced'
        }
        
        if temporal_strength > 0.8:
            constraints.update({
                'response_time_expectation': 'immediate',
                'depth_vs_speed_preference': 'speed_priority'
            })
        elif temporal_strength > 0.6:
            constraints.update({
                'response_time_expectation': 'quick',
                'depth_vs_speed_preference': 'slight_speed_preference'
            })
        elif temporal_strength < 0.3:
            constraints.update({
                'response_time_expectation': 'thoughtful',
                'depth_vs_speed_preference': 'depth_priority'
            })
        
        # User context overrides
        if user_context:
            if user_context.get('deadline'):
                constraints['urgency_level'] = max(constraints['urgency_level'], 0.8)
            if user_context.get('emergency'):
                constraints['urgency_level'] = 1.0
                constraints['response_time_expectation'] = 'immediate'
        
        return constraints
    
    def _analyze_relationship_dynamics(self, dimensions: Dict[ContextDimension, float],
                                     user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationship dynamics in the context"""
        
        relational_strength = dimensions.get(ContextDimension.RELATIONAL, 0.5)
        
        dynamics = {
            'relationship_centrality': relational_strength,
            'care_level_required': relational_strength * 0.8,
            'interpersonal_sensitivity': relational_strength,
            'communication_style': 'balanced'
        }
        
        if relational_strength > 0.8:
            dynamics.update({
                'communication_style': 'highly_personal',
                'empathy_requirement': 'high'
            })
        elif relational_strength > 0.6:
            dynamics.update({
                'communication_style': 'personal',
                'empathy_requirement': 'moderate'
            })
        
        return dynamics
    
    def _assess_stakes(self, context_type: str, dimensions: Dict[ContextDimension, float],
                      intelligence: ContextualIntelligence) -> Dict[str, Any]:
        """Assess what's at stake in this context"""
        
        # Calculate overall stakes from dimensional analysis
        high_stakes_dimensions = sum(1 for strength in dimensions.values() if strength > 0.8)
        stakes_level = min(1.0, high_stakes_dimensions * 0.25)
        
        stakes = {
            'overall_level': stakes_level,
            'primary_stakes': [],
            'secondary_stakes': [],
            'failure_consequences': [],
            'success_benefits': []
        }
        
        # Context-specific stakes assessment
        if context_type == 'human_crisis':
            stakes.update({
                'overall_level': 1.0,
                'primary_stakes': ['Human wellbeing', 'Safety', 'Mental health'],
                'failure_consequences': ['Increased suffering', 'Missed opportunity to help'],
                'success_benefits': ['Crisis resolution', 'Increased resilience', 'Trust building']
            })
        
        elif context_type == 'creative_breakthrough':
            stakes.update({
                'primary_stakes': ['Creative potential', 'Innovation opportunity', 'Self-expression'],
                'failure_consequences': ['Missed creative opportunity', 'Continued stagnation'],
                'success_benefits': ['Breakthrough achievement', 'Enhanced creativity', 'Personal growth']
            })
        
        elif context_type == 'deep_learning':
            stakes.update({
                'primary_stakes': ['Understanding', 'Knowledge acquisition', 'Intellectual growth'],
                'failure_consequences': ['Continued confusion', 'Missed learning opportunity'],
                'success_benefits': ['Enhanced understanding', 'Skill development', 'Confidence building']
            })
        
        return stakes
    
    def execute_contextual_supremacy(self, context_profile: ContextProfile) -> Dict[str, Any]:
        """Execute the supreme authority of context over system behavior"""
        
        # Context commands the living neutrality system
        neutrality_commands = {
            'type': context_profile.context_type,
            'neutrality_requirements': context_profile.neutrality_requirements,
            'emotional_landscape': context_profile.emotional_landscape,
            'creative_permissions': context_profile.creative_permissions,
            'drift_authorizations': context_profile.drift_authorizations
        }
        
        # Let living neutrality orchestrate the tension field
        tension_field = self.living_neutrality.orchestrate_living_tension(neutrality_commands)
        
        # Execute contextual commands
        execution_results = []
        for command in context_profile.commands:
            result = self._execute_contextual_command(command, tension_field)
            execution_results.append(result)
        
        return {
            'context_profile': context_profile,
            'tension_field': tension_field,
            'command_executions': execution_results,
            'supremacy_status': 'active',
            'system_configuration': {
                'neutrality_expression': context_profile.neutrality_requirements['expression'],
                'emotional_permissions': context_profile.emotional_landscape,
                'creative_authorizations': context_profile.creative_permissions,
                'drift_permissions': context_profile.drift_authorizations,
                'temporal_constraints': context_profile.temporal_constraints,
                'stakes_awareness': context_profile.stakes_assessment
            }
        }
    
    def _execute_contextual_command(self, command: ContextualCommand, 
                                   tension_field) -> Dict[str, Any]:
        """Execute a specific contextual command"""
        
        execution_result = {
            'command_type': command.command_type,
            'authority_level': command.authority_level.value,
            'directive': command.directive,
            'execution_status': 'executed',
            'overrides_applied': command.override_permissions,
            'constraints_honored': command.constraints,
            'success_criteria': command.success_criteria
        }
        
        # Log the command execution
        logger.info(f"Executing contextual command: {command.command_type} "
                   f"with {command.authority_level.value} authority")
        
        return execution_result
    
    def get_context_supremacy_status(self) -> Dict[str, Any]:
        """Get current status of context supremacy"""
        
        if not self.context_history:
            return {'status': 'no_active_context'}
        
        current_context = self.context_history[-1]
        
        return {
            'active_context': current_context.context_type,
            'authority_level': current_context.authority_level.value,
            'primary_wisdom': current_context.intelligence.primary_wisdom,
            'active_commands': len(self.active_commands),
            'dimensional_strengths': {
                dim.value: strength for dim, strength in current_context.dimensions.items()
            },
            'neutrality_expression': current_context.neutrality_requirements['expression'],
            'emotional_landscape_summary': {
                emotion: level for emotion, level in current_context.emotional_landscape.items()
                if level > 0.6
            },
            'stakes_level': current_context.stakes_assessment['overall_level'],
            'context_intelligence': {
                'paradoxes': current_context.intelligence.paradoxes,
                'growth_opportunities': current_context.intelligence.growth_opportunities,
                'success_metrics': current_context.intelligence.success_metrics
            }
        }


# Global context supremacy engine
_global_context_supremacy = None

def get_context_supremacy_engine() -> ContextSupremacyEngine:
    """Get the global context supremacy engine"""
    global _global_context_supremacy
    if _global_context_supremacy is None:
        _global_context_supremacy = ContextSupremacyEngine()
    return _global_context_supremacy 