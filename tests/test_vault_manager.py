import os
import sys
import importlib
from datetime import datetime
import pytest


def _init_modules(db_url: str):
    os.environ["DATABASE_URL"] = db_url
    sys.path.insert(0, os.path.abspath("."))
    import backend.vault.database as db_module
    importlib.reload(db_module)
    import backend.vault.vault_manager as vm_module
    importlib.reload(vm_module)
    return vm_module.VaultManager, db_module.SessionLocal, db_module.ScarDB


def _make_scar(i, weight=1.0):
    from backend.core.scar import ScarRecord
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


@pytest.fixture()
def vault_env(tmp_path):
    db_file = tmp_path / "vault.db"
    VaultManager, SessionLocal, ScarDB = _init_modules(f"sqlite:///{db_file}")
    return VaultManager(), SessionLocal, ScarDB


def test_detect_and_rebalance_counts(vault_env):
    vm, SessionLocal, ScarDB = vault_env
    with SessionLocal() as db:
        db.query(ScarDB).delete()
        db.commit()
    for i in range(6):
        vm.insert_scar(_make_scar(i), [0.0])
    with SessionLocal() as db:
        db.query(ScarDB).update({ScarDB.vault_id: "vault_a"})
        db.commit()

    imbal, over, _ = vm.detect_vault_imbalance()
    assert imbal and over == "vault_a"

    moved = vm.rebalance_vaults()
    assert moved == 3
    with SessionLocal() as db:
        count_a = db.query(ScarDB).filter(ScarDB.vault_id == "vault_a").count()
        count_b = db.query(ScarDB).filter(ScarDB.vault_id == "vault_b").count()
    assert count_a == 3 and count_b == 3


def test_detect_imbalance_by_weight(vault_env):
    vm, SessionLocal, ScarDB = vault_env
    with SessionLocal() as db:
        db.query(ScarDB).delete()
        db.commit()
    for i in range(4):
        weight = 5.0 if i < 3 else 1.0
        vm.insert_scar(_make_scar(10 + i, weight=weight), [0.0])
    with SessionLocal() as db:
        ids = [f"SC{10+i}" for i in range(3)]
        db.query(ScarDB).filter(ScarDB.scar_id.in_(ids)).update(
            {ScarDB.vault_id: "vault_a"}, synchronize_session=False
        )
        db.query(ScarDB).filter(~ScarDB.scar_id.in_(ids)).update(
            {ScarDB.vault_id: "vault_b"}, synchronize_session=False
        )
        db.commit()

    imbal, over, _ = vm.detect_vault_imbalance(by_weight=True)
    assert imbal and over in {"vault_a", "vault_b"}


def test_rebalance_by_weight_moves_correct_scars(vault_env):
    vm, SessionLocal, ScarDB = vault_env
    with SessionLocal() as db:
        db.query(ScarDB).delete()
        db.commit()
    weights = [1.0, 2.0, 2.0, 5.0]
    for i, w in enumerate(weights):
        vm.insert_scar(_make_scar(20 + i, weight=w), [0.0])
    with SessionLocal() as db:
        db.query(ScarDB).update({ScarDB.vault_id: "vault_a"})
        db.commit()

    moved = vm.rebalance_vaults(by_weight=True)
    assert moved == 3
    weight_a = vm.get_total_scar_weight("vault_a")
    weight_b = vm.get_total_scar_weight("vault_b")
    assert weight_a == pytest.approx(5.0)
    assert weight_b == pytest.approx(5.0)

