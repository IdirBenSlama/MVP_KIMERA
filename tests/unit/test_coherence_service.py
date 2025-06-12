import unittest
import numpy as np
from backend.engines.coherence import CoherenceService, GeoidState, TensionGradient

class TestCoherenceService(unittest.TestCase):

    def setUp(self):
        """Set up a new CoherenceService for each test."""
        self.service = CoherenceService()

    def test_high_coherence_scenario(self):
        """Test a scenario with high thematic alignment and no contradictions."""
        geoids = [
            GeoidState(semantic_state={"a": 1.0, "b": 0.8, "c": 0.0}),
            GeoidState(semantic_state={"a": 0.9, "b": 1.0, "c": 0.1}),
            GeoidState(semantic_state={"a": 0.8, "b": 0.9, "c": -0.1}),
        ]
        tensions = []
        coherence = self.service.compute_global_coherence(geoids, tensions)
        self.assertGreater(coherence, 0.8, "Coherence should be high for aligned geoids.")
        
        temperature = self.service.get_temperature_from_coherence(coherence)
        self.assertLess(temperature, 0.2, "Temperature should be low for high coherence.")

    def test_low_coherence_scenario(self):
        """Test a scenario with low thematic alignment and high contradictions."""
        geoids = [
            GeoidState(semantic_state={"a": 1.0, "b": -1.0, "c": 0.0}),
            GeoidState(semantic_state={"d": 1.0, "e": 1.0}),
            GeoidState(semantic_state={"x": -1.0, "y": -1.0}),
        ]
        tensions = [TensionGradient(tension_score=0.9), TensionGradient(tension_score=0.8)]
        coherence = self.service.compute_global_coherence(geoids, tensions)
        self.assertLess(coherence, 0.3, "Coherence should be low for contradictory geoids.")
        
        temperature = self.service.get_temperature_from_coherence(coherence)
        self.assertGreater(temperature, 0.7, "Temperature should be high for low coherence.")

    def test_contradiction_penalty(self):
        """Test that coherence decreases as contradiction penalty increases."""
        geoids = [
            GeoidState(semantic_state={"a": 1.0}),
            GeoidState(semantic_state={"a": 0.9}),
        ]
        
        coherence_no_tension = self.service.compute_global_coherence(geoids, [])
        
        tensions = [TensionGradient(tension_score=0.8)]
        coherence_with_tension = self.service.compute_global_coherence(geoids, tensions)
        
        self.assertGreater(coherence_no_tension, coherence_with_tension)

    def test_thematic_alignment(self):
        """Test the internal thematic alignment calculation."""
        # Perfectly aligned vectors
        aligned_geoids = [
            GeoidState(semantic_state={"a": 1.0, "b": 0.5}),
            GeoidState(semantic_state={"a": 1.0, "b": 0.5}),
        ]
        alignment = self.service._calculate_thematic_alignment(aligned_geoids)
        self.assertAlmostEqual(alignment, 1.0)
        
        # Perfectly opposed vectors
        opposed_geoids = [
            GeoidState(semantic_state={"a": 1.0, "b": 0.0}),
            GeoidState(semantic_state={"a": -1.0, "b": 0.0}),
        ]
        alignment = self.service._calculate_thematic_alignment(opposed_geoids)
        self.assertAlmostEqual(alignment, 0.0)

    def test_empty_system_coherence(self):
        """Test that an empty system is perfectly coherent."""
        coherence = self.service.compute_global_coherence([], [])
        self.assertEqual(coherence, 1.0)
        temperature = self.service.get_temperature_from_coherence(coherence)
        self.assertEqual(temperature, 0.0)

    def test_temperature_property(self):
        """Test that the temperature property correctly raises an error."""
        with self.assertRaises(NotImplementedError):
            _ = self.service.temperature

if __name__ == '__main__':
    unittest.main() 