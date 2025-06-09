import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from backend.engines.spde import SPDE
from backend.engines.kccl import KimeraCognitiveCycle


def test_spde_basic():
    eng = SPDE()
    out = eng.diffuse({'a': 1.0, 'b': 0.0})
    assert isinstance(out, dict)
    assert set(out) == {'a', 'b'}


def test_kccl_basic():
    cycle = KimeraCognitiveCycle()
    assert cycle.run_cycle() == 'cycle complete'
