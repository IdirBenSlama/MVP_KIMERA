# flake8: noqa
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

import pytest
from backend.engines.spde import SPDE  # noqa: E402
from backend.engines.kccl import KimeraCognitiveCycle  # noqa: E402
from backend.engines.contradiction_engine import ContradictionEngine  # noqa: E402
from backend.core.geoid import GeoidState  # noqa: E402


def test_spde_basic():
    eng = SPDE()
    out = eng.diffuse({'a': 1.0, 'b': 0.0})
    assert isinstance(out, dict)
    assert set(out) == {'a', 'b'}


def test_kccl_basic():
    cycle = KimeraCognitiveCycle()
    assert cycle.run_cycle() == 'cycle complete'


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
    assert tensions[0].tension_score == pytest.approx(0.85)


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
