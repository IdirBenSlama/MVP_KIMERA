from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np
import logging

# Mock objects for standalone development
@dataclass
class GeoidState:
    semantic_state: dict

@dataclass
class TensionGradient:
    tension_score: float

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@dataclass
class CoherenceService:
    """
    Computes global system coherence and exposes a temperature signal.
    Implements Task 3.7 from the Re-Contextualization roadmap.
    """

    def _calculate_thematic_alignment(self, geoids: List[GeoidState]) -> float:
        """
        Calculates how thematically aligned the active geoids are.
        Uses cosine similarity on a composite vector of all semantic features.
        """
        if len(geoids) < 2:
            return 1.0

        all_features = set(key for geoid in geoids for key in geoid.semantic_state.keys())
        if not all_features:
            return 1.0

        vectors = []
        for geoid in geoids:
            vector = [geoid.semantic_state.get(feat, 0.0) for feat in all_features]
            vectors.append(vector)
        
        vectors = np.array(vectors)
        # Normalize vectors to prevent magnitude bias
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors_normalized = vectors / np.where(norms > 0, norms, 1)

        # Calculate the mean vector and its magnitude
        mean_vector = np.mean(vectors_normalized, axis=0)
        mean_vector_magnitude = np.linalg.norm(mean_vector)

        # The magnitude of the mean vector of unit vectors is a measure of coherence
        # It's 1.0 if all vectors are identical, and ~0 if they are randomly distributed.
        return mean_vector_magnitude

    def compute_global_coherence(
        self,
        geoids: List[GeoidState],
        tensions: List[TensionGradient],
        support_links: int = 0 # Placeholder for future implementation
    ) -> float:
        """
        Computes the global coherence score ∈ [0, 1].

        Args:
            geoids: A list of active GeoidStates.
            tensions: A list of active TensionGradients.
            support_links: The number of reinforcing links between geoids.
        
        Returns:
            The global coherence score.
        """
        if not geoids:
            return 1.0 # An empty system is perfectly coherent

        # 1. Contradiction Score (lower is better)
        # Penalize based on number and average intensity of contradictions
        contradiction_penalty = 0.0
        if tensions:
            avg_tension = np.mean([t.tension_score for t in tensions])
            # Normalize penalty by number of geoids
            contradiction_penalty = (len(tensions) * avg_tension) / len(geoids)
        
        # 2. Thematic Alignment Score (higher is better)
        thematic_alignment = self._calculate_thematic_alignment(geoids)

        # 3. Support Score (higher is better) - Placeholder
        # More support links mean more coherence.
        support_score = 1.0 - (1 / (1 + support_links)) # Approaches 1 as links increase

        # Combine scores (weights can be tuned)
        # Base coherence is thematic alignment minus any contradiction penalties.
        base_coherence = thematic_alignment - contradiction_penalty
        
        # Support links provide a bonus to the final coherence
        coherence = base_coherence + (1 - base_coherence) * support_score * 0.5 # Bonus fills 50% of the gap to 1.0
        
        # Clamp the result to [0, 1]
        final_coherence = np.clip(coherence, 0, 1)
        log.info(f"Computed global coherence: {final_coherence:.4f} (Alignment: {thematic_alignment:.2f}, Penalty: {contradiction_penalty:.2f})")
        return final_coherence

    @property
    def temperature(self) -> float:
        """
        Exposes a system temperature signal based on coherence.
        Low coherence ⇒ high temperature (exploration mode).
        High coherence ⇒ low temperature (exploitation mode).
        
        Returns:
            A temperature value, typically between 0 and 1.
        """
        # This property must be calculated with a fresh coherence score each time
        # In a real implementation, you would pass the system state here.
        # For the purpose of this service, we assume coherence must be computed
        # externally and passed to this method.
        raise NotImplementedError("Temperature must be calculated from a coherence score. Call compute_global_coherence first.")

    def get_temperature_from_coherence(self, coherence: float) -> float:
        """Calculates temperature from a given coherence score."""
        return 1.0 - coherence 