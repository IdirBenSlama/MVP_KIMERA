import os
import sys
import importlib
from datetime import datetime

os.environ["DATABASE_URL"] = "sqlite:///./vault_test.db"
if os.path.exists("./vault_test.db"):
    os.remove("./vault_test.db")

sys.path.insert(0, os.path.abspath("."))

import backend.vault.database as db_module
importlib.reload(db_module)
import backend.vault.vault_manager as vm_module
importlib.reload(vm_module)

from backend.core.scar import ScarRecord

VaultManager = vm_module.VaultManager
SessionLocal = db_module.SessionLocal
ScarDB = db_module.ScarDB


def _make_scar(i, weight=1.0):
    return ScarRecord(
        scar_id=f"SC{i}",
        geoids=[f"G{i}"],
        reason="test",
        timestamp=datetime.utcnow().isoformat(),
        resolved_by="unit",
        pre_entropy=0.0,
        post_entropy=0.0,
        delta_entropy=0.0,
        cls_angle=0.0,
        semantic_polarity=0.0,
        mutation_frequency=0.0,
        weight=weight,
    )


def test_detect_and_rebalance_counts():
    vm = VaultManager()
    for i in range(6):
        vm.insert_scar(_make_scar(i), [0.0])
    # force all scars into vault_a to create imbalance
    with SessionLocal() as db:
        db.query(ScarDB).update({ScarDB.vault_id: "vault_a"})
        db.commit()

    imbal, over, under = vm.detect_vault_imbalance()
    assert imbal and over == "vault_a"

    moved = vm.rebalance_vaults()
    assert moved > 0
    balanced, *_ = vm.detect_vault_imbalance()
    assert not balanced


def test_detect_imbalance_by_weight():
    vm = VaultManager()
    for i in range(4):
        weight = 5.0 if i < 3 else 1.0
        vm.insert_scar(_make_scar(10 + i, weight=weight), [0.0])
    with SessionLocal() as db:
        ids = [f"SC{10+i}" for i in range(3)]
        db.query(ScarDB).filter(ScarDB.scar_id.in_(ids)).update({ScarDB.vault_id: "vault_a"}, synchronize_session=False)
        db.query(ScarDB).filter(~ScarDB.scar_id.in_(ids)).update({ScarDB.vault_id: "vault_b"}, synchronize_session=False)
        db.commit()

    imbal, over, _ = vm.detect_vault_imbalance(by_weight=True)
    assert imbal and over in {"vault_a", "vault_b"}

