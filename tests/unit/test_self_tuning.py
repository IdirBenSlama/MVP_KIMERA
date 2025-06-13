from pathlib import Path
import json
import tempfile

from backend.governance.self_tuning import SelfTuningMonitor


def test_self_tuning_adjusts_thresholds(tmp_path: Path):
    # Create a temporary config file
    cfg_path = tmp_path / "optimized_settings.json"
    initial_cfg = {
        "governance": {
            "tension_threshold": 0.5,
            "entropy_prune_threshold": 3.0,
        }
    }
    cfg_path.write_text(json.dumps(initial_cfg))

    monitor = SelfTuningMonitor(config_path=cfg_path)

    # Simulate high contradiction rate
    metrics = [{"contradictions_detected": 15, "entropy_delta": 0.2} for _ in range(5)]
    monitor.run_periodic_adjustment(metrics)

    updated = json.loads(cfg_path.read_text())
    assert updated["governance"]["tension_threshold"] > 0.5

    # Simulate low contradiction rate
    metrics_low = [{"contradictions_detected": 0, "entropy_delta": -0.6} for _ in range(5)]
    monitor.run_periodic_adjustment(metrics_low)

    updated2 = json.loads(cfg_path.read_text())
    assert updated2["governance"]["tension_threshold"] < updated["governance"]["tension_threshold"]


def test_threshold_bounds(tmp_path: Path):
    """Ensure tension_threshold never exceeds bounds even after many cycles."""
    cfg_path = tmp_path / "optimized_settings.json"
    initial_cfg = {
        "governance": {
            "tension_threshold": 0.5,
            "entropy_prune_threshold": 3.0,
        }
    }
    cfg_path.write_text(json.dumps(initial_cfg))

    monitor = SelfTuningMonitor(config_path=cfg_path)

    # Force repeated increases beyond MAX_TENSION
    high_metrics = [{"contradictions_detected": 50, "entropy_delta": 0.0}]
    for _ in range(50):
        monitor.run_periodic_adjustment(high_metrics)

    cfg = json.loads(cfg_path.read_text())
    assert cfg["governance"]["tension_threshold"] <= monitor.MAX_TENSION

    # Force repeated decreases below MIN_TENSION
    low_metrics = [{"contradictions_detected": 0, "entropy_delta": 0.0}]
    for _ in range(50):
        monitor.run_periodic_adjustment(low_metrics)

    cfg2 = json.loads(cfg_path.read_text())
    assert cfg2["governance"]["tension_threshold"] >= monitor.MIN_TENSION


def test_entropy_prune_threshold_adjustment(tmp_path: Path):
    """Verify prune threshold tightens or loosens based on entropy trend."""
    cfg_path = tmp_path / "optimized_settings.json"
    initial_cfg = {
        "governance": {
            "tension_threshold": 0.5,
            "entropy_prune_threshold": 3.0,
        }
    }
    cfg_path.write_text(json.dumps(initial_cfg))

    monitor = SelfTuningMonitor(config_path=cfg_path)

    # High positive entropy delta -> tighten (decrease) prune threshold
    high_entropy = [{"contradictions_detected": 5, "entropy_delta": 1.5}]
    monitor.run_periodic_adjustment(high_entropy)
    cfg = json.loads(cfg_path.read_text())
    assert cfg["governance"]["entropy_prune_threshold"] < 3.0

    # High negative entropy delta -> loosen (increase) prune threshold
    low_entropy = [{"contradictions_detected": 5, "entropy_delta": -1.0}]
    monitor.run_periodic_adjustment(low_entropy)
    cfg2 = json.loads(cfg_path.read_text())
    assert cfg2["governance"]["entropy_prune_threshold"] > cfg["governance"]["entropy_prune_threshold"] 