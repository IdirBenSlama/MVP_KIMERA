from __future__ import annotations
from typing import List, Tuple
from datetime import datetime
from sqlalchemy import func
import math

from ..core.scar import ScarRecord
from ..core.geoid import GeoidState
from .database import SessionLocal, ScarDB, GeoidDB
import uuid
from ..graph.models import create_scar, create_geoid


class VaultManager:
    """
    Manages the persistence of core system objects, including Geoids and Scars.
    
    This class abstracts all database interactions for reading and writing these
    critical data structures. It also contains the logic for maintaining
    balance between the dual scar vaults.
    """

    def __init__(self) -> None:
        """Initialize the vault manager."""
        # Sessions are created per-method; nothing needed here.
        pass

    def _select_vault(self) -> str:
        """Choose a vault based on current counts."""
        a_count = self.get_total_scar_count("vault_a")
        b_count = self.get_total_scar_count("vault_b")
        return "vault_a" if a_count <= b_count else "vault_b"

    def get_all_geoids(self) -> List[GeoidState]:
        """
        Fetches all geoids from the database and reconstitutes them into GeoidState objects.

        This method queries the GeoidDB table and reconstructs the full, in-memory
        representation of each geoid, including its semantic and symbolic states.

        :raises sqlalchemy.exc.SQLAlchemyError: If there is an issue with the database
                                                query or connection.
        :return: A list of all GeoidState objects currently in the system.
        """
        with SessionLocal() as db:
            geoid_db_records = db.query(GeoidDB).all()
            geoids = [
                GeoidState(
                    geoid_id=g.geoid_id,
                    semantic_state=g.semantic_state_json,
                    symbolic_state=g.symbolic_state,
                    embedding_vector=g.semantic_vector,
                    metadata=g.metadata_json,
                )
                for g in geoid_db_records
            ]
            # --- dual-write to Neo4j (idempotent) ---
            for geo in geoids:
                try:
                    create_geoid(geo.to_dict())
                except Exception:
                    pass  # don’t block SQLite retrieval if Neo4j down
            return geoids

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
        with SessionLocal() as db:
            db.add(scar_db)
            db.commit()
            db.refresh(scar_db)
        # --- async write to Neo4j (fire-and-forget) ---
        try:
            create_scar({
                **scar.__dict__,
                "vault_id": vault_id,
                "scar_vector": vector,
            })
        except Exception:
            pass  # do not disrupt primary persistence path
        return scar_db

    def get_scars_from_vault(self, vault_id: str, limit: int = 100) -> List[ScarDB]:
        """Return recent scars from the requested vault."""
        with SessionLocal() as db:
            scars = (
                db.query(ScarDB)
                .filter(ScarDB.vault_id == vault_id)
                .order_by(ScarDB.timestamp.desc())
                .limit(limit)
                .all()
            )
            now = datetime.utcnow()
            for s in scars:
                s.last_accessed = now
            db.commit()
        return scars

    def get_total_scar_count(self, vault_id: str) -> int:
        """Return the total number of scars stored in the given vault."""
        with SessionLocal() as db:
            return db.query(ScarDB).filter(ScarDB.vault_id == vault_id).count()

    def get_total_scar_weight(self, vault_id: str) -> float:
        """Return the sum of scar weights in the given vault."""
        with SessionLocal() as db:
            total = db.query(func.sum(ScarDB.weight)).filter(ScarDB.vault_id == vault_id).scalar()
            return float(total or 0.0)

    def detect_vault_imbalance(
        self,
        *,
        by_weight: bool = False,
        threshold: float = 1.5,
    ) -> Tuple[bool, str, str]:
        """Determine if one vault significantly outweighs the other.

        Returns a tuple of (imbalanced?, overloaded_vault, underloaded_vault).
        """
        if by_weight:
            a_val = self.get_total_scar_weight("vault_a")
            b_val = self.get_total_scar_weight("vault_b")
        else:
            a_val = self.get_total_scar_count("vault_a")
            b_val = self.get_total_scar_count("vault_b")

        if b_val == 0 and a_val == 0:
            return False, "", ""

        if a_val > threshold * max(b_val, 1e-9):
            return True, "vault_a", "vault_b"
        if b_val > threshold * max(a_val, 1e-9):
            return True, "vault_b", "vault_a"
        return False, "", ""

    def rebalance_vaults(
        self,
        *,
        by_weight: bool = False,
        threshold: float = 1.5,
    ) -> int:
        """Move low priority scars from the overloaded vault to the other."""
        imbalanced, from_vault, to_vault = self.detect_vault_imbalance(
            by_weight=by_weight, threshold=threshold
        )
        if not imbalanced:
            return 0

        with SessionLocal() as db:
            try:
                if by_weight:
                    from_val = self.get_total_scar_weight(from_vault)
                    to_val = self.get_total_scar_weight(to_vault)
                    diff = from_val - to_val
                    target = diff / 2.0
                    moved_weight = 0.0
                    scars = (
                        db.query(ScarDB)
                        .filter(ScarDB.vault_id == from_vault)
                        .order_by(ScarDB.weight)
                        .all()
                    )
                    moved = 0
                    for scar in scars:
                        if moved_weight >= target:
                            break
                        scar.vault_id = to_vault
                        moved_weight += scar.weight
                        moved += 1
                else:
                    from_val = self.get_total_scar_count(from_vault)
                    to_val = self.get_total_scar_count(to_vault)
                    diff = from_val - to_val
                    num_to_move = max(math.ceil(diff / 2.0), 1)
                    scars = (
                        db.query(ScarDB)
                        .filter(ScarDB.vault_id == from_vault)
                        .order_by(ScarDB.weight)
                        .limit(num_to_move)
                        .all()
                    )
                    for scar in scars:
                        scar.vault_id = to_vault
                    moved = len(scars)

                db.commit()
            except Exception:
                db.rollback()
                raise
        return moved

