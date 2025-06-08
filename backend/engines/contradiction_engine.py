from __future__ import annotations
from typing import List, Dict
from dataclasses import dataclass
from scipy.spatial.distance import cosine

from ..core.geoid import GeoidState

@dataclass
class TensionGradient:
    geoid_a: str
    geoid_b: str
    tension_score: float
    gradient_type: str

class ContradictionEngine:
    def __init__(self, tension_threshold: float = 0.75):
        self.tension_threshold = tension_threshold

    def detect_tension_gradients(self, geoids: List[GeoidState]) -> List[TensionGradient]:
        tensions = []
        for i, a in enumerate(geoids):
            for b in geoids[i+1:]:
                score = self._embedding_misalignment(a, b)
                if score > self.tension_threshold:
                    tensions.append(TensionGradient(a.geoid_id, b.geoid_id, score, 'embedding'))
        return tensions

    def _embedding_misalignment(self, a: GeoidState, b: GeoidState) -> float:
        if not a.semantic_state or not b.semantic_state:
            return 0.0
        keys = set(a.semantic_state) | set(b.semantic_state)
        vec_a = [a.semantic_state.get(k, 0.0) for k in keys]
        vec_b = [b.semantic_state.get(k, 0.0) for k in keys]
        if not any(vec_a) or not any(vec_b):
            return 0.0
        # Extra guard against zero vectors for scipy cosine
        import numpy as np
        if np.linalg.norm(vec_a) == 0 or np.linalg.norm(vec_b) == 0:
            return 0.0
        return float(cosine(vec_a, vec_b))

    def calculate_pulse_strength(self, tension: TensionGradient, geoids: Dict[str, GeoidState]) -> float:
        # For MVP use tension score as pulse strength
        return min(tension.tension_score, 1.0)

    def decide_collapse_or_surge(self, pulse_strength: float, stability: Dict[str, float]) -> str:
        if pulse_strength > 0.8:
            return 'collapse'
        if pulse_strength < 0.5:
            return 'surge'
        return 'buffer'
