"""
Symbolic Chaos Processor

This engine enriches a synthesized GeoidMosaic by applying a "Symbolic
Chaos" layer. It looks for thematic keywords in the mosaic's features
and maps them to archetypes and paradoxes to deepen the potential for
insight.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Assuming this class is defined in activation_synthesis
class GeoidMosaic:
    def __init__(self, source_ids: list, combined_features: dict, cost: float):
        self.source_ids = source_ids
        self.combined_features = combined_features
        self.synthesis_cost = cost
        self.archetype: Optional[str] = None
        self.paradox: Optional[str] = None

# --- Archetype Loading ---
def load_archetypes(file_path: Path) -> Dict[str, Any]:
    """Loads the archetypes from the JSON file."""
    try:
        # Forgivingly read the file, stripping comments
        lines = file_path.read_text().splitlines()
        json_lines = [line for line in lines if not line.strip().startswith('#')]
        return json.loads("\n".join(json_lines))
    except (FileNotFoundError, json.JSONDecodeError):
        # In case of error, return an empty dict
        return {}

ARCHETYPE_FILE = Path(__file__).parent.parent / "resources" / "archetypes.json"
ARCHETYPES = load_archetypes(ARCHETYPE_FILE)

def find_dominant_theme(mosaic: GeoidMosaic) -> Optional[str]:
    """Finds the dominant thematic keyword in a mosaic."""
    # This is a placeholder for a more complex thematic analysis.
    # It just checks for the first matching keyword.
    content_str = str(mosaic.combined_features).lower()
    for theme, data in ARCHETYPES.items():
        if any(keyword in content_str for keyword in data.get("keywords", [])):
            return theme
    return None

def apply_symbolic_chaos(mosaic: GeoidMosaic) -> GeoidMosaic:
    """
    Applies the symbolic chaos layer to a GeoidMosaic.

    It identifies a dominant theme and attaches the corresponding
    archetype and paradox to the mosaic.

    Args:
        mosaic: The GeoidMosaic to enrich.

    Returns:
        The enriched GeoidMosaic.
    """
    dominant_theme = find_dominant_theme(mosaic)
    
    if dominant_theme and dominant_theme in ARCHETYPES:
        theme_data = ARCHETYPES[dominant_theme]
        mosaic.archetype = theme_data.get("archetype")
        mosaic.paradox = theme_data.get("paradox")
        # logger.info(f"Applied archetype '{mosaic.archetype}' to mosaic.")

    return mosaic 