from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass
class ScarRecord:
    """Structured record of a resolved contradiction (DOC-201)."""

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
    weight: float = 1.0
    quarantined: bool = False
