from typing import List, Dict
import numpy as np
from scipy.spatial.distance import cosine
from dataclasses import dataclass
from ..core.geoid import GeoidState

@dataclass
class TensionGradient:
    """Represents semantic tension between Geoids"""
    geoid_a: str
    geoid_b: str
    tension_score: float
    gradient_type: str  # 'symbolic', 'embedding', 'layer'

class ContradictionEngine:
    """Implementation of DOC-205a Contradiction Engine specification"""

    def __init__(self, tension_threshold: float = 0.75):
        self.tension_threshold = tension_threshold
        self.active_tensions = {}

    def detect_tension_gradients(self, geoids: List[GeoidState]) -> List[TensionGradient]:
        """Map tension gradients across semantic field"""
        tensions = []

        for i, geoid_a in enumerate(geoids):
            for geoid_b in geoids[i+1:]:
                tension = self._calculate_composite_tension(geoid_a, geoid_b)

                if tension.tension_score > self.tension_threshold:
                    tensions.append(tension)

        return tensions

    def _calculate_composite_tension(self, geoid_a: GeoidState, geoid_b: GeoidState) -> TensionGradient:
        """Calculate composite tension score using multiple measures"""

        # Vector misalignment (semantic_state embedding distance)
        vector_misalignment = self._embedding_misalignment(geoid_a, geoid_b)

        # Layer conflict (semantic vs symbolic disagreement)
        layer_conflict = self._layer_conflict_intensity(geoid_a, geoid_b)

        # Symbolic opposition (direct logical conflicts)
        symbolic_opposition = self._symbolic_opposition(geoid_a, geoid_b)

        # Composite score with tunable coefficients
        composite_score = (0.4 * vector_misalignment +
                          0.3 * layer_conflict +
                          0.3 * symbolic_opposition)

        gradient_type = self._determine_gradient_type(vector_misalignment, layer_conflict, symbolic_opposition)

        return TensionGradient(
            geoid_a=geoid_a.geoid_id,
            geoid_b=geoid_b.geoid_id,
            tension_score=composite_score,
            gradient_type=gradient_type
        )

    def _embedding_misalignment(self, geoid_a: GeoidState, geoid_b: GeoidState) -> float:
        """Calculate semantic embedding distance"""
        if not geoid_a.semantic_state or not geoid_b.semantic_state:
            return 0.0

        # Create aligned feature vectors
        all_features = set(geoid_a.semantic_state.keys()) | set(geoid_b.semantic_state.keys())

        vec_a = [geoid_a.semantic_state.get(f, 0.0) for f in all_features]
        vec_b = [geoid_b.semantic_state.get(f, 0.0) for f in all_features]

        if not any(vec_a) or not any(vec_b):
            return 0.0

        import numpy as np
        if np.linalg.norm(vec_a) == 0 or np.linalg.norm(vec_b) == 0:
            return 0.0

        return cosine(vec_a, vec_b)

    def calculate_pulse_strength(self, tension: TensionGradient,
                                geoids_dict: Dict[str, GeoidState]) -> float:
        """Calculate semantic pulse strength per DOC-205a"""
        geoid_a = geoids_dict[tension.geoid_a]
        geoid_b = geoids_dict[tension.geoid_b]

        # Factors: Tension + Axis Misalignment + Mutation Coherence
        axis_misalignment = self._calculate_axis_misalignment(geoid_a, geoid_b)
        mutation_coherence = self._calculate_mutation_coherence(geoid_a, geoid_b)

        pulse_strength = tension.tension_score * axis_misalignment * mutation_coherence
        return min(pulse_strength, 1.0)  # Cap at 1.0

    def decide_collapse_or_surge(self, pulse_strength: float,
                                stability_metrics: Dict[str, float]) -> str:
        """Determine whether to collapse or surge based on pulse analysis"""

        # Collapse conditions (from DOC-205a)
        if (pulse_strength > 0.8 and
            stability_metrics.get('axis_convergence', 0) > 0.75 and
            stability_metrics.get('vault_resonance', 0) > 0.6):
            return 'collapse'

        # Surge conditions
        elif (pulse_strength < 0.5 or
              stability_metrics.get('contradiction_lineage_ambiguity', 0) > 0.7):
            return 'surge'

        else:
            return 'buffer'  # Hold for next cycle

    # Placeholder implementations for internal methods
    def _layer_conflict_intensity(self, geoid_a: GeoidState, geoid_b: GeoidState) -> float:
        return 0.0

    def _symbolic_opposition(self, geoid_a: GeoidState, geoid_b: GeoidState) -> float:
        return 0.0

    def _determine_gradient_type(self, *args) -> str:
        return 'embedding'

    def _calculate_axis_misalignment(self, geoid_a: GeoidState, geoid_b: GeoidState) -> float:
        return 1.0

    def _calculate_mutation_coherence(self, geoid_a: GeoidState, geoid_b: GeoidState) -> float:
        return 1.0
