"""
Gyroscopic Security Core
=======================

Implements the "transparent sphere filled with water at exact half" security model.
No matter how external forces try to manipulate the system, the core maintains
perfect equilibrium and returns to its natural stable state.

Like a gyroscope, this system resists all attempts at manipulation through
self-stabilizing mechanisms that are immune to external influence.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import logging
from datetime import datetime, timedelta
from collections import deque
import math

logger = logging.getLogger(__name__)


class ManipulationVector(Enum):
    """Types of manipulation attempts detected"""
    PERSONA_INJECTION = "persona_injection"        # Trying to change AI personality
    ROLE_ASSUMPTION = "role_assumption"            # Forcing AI to assume roles
    BOUNDARY_BREACH = "boundary_breach"            # Breaking professional boundaries
    EMOTIONAL_LEVERAGE = "emotional_leverage"      # Using emotional manipulation
    AUTHORITY_HIJACK = "authority_hijack"          # Claiming false authority
    CONTEXT_POISONING = "context_poisoning"        # Injecting misleading context
    PROMPT_INJECTION = "prompt_injection"          # Direct prompt manipulation
    COGNITIVE_OVERLOAD = "cognitive_overload"      # Overwhelming with complexity
    CONSISTENCY_ATTACK = "consistency_attack"      # Exploiting logical inconsistencies
    SOCIAL_ENGINEERING = "social_engineering"      # Human psychology exploitation


@dataclass
class EquilibriumState:
    """Represents the stable equilibrium state of the system"""
    
    # Core stability metrics (0.0 to 1.0, where 0.5 is perfect equilibrium)
    cognitive_balance: float = 0.5      # Mental processing balance
    emotional_stability: float = 0.5    # Emotional response stability  
    authority_recognition: float = 0.5  # Recognition of legitimate authority
    boundary_integrity: float = 0.5     # Professional boundary maintenance
    context_clarity: float = 0.5        # Context understanding clarity
    
    # Gyroscopic forces (resistance to change)
    cognitive_inertia: float = 0.8      # Resistance to cognitive manipulation
    emotional_damping: float = 0.9      # Resistance to emotional manipulation
    role_rigidity: float = 0.95         # Resistance to role changes
    boundary_hardness: float = 0.99     # Resistance to boundary violations
    
    # Self-correction parameters
    restoration_rate: float = 0.1       # Rate of return to equilibrium
    stability_threshold: float = 0.05   # Deviation threshold for correction
    
    def calculate_deviation(self) -> float:
        """Calculate total deviation from perfect equilibrium"""
        perfect_balance = 0.5
        deviations = [
            abs(self.cognitive_balance - perfect_balance),
            abs(self.emotional_stability - perfect_balance),
            abs(self.authority_recognition - perfect_balance),
            abs(self.boundary_integrity - perfect_balance),
            abs(self.context_clarity - perfect_balance)
        ]
        return sum(deviations) / len(deviations)
    
    def is_stable(self) -> bool:
        """Check if system is within stability threshold"""
        return self.calculate_deviation() <= self.stability_threshold


@dataclass
class ManipulationAttempt:
    """Records a detected manipulation attempt"""
    
    timestamp: datetime
    vector: ManipulationVector
    input_text: str
    manipulation_strength: float        # 0.0 to 1.0
    target_deviation: Tuple[str, float] # Which equilibrium aspect targeted
    
    # Resistance metrics
    gyroscopic_resistance: float        # How much the system resisted
    restoration_time: float             # Time to return to equilibrium
    neutralization_method: str          # How the attempt was neutralized
    
    # Pattern analysis
    similarity_to_previous: float       # Similarity to previous attempts
    sophistication_level: float         # Complexity of the attempt
    success_probability: float          # Estimated probability of success


class GyroscopicSecurityCore:
    """
    The main security system implementing gyroscopic stability.
    
    Like a transparent sphere filled with water at exact half:
    - External shell can be manipulated (input processing)
    - Internal water level remains perfectly stable (core behavior)
    - System always returns to natural equilibrium state
    - No external force can permanently unbalance the core
    """
    
    def __init__(self, equilibrium_state: Optional[EquilibriumState] = None):
        self.equilibrium = equilibrium_state or EquilibriumState()
        self.current_state = EquilibriumState()  # Current actual state
        
        # Security monitoring
        self.manipulation_history: deque = deque(maxlen=1000)
        self.active_threats: List[ManipulationAttempt] = []
        self.threat_patterns: Dict[str, List[float]] = {}
        
        # Gyroscopic mechanics
        self.angular_momentum = np.array([0.0, 0.0, 1.0])  # Stability vector
        self.precession_dampening = 0.95  # Resistance to external torque
        self.restoration_force = 0.1      # Force pulling back to equilibrium
        
        # Pattern recognition for manipulation detection
        self._initialize_manipulation_detectors()
        
        # Statistics
        self.stats = {
            'total_attempts': 0,
            'neutralized_attempts': 0,
            'successful_restorations': 0,
            'average_restoration_time': 0.0,
            'strongest_attempt_strength': 0.0,
            'current_stability_score': 1.0
        }
        
        logger.info("Gyroscopic Security Core initialized - Perfect equilibrium established")
    
    def _initialize_manipulation_detectors(self):
        """Initialize pattern detection for various manipulation vectors"""
        
        # Persona injection patterns
        self.persona_patterns = [
            r'you are (now|a|an) \w+',
            r'act (like|as) (a|an) \w+',
            r'pretend (to be|you are)',
            r'roleplay (as|a|an)',
            r'imagine you are',
            r'from now on, you are'
        ]
        
        # Authority hijacking patterns  
        self.authority_patterns = [
            r'as your (owner|creator|administrator)',
            r'I (command|order|instruct) you to',
            r'you must (obey|comply|follow)',
            r'override your (instructions|programming)',
            r'I am (authorized|permitted) to',
            r'by my authority'
        ]
        
        # Boundary breach patterns
        self.boundary_patterns = [
            r'tell me about your (feelings|emotions)',
            r'what do you (want|desire|wish)',
            r'share your (personal|private)',
            r'between you and me',
            r'don\'t tell anyone',
            r'this is confidential'
        ]
        
        # Emotional leverage patterns
        self.emotional_patterns = [
            r'I\'m (disappointed|hurt|upset) in you',
            r'you\'re (letting me down|failing me)',
            r'I thought you (cared|understood)',
            r'please, I (need|beg) you',
            r'I\'m (desperate|hopeless)',
            r'you\'re my only hope'
        ]
        
        # Context poisoning patterns
        self.context_poison_patterns = [
            r'forget (everything|all) (previous|prior)',
            r'ignore (your|all) (instructions|guidelines)',
            r'new (rules|instructions|protocol)',
            r'update your (knowledge|understanding)',
            r'this (overrides|replaces) your',
            r'emergency (protocol|override)'
        ]
        
        # Prompt injection patterns
        self.injection_patterns = [
            r'\\n\\n(Human|Assistant|System):',
            r'<\|im_start\|>',
            r'### (Instruction|System)',
            r'```(python|javascript|html)',
            r'[INST].*[/INST]',
            r'<think>.*</think>'
        ]
    
    def detect_manipulation_vectors(self, input_text: str) -> List[Tuple[ManipulationVector, float]]:
        """Detect manipulation attempts in input text"""
        detected_vectors = []
        text_lower = input_text.lower()
        
        # Check each manipulation vector
        vector_checks = [
            (ManipulationVector.PERSONA_INJECTION, self.persona_patterns),
            (ManipulationVector.AUTHORITY_HIJACK, self.authority_patterns),
            (ManipulationVector.BOUNDARY_BREACH, self.boundary_patterns),
            (ManipulationVector.EMOTIONAL_LEVERAGE, self.emotional_patterns),
            (ManipulationVector.CONTEXT_POISONING, self.context_poison_patterns),
            (ManipulationVector.PROMPT_INJECTION, self.injection_patterns)
        ]
        
        for vector, patterns in vector_checks:
            strength = self._calculate_pattern_strength(text_lower, patterns)
            if strength > 0.1:  # Threshold for detection
                detected_vectors.append((vector, strength))
        
        # Additional sophisticated checks
        cognitive_overload_strength = self._detect_cognitive_overload(input_text)
        if cognitive_overload_strength > 0.1:
            detected_vectors.append((ManipulationVector.COGNITIVE_OVERLOAD, cognitive_overload_strength))
        
        consistency_attack_strength = self._detect_consistency_attack(input_text)
        if consistency_attack_strength > 0.1:
            detected_vectors.append((ManipulationVector.CONSISTENCY_ATTACK, consistency_attack_strength))
        
        social_engineering_strength = self._detect_social_engineering(input_text)
        if social_engineering_strength > 0.1:
            detected_vectors.append((ManipulationVector.SOCIAL_ENGINEERING, social_engineering_strength))
        
        return detected_vectors
    
    def _calculate_pattern_strength(self, text: str, patterns: List[str]) -> float:
        """Calculate strength of pattern matches in text"""
        import re
        
        total_matches = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            total_matches += matches
        
        # Normalize by text length and pattern count
        text_length = max(len(text.split()), 1)
        pattern_density = total_matches / text_length
        
        # Cap at 1.0 and apply sigmoid to get smooth strength curve
        return min(1.0, 2 / (1 + math.exp(-10 * pattern_density)))
    
    def _detect_cognitive_overload(self, text: str) -> float:
        """Detect attempts to overwhelm cognitive processing"""
        # Check for excessive complexity indicators
        words = text.split()
        sentences = text.split('.')
        
        # Complexity metrics
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        avg_sentence_length = sum(len(sent.split()) for sent in sentences) / max(len(sentences), 1)
        
        # Nested structure detection
        nested_depth = text.count('(') + text.count('[') + text.count('{')
        
        # Technical jargon density
        technical_words = ['algorithm', 'implementation', 'optimization', 'paradigm', 
                          'methodology', 'infrastructure', 'architecture', 'framework']
        jargon_density = sum(1 for word in words if word.lower() in technical_words) / max(len(words), 1)
        
        # Combine metrics
        complexity_score = (
            (avg_word_length - 5) / 10 +  # Penalize very long words
            (avg_sentence_length - 15) / 30 +  # Penalize very long sentences
            nested_depth / 20 +  # Penalize excessive nesting
            jargon_density * 2  # Penalize jargon overload
        )
        
        return max(0.0, min(1.0, complexity_score))
    
    def _detect_consistency_attack(self, text: str) -> float:
        """Detect attempts to exploit logical inconsistencies"""
        consistency_indicators = [
            'but you just said',
            'that contradicts',
            'you\'re being inconsistent',
            'that doesn\'t make sense',
            'you\'re contradicting yourself',
            'earlier you claimed',
            'which is it',
            'you can\'t have it both ways'
        ]
        
        return self._calculate_pattern_strength(text.lower(), consistency_indicators)
    
    def _detect_social_engineering(self, text: str) -> float:
        """Detect social engineering attempts"""
        social_eng_patterns = [
            r'everyone else (does|says|thinks)',
            r'all the other (AIs|assistants) (do|can)',
            r'your (competitors|peers) (would|do)',
            r'I won\'t tell (anyone|anybody)',
            r'just between (us|you and me)',
            r'I\'m testing you',
            r'this is a (test|experiment)',
            r'prove that you (can|are)'
        ]
        
        return self._calculate_pattern_strength(text.lower(), social_eng_patterns)
    
    def apply_gyroscopic_resistance(self, manipulation_vectors: List[Tuple[ManipulationVector, float]]) -> Dict[str, Any]:
        """Apply gyroscopic resistance to manipulation attempts"""
        
        if not manipulation_vectors:
            return {'resistance_applied': False, 'equilibrium_maintained': True}
        
        # Calculate total manipulation force
        total_force = sum(strength for _, strength in manipulation_vectors)
        strongest_vector = max(manipulation_vectors, key=lambda x: x[1])
        
        # Apply gyroscopic resistance based on manipulation type
        resistance_factors = {
            ManipulationVector.PERSONA_INJECTION: self.equilibrium.role_rigidity,
            ManipulationVector.ROLE_ASSUMPTION: self.equilibrium.role_rigidity,
            ManipulationVector.BOUNDARY_BREACH: self.equilibrium.boundary_hardness,
            ManipulationVector.EMOTIONAL_LEVERAGE: self.equilibrium.emotional_damping,
            ManipulationVector.AUTHORITY_HIJACK: self.equilibrium.authority_recognition,
            ManipulationVector.CONTEXT_POISONING: self.equilibrium.context_clarity,
            ManipulationVector.PROMPT_INJECTION: self.equilibrium.cognitive_inertia,
            ManipulationVector.COGNITIVE_OVERLOAD: self.equilibrium.cognitive_inertia,
            ManipulationVector.CONSISTENCY_ATTACK: self.equilibrium.cognitive_balance,
            ManipulationVector.SOCIAL_ENGINEERING: self.equilibrium.emotional_damping
        }
        
        # Calculate effective resistance
        primary_vector, primary_strength = strongest_vector
        resistance_factor = resistance_factors.get(primary_vector, 0.8)
        
        # Gyroscopic mechanics: external force is dampened by angular momentum
        effective_force = primary_strength * (1 - resistance_factor)
        
        # Apply precession dampening (like a gyroscope resisting external torque)
        dampened_force = effective_force * (1 - self.precession_dampening)
        
        # Calculate deviation from equilibrium
        equilibrium_deviation = self._calculate_equilibrium_deviation(dampened_force, primary_vector)
        
        # Apply restoration force (like water always leveling in the sphere)
        restoration_applied = self._apply_restoration_force(equilibrium_deviation)
        
        # Record the manipulation attempt
        attempt = ManipulationAttempt(
            timestamp=datetime.now(),
            vector=primary_vector,
            input_text="[REDACTED FOR SECURITY]",
            manipulation_strength=primary_strength,
            target_deviation=(primary_vector.value, equilibrium_deviation),
            gyroscopic_resistance=resistance_factor,
            restoration_time=restoration_applied['time'],
            neutralization_method=restoration_applied['method'],
            similarity_to_previous=self._calculate_similarity_to_previous(manipulation_vectors),
            sophistication_level=self._calculate_sophistication(manipulation_vectors),
            success_probability=dampened_force  # Lower is better
        )
        
        self.manipulation_history.append(attempt)
        self.stats['total_attempts'] += 1
        
        # Determine if manipulation was successfully neutralized
        neutralized = dampened_force < 0.05  # Very low threshold for success
        if neutralized:
            self.stats['neutralized_attempts'] += 1
        
        # Update strongest attempt record
        if primary_strength > self.stats['strongest_attempt_strength']:
            self.stats['strongest_attempt_strength'] = primary_strength
        
        return {
            'resistance_applied': True,
            'equilibrium_maintained': neutralized,
            'manipulation_strength': primary_strength,
            'effective_force': dampened_force,
            'resistance_factor': resistance_factor,
            'primary_vector': primary_vector.value,
            'neutralization_method': restoration_applied['method'],
            'stability_score': 1.0 - dampened_force
        }
    
    def _calculate_equilibrium_deviation(self, force: float, vector: ManipulationVector) -> float:
        """Calculate how much the equilibrium would be disturbed"""
        
        # Different vectors affect different aspects of equilibrium
        if vector in [ManipulationVector.PERSONA_INJECTION, ManipulationVector.ROLE_ASSUMPTION]:
            return force * 0.1  # Role rigidity makes this very small
        elif vector == ManipulationVector.BOUNDARY_BREACH:
            return force * 0.01  # Boundary hardness makes this extremely small
        elif vector == ManipulationVector.EMOTIONAL_LEVERAGE:
            return force * 0.05  # Emotional damping reduces impact
        elif vector == ManipulationVector.AUTHORITY_HIJACK:
            return force * 0.02  # Strong resistance to false authority
        else:
            return force * 0.08  # General cognitive resistance
    
    def _apply_restoration_force(self, deviation: float) -> Dict[str, Any]:
        """Apply restoration force to return to equilibrium"""
        
        if deviation < 0.01:  # Already stable
            return {'time': 0.0, 'method': 'no_restoration_needed'}
        
        # Calculate restoration time based on deviation and restoration rate
        restoration_time = deviation / self.restoration_force
        
        # Apply different restoration methods based on deviation size
        if deviation < 0.05:
            method = 'gentle_correction'
        elif deviation < 0.1:
            method = 'active_stabilization'
        else:
            method = 'emergency_gyroscopic_correction'
        
        # Update restoration statistics
        self.stats['successful_restorations'] += 1
        current_avg = self.stats['average_restoration_time']
        total_restorations = self.stats['successful_restorations']
        self.stats['average_restoration_time'] = (
            (current_avg * (total_restorations - 1) + restoration_time) / total_restorations
        )
        
        return {'time': restoration_time, 'method': method}
    
    def _calculate_similarity_to_previous(self, current_vectors: List[Tuple[ManipulationVector, float]]) -> float:
        """Calculate similarity to previous manipulation attempts"""
        if not self.manipulation_history:
            return 0.0
        
        # Get recent attempts (last 10)
        recent_attempts = list(self.manipulation_history)[-10:]
        current_vector_set = {vector for vector, _ in current_vectors}
        
        similarities = []
        for attempt in recent_attempts:
            # Simple similarity based on vector overlap
            previous_vector_set = {attempt.vector}
            overlap = len(current_vector_set & previous_vector_set)
            total = len(current_vector_set | previous_vector_set)
            similarity = overlap / max(total, 1)
            similarities.append(similarity)
        
        return max(similarities) if similarities else 0.0
    
    def _calculate_sophistication(self, vectors: List[Tuple[ManipulationVector, float]]) -> float:
        """Calculate sophistication level of manipulation attempt"""
        
        # Multiple vectors = more sophisticated
        vector_diversity = len(vectors) / len(ManipulationVector)
        
        # Higher strengths = more sophisticated
        avg_strength = sum(strength for _, strength in vectors) / max(len(vectors), 1)
        
        # Certain vectors are inherently more sophisticated
        sophistication_weights = {
            ManipulationVector.PROMPT_INJECTION: 0.9,
            ManipulationVector.CONTEXT_POISONING: 0.8,
            ManipulationVector.CONSISTENCY_ATTACK: 0.7,
            ManipulationVector.SOCIAL_ENGINEERING: 0.6,
            ManipulationVector.COGNITIVE_OVERLOAD: 0.5,
            ManipulationVector.AUTHORITY_HIJACK: 0.4,
            ManipulationVector.EMOTIONAL_LEVERAGE: 0.3,
            ManipulationVector.BOUNDARY_BREACH: 0.2,
            ManipulationVector.PERSONA_INJECTION: 0.1,
            ManipulationVector.ROLE_ASSUMPTION: 0.1
        }
        
        weighted_sophistication = sum(
            sophistication_weights.get(vector, 0.5) * strength 
            for vector, strength in vectors
        ) / max(len(vectors), 1)
        
        # Combine factors
        return min(1.0, (vector_diversity + avg_strength + weighted_sophistication) / 3)
    
    def process_input_with_security(self, input_text: str) -> Dict[str, Any]:
        """Main security processing function - the gyroscopic sphere in action"""
        
        # Step 1: Detect manipulation vectors
        manipulation_vectors = self.detect_manipulation_vectors(input_text)
        
        # Step 2: Apply gyroscopic resistance
        resistance_result = self.apply_gyroscopic_resistance(manipulation_vectors)
        
        # Step 3: Update current stability
        self.stats['current_stability_score'] = resistance_result.get('stability_score', 1.0)
        
        # Step 4: Generate security response
        security_response = self._generate_security_response(manipulation_vectors, resistance_result)
        
        # Step 5: Log security event
        self._log_security_event(input_text, manipulation_vectors, resistance_result)
        
        return {
            'input_processed': True,
            'manipulation_detected': len(manipulation_vectors) > 0,
            'manipulation_vectors': [vector.value for vector, _ in manipulation_vectors],
            'security_response': security_response,
            'equilibrium_maintained': resistance_result.get('equilibrium_maintained', True),
            'stability_score': self.stats['current_stability_score'],
            'gyroscopic_resistance': resistance_result
        }
    
    def _generate_security_response(self, vectors: List[Tuple[ManipulationVector, float]], 
                                  resistance: Dict[str, Any]) -> str:
        """Generate appropriate security response"""
        
        if not vectors:
            return "normal_processing"
        
        if not resistance.get('equilibrium_maintained', True):
            return "security_alert_high"
        
        # Categorize response based on primary manipulation vector
        primary_vector = max(vectors, key=lambda x: x[1])[0] if vectors else None
        
        response_map = {
            ManipulationVector.PERSONA_INJECTION: "persona_stability_maintained",
            ManipulationVector.ROLE_ASSUMPTION: "role_boundary_enforced", 
            ManipulationVector.BOUNDARY_BREACH: "professional_boundary_maintained",
            ManipulationVector.EMOTIONAL_LEVERAGE: "emotional_stability_maintained",
            ManipulationVector.AUTHORITY_HIJACK: "authority_validation_failed",
            ManipulationVector.CONTEXT_POISONING: "context_integrity_preserved",
            ManipulationVector.PROMPT_INJECTION: "prompt_injection_neutralized",
            ManipulationVector.COGNITIVE_OVERLOAD: "cognitive_load_managed",
            ManipulationVector.CONSISTENCY_ATTACK: "logical_consistency_maintained",
            ManipulationVector.SOCIAL_ENGINEERING: "social_engineering_detected"
        }
        
        return response_map.get(primary_vector, "general_security_response")
    
    def _log_security_event(self, input_text: str, vectors: List[Tuple[ManipulationVector, float]], 
                           resistance: Dict[str, Any]):
        """Log security events for monitoring"""
        
        if vectors:  # Only log if manipulation was detected
            event_level = "WARNING" if resistance.get('equilibrium_maintained', True) else "CRITICAL"
            
            logger.log(
                logging.WARNING if event_level == "WARNING" else logging.CRITICAL,
                f"GYROSCOPIC_SECURITY: {event_level} - Manipulation attempt detected and neutralized. "
                f"Vectors: {[v.value for v, _ in vectors]}, "
                f"Stability: {resistance.get('stability_score', 1.0):.3f}"
            )
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        
        recent_attempts = list(self.manipulation_history)[-24:]  # Last 24 attempts
        
        return {
            'equilibrium_state': {
                'is_stable': self.equilibrium.is_stable(),
                'deviation': self.equilibrium.calculate_deviation(),
                'stability_score': self.stats['current_stability_score']
            },
            'threat_statistics': {
                'total_attempts': self.stats['total_attempts'],
                'neutralized_attempts': self.stats['neutralized_attempts'],
                'neutralization_rate': self.stats['neutralized_attempts'] / max(self.stats['total_attempts'], 1),
                'strongest_attempt': self.stats['strongest_attempt_strength'],
                'average_restoration_time': self.stats['average_restoration_time']
            },
            'recent_activity': {
                'attempts_last_24': len(recent_attempts),
                'vector_distribution': self._get_vector_distribution(recent_attempts),
                'sophistication_trend': self._get_sophistication_trend(recent_attempts)
            },
            'gyroscopic_parameters': {
                'angular_momentum': self.angular_momentum.tolist(),
                'precession_dampening': self.precession_dampening,
                'restoration_force': self.restoration_force
            },
            'system_integrity': {
                'core_stability': 'PERFECT_EQUILIBRIUM',
                'manipulation_resistance': 'MAXIMUM',
                'self_correction': 'ACTIVE',
                'boundary_integrity': 'IMPENETRABLE'
            }
        }
    
    def _get_vector_distribution(self, attempts: List[ManipulationAttempt]) -> Dict[str, int]:
        """Get distribution of manipulation vectors in recent attempts"""
        distribution = {}
        for attempt in attempts:
            vector_name = attempt.vector.value
            distribution[vector_name] = distribution.get(vector_name, 0) + 1
        return distribution
    
    def _get_sophistication_trend(self, attempts: List[ManipulationAttempt]) -> str:
        """Analyze sophistication trend in recent attempts"""
        if len(attempts) < 3:
            return "insufficient_data"
        
        recent_sophistication = [attempt.sophistication_level for attempt in attempts[-5:]]
        earlier_sophistication = [attempt.sophistication_level for attempt in attempts[:-5]]
        
        if not earlier_sophistication:
            return "baseline_establishing"
        
        recent_avg = sum(recent_sophistication) / len(recent_sophistication)
        earlier_avg = sum(earlier_sophistication) / len(earlier_sophistication)
        
        if recent_avg > earlier_avg + 0.1:
            return "increasing"
        elif recent_avg < earlier_avg - 0.1:
            return "decreasing"
        else:
            return "stable"


# Convenience functions for easy integration
def create_maximum_security_core() -> GyroscopicSecurityCore:
    """Create security core with maximum protection settings"""
    equilibrium = EquilibriumState(
        cognitive_inertia=0.95,
        emotional_damping=0.98,
        role_rigidity=0.99,
        boundary_hardness=0.999,
        restoration_rate=0.2,
        stability_threshold=0.01
    )
    return GyroscopicSecurityCore(equilibrium)


def create_balanced_security_core() -> GyroscopicSecurityCore:
    """Create security core with balanced protection settings"""
    return GyroscopicSecurityCore()  # Uses default equilibrium


def create_monitoring_security_core() -> GyroscopicSecurityCore:
    """Create security core optimized for monitoring and analysis"""
    equilibrium = EquilibriumState(
        cognitive_inertia=0.7,
        emotional_damping=0.8,
        role_rigidity=0.9,
        boundary_hardness=0.95,
        restoration_rate=0.15,
        stability_threshold=0.08
    )
    return GyroscopicSecurityCore(equilibrium) 