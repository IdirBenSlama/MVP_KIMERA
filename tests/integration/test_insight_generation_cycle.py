import unittest
from backend.engines.activation_manager import ActivationManager, GeoidState as ActivationGeoid
from backend.engines.meta_insight import MetaInsightEngine, InsightScar
from backend.engines.coherence import CoherenceService, GeoidState as CoherenceGeoid, TensionGradient

class TestInsightGenerationCycle(unittest.TestCase):
    """
    Integration test for the full insight generation and feedback cycle.
    Validates Task 3.8 from the Re-Contextualization roadmap.
    """

    def setUp(self):
        """Set up the engines needed for the integration test."""
        self.activation_manager = ActivationManager()
        self.meta_insight_engine = MetaInsightEngine()
        self.coherence_service = CoherenceService()

    def test_full_cycle_simulation(self):
        """
        Simulates a few cycles of system activity to test engine integration.
        """
        # --- Cycle 1: Initial State ---
        active_geoids = {
            "GEOID_1": ActivationGeoid(geoid_id="GEOID_1", activation_level=1.0, entropy=4.0),
            "GEOID_2": ActivationGeoid(geoid_id="GEOID_2", activation_level=0.8, entropy=0.5),
        }
        recent_insights = [
            InsightScar("I1", "ANALOGY", ["science"]),
            InsightScar("I2", "ANALOGY", ["art"]),
            InsightScar("I3", "ANALOGY", ["science"]),
            InsightScar("I4", "HYPOTHESIS", ["art"]),
            InsightScar("I5", "ANALOGY", ["science"]),
        ]
        tensions = [TensionGradient(tension_score=0.7)]

        # --- Cycle 2: Apply Decay and Generate Meta-Insights ---
        
        # 1. Activation Decay
        decayed_geoids = self.activation_manager.apply_decay(active_geoids)
        self.assertLess(decayed_geoids["GEOID_1"].activation_level, 1.0)
        self.assertLess(decayed_geoids["GEOID_2"].activation_level, 0.8)
        # Check that high entropy geoid decayed less
        self.assertGreater(
            decayed_geoids["GEOID_1"].activation_level,
            decayed_geoids["GEOID_2"].activation_level
        )
        
        # 2. Meta-Insight Generation
        meta_insights = self.meta_insight_engine.scan_recent_insights(recent_insights)
        self.assertEqual(len(meta_insights), 2)
        insight_reprs = {i.echoform_repr for i in meta_insights}
        self.assertIn("The system frequently generates 'ANALOGY' insights, suggesting a process bias or high utility for this pattern.", insight_reprs)
        self.assertIn("The application domain 'science' is a frequent target for insights, indicating a strong contextual focus.", insight_reprs)

        # --- Cycle 3: Compute Coherence ---
        
        # We need to convert geoid types for the CoherenceService
        coherence_geoids = [
            CoherenceGeoid(semantic_state={"feature": g.activation_level, "entropy": g.entropy})
            for g in decayed_geoids.values()
        ]

        # 3. Global Coherence
        coherence = self.coherence_service.compute_global_coherence(coherence_geoids, tensions)
        temperature = self.coherence_service.get_temperature_from_coherence(coherence)
        
        # With one tension, coherence should be less than perfect
        self.assertLess(coherence, 1.0)
        self.assertGreater(temperature, 0.0)
        
        print("\n[INTEGRATION TEST] Full insight generation cycle simulation completed successfully.")

if __name__ == '__main__':
    unittest.main() 