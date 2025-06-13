from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
import math
import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Mock GeoidState for standalone development
@dataclass
class GeoidState:
    geoid_id: str
    activation_level: float = 1.0
    entropy: float = 0.0

@dataclass
class ActivationManager:
    """
    Manages the decay of geoid activations over time for thermodynamic alignment.
    Implements Task 3.6 from the Re-Contextualization roadmap.
    """
    
    # Exponential decay constant (lambda)
    lambda_decay: float = 0.1
    
    # Entropy boost factor for high-entropy geoids
    entropy_boost_threshold: float = 3.5
    
    # Damping factor for low-entropy geoids
    entropy_damping_threshold: float = 1.0
    damping_factor: float = 0.7 # 70% faster damping

    # Threshold below which activation is considered zero
    activation_floor_threshold: float = 1e-9

    def apply_decay(self, geoids: Dict[str, GeoidState]) -> Dict[str, GeoidState]:
        """
        Applies a single step of activation decay to a dictionary of geoids.

        Args:
            geoids: A dictionary of geoid_id -> GeoidState objects.

        Returns:
            The dictionary of geoids with updated activation levels.
        """
        log.info(f"Applying activation decay to {len(geoids)} geoids.")
        for geoid in geoids.values():
            
            decay_rate = self.lambda_decay
            
            # Apply entropy-based adjustments
            if geoid.entropy > self.entropy_boost_threshold:
                # High entropy slows decay (boosts activation)
                decay_rate /= (1 + (geoid.entropy - self.entropy_boost_threshold))
            elif geoid.entropy < self.entropy_damping_threshold:
                # Low entropy speeds up decay (damps activation)
                decay_rate *= (1 + self.damping_factor)

            # Apply exponential decay formula: A(t) = A(0) * e^(-lambda * t)
            # For a single time step (t=1), this simplifies to:
            geoid.activation_level *= math.exp(-decay_rate)
            
            # If activation is below the threshold, snap to zero
            if geoid.activation_level < self.activation_floor_threshold:
                geoid.activation_level = 0.0
            else:
                # Ensure activation doesn't go below zero (redundant but safe)
                geoid.activation_level = max(0, geoid.activation_level)

        return geoids 