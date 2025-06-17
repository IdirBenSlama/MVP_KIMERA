from typing import List
from ..core.geoid import GeoidState
from .scar_repository import ScarRepository
from .schemas import VaultType, ScarRecord

class VaultManager:
    """Implementation of DOC-204 Vault Subsystem"""

    def __init__(self, capacity_per_vault: int = 10000, db_path: str = "vault.db"):
        self.vault_a = {}
        self.vault_b = {}
        self.capacity = capacity_per_vault
        self.repository = ScarRepository(db_path)
        self.repository.load_scars_to_manager(self)
        self.interference_fields = {
            'echo_interference_index': 0.0,
            'scar_overlap_zones': [],
            'entropic_drift_direction': 0.0
        }

    def route_scar(self, scar: ScarRecord) -> VaultType:
        """Route scar using DOC-204 three-stage logic"""

        # Stage 1: Mutation Frequency Check
        if scar.mutation_frequency > 0.75:
            return VaultType.VAULT_A

        # Stage 2: Semantic Polarity Check
        if abs(scar.semantic_polarity) >= 0.5:
            return VaultType.VAULT_A

        # Stage 3: CLS Torsion Proximity Check
        vault_a_avg_cls = self._calculate_average_cls_angle(VaultType.VAULT_A)
        vault_b_avg_cls = self._calculate_average_cls_angle(VaultType.VAULT_B)

        a_distance = abs(scar.cls_angle - vault_a_avg_cls)
        b_distance = abs(scar.cls_angle - vault_b_avg_cls)

        return VaultType.VAULT_A if a_distance < b_distance else VaultType.VAULT_B

    def insert_scar(self, scar: ScarRecord) -> bool:
        """Insert scar with fracture topology handling"""
        vault_type = self.route_scar(scar)
        target_vault = self.vault_a if vault_type == VaultType.VAULT_A else self.vault_b

        # Check vault stress index
        vsi = len(target_vault) / self.capacity if self.capacity > 0 else 0
        if vsi >= 0.8:  # VSI_fracture_threshold
            return self._handle_vault_fracture(scar, vault_type)

        # Normal insertion
        target_vault[scar.scar_id] = scar
        self.repository.add_scar(scar, vault_type)
        self._update_interference_fields()
        return True

    def _handle_vault_fracture(self, scar: ScarRecord, vault_type: VaultType) -> bool:
        """Handle vault fracture per DOC-204"""
        print(f"Vault fracture triggered for {vault_type.value}")

        # Lock both vaults (simplified - just log the event)
        high_tension_scars = self._identify_high_tension_scars(vault_type)

        # Remove 20% of high-tension scars to fallback queue
        removal_count = max(1, len(high_tension_scars) // 5)
        scars_to_move = high_tension_scars[:removal_count]
        
        for scar_to_move in scars_to_move:
            self._move_to_fallback_queue(scar_to_move.scar_id, vault_type)

        # Insert new scar
        target_vault = self.vault_a if vault_type == VaultType.VAULT_A else self.vault_b
        target_vault[scar.scar_id] = scar
        self.repository.add_scar(scar, vault_type)

        return True

    def _update_interference_fields(self):
        pass

    def _identify_high_tension_scars(self, vault_type: VaultType) -> List[ScarRecord]:
        """Identifies high-tension scars based on delta_entropy and weight."""
        target_vault = self.vault_a if vault_type == VaultType.VAULT_A else self.vault_b
        if not target_vault:
            return []
            
        # Sort by a combined metric of weight and delta_entropy
        sorted_scars = sorted(
            target_vault.values(),
            key=lambda s: s.weight * s.delta_entropy,
            reverse=True
        )
        return sorted_scars

    def _move_to_fallback_queue(self, scar_id: str, vault_type: VaultType):
        """Moves a scar to a fallback queue and removes it from the in-memory vault."""
        target_vault = self.vault_a if vault_type == VaultType.VAULT_A else self.vault_b
        if scar_id in target_vault:
            # First, handle the database operation
            self.repository.move_to_fallback(scar_id)
            # Then, remove from the in-memory dictionary
            del target_vault[scar_id]
            print(f"Moved scar {scar_id} to fallback queue from {vault_type.value}")

    def _calculate_average_cls_angle(self, vault_type: VaultType) -> float:
        """Calculates the average CLS angle for a given vault."""
        target_vault = self.vault_a if vault_type == VaultType.VAULT_A else self.vault_b
        if not target_vault:
            return 0.0
        
        total_cls_angle = sum(scar.cls_angle for scar in target_vault.values())
        return total_cls_angle / len(target_vault)

