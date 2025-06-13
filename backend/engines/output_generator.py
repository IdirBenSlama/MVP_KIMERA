"""
Insight Output Generator

This engine takes a fully processed GeoidMosaic (after synthesis and
symbolic enrichment) and generates the final, storable InsightScar object.
"""
import uuid
from typing import Dict, Any

from ..core.insight import InsightScar
# Placeholder for GeoidMosaic from activation_synthesis
class GeoidMosaic:
    def __init__(self, source_ids: list, combined_features: dict, cost: float):
        self.source_ids = source_ids
        self.combined_features = combined_features
        self.synthesis_cost = cost
        self.archetype = "The Seeker"
        self.paradox = "The destination is not a place, but a new way of seeing."

def calculate_insight_quality_score(entropy_reduction: float, synthesis_cost: float) -> float:
    """
    Calculates a quality score for the insight.

    A good insight provides a high entropy reduction for a low synthesis cost.

    Args:
        entropy_reduction: The reduction in system entropy from the insight.
        synthesis_cost: The computational cost to generate the insight.

    Returns:
        A normalized quality score.
    """
    if synthesis_cost == 0:
        return entropy_reduction
    # Normalize to prevent extreme values, this can be refined
    return (entropy_reduction / synthesis_cost) * 100

def generate_insight_scar(mosaic: GeoidMosaic, resonance_id: str, entropy_reduction: float) -> InsightScar:
    """
    Generates a final InsightScar from a GeoidMosaic.

    Args:
        mosaic: The enriched GeoidMosaic.
        resonance_id: The ID of the resonance event that started the process.
        entropy_reduction: The calculated reduction in system entropy.

    Returns:
        A populated InsightScar object ready for validation and storage.
    """
    quality_score = calculate_insight_quality_score(entropy_reduction, mosaic.synthesis_cost)
    
    # The echoform representation would be a structured summary of the insight
    echoform_repr = {
        "type": "ANALOGY", # This would be determined dynamically
        "core_concept": mosaic.combined_features,
        "archetype": mosaic.archetype,
        "paradox": mosaic.paradox,
        "quality_score": quality_score
    }

    insight = InsightScar(
        insight_id=f"INS_{uuid.uuid4().hex[:12]}",
        insight_type="ANALOGY", # Placeholder
        source_resonance_id=resonance_id,
        echoform_repr=echoform_repr,
        application_domains=["cross-domain"], # Placeholder
        confidence=quality_score, # Use quality score as confidence for now
        entropy_reduction=entropy_reduction
    )

    return insight 