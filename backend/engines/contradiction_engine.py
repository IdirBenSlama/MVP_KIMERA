from __future__ import annotations
from typing import List, Dict, Optional
from dataclasses import dataclass

from ..core.geoid import GeoidState
from ..core.insight import InsightScar
from ..core.native_math import NativeMath
from ..governance import erl

@dataclass
class TensionGradient:
    geoid_a: str
    geoid_b: str
    tension_score: float
    gradient_type: str

class ContradictionEngine:
    def __init__(self, tension_threshold: float = 0.4):
        self.tension_threshold = tension_threshold

    def detect_tension_gradients(self, geoids: List[GeoidState]) -> List[TensionGradient]:
        """Detect tension gradients using composite scoring."""
        tensions = []
        for i, a in enumerate(geoids):
            for b in geoids[i + 1 :]:
                emb = self._embedding_misalignment(a, b)
                layer = self._layer_conflict_intensity(a, b)
                sym = self._symbolic_opposition(a, b)
                score = (emb + layer + sym) / 3

                if score > self.tension_threshold:
                    tensions.append(
                        TensionGradient(a.geoid_id, b.geoid_id, score, "composite")
                    )
        return tensions

    def _embedding_misalignment(self, a: GeoidState, b: GeoidState) -> float:
        if a.embedding_vector is None or b.embedding_vector is None or \
           len(a.embedding_vector) == 0 or len(b.embedding_vector) == 0:
            return 0.0
        
        # Use native cosine distance implementation
        return NativeMath.cosine_distance(a.embedding_vector, b.embedding_vector)

    def _layer_conflict_intensity(self, a: GeoidState, b: GeoidState) -> float:
        """Simple proxy for semantic vs symbolic layer disagreement."""
        sem_a = set(a.semantic_state)
        sem_b = set(b.semantic_state)
        sym_a = set(a.symbolic_state)
        sym_b = set(b.symbolic_state)

        if not (sem_a or sem_b or sym_a or sym_b):
            return 0.0

        def jaccard_distance(x: set, y: set) -> float:
            if not (x or y):
                return 0.0
            inter = len(x & y)
            union = len(x | y)
            return 1.0 - inter / union

        sem_diff = jaccard_distance(sem_a, sem_b)
        sym_diff = jaccard_distance(sym_a, sym_b)

        return (sem_diff + sym_diff) / 2

    def _symbolic_opposition(self, a: GeoidState, b: GeoidState) -> float:
        """Measure direct conflicts in overlapping symbolic assertions."""
        overlap = set(a.symbolic_state) & set(b.symbolic_state)
        if not overlap:
            return 0.0
        conflicts = sum(
            1 for key in overlap if a.symbolic_state.get(key) != b.symbolic_state.get(key)
        )
        return conflicts / len(overlap)

    def calculate_pulse_strength(self, tension: TensionGradient, geoids: Dict[str, GeoidState]) -> float:
        # For MVP use tension score as pulse strength
        return min(tension.tension_score, 1.0)

    def decide_collapse_or_surge(
        self,
        pulse_strength: float,
        stability: Dict[str, float],
        profile: Dict[str, object] | None = None,
    ) -> str:
        """Determine whether to collapse or surge based on pulse and profile."""

        allow_surges = True
        if profile is not None:
            allow_surges = bool(profile.get("allow_surges", True))

        decision: str
        if pulse_strength > 0.5:
            # More aggressive collapse threshold for MVP tests
            decision = "collapse"
        elif pulse_strength < 0.3:
            decision = "surge"
        else:
            decision = "buffer"

        if not allow_surges and decision == "surge":
            decision = "collapse"

        return decision

    def check_insight_conflict(self, insight: InsightScar, existing_insights: List[InsightScar]) -> Optional[InsightScar]:
        """
        Checks a new insight for conflicts against existing ones and validates it.

        Args:
            insight: The newly generated InsightScar.
            existing_insights: A list of existing insights to check against.

        Returns:
            The validated insight if it's not a conflict, otherwise None.
        """
        # 1. Ethical Reflex Layer (ERL) Hook
        if not erl.validate(insight.echoform_repr):
            # logger.warning(f"Insight {insight.insight_id} rejected by ERL.")
            insight.status = 'deprecated' # Or a new 'quarantined' status
            return None # Fails validation

        # 2. Check for semantic duplicates (simplified for MVP)
        for old_insight in existing_insights:
            # A more robust check would use embedding similarity
            if old_insight.echoform_repr == insight.echoform_repr:
                # logger.info(f"Insight {insight.insight_id} rejected as duplicate of {old_insight.insight_id}")
                return None # It's a duplicate

        # 3. Add more sophisticated contradiction logic here in the future
        # (e.g., if one insight makes a claim that another refutes)

        return insight

