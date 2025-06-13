import unittest
import os
import sys

# Ensure the backend is in the path
sys.path.insert(0, os.path.abspath('.'))

from backend.core.geoid import GeoidState
from backend.engines.contradiction_engine import ContradictionEngine

class TestContradictionEngine(unittest.TestCase):
    """
    Unit tests for the core logic of the ContradictionEngine.
    """

    def setUp(self):
        """Set up the test case with a standard engine."""
        self.engine = ContradictionEngine(tension_threshold=0.5)

    def test_detects_strong_contradiction(self):
        """
        Tests if the engine detects a clear, multi-faceted contradiction.
        """
        print("\n[UNIT TEST] Running: Contradiction Engine Strong Contradiction...")

        # Geoid A: A stable, growing economy
        geoid_a = GeoidState(
            geoid_id="GEOID_ECON_A",
            semantic_state={
                "growth": 0.9,
                "stability": 0.8,
                "employment": 0.9,
                "risk": 0.1
            },
            embedding_vector=[0.9, 0.8, 0.1], # Strong positive vector
            symbolic_state={
                "trend": "positive",
                "outlook": "stable",
                "sector": "finance"
            }
        )

        # Geoid B: A shrinking, volatile economy
        geoid_b = GeoidState(
            geoid_id="GEOID_ECON_B",
            semantic_state={
                "recession": 0.9,
                "volatility": 0.8,
                "unemployment": 0.9,
                "risk": 0.9
            },
            embedding_vector=[-0.9, -0.8, 0.9], # Strong negative vector
            symbolic_state={
                "trend": "negative",
                "outlook": "volatile",
                "sector": "finance" # Overlapping key with different value
            }
        )

        # Expected outcome:
        # 1. _embedding_misalignment should be high (conflicting concepts).
        # 2. _layer_conflict_intensity should be high (different semantic keys).
        # 3. _symbolic_opposition should be high (conflicting values for 'trend' and 'outlook').

        tensions = self.engine.detect_tension_gradients([geoid_a, geoid_b])

        print(f"[RESULT] Detected {len(tensions)} tension(s).")
        
        self.assertEqual(len(tensions), 1, "Should have detected exactly one tension gradient.")
        
        tension_score = tensions[0].tension_score
        print(f"[RESULT] Tension Score: {tension_score:.4f}")
        
        self.assertGreater(tension_score, self.engine.tension_threshold,
                             "Detected tension score is not above the threshold.")
        print("[SUCCESS] Engine correctly identified the strong contradiction.")

    def test_ignores_weak_contradiction(self):
        """
        Tests if the engine correctly ignores geoids with low tension.
        """
        print("\n[UNIT TEST] Running: Contradiction Engine Weak Contradiction...")

        # Geoid C: A tech company
        geoid_c = GeoidState(
            geoid_id="GEOID_TECH_C",
            semantic_state={"innovation": 0.9, "software": 0.8, "revenue": 0.7},
            embedding_vector=[0.9, 0.8, 0.7], # Similar vectors
            symbolic_state={"market": "enterprise", "platform": "cloud"}
        )

        # Geoid D: A slightly different tech company
        geoid_d = GeoidState(
            geoid_id="GEOID_TECH_D",
            semantic_state={"innovation": 0.8, "software": 0.9, "profit": 0.6},
            embedding_vector=[0.8, 0.9, 0.6], # Similar vectors
            symbolic_state={"market": "consumer", "platform": "cloud"}
        )
        
        # Expected outcome: Tension score should be low.
        # 1. Embeddings are similar.
        # 2. Semantic layers are mostly overlapping.
        # 3. Symbolic opposition is low (only 'market' conflicts).

        tensions = self.engine.detect_tension_gradients([geoid_c, geoid_d])

        print(f"[RESULT] Detected {len(tensions)} tension(s).")
        self.assertEqual(len(tensions), 0, "Should not have detected any significant tension.")
        print("[SUCCESS] Engine correctly ignored the weak contradiction.")

if __name__ == '__main__':
    unittest.main() 