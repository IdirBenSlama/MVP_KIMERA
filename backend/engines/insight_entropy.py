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


import json
from pathlib import Path
import numpy as np

# Load fine-tuning configuration
def _load_adaptive_config():
    """Load adaptive threshold configuration"""
    config_file = Path(__file__).parent.parent.parent / "config" / "scientific_fine_tuning_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

_ADAPTIVE_CONFIG = _load_adaptive_config()

def calculate_adaptive_entropy_threshold(system_entropy: float = 2.0,
                                       system_complexity: float = 50.0,
                                       recent_performance: float = 0.8) -> float:
    """
    Calculate adaptive entropy threshold based on system state.
    
    This function implements the scientifically validated adaptive threshold
    calculation derived from the thermodynamic constraint tests.
    """
    base_threshold = _ADAPTIVE_CONFIG.get('base_entropy_threshold', MIN_ENTROPY_REDUCTION_THRESHOLD)
    entropy_normalization = _ADAPTIVE_CONFIG.get('entropy_normalization_point', 2.0)
    entropy_factor_weight = _ADAPTIVE_CONFIG.get('entropy_adjustment_factor', 0.1)
    complexity_factor_weight = _ADAPTIVE_CONFIG.get('complexity_adjustment_factor', 0.2)
    performance_weight = _ADAPTIVE_CONFIG.get('performance_weight', 0.4)
    
    # Calculate adjustment factors
    entropy_deviation = system_entropy - entropy_normalization
    entropy_factor = 1.0 + (entropy_deviation * entropy_factor_weight)
    
    normalized_complexity = min(system_complexity / 100.0, 1.0)
    complexity_factor = 1.0 + (normalized_complexity * complexity_factor_weight)
    
    performance_factor = 0.6 + (recent_performance * performance_weight)
    
    # Calculate adaptive threshold
    adaptive_threshold = base_threshold * entropy_factor * complexity_factor * performance_factor
    
    # Ensure reasonable bounds
    return max(0.01, min(adaptive_threshold, 0.2))

def is_insight_valid_adaptive(insight: InsightScar, 
                            system_entropy: float = 2.0,
                            system_complexity: float = 50.0,
                            recent_performance: float = 0.8) -> bool:
    """
    Enhanced insight validation using adaptive entropy threshold.
    
    This function uses scientifically validated adaptive thresholds
    instead of the fixed MIN_ENTROPY_REDUCTION_THRESHOLD.
    """
    adaptive_threshold = calculate_adaptive_entropy_threshold(
        system_entropy, system_complexity, recent_performance
    )
    
    return insight.entropy_reduction >= adaptive_threshold


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