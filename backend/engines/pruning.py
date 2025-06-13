"""
Pruning Engine for KIMERA SWM

This module contains the logic for pruning entities from memory,
such as Scars and Insights, based on thermodynamic and lifecycle criteria.
"""
from typing import List, Union
from ..core.insight import InsightScar
# from ..core.scar import Scar # Assuming a Scar class exists

# A placeholder for the Scar class for type hinting
class Scar:
    def __init__(self, scar_id: str, utility_score: float = 0.0):
        self.scar_id = scar_id
        self.status = 'active'
        self.utility_score = utility_score # A generic score for non-insights

# A combined type for items that can be pruned
Prunable = Union[InsightScar, Scar]

DEPRECATED_INSIGHT_PRUNING_PRIORITY = 10.0
DEFAULT_PRUNING_PRIORITY = 1.0

def should_prune(item: Prunable, vault_pressure: float) -> float:
    """
    Calculates a pruning score for a given item. A higher score means
    it's a more likely candidate for pruning.

    This function fulfills the roadmap task of integrating pruning with the
    insight lifecycle by giving a high priority to deprecated insights.

    Args:
        item: The InsightScar or Scar to evaluate.
        vault_pressure: A metric (0-1) representing how full the vault is.

    Returns:
        A float score indicating pruning priority.
    """
    pruning_score = 0.0

    # Task 2.5: Prioritize pruning deprecated insights
    if isinstance(item, InsightScar) and item.status == 'deprecated':
        pruning_score += DEPRECATED_INSIGHT_PRUNING_PRIORITY

    # Lower utility items are higher priority for pruning
    # We use 1 - score to invert the priority
    pruning_score += (1 - item.utility_score)

    # Higher vault pressure increases the priority of pruning everything
    pruning_score *= (1 + vault_pressure)
    
    return pruning_score

def get_pruning_candidates(items: List[Prunable], vault_pressure: float, num_to_prune: int) -> List[Prunable]:
    """
    Gets a list of the best candidates for pruning from a list of items.
    
    Args:
        items: A list of prunable items.
        vault_pressure: The current memory pressure of the vault.
        num_to_prune: The number of items to select for pruning.

    Returns:
        A list of items recommended for pruning, sorted by priority.
    """
    scored_items = [(item, should_prune(item, vault_pressure)) for item in items]
    
    # Sort by score in descending order (higher score = prune first)
    scored_items.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top N candidates
    return [item for item, score in scored_items[:num_to_prune]] 