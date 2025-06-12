from typing import List
from enum import Enum
from dataclasses import dataclass

class VaultType(Enum):
    VAULT_A = "vault_a"
    VAULT_B = "vault_b"

@dataclass
class ScarRecord:
    """Implementation of DOC-201 Scar schema"""
    scar_id: str
    geoids: List[str]
    reason: str
    timestamp: str
    resolved_by: str
    pre_entropy: float
    post_entropy: float
    delta_entropy: float
    cls_angle: float
    semantic_polarity: float
    mutation_frequency: float
    initial_weight: float = 1.0
    weight: float = 1.0
    quarantined: bool = False 