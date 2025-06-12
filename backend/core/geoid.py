from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List
import numpy as np

@dataclass
class GeoidState:
    """Core Geoid implementation following DOC-201 specification"""

    geoid_id: str
    semantic_state: Dict[str, float] = field(default_factory=dict)
    symbolic_state: Dict[str, Any] = field(default_factory=dict)
    embedding_vector: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_entropy(self) -> float:
        """Calculate Shannon entropy of the semantic state."""
        if not self.semantic_state:
            return 0.0

        # Normalize the semantic state values into a probability distribution
        # before calculating entropy. This is done on-the-fly.
        values = np.array(list(self.semantic_state.values()))
        total = np.sum(values)
        if total <= 0:
            return 0.0
            
        probabilities = values / total
        probabilities = probabilities[probabilities > 0]
        
        if probabilities.size == 0:
            return 0.0
        return float(-np.sum(probabilities * np.log2(probabilities)))

    def update_semantic_state(self, new_features: Dict[str, float]):
        self.semantic_state.update(new_features)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'geoid_id': self.geoid_id,
            'semantic_state': self.semantic_state,
            'symbolic_state': self.symbolic_state,
            'embedding_vector': self.embedding_vector,
            'metadata': self.metadata
        }

