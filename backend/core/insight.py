"""
Defines the data structure for an InsightScar, a specialized record
representing a generated insight (e.g., analogy, hypothesis).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Literal

# Type definition for the insight lifecycle status
InsightStatus = Literal['provisional', 'active', 'strengthened', 'deprecated']

@dataclass
class InsightScar:
    """
    A specialized Scar that encodes a generated insight.

    This structure captures not only the insight itself but also its
    origin, its impact (entropy reduction), and its lifecycle state.
    """
    insight_id: str
    insight_type: Literal['ANALOGY', 'HYPOTHESIS', 'FRAMEWORK', 'SOLUTION']
    source_resonance_id: str
    
    # Core insight data
    echoform_repr: Dict[str, Any]
    confidence: float
    entropy_reduction: float
    application_domains: List[str] = field(default_factory=list)
    
    # Metrics and Lifecycle
    utility_score: float = 0.0
    status: InsightStatus = 'provisional'
    
    # Timestamps and Provenance
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_reinforced_cycle: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the InsightScar to a dictionary."""
        return {
            "insight_id": self.insight_id,
            "insight_type": self.insight_type,
            "source_resonance_id": self.source_resonance_id,
            "echoform_repr": self.echoform_repr,
            "application_domains": self.application_domains,
            "confidence": self.confidence,
            "entropy_reduction": self.entropy_reduction,
            "utility_score": self.utility_score,
            "status": self.status,
            "created_at": self.created_at,
            "last_reinforced_cycle": self.last_reinforced_cycle,
        } 