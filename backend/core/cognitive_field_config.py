"""
Configuration parameters for the Cognitive Field Dynamics engine.

Externalizing these values allows for easier tuning and experimentation without
modifying the core engine logic. This addresses the "magic numbers" critique
of the initial prototype.
"""

from dataclasses import dataclass, field

@dataclass
class FieldParams:
    """Parameters for individual semantic fields."""
    DEFAULT_FIELD_STRENGTH: float = 1.0
    DEFAULT_DECAY_RATE: float = 0.1
    RESONANCE_DISTANCE_FACTOR: float = 0.1
    RESONANCE_FREQUENCY_EMBEDDING_SLICE: int = 10
    PHASE_EMBEDDING_SPLIT_FACTOR: int = 2

@dataclass
class WaveParams:
    """Parameters for propagating semantic waves."""
    PROPAGATION_SPEED: float = 1.0 # Default speed of semantic waves
    AMPLITUDE_DECAY_RATE: float = 0.01
    INTERACTION_STRENGTH_THRESHOLD: float = 0.1
    RESONANCE_EFFECT_STRENGTH: float = 0.1
    AMPLITUDE_CUTOFF: float = 0.01
    WAVE_THICKNESS: float = 0.1  # Defines the tolerance for a wave hitting a field
    RESONANCE_THRESHOLD: float = 0.1  # Threshold for resonance detection

@dataclass
class InteractionParams:
    """Parameters for field-to-field interactions."""
    INTERFERENCE_FACTOR: float = 0.5
    RESONANCE_CONTRIBUTION_FACTOR: float = 0.3

@dataclass
class AnomalyParams:
    """Parameters for anomaly detection."""
    FIELD_GRADIENT_THRESHOLD: float = 2.0
    FIELD_GRADIENT_SAMPLING_POINTS: int = 10
    FIELD_GRADIENT_EPSILON: float = 0.01
    DESTRUCTIVE_INTERFERENCE_THRESHOLD: float = -0.1
    DESTRUCTIVE_INTERFERENCE_COUNT_THRESHOLD: int = 3

@dataclass
class ClusterParams:
    """Parameters for resonance-based clustering."""
    RESONANCE_THRESHOLD: float = 0.5
    FREQUENCY_SIMILARITY_THRESHOLD: float = 0.7
    BASE_FREQUENCY_DAMPING_FACTOR: int = 10

@dataclass
class CognitiveFieldConfig:
    """Master configuration for the Cognitive Field Dynamics engine."""
    field_params: FieldParams = field(default_factory=FieldParams)
    wave_params: WaveParams = field(default_factory=WaveParams)
    interaction_params: InteractionParams = field(default_factory=InteractionParams)
    anomaly_params: AnomalyParams = field(default_factory=AnomalyParams)
    cluster_params: ClusterParams = field(default_factory=ClusterParams)

# Create a single, importable instance of the configuration.
cognitive_field_config = CognitiveFieldConfig() 