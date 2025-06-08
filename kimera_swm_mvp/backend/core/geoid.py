from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

@dataclass
class GeoidState:
    """Core Geoid implementation following DOC-201 specification"""

    geoid_id: str
    semantic_state: Dict[str, float] = field(default_factory=dict)
    symbolic_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure semantic_state is normalized probability distribution"""
        if self.semantic_state:
            total = sum(self.semantic_state.values())
            if total > 0:
                self.semantic_state = {k: v/total for k, v in self.semantic_state.items()}

    def calculate_entropy(self) -> float:
        """Calculate Shannon entropy of semantic_state"""
        if not self.semantic_state:
            return 0.0

        probs = list(self.semantic_state.values())
        # Shannon entropy: -Σ(p * log2(p))
        return -sum(p * np.log2(p) for p in probs if p > 0)

    def update_semantic_state(self, new_features: Dict[str, float]):
        """Update semantic state while maintaining normalization"""
        self.semantic_state.update(new_features)
        self.__post_init__()  # Re-normalize

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'geoid_id': self.geoid_id,
            'semantic_state': self.semantic_state,
            'symbolic_state': self.symbolic_state,
            'metadata': self.metadata
        }
