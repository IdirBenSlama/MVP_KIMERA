from __future__ import annotations
from typing import Dict

from ..core.scar import ScarRecord

class VaultManager:
    def __init__(self):
        self.vault_a: Dict[str, ScarRecord] = {}
        self.vault_b: Dict[str, ScarRecord] = {}

    def insert_scar(self, scar: ScarRecord) -> None:
        target = self.vault_a if len(self.vault_a) <= len(self.vault_b) else self.vault_b
        target[scar.scar_id] = scar
