from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List
from collections import Counter
import logging

# Assuming InsightScar is defined in a reachable path.
# from ..core.insight import InsightScar 

# Placeholder for InsightScar until it's properly defined and imported.
@dataclass
class InsightScar:
    insight_id: str
    insight_type: str
    application_domains: List[str] = field(default_factory=list)
    echoform_repr: str = ""

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@dataclass
class MetaInsightEngine:
    """
    Generates insights about the system's own insight generation process.
    Implements Task 3.5 from the Re-Contextualization roadmap.
    """

    min_pattern_frequency: int = 3 # Minimum occurrences to be considered a pattern

    def scan_recent_insights(self, insight_scars: List[InsightScar]) -> List[InsightScar]:
        """
        Scans a list of recent insights to detect recurring patterns and generate meta-insights.

        Args:
            insight_scars: A list of InsightScar objects from recent cycles.

        Returns:
            A list of new meta-insight scars.
        """
        if not insight_scars or len(insight_scars) < self.min_pattern_frequency:
            return []

        log.info(f"Scanning {len(insight_scars)} insights for meta-patterns.")
        
        patterns = self.detect_recurring_patterns(insight_scars)
        meta_insights = self._generate_meta_insights_from_patterns(patterns)
        
        return meta_insights

    def detect_recurring_patterns(self, insight_scars: List[InsightScar]) -> Dict[str, Counter]:
        """
        Detects recurring patterns in insight types and application domains.
        """
        type_counter = Counter(s.insight_type for s in insight_scars)
        domain_counter = Counter(d for s in insight_scars for d in s.application_domains)

        significant_patterns = {
            "insight_types": Counter({t: c for t, c in type_counter.items() if c >= self.min_pattern_frequency}),
            "application_domains": Counter({d: c for d, c in domain_counter.items() if c >= self.min_pattern_frequency})
        }
        
        return significant_patterns

    def _generate_meta_insights_from_patterns(self, patterns: Dict[str, Counter]) -> List[InsightScar]:
        """
        Generates new META_FRAMEWORK InsightScars from detected patterns.
        """
        meta_insights = []

        # Generate meta-insight for frequent insight types
        for insight_type, count in patterns.get("insight_types", {}).items():
            meta_insight = InsightScar(
                insight_id=f"META_{insight_type.upper()}_PATTERN",
                insight_type="META_FRAMEWORK",
                echoform_repr=f"The system frequently generates '{insight_type}' insights, suggesting a process bias or high utility for this pattern."
            )
            meta_insights.append(meta_insight)
            log.info(f"Generated meta-insight for recurring type: '{insight_type}'")

        # Generate meta-insight for frequent domains
        for domain, count in patterns.get("application_domains", {}).items():
            meta_insight = InsightScar(
                insight_id=f"META_{domain.upper()}_DOMAIN_FOCUS",
                insight_type="META_FRAMEWORK",
                echoform_repr=f"The application domain '{domain}' is a frequent target for insights, indicating a strong contextual focus."
            )
            meta_insights.append(meta_insight)
            log.info(f"Generated meta-insight for recurring domain: '{domain}'")

        return meta_insights 