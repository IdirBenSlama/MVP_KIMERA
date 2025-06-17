"""KIMERA SWM Graph Database Package

This package provides Neo4j integration for the KIMERA system, enabling
graph-based storage and querying of semantic relationships, causal chains,
and understanding structures.

Key modules:
- session: Neo4j driver factory and connection management
- models: High-level CRUD operations for graph entities

Usage:
    from backend.graph.session import get_session
    from backend.graph.models import create_geoid, get_geoid
"""

from .session import get_driver, get_session, driver_liveness_check
from .models import create_geoid, get_geoid, create_scar, get_scar

__all__ = [
    "get_driver",
    "get_session", 
    "driver_liveness_check",
    "create_geoid",
    "get_geoid",
    "create_scar", 
    "get_scar"
]