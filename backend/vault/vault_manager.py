from __future__ import annotations
from typing import List
from datetime import datetime

from ..core.scar import ScarRecord
from ..core.geoid import GeoidState
from .database import SessionLocal, ScarDB
import uuid


class VaultManager:
    """Manage persistence of Scar records across multiple vaults."""

    def __init__(self):
        self.db = SessionLocal()

    def _select_vault(self) -> str:
        """Choose a vault based on current counts."""
        a_count = self.get_total_scar_count("vault_a")
        b_count = self.get_total_scar_count("vault_b")
        return "vault_a" if a_count <= b_count else "vault_b"

    def insert_scar(self, scar: ScarRecord | GeoidState, vector: list[float]) -> ScarDB:
        """Insert a ScarRecord and its vector into the persistent store."""
        if isinstance(scar, GeoidState):
            scar = ScarRecord(
                scar_id=f"SCAR_{uuid.uuid4().hex[:8]}",
                geoids=[scar.geoid_id],
                reason="auto-generated",
                timestamp=datetime.utcnow().isoformat(),
                resolved_by="vault_manager",
                pre_entropy=0.0,
                post_entropy=0.0,
                delta_entropy=0.0,
                cls_angle=0.0,
                semantic_polarity=0.0,
                mutation_frequency=0.0,
            )
        vault_id = self._select_vault()
        scar_db = ScarDB(
            scar_id=scar.scar_id,
            geoids=scar.geoids,
            reason=scar.reason,
            timestamp=datetime.fromisoformat(scar.timestamp),
            resolved_by=scar.resolved_by,
            pre_entropy=scar.pre_entropy,
            post_entropy=scar.post_entropy,
            delta_entropy=scar.delta_entropy,
            cls_angle=scar.cls_angle,
            semantic_polarity=scar.semantic_polarity,
            mutation_frequency=scar.mutation_frequency,
            weight=scar.weight,
            scar_vector=vector,
            vault_id=vault_id,
        )
        self.db.add(scar_db)
        self.db.commit()
        self.db.refresh(scar_db)
        return scar_db

    def get_scars_from_vault(self, vault_id: str, limit: int = 100) -> List[ScarDB]:
        scars = (
            self.db.query(ScarDB)
            .filter(ScarDB.vault_id == vault_id)
            .order_by(ScarDB.timestamp.desc())
            .limit(limit)
            .all()
        )
        now = datetime.utcnow()
        for s in scars:
            s.last_accessed = now
        self.db.commit()
        return scars

    def get_total_scar_count(self, vault_id: str) -> int:
        return self.db.query(ScarDB).filter(ScarDB.vault_id == vault_id).count()
