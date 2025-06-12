"""backend/engines/insight_feedback.py
Insight Feedback Engine
=======================
This module provides a light–weight feedback mechanism that the KIMERA SWM
runtime can use to learn from user / system interactions with generated
`InsightScar` objects.  It satisfies Phase 3 – task 3.4 of the
"Re-Contextualization & Insight Engine" roadmap.

For an initial MVP we keep the implementation entirely in-memory so that it
can be exercised by the existing test-suite without introducing new storage
requirements.  Repositories that require persistence can inject a subclass of
`BaseFeedbackStore` later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Dict, List, Protocol, Any

import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data-structures
# ---------------------------------------------------------------------------

class EngagementType(str, Enum):
    """Enumerates the kinds of engagement events we recognise."""

    EXPLORED = "explored"          # User opened / inspected the insight
    DISMISSED = "dismissed"        # User discarded or hid the insight
    ELABORATED = "elaborated"      # User extended / built upon the insight
    SYSTEM_REINFORCED = "reinforced"  # Subsequent automated process used the insight


action_to_weight: Dict[EngagementType, float] = {
    EngagementType.EXPLORED: +0.10,
    EngagementType.ELABORATED: +0.25,
    EngagementType.SYSTEM_REINFORCED: +0.05,
    EngagementType.DISMISSED: -0.20,
}


@dataclass(slots=True)
class EngagementRecord:
    """Captures a single engagement event for an insight."""

    cycle: int
    action: EngagementType
    weight: float


class BaseFeedbackStore(Protocol):
    """Storage interface so that different backends can be swapped in."""

    def add_event(self, insight_id: str, event: EngagementRecord) -> None: ...

    def get_events(self, insight_id: str) -> List[EngagementRecord]: ...


# ---------------------------------------------------------------------------
# In-memory store implementation (default)
# ---------------------------------------------------------------------------


class InMemoryFeedbackStore(dict, BaseFeedbackStore):
    """A naive in-memory store mapping *insight_id* → list[EngagementRecord]."""

    def add_event(self, insight_id: str, event: EngagementRecord) -> None:  # noqa: D401
        self.setdefault(insight_id, []).append(event)

    def get_events(self, insight_id: str) -> List[EngagementRecord]:  # noqa: D401
        return self.get(insight_id, [])


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


@dataclass
class InsightFeedbackEngine:
    """
    Manages feedback on generated insights to tune the synthesis process.
    Implements Task 3.4 from the Re-Contextualization roadmap.
    """

    engagement_data: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def track_insight_engagement(self, insight_id: str, user_action: str):
        """
        Logs user interactions with a specific insight.

        Args:
            insight_id: The unique identifier of the insight.
            user_action: The action taken by the user (e.g., 'explored', 'dismissed').
        """
        if insight_id not in self.engagement_data:
            self.engagement_data[insight_id] = {
                'explored': 0,
                'dismissed': 0,
                'elaborated': 0
            }
        
        if user_action in self.engagement_data[insight_id]:
            self.engagement_data[insight_id][user_action] += 1
            log.info(f"Tracked engagement for insight {insight_id}: {user_action}")
        else:
            log.warning(f"Unknown user action '{user_action}' for insight {insight_id}")

    def adjust_synthesis_parameters(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjusts synthesis engine parameters based on collective feedback.
        
        This is a placeholder for a more sophisticated heuristic model.

        Args:
            feedback_data: Aggregated data about insight performance.

        Returns:
            A dictionary of adjusted parameters for the synthesis engine.
        """
        log.info("Adjusting synthesis parameters based on feedback (heuristic).")
        
        # Placeholder heuristic: if insights are dismissed more than explored,
        # increase the 'exploration_factor' to encourage diversity.
        total_explored = sum(d.get('explored', 0) for d in self.engagement_data.values())
        total_dismissed = sum(d.get('dismissed', 0) for d in self.engagement_data.values())

        new_params = {'exploration_factor': 1.0} # Default value

        if total_dismissed > total_explored:
            new_params['exploration_factor'] = 1.2 # Increase exploration
            log.info("Feedback indicates low engagement; increasing exploration factor.")
        elif total_explored > total_dismissed * 2:
            new_params['exploration_factor'] = 0.8 # Decrease exploration, focus on quality
            log.info("Feedback indicates high engagement; decreasing exploration factor.")

        return new_params

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_engagement_summary(self, insight_id: str) -> Dict[str, int]:
        """Returns a frequency table of actions for *insight_id*."""
        summary: Dict[str, int] = {}
        for record in self.store.get_events(insight_id):
            summary[record.action.value] = summary.get(record.action.value, 0) + 1
        return summary


# ---------------------------------------------------------------------------
# Module-level default instance for convenience
# ---------------------------------------------------------------------------

_default_engine = InsightFeedbackEngine()

track_insight_engagement = _default_engine.track_insight_engagement  # noqa: E305
adjust_synthesis_parameters = _default_engine.adjust_synthesis_parameters
get_engagement_summary = _default_engine.get_engagement_summary
