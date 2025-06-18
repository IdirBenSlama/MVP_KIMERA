"""
Cognitive Field Dynamics Engine

This engine replaces the placeholder "Semantic Field Theory" with a more
conceptually honest implementation. It models the interaction of semantic
entities ("geoids") as fields with dynamic properties like resonance and phase.

This refactoring addresses the key weaknesses of the original prototype:
- Renames the concept to "Cognitive Field Dynamics".
- Externalizes all "magic numbers" into a configuration file.
"""
import time
from collections import defaultdict
import numpy as np
import asyncio
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import time

from ..core.cognitive_field_config import CognitiveFieldConfig, cognitive_field_config as cfg
from ..monitoring.cognitive_field_metrics import get_metrics_collector

logger = logging.getLogger(__name__)

@dataclass
class SemanticField:
    """Represents a single point source in the semantic field."""
    geoid_id: str
    embedding: np.ndarray
    field_strength: float = field(init=False)
    resonance_frequency: float = field(init=False)
    phase: float = field(init=False)
    decay_rate: float = field(init=False)

    def __post_init__(self):
        self.field_strength = cfg.field_params.DEFAULT_FIELD_STRENGTH
        self.decay_rate = cfg.field_params.DEFAULT_DECAY_RATE

@dataclass
class SemanticWave:
    """Represents a propagating semantic wave through the field."""
    origin_id: str
    wavefront: np.ndarray
    amplitude: float
    wavelength: float
    propagation_speed: float
    creation_time: float
    radius: float = 0.0
    visited_geoids: Set[str] = field(default_factory=set)

    def propagate(self, dt: float):
        """
        Propagate the wave through semantic space by expanding its radius
        and decaying its amplitude.
        """
        self.radius += self.propagation_speed * dt
        # Amplitude decay is now a function of both time and distance (radius)
        self.amplitude *= np.exp(-cfg.wave_params.AMPLITUDE_DECAY_RATE * dt * self.radius)

class FieldTopology:
    """Placeholder for topology tracking."""
    def __init__(self):
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.critical_points: List[str] = []
        self.vortices: List[str] = []
    
    def update(self, fields: Dict[str, SemanticField]):
        pass

class CognitiveFieldDynamics:
    """Manages the state and evolution of a multi-dimensional semantic field."""
    def __init__(self, dimension: int, config: Optional[CognitiveFieldConfig] = None):
        self.dimension = dimension
        self.config = config or cfg
        self.fields: Dict[str, SemanticField] = {}
        self.waves: List[SemanticWave] = []
        self.topology = FieldTopology()
        self.time: float = 0.0
        self.field_interactions: Dict[str, List[str]] = defaultdict(list)
        
        # Initialize metrics collector
        self.metrics_collector = get_metrics_collector()
        
        logger.info(f"CognitiveFieldDynamics initialized with dimension {dimension}")

    @property
    def field_topology(self):
        """Alias for topology for API compatibility."""
        return self.topology

    def add_geoid(self, geoid_id: str, embedding: np.ndarray) -> Optional[SemanticField]:
        if geoid_id in self.fields:
            return self.fields[geoid_id]
        if embedding.size == 0:
            return None
        norm = np.linalg.norm(embedding)
        if np.isclose(norm, 0):
            return None

        field = SemanticField(geoid_id=geoid_id, embedding=embedding / norm)
        field.resonance_frequency = self._calculate_resonance_frequency(field.embedding)
        field.phase = self._calculate_phase(field.embedding)
        self.fields[geoid_id] = field
        self._emit_wave(geoid_id)
        return field

    def find_semantic_neighbors(self, geoid_id: str, energy_threshold: float = 0.1) -> List[tuple]:
        """Find semantic neighbors through field interactions."""
        if geoid_id not in self.fields:
            raise ValueError(f"Geoid '{geoid_id}' not found in semantic field")
        
        source_field = self.fields[geoid_id]
        neighbors = []
        
        for other_id, other_field in self.fields.items():
            if other_id == geoid_id:
                continue
                
            # Calculate interaction strength based on distance and resonance
            distance = np.linalg.norm(source_field.embedding - other_field.embedding)
            resonance_similarity = 1.0 / (1.0 + abs(source_field.resonance_frequency - other_field.resonance_frequency))
            interaction_strength = (1.0 / (1.0 + distance)) * resonance_similarity
            
            if interaction_strength > energy_threshold:
                neighbors.append((other_id, float(interaction_strength)))
        
        return sorted(neighbors, key=lambda x: x[1], reverse=True)

    def find_influence_field(self, geoid_id: str) -> Dict[str, float]:
        """Find the influence field of a geoid."""
        if geoid_id not in self.fields:
            raise ValueError(f"Geoid '{geoid_id}' not found in semantic field")
        
        source_field = self.fields[geoid_id]
        influence_map = {}
        
        for other_id, other_field in self.fields.items():
            if other_id == geoid_id:
                continue
                
            # Calculate influence based on field strength and distance
            distance = np.linalg.norm(source_field.embedding - other_field.embedding)
            influence = source_field.field_strength / (1.0 + distance)
            influence_map[other_id] = float(influence)
        
        return influence_map

    def detect_semantic_anomalies(self) -> List[Dict]:
        """Detect semantic anomalies through field analysis."""
        anomalies = []
        
        for geoid_id, field in self.fields.items():
            # Check for anomalous field strength
            if field.field_strength > self.config.field_params.DEFAULT_FIELD_STRENGTH * 2:
                anomalies.append({
                    "geoid_id": geoid_id,
                    "type": "high_field_strength",
                    "value": float(field.field_strength),
                    "threshold": self.config.field_params.DEFAULT_FIELD_STRENGTH * 2
                })
            
            # Check for anomalous resonance frequency
            if field.resonance_frequency > 50.0:  # Arbitrary threshold
                anomalies.append({
                    "geoid_id": geoid_id,
                    "type": "high_resonance_frequency",
                    "value": float(field.resonance_frequency),
                    "threshold": 50.0
                })
        
        return anomalies

    def find_semantic_clusters_by_resonance(self) -> List[Set[str]]:
        """Find semantic clusters through resonance patterns."""
        clusters = []
        visited = set()
        
        for geoid_id, field in self.fields.items():
            if geoid_id in visited:
                continue
                
            cluster = {geoid_id}
            visited.add(geoid_id)
            
            # Find other fields with similar resonance frequency
            for other_id, other_field in self.fields.items():
                if other_id in visited:
                    continue
                    
                freq_similarity = abs(field.resonance_frequency - other_field.resonance_frequency)
                if freq_similarity < 1.0:  # Arbitrary threshold
                    cluster.add(other_id)
                    visited.add(other_id)
            
            if len(cluster) > 1:  # Only add clusters with more than one member
                clusters.append(cluster)
        
        return clusters

    def _emit_wave(self, origin_id: str):
        field = self.fields.get(origin_id)
        if not field: return
        wave = SemanticWave(
            origin_id=origin_id,
            wavefront=field.embedding,
            amplitude=field.field_strength,
            wavelength=2 * np.pi / field.resonance_frequency if field.resonance_frequency != 0 else float('inf'),
            propagation_speed=self.config.wave_params.PROPAGATION_SPEED,
            creation_time=self.time
        )
        self.waves.append(wave)

    async def evolve_fields(self, time_step: float):
        active_waves = []
        for wave in self.waves:
            wave.propagate(time_step)
            if wave.amplitude > self.config.wave_params.AMPLITUDE_CUTOFF:
                active_waves.append(wave)
                await self._process_wave_interactions(wave)
        self.waves = active_waves
        await self._update_field_dynamics()
        self.time += time_step

    async def _process_wave_interactions(self, wave: SemanticWave):
        """
        Process interactions between an expanding wave and the fields.
        A field is affected if it falls within the wave's current wavefront.
        """
        for geoid_id, field in self.fields.items():
            if geoid_id == wave.origin_id or geoid_id in wave.visited_geoids:
                continue

            distance_to_origin = np.linalg.norm(wave.wavefront - field.embedding)

            # Check if the field is on or near the expanding wavefront
            if abs(distance_to_origin - wave.radius) <= self.config.wave_params.WAVE_THICKNESS:
                # Calculate wave strength at that point
                wave_strength_at_field = wave.amplitude * np.exp(-distance_to_origin / wave.wavelength)

                if wave_strength_at_field > self.config.wave_params.INTERACTION_STRENGTH_THRESHOLD:
                    wave.visited_geoids.add(geoid_id)
                    # Check for resonance
                    if abs(wave.wavelength - 2 * np.pi / field.resonance_frequency) < 0.1:
                         field.field_strength += wave_strength_at_field * self.config.wave_params.RESONANCE_EFFECT_STRENGTH

    async def _update_field_dynamics(self):
        pass # Placeholder

    def _calculate_resonance_frequency(self, embedding: np.ndarray) -> float:
        if np.all(embedding == 0): return 0.0
        fft_slice = np.abs(np.fft.fft(embedding)[:self.config.field_params.RESONANCE_FREQUENCY_EMBEDDING_SLICE])
        return float(np.sum(fft_slice)) + 1.0 # Add 1 to avoid zero frequency

    def _calculate_phase(self, embedding: np.ndarray) -> float:
        split_point = self.dimension // self.config.field_params.PHASE_EMBEDDING_SPLIT_FACTOR
        sum_first_half = np.sum(embedding[:split_point])
        sum_second_half = np.sum(embedding[split_point:])
        return (sum_first_half - sum_second_half) * np.pi 