from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import uuid

from ..core.scar import ScarRecord
from ..core.embedding_utils import encode_text


@dataclass
class KimeraCognitiveCycle:
    """Minimal cognitive loop used for the test suite."""

    def run_cycle(self, system: dict) -> str:
        """Execute one cognitive cycle over the provided system."""

        spde = system["spde_engine"]
        contradiction_engine = system["contradiction_engine"]
        vault_manager = system["vault_manager"]

        cycle_stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "contradictions_detected": 0,
            "scars_created": 0,
        }

        # --- Semantic Pressure Diffusion ---
        for geoid in system["active_geoids"].values():
            geoid.semantic_state = spde.diffuse(geoid.semantic_state)

        # --- Contradiction Detection ---
        geoids = list(system["active_geoids"].values())
        tensions = contradiction_engine.detect_tension_gradients(geoids)
        cycle_stats["contradictions_detected"] = len(tensions)
        for tension in tensions:
            summary = f"Tension {tension.geoid_a}-{tension.geoid_b}"
            vector = encode_text(summary)
            scar = ScarRecord(
                scar_id=f"SCAR_{uuid.uuid4().hex[:8]}",
                geoids=[tension.geoid_a, tension.geoid_b],
                reason="auto-cycle",
                timestamp=datetime.utcnow().isoformat(),
                resolved_by="KimeraCognitiveCycle",
                pre_entropy=0.0,
                post_entropy=0.0,
                delta_entropy=0.0,
                cls_angle=tension.tension_score * 180,
                semantic_polarity=0.0,
                mutation_frequency=tension.tension_score,
            )
            vault_manager.insert_scar(scar, vector)
            cycle_stats["scars_created"] += 1

        # --- Cycle bookkeeping ---
        state = system.setdefault("system_state", {})
        state["cycle_count"] = state.get("cycle_count", 0) + 1
        state["last_cycle"] = cycle_stats

        return "cycle complete"
