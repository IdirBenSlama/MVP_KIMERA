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