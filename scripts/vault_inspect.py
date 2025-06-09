#!/usr/bin/env python
"""Display scar counts and weight totals for each vault."""

from __future__ import annotations

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from backend.vault.vault_manager import VaultManager


def main() -> None:
    vm = VaultManager()
    for vault_id in ("vault_a", "vault_b"):
        count = vm.get_total_scar_count(vault_id)
        weight = vm.get_total_scar_weight(vault_id)
        print(f"{vault_id}: {count} scars (total weight {weight:.2f})")


if __name__ == "__main__":
    main()
