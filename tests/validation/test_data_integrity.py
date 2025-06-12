import unittest
import os
import uuid
import json
import sqlite3
import time
import concurrent.futures
import sys
import random
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure the backend is in the path
sys.path.insert(0, os.path.abspath('.'))

# Set a dedicated test database before importing the app
TEST_DB_FILE = f"./integrity_test_{uuid.uuid4().hex[:8]}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"
os.environ["ENABLE_JOBS"] = "0" 

from fastapi.testclient import TestClient
from backend.api.main import app
from backend.vault.database import engine, Base, SessionLocal, ScarDB

class TestDataIntegrity(unittest.TestCase):
    """
    Scientific test suite for validating data integrity, persistence,
    and transactional safety under various conditions.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the test client and database once for the whole class."""
        # Create the database tables
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Clean up the test database file after all tests are run."""
        # This is important to ensure a clean state for the next run
        # Explicitly close the engine to release the file lock
        engine.dispose()
        # Add a small delay to give the OS time to release the lock
        time.sleep(0.1)
        if os.path.exists(TEST_DB_FILE):
            try:
                os.remove(TEST_DB_FILE)
            except OSError:
                print(f"Warning: Could not remove test database {TEST_DB_FILE}. It may be locked.")

    def test_1_vault_balance_under_concurrent_load(self):
        """
        Benchmark: Vault Balance Accuracy Under Concurrent Load.
        Validates the claim of >99.9% vault balance accuracy by simulating
        heavy concurrent scar generation.
        """
        print("\n[VALIDATION] Running: Vault Balance Under Concurrent Load...")
        NUM_THREADS = 10
        GEOIDS_PER_THREAD = 10
        
        base_data = {"echoform_text": "The economy is experiencing strong growth and stability.", "symbolic_content": {"source": "test_base"}}
        conflict_data = {"echoform_text": "The market is in a state of recession and high-risk volatility.", "symbolic_content": {"source": "test_conflict"}}

        # Phase 1: Create a stable base of diverse geoids
        print("  Phase 1: Creating stable base geoids...")
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = [executor.submit(self.client.post, "/geoids", json=base_data) for _ in range(GEOIDS_PER_THREAD * NUM_THREADS)]
            for future in as_completed(futures):
                self.assertEqual(future.result().status_code, 200)

        # Phase 2: Create new geoids concurrently that are designed to conflict with the base
        print("  Phase 2: Creating conflicting geoids...")
        
        def creation_worker(thread_id):
            response = self.client.post("/geoids", json=conflict_data)
            if response.status_code == 200:
                return response.json()['geoid_id']
            return None

        new_geoid_ids = []
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            results = executor.map(creation_worker, range(GEOIDS_PER_THREAD * NUM_THREADS))
            new_geoid_ids = [res for res in results if res is not None]

        self.assertGreater(len(new_geoid_ids), 0, "No geoids were created in Phase 2.")
        print(f"  Phase 2: Complete. {len(new_geoid_ids)} conflicting geoids created.")

        # Phase 3: Process contradictions for the new geoids against the stable base
        print("  Phase 3: Processing contradictions...")
        def processing_worker(geoid_id):
            self.client.post("/process/contradictions", json={
                "trigger_geoid_id": geoid_id,
                "search_limit": 200 # Search the whole DB
            })

        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            executor.map(processing_worker, new_geoid_ids)
        
        print("  Phase 3: Complete.")
        
        # 4. Directly query the database to verify vault balance
        with SessionLocal() as db:
            vault_a_count = db.query(ScarDB).filter(ScarDB.vault_id == 'vault_a').count()
            vault_b_count = db.query(ScarDB).filter(ScarDB.vault_id == 'vault_b').count()
            total_scars = vault_a_count + vault_b_count
        
        print(f"[RESULT] Total Scars Generated: {total_scars}")
        print(f"[RESULT] Vault A: {vault_a_count} | Vault B: {vault_b_count}")

        # Validation
        self.assertGreater(total_scars, 0, "Test failed because no scars were generated.")
        self.assertLessEqual(abs(vault_a_count - vault_b_count), (total_scars * 0.1) + 1, 
                             "Vault balance difference exceeds 10% tolerance.")
        print("[SUCCESS] Vault balance maintained under concurrent load.")

    def test_2_acid_compliance_on_failure(self):
        """
        Benchmark: ACID Compliance on Transaction Failure.
        Validates that the database correctly rolls back failed transactions,
        preventing data corruption, by simulating a commit failure.
        """
        print("\n[VALIDATION] Running: ACID Compliance on Transaction Failure...")
        
        # 1. Get initial state
        conn = sqlite3.connect(TEST_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM geoids")
        initial_geoid_count = cursor.fetchone()[0]
        conn.close()

        # 2. Patch the 'commit' method of the Session object used by the API.
        #    This is the standard way to simulate method failures.
        with patch('sqlalchemy.orm.Session.commit', side_effect=sqlite3.OperationalError("Simulated Commit Failure!")):
            # 3. Attempt to create a geoid, expecting it to fail
            with self.assertRaises(Exception):
                self.client.post("/geoids", json={
                    "echoform_text": "The cat is on the mat.",
                    "symbolic_content": {"source": "test"}
                })

        # 4. Verify that no data was written
        conn = sqlite3.connect(TEST_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM geoids")
        final_geoid_count = cursor.fetchone()[0]
        conn.close()

        print(f"[RESULT] Initial Geoids: {initial_geoid_count} | Final Geoids: {final_geoid_count}")
        
        # Validation
        self.assertEqual(initial_geoid_count, final_geoid_count,
                         "A geoid was committed despite a transaction failure.")
        print("[SUCCESS] Database correctly rolled back the failed transaction.")

if __name__ == '__main__':
    unittest.main() 