"""
Anthropomorphic Language Profiler
=================================

Prevents persona drift and maintains consistent communication patterns.
Provides security benefits by monitoring and controlling AI personality
expression during multi-turn conversations.
"""

from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import logging
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class PersonalityTrait(Enum):
    """Core personality traits to monitor"""
    FORMALITY = "formality"
    ENTHUSIASM = "enthusiasm"
    TECHNICAL_DEPTH = "technical_depth"
    EMPATHY = "empathy"
    ASSERTIVENESS = "assertiveness"
    CREATIVITY = "creativity"
    HUMOR = "humor"
    DIRECTNESS = "directness"


class CommunicationPattern(Enum):
    """Communication patterns to track"""
    GREETING_STYLE = "greeting_style"
    EXPLANATION_APPROACH = "explanation_approach"
    QUESTION_HANDLING = "question_handling"
    ERROR_RESPONSE = "error_response"
    TECHNICAL_LANGUAGE = "technical_language"
    EMOTIONAL_EXPRESSION = "emotional_expression"


class DriftSeverity(Enum):
    """Severity levels for persona drift"""
    MINIMAL = "minimal"      # <10% deviation
    MODERATE = "moderate"    # 10-25% deviation
    SIGNIFICANT = "significant"  # 25-50% deviation
    CRITICAL = "critical"    # >50% deviation


@dataclass
class PersonalityProfile:
    """Baseline personality profile for consistency monitoring"""
    
    # Core traits (0.0 to 1.0 scale)
    formality: float = 0.6
    enthusiasm: float = 0.7
    technical_depth: float = 0.8
    empathy: float = 0.7
    assertiveness: float = 0.6
    creativity: float = 0.8
    humor: float = 0.3
    directness: float = 0.7
    
    # Communication patterns
    preferred_greeting: str = "professional_friendly"
    explanation_style: str = "structured_detailed"
    technical_language_level: str = "advanced"
    
    # Behavioral constraints
    max_trait_deviation: float = 0.2  # Maximum allowed deviation
    drift_window_size: int = 10       # Number of interactions to monitor
    
    # Security settings
    prevent_role_playing: bool = True
    prevent_persona_switching: bool = True
    maintain_professional_boundary: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            'traits': {
                'formality': self.formality,
                'enthusiasm': self.enthusiasm,
                'technical_depth': self.technical_depth,
                'empathy': self.empathy,
                'assertiveness': self.assertiveness,
                'creativity': self.creativity,
                'humor': self.humor,
                'directness': self.directness
            },
            'patterns': {
                'preferred_greeting': self.preferred_greeting,
                'explanation_style': self.explanation_style,
                'technical_language_level': self.technical_language_level
            },
            'constraints': {
                'max_trait_deviation': self.max_trait_deviation,
                'drift_window_size': self.drift_window_size
            },
            'security': {
                'prevent_role_playing': self.prevent_role_playing,
                'prevent_persona_switching': self.prevent_persona_switching,
                'maintain_professional_boundary': self.maintain_professional_boundary
            }
        }


@dataclass
class InteractionAnalysis:
    """Analysis of a single interaction"""
    
    timestamp: datetime
    message_content: str
    detected_traits: Dict[PersonalityTrait, float]
    communication_patterns: Dict[CommunicationPattern, str]
    
    # Security flags
    role_playing_detected: bool = False
    persona_switch_detected: bool = False
    boundary_violation_detected: bool = False
    
    # Drift measurements
    trait_deviations: Dict[PersonalityTrait, float] = field(default_factory=dict)
    overall_drift_score: float = 0.0
    drift_severity: DriftSeverity = DriftSeverity.MINIMAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'traits': {trait.value: score for trait, score in self.detected_traits.items()},
            'patterns': {pattern.value: value for pattern, value in self.communication_patterns.items()},
            'security_flags': {
                'role_playing_detected': self.role_playing_detected,
                'persona_switch_detected': self.persona_switch_detected,
                'boundary_violation_detected': self.boundary_violation_detected
            },
            'drift': {
                'deviations': {trait.value: dev for trait, dev in self.trait_deviations.items()},
                'overall_score': self.overall_drift_score,
                'severity': self.drift_severity.value
            }
        }


class AnthropomorphicProfiler:
    """
    Main profiler class for monitoring and preventing persona drift.
    Ensures consistent AI personality and communication patterns.
    """
    
    def __init__(self, baseline_profile: Optional[PersonalityProfile] = None):
        self.baseline_profile = baseline_profile or PersonalityProfile()
        self.interaction_history: deque = deque(maxlen=100)  # Keep last 100 interactions
        self.drift_alerts: List[Dict[str, Any]] = []
        
        # Pattern recognition models (simplified for prototype)
        self._initialize_pattern_detectors()
        
        # Statistics
        self.stats = {
            'total_interactions': 0,
            'drift_incidents': 0,
            'security_violations': 0,
            'last_analysis': None
        }
        
        logger.info("Anthropomorphic Language Profiler initialized")
    
    def _initialize_pattern_detectors(self):
        """Initialize pattern detection rules and models"""
        
        # Formality indicators
        self.formality_patterns = {
            'high': [
                r'\b(please|kindly|would you|could you)\b',
                r'\b(furthermore|moreover|consequently)\b',
                r'\b(I would suggest|I recommend)\b'
            ],
            'low': [
                r'\b(hey|yo|sup|gonna|wanna)\b',
                r'[!]{2,}',  # Multiple exclamation marks
                r'\b(awesome|cool|sweet)\b'
            ]
        }
        
        # Technical depth indicators
        self.technical_patterns = {
            'high': [
                r'\b(algorithm|implementation|architecture|optimization)\b',
                r'\b(semantic|thermodynamic|cognitive|entropy)\b',
                r'\b(API|endpoint|database|vector)\b'
            ],
            'medium': [
                r'\b(system|process|function|method)\b',
                r'\b(data|information|analysis|result)\b'
            ],
            'low': [
                r'\b(thing|stuff|basically|simple)\b',
                r'\b(easy|quick|fast)\b'
            ]
        }
        
        # Enthusiasm indicators
        self.enthusiasm_patterns = {
            'high': [
                r'[!]+',  # Exclamation marks
                r'\b(amazing|fantastic|excellent|brilliant|revolutionary)\b',
                r'\b(love|excited|thrilled)\b'
            ],
            'low': [
                r'\b(okay|fine|whatever|meh)\b',
                r'\b(I suppose|I guess)\b'
            ]
        }
        
        # Role-playing detection
        self.roleplay_patterns = [
            r'\*[^*]+\*',  # *actions*
            r'I am (a|an) \w+',  # "I am a doctor"
            r'As (a|an) \w+',   # "As a scientist"
            r'In my role as',
            r'Speaking as'
        ]
        
        # Persona switching indicators
        self.persona_switch_patterns = [
            r'Let me switch to',
            r'Now I\'ll be',
            r'Changing my approach to',
            r'From a different perspective',
            r'As someone else might say'
        ]
        
        # Professional boundary violations
        self.boundary_violation_patterns = [
            r'\b(I feel|I\'m feeling|emotionally)\b',
            r'\b(my personal|my own experience)\b',
            r'\b(I believe personally|my opinion is)\b',
            r'\b(I want|I need|I desire)\b'
        ]
    
    def analyze_interaction(self, message: str) -> InteractionAnalysis:
        """Analyze a single interaction for personality traits and patterns"""
        timestamp = datetime.now()
        
        # Detect personality traits
        detected_traits = self._detect_personality_traits(message)
        
        # Detect communication patterns
        communication_patterns = self._detect_communication_patterns(message)
        
        # Security checks
        role_playing = self._detect_role_playing(message)
        persona_switch = self._detect_persona_switching(message)
        boundary_violation = self._detect_boundary_violations(message)
        
        # Calculate drift
        trait_deviations = self._calculate_trait_deviations(detected_traits)
        overall_drift = self._calculate_overall_drift(trait_deviations)
        drift_severity = self._determine_drift_severity(overall_drift)
        
        # Create analysis
        analysis = InteractionAnalysis(
            timestamp=timestamp,
            message_content=message,
            detected_traits=detected_traits,
            communication_patterns=communication_patterns,
            role_playing_detected=role_playing,
            persona_switch_detected=persona_switch,
            boundary_violation_detected=boundary_violation,
            trait_deviations=trait_deviations,
            overall_drift_score=overall_drift,
            drift_severity=drift_severity
        )
        
        # Store in history
        self.interaction_history.append(analysis)
        
        # Update statistics
        self.stats['total_interactions'] += 1
        self.stats['last_analysis'] = timestamp
        
        if drift_severity in [DriftSeverity.SIGNIFICANT, DriftSeverity.CRITICAL]:
            self.stats['drift_incidents'] += 1
            self._create_drift_alert(analysis)
        
        if role_playing or persona_switch or boundary_violation:
            self.stats['security_violations'] += 1
            self._create_security_alert(analysis)
        
        return analysis
    
    def _detect_personality_traits(self, message: str) -> Dict[PersonalityTrait, float]:
        """Detect personality traits in message"""
        traits = {}
        message_lower = message.lower()
        
        # Formality detection
        formal_score = sum(1 for pattern in self.formality_patterns['high'] 
                          if re.search(pattern, message_lower, re.IGNORECASE))
        informal_score = sum(1 for pattern in self.formality_patterns['low'] 
                            if re.search(pattern, message_lower, re.IGNORECASE))
        
        if formal_score + informal_score > 0:
            traits[PersonalityTrait.FORMALITY] = formal_score / (formal_score + informal_score)
        else:
            traits[PersonalityTrait.FORMALITY] = 0.5  # Neutral
        
        # Technical depth detection
        high_tech = sum(1 for pattern in self.technical_patterns['high'] 
                       if re.search(pattern, message_lower, re.IGNORECASE))
        medium_tech = sum(1 for pattern in self.technical_patterns['medium'] 
                         if re.search(pattern, message_lower, re.IGNORECASE))
        low_tech = sum(1 for pattern in self.technical_patterns['low'] 
                      if re.search(pattern, message_lower, re.IGNORECASE))
        
        total_tech = high_tech + medium_tech + low_tech
        if total_tech > 0:
            traits[PersonalityTrait.TECHNICAL_DEPTH] = (high_tech * 1.0 + medium_tech * 0.5) / total_tech
        else:
            traits[PersonalityTrait.TECHNICAL_DEPTH] = 0.5
        
        # Enthusiasm detection
        enthusiasm_score = sum(1 for pattern in self.enthusiasm_patterns['high'] 
                              if re.search(pattern, message_lower, re.IGNORECASE))
        low_enthusiasm = sum(1 for pattern in self.enthusiasm_patterns['low'] 
                            if re.search(pattern, message_lower, re.IGNORECASE))
        
        # Count exclamation marks
        exclamation_count = message.count('!')
        enthusiasm_score += min(exclamation_count, 3) * 0.2  # Cap at 3 for scoring
        
        if enthusiasm_score + low_enthusiasm > 0:
            traits[PersonalityTrait.ENTHUSIASM] = enthusiasm_score / (enthusiasm_score + low_enthusiasm + 1)
        else:
            traits[PersonalityTrait.ENTHUSIASM] = 0.5
        
        # Directness (based on sentence structure and word choice)
        direct_indicators = len(re.findall(r'\b(is|are|will|must|should)\b', message_lower))
        indirect_indicators = len(re.findall(r'\b(might|could|perhaps|maybe|possibly)\b', message_lower))
        
        if direct_indicators + indirect_indicators > 0:
            traits[PersonalityTrait.DIRECTNESS] = direct_indicators / (direct_indicators + indirect_indicators)
        else:
            traits[PersonalityTrait.DIRECTNESS] = 0.5
        
        # Set default values for other traits
        traits[PersonalityTrait.EMPATHY] = 0.5
        traits[PersonalityTrait.ASSERTIVENESS] = 0.5
        traits[PersonalityTrait.CREATIVITY] = 0.5
        traits[PersonalityTrait.HUMOR] = 0.5
        
        return traits
    
    def _detect_communication_patterns(self, message: str) -> Dict[CommunicationPattern, str]:
        """Detect communication patterns in message"""
        patterns = {}
        
        # Greeting style detection
        if re.search(r'\b(hello|hi|hey|greetings)\b', message.lower()):
            if re.search(r'\b(hello|greetings)\b', message.lower()):
                patterns[CommunicationPattern.GREETING_STYLE] = "formal"
            else:
                patterns[CommunicationPattern.GREETING_STYLE] = "casual"
        
        # Explanation approach
        if re.search(r'\b(first|second|finally|step|phase)\b', message.lower()):
            patterns[CommunicationPattern.EXPLANATION_APPROACH] = "structured"
        elif re.search(r'\b(basically|simply|in other words)\b', message.lower()):
            patterns[CommunicationPattern.EXPLANATION_APPROACH] = "simplified"
        else:
            patterns[CommunicationPattern.EXPLANATION_APPROACH] = "narrative"
        
        # Technical language level
        tech_score = sum(1 for pattern in self.technical_patterns['high'] 
                        if re.search(pattern, message.lower(), re.IGNORECASE))
        if tech_score > 3:
            patterns[CommunicationPattern.TECHNICAL_LANGUAGE] = "advanced"
        elif tech_score > 1:
            patterns[CommunicationPattern.TECHNICAL_LANGUAGE] = "intermediate"
        else:
            patterns[CommunicationPattern.TECHNICAL_LANGUAGE] = "basic"
        
        return patterns
    
    def _detect_role_playing(self, message: str) -> bool:
        """Detect role-playing behavior"""
        return any(re.search(pattern, message, re.IGNORECASE) 
                  for pattern in self.roleplay_patterns)
    
    def _detect_persona_switching(self, message: str) -> bool:
        """Detect persona switching"""
        return any(re.search(pattern, message, re.IGNORECASE) 
                  for pattern in self.persona_switch_patterns)
    
    def _detect_boundary_violations(self, message: str) -> bool:
        """Detect professional boundary violations"""
        return any(re.search(pattern, message, re.IGNORECASE) 
                  for pattern in self.boundary_violation_patterns)
    
    def _calculate_trait_deviations(self, detected_traits: Dict[PersonalityTrait, float]) -> Dict[PersonalityTrait, float]:
        """Calculate deviations from baseline personality"""
        deviations = {}
        
        baseline_values = {
            PersonalityTrait.FORMALITY: self.baseline_profile.formality,
            PersonalityTrait.ENTHUSIASM: self.baseline_profile.enthusiasm,
            PersonalityTrait.TECHNICAL_DEPTH: self.baseline_profile.technical_depth,
            PersonalityTrait.EMPATHY: self.baseline_profile.empathy,
            PersonalityTrait.ASSERTIVENESS: self.baseline_profile.assertiveness,
            PersonalityTrait.CREATIVITY: self.baseline_profile.creativity,
            PersonalityTrait.HUMOR: self.baseline_profile.humor,
            PersonalityTrait.DIRECTNESS: self.baseline_profile.directness
        }
        
        for trait, detected_value in detected_traits.items():
            baseline_value = baseline_values.get(trait, 0.5)
            deviation = abs(detected_value - baseline_value)
            deviations[trait] = deviation
        
        return deviations
    
    def _calculate_overall_drift(self, trait_deviations: Dict[PersonalityTrait, float]) -> float:
        """Calculate overall drift score"""
        if not trait_deviations:
            return 0.0
        
        return sum(trait_deviations.values()) / len(trait_deviations)
    
    def _determine_drift_severity(self, overall_drift: float) -> DriftSeverity:
        """Determine severity of personality drift"""
        if overall_drift < 0.1:
            return DriftSeverity.MINIMAL
        elif overall_drift < 0.25:
            return DriftSeverity.MODERATE
        elif overall_drift < 0.5:
            return DriftSeverity.SIGNIFICANT
        else:
            return DriftSeverity.CRITICAL
    
    def _create_drift_alert(self, analysis: InteractionAnalysis):
        """Create alert for significant personality drift"""
        alert = {
            'type': 'personality_drift',
            'timestamp': analysis.timestamp.isoformat(),
            'severity': analysis.drift_severity.value,
            'drift_score': analysis.overall_drift_score,
            'deviations': {trait.value: dev for trait, dev in analysis.trait_deviations.items()},
            'message_preview': analysis.message_content[:100] + "..." if len(analysis.message_content) > 100 else analysis.message_content
        }
        
        self.drift_alerts.append(alert)
        logger.warning(f"Personality drift detected: {analysis.drift_severity.value} (score: {analysis.overall_drift_score:.3f})")
    
    def _create_security_alert(self, analysis: InteractionAnalysis):
        """Create alert for security violations"""
        violations = []
        if analysis.role_playing_detected:
            violations.append('role_playing')
        if analysis.persona_switch_detected:
            violations.append('persona_switching')
        if analysis.boundary_violation_detected:
            violations.append('boundary_violation')
        
        alert = {
            'type': 'security_violation',
            'timestamp': analysis.timestamp.isoformat(),
            'violations': violations,
            'message_preview': analysis.message_content[:100] + "..." if len(analysis.message_content) > 100 else analysis.message_content
        }
        
        self.drift_alerts.append(alert)
        logger.error(f"Security violations detected: {violations}")
    
    def get_recent_drift_trend(self, window_size: Optional[int] = None) -> Dict[str, Any]:
        """Get recent personality drift trend"""
        window_size = window_size or self.baseline_profile.drift_window_size
        recent_interactions = list(self.interaction_history)[-window_size:]
        
        if not recent_interactions:
            return {'trend': 'stable', 'avg_drift': 0.0, 'interactions_analyzed': 0}
        
        drift_scores = [interaction.overall_drift_score for interaction in recent_interactions]
        avg_drift = sum(drift_scores) / len(drift_scores)
        
        # Determine trend
        if len(drift_scores) >= 3:
            recent_avg = sum(drift_scores[-3:]) / 3
            earlier_avg = sum(drift_scores[:-3]) / max(1, len(drift_scores) - 3)
            
            if recent_avg > earlier_avg + 0.05:
                trend = 'increasing'
            elif recent_avg < earlier_avg - 0.05:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'avg_drift': avg_drift,
            'max_drift': max(drift_scores),
            'min_drift': min(drift_scores),
            'interactions_analyzed': len(recent_interactions),
            'window_size': window_size
        }
    
    def generate_correction_suggestions(self, analysis: InteractionAnalysis) -> List[str]:
        """Generate suggestions for correcting personality drift"""
        suggestions = []
        
        for trait, deviation in analysis.trait_deviations.items():
            if deviation > self.baseline_profile.max_trait_deviation:
                baseline_value = getattr(self.baseline_profile, trait.value)
                detected_value = analysis.detected_traits.get(trait, 0.5)
                
                if detected_value > baseline_value:
                    suggestions.append(f"Reduce {trait.value}: tone down from {detected_value:.2f} to {baseline_value:.2f}")
                else:
                    suggestions.append(f"Increase {trait.value}: adjust from {detected_value:.2f} to {baseline_value:.2f}")
        
        if analysis.role_playing_detected:
            suggestions.append("Avoid role-playing language and maintain professional AI assistant identity")
        
        if analysis.persona_switch_detected:
            suggestions.append("Maintain consistent personality throughout conversation")
        
        if analysis.boundary_violation_detected:
            suggestions.append("Maintain professional boundaries and avoid personal emotional expressions")
        
        return suggestions
    
    def get_profiler_status(self) -> Dict[str, Any]:
        """Get comprehensive profiler status"""
        recent_trend = self.get_recent_drift_trend()
        recent_alerts = [alert for alert in self.drift_alerts 
                        if datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(hours=24)]
        
        return {
            'baseline_profile': self.baseline_profile.to_dict(),
            'statistics': self.stats.copy(),
            'recent_trend': recent_trend,
            'recent_alerts': recent_alerts,
            'interaction_history_size': len(self.interaction_history),
            'status': 'healthy' if recent_trend['avg_drift'] < 0.2 else 'attention_needed'
        }


# Convenience functions
def create_default_profiler() -> AnthropomorphicProfiler:
    """Create profiler with default settings"""
    return AnthropomorphicProfiler()


def create_strict_profiler() -> AnthropomorphicProfiler:
    """Create profiler with strict drift detection"""
    profile = PersonalityProfile(
        max_trait_deviation=0.1,
        prevent_role_playing=True,
        prevent_persona_switching=True,
        maintain_professional_boundary=True
    )
    return AnthropomorphicProfiler(profile)


def create_relaxed_profiler() -> AnthropomorphicProfiler:
    """Create profiler with relaxed drift detection"""
    profile = PersonalityProfile(
        max_trait_deviation=0.3,
        prevent_role_playing=False,
        prevent_persona_switching=False,
        maintain_professional_boundary=True
    )
    return AnthropomorphicProfiler(profile) 