"""Insight Lineage Tracer
----------------------------------
Provides a developer utility to trace the full provenance of an InsightScar.
This minimal implementation walks back through source geoids and resonance events
stored in memory (kimera_system dict).
"""
from __future__ import annotations

from typing import Dict, Any, List
import logging

from ..core.insight import InsightScar

log = logging.getLogger(__name__)


def trace(insight_id: str, system: Dict[str, Any]) -> Dict[str, Any]:
    """Returns a JSON-serialisable lineage graph for a given insight.

    Args:
        insight_id: The ID of the insight to trace.
        system: The kimera_system dictionary (or a subset) providing access
                 to insights and geoids.

    Returns:
        A nested dict describing the lineage graph.
    """
    insights: Dict[str, InsightScar] = system.get("insights", {})  # type: ignore
    insight = insights.get(insight_id)
    if not insight:
        raise ValueError(f"Insight '{insight_id}' not found")

    # Base structure
    lineage = {
        "insight": insight.to_dict(),
        "source_resonance_id": insight.source_resonance_id,
        "source_geoids": [],
    }

    # Resolve source geoids if present in active geoids
    active_geoids = system.get("active_geoids", {})
    resonance_id = insight.source_resonance_id
    if resonance_id in active_geoids:
        lineage["source_geoids"].append(active_geoids[resonance_id].to_dict())

    return lineage 