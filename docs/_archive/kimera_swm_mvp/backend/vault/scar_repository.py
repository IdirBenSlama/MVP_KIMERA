"""Placeholder for scar repository."""

import sqlite3
from typing import List, Optional, TYPE_CHECKING
from .schemas import ScarRecord, VaultType

if TYPE_CHECKING:
    from .vault_manager import VaultManager

DB_PATH = "vault.db"

class ScarRepository:
    """Manages persistent storage of scars in a SQLite database."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Creates or updates the necessary database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Schema for the main scars table
        scars_table_sql = """
            CREATE TABLE IF NOT EXISTS scars (
                scar_id TEXT PRIMARY KEY, geoids TEXT, reason TEXT, timestamp TEXT,
                resolved_by TEXT, pre_entropy REAL, post_entropy REAL, delta_entropy REAL,
                cls_angle REAL, semantic_polarity REAL, mutation_frequency REAL,
                weight REAL, quarantined INTEGER, initial_weight REAL, vault_type TEXT
            );
        """
        # Schema for the fallback queue table
        fallback_table_sql = """
            CREATE TABLE IF NOT EXISTS fallback_queue (
                scar_id TEXT PRIMARY KEY, geoids TEXT, reason TEXT, timestamp TEXT,
                resolved_by TEXT, pre_entropy REAL, post_entropy REAL, delta_entropy REAL,
                cls_angle REAL, semantic_polarity REAL, mutation_frequency REAL,
                weight REAL, quarantined INTEGER, initial_weight REAL
            );
        """
        cursor.execute(scars_table_sql)
        cursor.execute(fallback_table_sql)

        # Migration for older databases: add initial_weight if it doesn't exist
        for table_name in ["scars", "fallback_queue"]:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            if 'initial_weight' not in columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN initial_weight REAL DEFAULT 1.0")

        conn.commit()
        conn.close()

    def _scar_to_row(self, scar: ScarRecord, vault_type: Optional[VaultType] = None):
        """Converts a ScarRecord to a tuple for database insertion, ensuring correct order."""
        row = (
            scar.scar_id, ",".join(scar.geoids), scar.reason, scar.timestamp,
            scar.resolved_by, scar.pre_entropy, scar.post_entropy, scar.delta_entropy,
            scar.cls_angle, scar.semantic_polarity, scar.mutation_frequency,
            scar.weight, 1 if scar.quarantined else 0, scar.initial_weight
        )
        # Add vault_type only if it's for the 'scars' table
        if vault_type:
            return row + (vault_type.value,)
        return row

    def _row_to_scar(self, row: tuple) -> ScarRecord:
        """Converts a database row tuple back to a ScarRecord."""
        # Detect if the row is from the 'scars' table (15 columns) or 'fallback_queue' (14 columns)
        has_vault_type = len(row) == 15
        
        # Gracefully handle missing initial_weight from old DB versions
        # fallback_queue has initial_weight at index 13
        # scars table has initial_weight at index 13
        initial_weight_val = row[13] if row[13] is not None else row[11] # Use weight as fallback

        return ScarRecord(
            scar_id=row[0], geoids=row[1].split(','), reason=row[2], timestamp=row[3],
            resolved_by=row[4], pre_entropy=row[5], post_entropy=row[6], delta_entropy=row[7],
            cls_angle=row[8], semantic_polarity=row[9], mutation_frequency=row[10],
            weight=row[11], quarantined=bool(row[12]), initial_weight=initial_weight_val
        )

    def add_scar(self, scar: ScarRecord, vault_type: VaultType):
        """Adds a new scar to the scars table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO scars (scar_id, geoids, reason, timestamp, resolved_by, pre_entropy, post_entropy,
                               delta_entropy, cls_angle, semantic_polarity, mutation_frequency,
                               weight, quarantined, initial_weight, vault_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        scar.initial_weight = scar.weight
        params = self._scar_to_row(scar, vault_type)
        cursor.execute(sql, params)
        conn.commit()
        conn.close()

    def get_scar(self, scar_id: str) -> Optional[ScarRecord]:
        """Retrieves a single scar by its ID from the scars table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scars WHERE scar_id=?", (scar_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_scar(row) if row else None

    def get_scars_by_vault(self, vault_type: VaultType) -> List[ScarRecord]:
        """Retrieves all scars for a specific vault."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scars WHERE vault_type=?", (vault_type.value,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_scar(row) for row in rows]

    def update_scar(self, scar: ScarRecord):
        """Updates an existing scar in the scars table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Note: vault_type is not updatable.
        sql = """
            UPDATE scars SET
                geoids=?, reason=?, timestamp=?, resolved_by=?, pre_entropy=?, post_entropy=?,
                delta_entropy=?, cls_angle=?, semantic_polarity=?, mutation_frequency=?,
                weight=?, quarantined=?, initial_weight=?
            WHERE scar_id=?
        """
        # self._scar_to_row returns 14 values. We need 13 for the SET clause.
        # The row is (geoids, ..., initial_weight). We need all of them.
        row_without_id = self._scar_to_row(scar)[1:]
        params = row_without_id + (scar.scar_id,)
        cursor.execute(sql, params)
        conn.commit()
        conn.close()

    def delete_scar(self, scar_id: str):
        """Deletes a scar from the scars table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scars WHERE scar_id=?", (scar_id,))
        conn.commit()
        conn.close()

    def move_to_fallback(self, scar_id: str):
        """Moves a scar from the main table to the fallback queue."""
        scar = self.get_scar(scar_id)
        if not scar:
            return

        conn = self._get_connection()
        cursor = conn.cursor()
        fallback_sql = """
            INSERT INTO fallback_queue (scar_id, geoids, reason, timestamp, resolved_by, pre_entropy,
                                        post_entropy, delta_entropy, cls_angle, semantic_polarity,
                                        mutation_frequency, weight, quarantined, initial_weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # _scar_to_row without vault_type gives the correct 14 columns.
        cursor.execute(fallback_sql, self._scar_to_row(scar))
        cursor.execute("DELETE FROM scars WHERE scar_id=?", (scar_id,))
        conn.commit()
        conn.close()

    def load_scars_to_manager(self, manager: 'VaultManager'):
        """Loads all scars from the DB into the VaultManager's in-memory vaults."""
        scars_a = self.get_scars_by_vault(VaultType.VAULT_A)
        scars_b = self.get_scars_by_vault(VaultType.VAULT_B)

        for scar in scars_a:
            manager.vault_a[scar.scar_id] = scar
        for scar in scars_b:
            manager.vault_b[scar.scar_id] = scar
        
        print(f"Loaded {len(scars_a)} scars into Vault A and {len(scars_b)} into Vault B.")

