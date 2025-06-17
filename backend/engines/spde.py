from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from ..core.native_math import NativeMath


@dataclass
class SPDE:
    """Simple Semantic Pressure Diffusion Engine."""

    diffusion_rate: float = 0.5
    decay_factor: float = 1.0

    def diffuse(self, state: dict[str, float]) -> dict[str, float]:
        """Return a diffused copy of the state using a Gaussian blur."""
        if not state:
            return {}

        keys = list(state)
        values = [state[k] for k in keys]

        # Gaussian blur across the ordered feature vector using native implementation
        blurred = NativeMath.gaussian_filter_1d(values, sigma=self.decay_factor)
        
        # Apply diffusion
        diffused = [(1 - self.diffusion_rate) * v + self.diffusion_rate * b 
                   for v, b in zip(values, blurred)]

        return dict(zip(keys, diffused))

