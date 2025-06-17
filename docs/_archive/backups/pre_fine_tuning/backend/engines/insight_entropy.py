"""
The Entropy Validator for the Insight Generation Engine.

This module is responsible for validating generated insights against
thermodynamic principles, specifically ensuring that a valid insight
results in a net reduction of semantic entropy in the system.
"""

from ..core.insight import InsightScar

# This would be loaded from a config file as per the roadmap.
# e.g., config.get('insight_engine.min_entropy_reduction_threshold')
MIN_ENTROPY_REDUCTION_THRESHOLD = 0.05 

def is_insight_valid(insight: InsightScar) -> bool:
    """
    Validates an InsightScar based on its entropy reduction.

    An insight is considered valid if the clarity it brings (represented
    by entropy_reduction) exceeds a minimum system-wide threshold.

    Args:
        insight: The InsightScar object to validate.

    Returns:
        True if the insight is valid, False otherwise.
    """
    if insight.entropy_reduction >= MIN_ENTROPY_REDUCTION_THRESHOLD:
        return True
    
    # Optionally log the invalid insight for analysis
    # logger.info(f"Insight {insight.insight_id} rejected due to low entropy reduction: {insight.entropy_reduction}")
    return False 