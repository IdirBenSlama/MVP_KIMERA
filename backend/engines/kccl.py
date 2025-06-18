from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from ..core.scar import ScarRecord
from ..core.embedding_utils import encode_text


@dataclass
class KimeraCognitiveCycle:
    """Minimal cognitive loop used for the test suite."""

    def run_cycle(self, system: dict) -> str:
        """Execute one cognitive cycle over the provided system."""
        
        try:
            spde = system["spde_engine"]
            contradiction_engine = system["contradiction_engine"]
            vault_manager = system["vault_manager"]

            cycle_stats = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "contradictions_detected": 0,
                "scars_created": 0,
                "entropy_before_diffusion": 0.0,
                "entropy_after_diffusion": 0.0,
                "entropy_delta": 0.0,
                "errors_encountered": 0,
                "geoids_processed": 0
            }

            # Safety check: limit processing if too many geoids
            active_geoids = system["active_geoids"]
            geoids_to_process = list(active_geoids.values())
            
            if len(geoids_to_process) > 500:  # Safety limit
                import logging
                logging.warning(f"Large geoid count ({len(geoids_to_process)}), limiting to 500 for cycle")
                geoids_to_process = geoids_to_process[:500]
            
            cycle_stats["geoids_processed"] = len(geoids_to_process)

            # --- Semantic Pressure Diffusion ---
            try:
                entropy_before = sum(
                    g.calculate_entropy() for g in geoids_to_process
                )
                
                for geoid in geoids_to_process:
                    try:
                        geoid.semantic_state = spde.diffuse(geoid.semantic_state)
                    except Exception as e:
                        cycle_stats["errors_encountered"] += 1
                        # Continue processing other geoids
                        continue
                        
                entropy_after = sum(
                    g.calculate_entropy() for g in geoids_to_process
                )
                
                cycle_stats["entropy_before_diffusion"] = entropy_before
                cycle_stats["entropy_after_diffusion"] = entropy_after
                cycle_stats["entropy_delta"] = entropy_after - entropy_before
                
            except Exception as e:
                import logging
                logging.error(f"SPDE diffusion failed: {e}")
                cycle_stats["errors_encountered"] += 1

            # --- Contradiction Detection ---
            try:
                tensions = contradiction_engine.detect_tension_gradients(geoids_to_process)
                cycle_stats["contradictions_detected"] = len(tensions)
                
                # Limit tension processing to prevent overload
                tensions_to_process = tensions[:20]  # Process max 20 tensions per cycle
                
                for tension in tensions_to_process:
                    try:
                        summary = f"Tension {tension.geoid_a}-{tension.geoid_b}"
                        vector = encode_text(summary)
                        scar = ScarRecord(
                            scar_id=f"SCAR_{uuid.uuid4().hex[:8]}",
                            geoids=[tension.geoid_a, tension.geoid_b],
                            reason="auto-cycle",
                            timestamp=datetime.now(timezone.utc).isoformat(),
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
                    except Exception as e:
                        import logging
                        logging.warning(f"Failed to process tension {tension.geoid_a}-{tension.geoid_b}: {e}")
                        cycle_stats["errors_encountered"] += 1
                        continue
                        
            except Exception as e:
                import logging
                logging.error(f"Contradiction detection failed: {e}")
                cycle_stats["errors_encountered"] += 1

            # --- Cycle bookkeeping ---
            state = system.setdefault("system_state", {})
            state["cycle_count"] = state.get("cycle_count", 0) + 1
            state["last_cycle"] = cycle_stats

            # --- Meta-Insight Hook (Phase 3.5) ---
            try:
                meta_engine = system.get("meta_insight_engine")
                recent_insights = system.get("recent_insights", [])

                META_INTERVAL = 5  # trigger every N cycles
                if meta_engine and state["cycle_count"] % META_INTERVAL == 0:
                    meta_insights = meta_engine.scan_recent_insights(recent_insights)
                    if meta_insights:
                        # Append generated meta-insights to recent insights list
                        recent_insights.extend(meta_insights)
                        # Keep list size reasonable (latest 100)
                        if len(recent_insights) > 100:
                            del recent_insights[: len(recent_insights) - 100]
            except Exception as exc:
                # Log but never crash the cognitive cycle
                import logging
                logging.getLogger(__name__).warning(
                    "Meta-Insight Engine failed: %s", exc, exc_info=True
                )
                cycle_stats["errors_encountered"] += 1

            # Determine cycle status based on errors
            if cycle_stats["errors_encountered"] == 0:
                return "cycle complete"
            elif cycle_stats["errors_encountered"] < cycle_stats["geoids_processed"] * 0.1:  # Less than 10% error rate
                return "cycle partial"
            else:
                return "cycle degraded"
                
        except Exception as e:
            # Catastrophic failure - log and return error status
            import logging
            logging.error(f"Cognitive cycle catastrophic failure: {e}")
            
            # Ensure basic cycle bookkeeping even on failure
            state = system.setdefault("system_state", {})
            state["cycle_count"] = state.get("cycle_count", 0) + 1
            state["last_cycle"] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "contradictions_detected": 0,
                "scars_created": 0,
                "entropy_before_diffusion": 0.0,
                "entropy_after_diffusion": 0.0,
                "entropy_delta": 0.0,
                "errors_encountered": 1,
                "geoids_processed": 0,
                "failure_reason": str(e)
            }
            
            return "cycle failed"

