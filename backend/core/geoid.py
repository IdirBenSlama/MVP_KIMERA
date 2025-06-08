from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
import numpy as np

@dataclass
class GeoidState:
    """Core Geoid implementation following DOC-201 specification"""

    geoid_id: str
    semantic_state: Dict[str, float] = field(default_factory=dict)
    symbolic_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.semantic_state:
            total = sum(self.semantic_state.values())
            if total > 0:
                self.semantic_state = {k: v/total for k, v in self.semantic_state.items()}

    def calculate_entropy(self) -> float:
        if not self.semantic_state:
            return 0.0
        probs = list(self.semantic_state.values())
        return float(-sum(p * np.log2(p) for p in probs if p > 0))

    def update_semantic_state(self, new_features: Dict[str, float]):
        self.semantic_state.update(new_features)
        self.__post_init__()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'geoid_id': self.geoid_id,
            'semantic_state': self.semantic_state,
            'symbolic_state': self.symbolic_state,
            'metadata': self.metadata
        }
