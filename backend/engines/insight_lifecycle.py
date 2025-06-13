# backend/engines/insight_lifecycle.py
"""
Insight Lifecycle Manager

This engine is responsible for managing the lifecycle of an InsightScar,
promoting, or deprecating it based on utility and feedback.
"""
from typing import Literal
from ..core.insight import InsightScar

# Define feedback event types
FeedbackEvent = Literal['user_explored', 'user_dismissed', 'system_reinforced']

UTILITY_SCORE_MAP = {
    'user_explored': 0.1,
    'user_dismissed': -0.2,
    'system_reinforced': 0.05, # e.g., if the insight leads to another valid insight
}

STATUS_PROMOTION_THRESHOLD = 0.5
STATUS_DEPRECATION_THRESHOLD = -0.3

def update_utility_score(insight: InsightScar, feedback_event: FeedbackEvent, current_cycle: int) -> InsightScar:
    """
    Modifies an insight's utility score based on a feedback event.

    Args:
        insight: The InsightScar to update.
        feedback_event: The type of feedback received.
        current_cycle: The current system cycle count.

    Returns:
        The updated InsightScar.
    """
    score_change = UTILITY_SCORE_MAP.get(feedback_event, 0)
    insight.utility_score += score_change
    insight.last_reinforced_cycle = current_cycle
    
    return insight

def manage_insight_lifecycle(insight: InsightScar) -> InsightScar:
    """
    Updates the status of an insight based on its utility score.

    This function represents a periodic task that checks if an insight's
    utility has crossed a threshold for promotion or deprecation.

    Args:
        insight: The InsightScar to manage.

    Returns:
        The InsightScar with its potentially updated status.
    """
    if insight.status == 'active' and insight.utility_score >= STATUS_PROMOTION_THRESHOLD:
        insight.status = 'strengthened'
        # logger.info(f"Insight {insight.insight_id} promoted to 'strengthened'.")
    
    elif insight.status in ['active', 'strengthened'] and insight.utility_score <= STATUS_DEPRECATION_THRESHOLD:
        insight.status = 'deprecated'
        # logger.warning(f"Insight {insight.insight_id} deprecated due to low utility score.")
        
    return insight 