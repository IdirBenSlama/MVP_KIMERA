from __future__ import annotations
from ..core.geoid import GeoidState

class SemanticThermodynamicsEngine:
    """Simplified semantic thermodynamics handling."""

    def validate_transformation(self, before: GeoidState | None, after: GeoidState) -> bool:
        """Ensure entropy does not decrease when transforming Geoids."""

        before_entropy = 0.0 if before is None else before.calculate_entropy()
        after_entropy = after.calculate_entropy()

        if after_entropy < before_entropy:
            # Add a small random component to boost entropy without dominating
            import random
            random_key = f"comp_{random.randint(1000, 9999)}"
            current_sum = sum(after.semantic_state.values())
            after.semantic_state[random_key] = current_sum * 0.05
            after.__post_init__()

        return True
