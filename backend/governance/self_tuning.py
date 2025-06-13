"""Self-Tuning Governance Monitor
================================
Implements automatic parameter tuning as described in Phase 5 task 5.1.
The monitor analyses recent system metrics and adjusts thresholds in
`config/optimized_settings.json` to maintain optimal behaviour while
respecting safety limits.
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Dict, Any, List

log = logging.getLogger(__name__)
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "optimized_settings.json"

# ──────────────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────────────

def _load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with config_path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _save_config(cfg: Dict[str, Any], config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    with config_path.open("w", encoding="utf-8") as fp:
        json.dump(cfg, fp, indent=2, sort_keys=True)


# ──────────────────────────────────────────────────────────────────────────────
# Self-Tuning Monitor
# ──────────────────────────────────────────────────────────────────────────────

class SelfTuningMonitor:  # noqa: D101
    CONTRADICTION_UPPER = 10  # per cycle
    CONTRADICTION_LOWER = 2

    ENTROPY_DELTA_UPPER = 1.0
    ENTROPY_DELTA_LOWER = -0.5

    MIN_TENSION = 0.1
    MAX_TENSION = 0.9
    STEP = 0.05

    def __init__(self, config_path: Path | str | None = None) -> None:
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.config_cache: Dict[str, Any] | None = None

    # Public API -------------------------------------------------------------

    def run_periodic_adjustment(self, recent_metrics: List[Dict[str, Any]]) -> None:  # noqa: D401
        """Analyse recent metrics and adjust thresholds if required.

        Args:
            recent_metrics: A list of per-cycle metric dictionaries that MUST
                include keys `contradictions_detected` and `entropy_delta`.
        """
        if not recent_metrics:
            log.warning("No metrics supplied to SelfTuningMonitor – skipping.")
            return

        avg_contradictions = sum(m.get("contradictions_detected", 0) for m in recent_metrics) / len(recent_metrics)
        avg_entropy_delta = sum(m.get("entropy_delta", 0.0) for m in recent_metrics) / len(recent_metrics)

        cfg = self._get_config()
        tension_threshold: float = cfg.setdefault("governance", {}).get("tension_threshold", 0.5)

        # --- Adjust tension threshold based on contradiction rate -----------
        if avg_contradictions > self.CONTRADICTION_UPPER:
            tension_threshold = min(self.MAX_TENSION, tension_threshold + self.STEP)
            log.info("High contradiction rate detected (%.2f). Raising tension threshold to %.2f", avg_contradictions, tension_threshold)
        elif avg_contradictions < self.CONTRADICTION_LOWER:
            tension_threshold = max(self.MIN_TENSION, tension_threshold - self.STEP)
            log.info("Low contradiction rate detected (%.2f). Lowering tension threshold to %.2f", avg_contradictions, tension_threshold)

        # --- Potential place for entropy-driven tuning ----------------------
        prune_threshold: float = cfg["governance"].get("entropy_prune_threshold", 3.0)
        if avg_entropy_delta > self.ENTROPY_DELTA_UPPER:
            prune_threshold = max(1.0, prune_threshold - 0.1)
            log.info("Entropy growing quickly (Δ=%.2f). Tightening prune threshold to %.2f", avg_entropy_delta, prune_threshold)
        elif avg_entropy_delta < self.ENTROPY_DELTA_LOWER:
            prune_threshold = min(5.0, prune_threshold + 0.1)
            log.info("Entropy dropping (Δ=%.2f). Loosening prune threshold to %.2f", avg_entropy_delta, prune_threshold)

        # Persist updates
        cfg["governance"]["tension_threshold"] = tension_threshold
        cfg["governance"]["entropy_prune_threshold"] = prune_threshold
        self._save_config(cfg)

    # Internal helpers -------------------------------------------------------

    def _get_config(self) -> Dict[str, Any]:
        if self.config_cache is None:
            self.config_cache = _load_config(self.config_path)
        return self.config_cache

    def _save_config(self, cfg: Dict[str, Any]) -> None:  # noqa: D401
        _save_config(cfg, self.config_path)
        self.config_cache = cfg 