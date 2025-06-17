"""KIMERA SWM – Vault package

This package bundles all persistence-related functionality: the classic pattern-recognition
`VaultManager` and the roadmap-oriented `UnderstandingVaultManager`.

Importing the package guarantees that BOTH the legacy tables (defined in
`backend.vault.database`) and the enhanced understanding-oriented tables (defined in
`backend.vault.enhanced_database_schema`) are materialised in the configured SQLAlchemy
engine.  This makes it safe to switch between managers at runtime without worrying about
missing tables.
"""
from __future__ import annotations

from importlib import import_module

# ---------------------------------------------------------------------------
# Baseline vault (pattern-recognition)
# ---------------------------------------------------------------------------
from .vault_manager import VaultManager  # noqa: E402  (import order required below)

# ---------------------------------------------------------------------------
# Enhanced schema – MUST be imported before UnderstandingVaultManager so that the
# tables are registered with SQLAlchemy before any code attempts to use them.
# Importing the module is sufficient because it calls `Base.metadata.create_all(...)`
# at import-time.
# ---------------------------------------------------------------------------
import_module("backend.vault.enhanced_database_schema")  # side-effect: create tables

# ---------------------------------------------------------------------------
# Roadmap vault (genuine understanding)
# ---------------------------------------------------------------------------
from .understanding_vault_manager import UnderstandingVaultManager  # noqa: E402

# ---------------------------------------------------------------------------
# Helper – optional factory
# ---------------------------------------------------------------------------

def get_vault_manager(mode: str = "standard"):
    """Factory returning the appropriate vault manager.

    Parameters
    ----------
    mode : str, optional
        "standard"  – return :class:`VaultManager` (default)
        "understanding" – return :class:`UnderstandingVaultManager`
    """
    if mode.lower() in {"understanding", "genuine", "advanced"}:
        return UnderstandingVaultManager()
    return VaultManager()


__all__ = [
    "VaultManager",
    "UnderstandingVaultManager",
    "get_vault_manager",
]
