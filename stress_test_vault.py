import os
import sys
import time
import uuid
import random
from datetime import datetime

# Add the project root to the Python path to allow for module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from kimera_swm_mvp.backend.vault import VaultManager, ScarRecord, VaultOptimizer

# --- Configuration ---
DB_PATH = "stress_test_vault.db"
NUM_SCARS = 50_000
VAULT_CAPACITY = 10_000
OPTIMIZATION_CYCLES = 5

def create_random_scar():
    """Creates a randomized ScarRecord for stress testing."""
    weight = random.uniform(0.1, 1.5)
    return ScarRecord(
        scar_id=str(uuid.uuid4()),
        geoids=[f"geo_{random.randint(1, 1000)}" for _ in range(random.randint(1, 5))],
        reason="Stress test contradiction",
        timestamp=datetime.now().isoformat(),
        resolved_by="stress_test_system",
        pre_entropy=random.uniform(0, 1),
        post_entropy=random.uniform(0, 1),
        delta_entropy=random.uniform(-0.5, 0.5),
        cls_angle=random.uniform(0, 1),
        semantic_polarity=random.uniform(-1, 1),
        mutation_frequency=random.uniform(0, 1),
        initial_weight=weight,
        weight=weight,
        quarantined=False,
    )

def main():
    """Runs the vault stress test."""
    print("--- Vault Stress Test Initializing ---")
    
    # Clean up previous database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")

    # 1. Initialize components
    print(f"Initializing VaultManager with capacity {VAULT_CAPACITY} per vault...")
    vault_manager = VaultManager(capacity_per_vault=VAULT_CAPACITY, db_path=DB_PATH)
    vault_optimizer = VaultOptimizer(vault_manager, vault_manager.repository)
    
    # 2. Generate scars
    print(f"Generating {NUM_SCARS:,} random scars in memory...")
    scars = [create_random_scar() for _ in range(NUM_SCARS)]
    print("Scar generation complete.")

    # 3. Insert scars and measure time
    print("\n--- Starting Scar Insertion Phase ---")
    insertion_start_time = time.time()
    
    for i, scar in enumerate(scars):
        vault_manager.insert_scar(scar)
        if (i + 1) % 5000 == 0:
            print(f"  Inserted {i + 1:,}/{NUM_SCARS:,} scars...")

    insertion_end_time = time.time()
    print("--- Scar Insertion Phase Complete ---")
    print(f"Time taken for insertion: {insertion_end_time - insertion_start_time:.2f} seconds")

    # 4. Report state after insertion
    print("\n--- State After Insertion ---")
    repo = vault_manager.repository
    conn = repo._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scars WHERE vault_type='vault_a'")
    count_a = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM scars WHERE vault_type='vault_b'")
    count_b = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM fallback_queue")
    fallback_count = cursor.fetchone()[0]
    conn.close()

    print(f"Scars in Vault A (DB): {count_a:,}")
    print(f"Scars in Vault B (DB): {count_b:,}")
    print(f"Scars in Fallback Queue (DB): {fallback_count:,}")
    print(f"Total scars in DB: {count_a + count_b:,}")
    print(f"Scars in Vault A (Memory): {len(vault_manager.vault_a):,}")
    print(f"Scars in Vault B (Memory): {len(vault_manager.vault_b):,}")

    # 5. Run optimization cycles
    print(f"\n--- Starting {OPTIMIZATION_CYCLES} Optimization Cycles ---")
    optimization_start_time = time.time()

    for i in range(OPTIMIZATION_CYCLES):
        print(f"\n--- Cycle {i + 1}/{OPTIMIZATION_CYCLES} ---")
        vault_optimizer.run_optimization_cycle()
        
        conn = repo._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scars")
        total_scars = cursor.fetchone()[0]
        conn.close()
        print(f"Total scars remaining in DB after cycle {i + 1}: {total_scars:,}")

    optimization_end_time = time.time()
    print("\n--- Optimization Phase Complete ---")
    print(f"Time taken for optimization: {optimization_end_time - optimization_start_time:.2f} seconds")

    # 6. Final state report
    print("\n--- Final State ---")
    conn = repo._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scars WHERE vault_type='vault_a'")
    final_count_a = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM scars WHERE vault_type='vault_b'")
    final_count_b = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM fallback_queue")
    final_fallback_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"Final scars in Vault A (DB): {final_count_a:,}")
    print(f"Final scars in Vault B (DB): {final_count_b:,}")
    print(f"Final scars in Fallback Queue (DB): {final_fallback_count:,}")
    print(f"Scars in Vault A (Memory): {len(vault_manager.vault_a):,}")
    print(f"Scars in Vault B (Memory): {len(vault_manager.vault_b):,}")
    
    # 7. Clean up
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"\nCleaned up stress test database: {DB_PATH}")

    print("\n--- Stress Test Complete ---")

if __name__ == "__main__":
    main() 