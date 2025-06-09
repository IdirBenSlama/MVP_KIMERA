import os
import sys
import pytest

os.environ["ENABLE_JOBS"] = "0"

sys.path.insert(0, os.path.abspath('.'))

from backend.engines.spde import SPDE
from backend.engines.kccl import KimeraCognitiveCycle
from backend.engines.contradiction_engine import ContradictionEngine
from backend.core.geoid import GeoidState
from scipy.ndimage import gaussian_filter1d
import numpy as np


def test_spde_basic():
    eng = SPDE()
    state = {'a': 1.0, 'b': 0.0}
    out = eng.diffuse(state)

    vals = np.array([1.0, 0.0])
    blurred = gaussian_filter1d(vals, sigma=1.0, mode='nearest')
    expected = (1 - 0.5) * vals + 0.5 * blurred

    assert isinstance(out, dict)
    assert set(out) == {'a', 'b'}
    assert out['a'] == pytest.approx(expected[0])
    assert out['b'] == pytest.approx(expected[1])


def test_spde_custom_parameters():
    eng = SPDE(diffusion_rate=1.0, decay_factor=0.5)
    state = {'a': 1.0, 'b': 0.0, 'c': 0.0}
    out = eng.diffuse(state)

    vals = np.array([1.0, 0.0, 0.0])
    expected = gaussian_filter1d(vals, sigma=0.5, mode='nearest')

    assert [out[k] for k in state] == pytest.approx(expected)


def test_kccl_basic():
    cycle = KimeraCognitiveCycle()
    class DummyVault:
        def __init__(self):
            self.count = 0
        def insert_scar(self, scar, vector):
            self.count += 1

    system = {
        'spde_engine': SPDE(),
        'contradiction_engine': ContradictionEngine(tension_threshold=0.5),
        'vault_manager': DummyVault(),
        'active_geoids': {
            'A': GeoidState('A', {'x': 1.0}),
            'B': GeoidState('B', {'y': 1.0}),
        },
        'system_state': {'cycle_count': 0},
    }

    out = cycle.run_cycle(system)
    assert out == 'cycle complete'
    assert system['system_state']['cycle_count'] == 1


def test_kccl_cycle_stats_and_scars():
    cycle = KimeraCognitiveCycle()

    class DummyVault:
        def __init__(self):
            self.count = 0

        def insert_scar(self, scar, vector):
            self.count += 1

    system = {
        'spde_engine': SPDE(),
        'contradiction_engine': ContradictionEngine(tension_threshold=0.5),
        'vault_manager': DummyVault(),
        'active_geoids': {
            'A': GeoidState('A', {'x': 1.0}),
            'B': GeoidState('B', {'y': 1.0}),
        },
        'system_state': {'cycle_count': 0},
    }

    cycle.run_cycle(system)

    assert system['system_state']['cycle_count'] == 1
    stats = system['system_state'].get('last_cycle', {})
    assert stats.get('scars_created', 0) == system['vault_manager'].count
    assert stats.get('contradictions_detected', 0) >= 1
    assert 'entropy_before_diffusion' in stats
    assert 'entropy_after_diffusion' in stats
    assert 'entropy_delta' in stats
    assert stats['entropy_delta'] == pytest.approx(
        stats['entropy_after_diffusion'] - stats['entropy_before_diffusion']
    )


def test_contradiction_engine_scoring():
    eng = ContradictionEngine(tension_threshold=0.5)
    g1 = GeoidState(
        geoid_id="A",
        semantic_state={"a": 1.0},
        symbolic_state={"status": "on"},
    )
    g2 = GeoidState(
        geoid_id="B",
        semantic_state={"b": 1.0},
        symbolic_state={"status": "off"},
    )

    tensions = eng.detect_tension_gradients([g1, g2])
    assert len(tensions) == 1
    assert tensions[0].gradient_type == "composite"
    assert tensions[0].tension_score == pytest.approx(0.833333, rel=1e-3)


def test_contradiction_engine_no_tension():
    eng = ContradictionEngine(tension_threshold=0.1)
    g1 = GeoidState(
        geoid_id="A",
        semantic_state={"a": 1.0},
        symbolic_state={"status": "on"},
    )
    g2 = GeoidState(
        geoid_id="B",
        semantic_state={"a": 1.0},
        symbolic_state={"status": "on"},
    )

    tensions = eng.detect_tension_gradients([g1, g2])
    assert tensions == []
