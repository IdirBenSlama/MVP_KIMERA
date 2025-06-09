from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.ndimage import gaussian_filter1d


@dataclass
class SPDE:
    """Simple Semantic Pressure Diffusion Engine."""

    diffusion_rate: float = 0.5
    decay_factor: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.diffusion_rate <= 1.0:
            raise ValueError("diffusion_rate must be between 0 and 1")
        if self.decay_factor <= 0.0:
            raise ValueError("decay_factor must be positive")

    def diffuse(self, state: dict[str, float]) -> dict[str, float]:
        """Return a diffused copy of the state using a Gaussian blur."""
        if not state:
            return {}

        keys = list(state)
        values = np.array([state[k] for k in keys], dtype=float)

        # Gaussian blur across the ordered feature vector
        blurred = gaussian_filter1d(values, sigma=self.decay_factor, mode="nearest")
        diffused = (1 - self.diffusion_rate) * values + self.diffusion_rate * blurred

        return dict(zip(keys, diffused.tolist()))
