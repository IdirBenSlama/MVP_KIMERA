"""
Comprehensive Scientific Tests for System-Level Thermodynamic Rules.

This test suite validates the application of thermodynamic and entropic
principles at the system level, ensuring that engine behaviors align
with the specified rules.

Part 1: Insight Validation Engine
Part 2: Semantic Thermodynamics Engine
"""

import unittest

# Assuming the project is installed in editable mode or path is configured
from backend.core.insight import InsightScar
from backend.engines.insight_entropy import is_insight_valid, MIN_ENTROPY_REDUCTION_THRESHOLD
from backend.core.geoid import GeoidState
from backend.engines.thermodynamics import SemanticThermodynamicsEngine

class TestThermodynamicsSystem(unittest.TestCase):
    """Validates the application of system-level thermodynamic and entropy rules."""

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Part 1: Insight Validation Engine
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def test_insight_validation_sufficient_entropy_reduction(self):
        """Test that an insight with sufficient entropy reduction is considered valid."""
        # Create an InsightScar with entropy reduction greater than the threshold
        valid_insight = InsightScar(
            insight_id="insight_valid",
            insight_type="ANALOGY",
            source_resonance_id="res1",
            echoform_repr={},
            confidence=0.9,
            entropy_reduction=MIN_ENTROPY_REDUCTION_THRESHOLD + 0.1
        )
        self.assertTrue(is_insight_valid(valid_insight), 
                        "Insight with sufficient entropy reduction should be valid.")

    def test_insight_validation_insufficient_entropy_reduction(self):
        """Test that an insight with insufficient entropy reduction is considered invalid."""
        # Create an InsightScar with entropy reduction less than the threshold
        invalid_insight = InsightScar(
            insight_id="insight_invalid",
            insight_type="ANALOGY",
            source_resonance_id="res2",
            echoform_repr={},
            confidence=0.9,
            entropy_reduction=MIN_ENTROPY_REDUCTION_THRESHOLD - 0.01
        )
        self.assertFalse(is_insight_valid(invalid_insight),
                         "Insight with insufficient entropy reduction should be invalid.")

    def test_insight_validation_at_threshold(self):
        """Test that an insight with entropy reduction exactly at the threshold is valid."""
        # Create an InsightScar with entropy reduction equal to the threshold
        threshold_insight = InsightScar(
            insight_id="insight_threshold",
            insight_type="ANALOGY",
            source_resonance_id="res3",
            echoform_repr={},
            confidence=0.9,
            entropy_reduction=MIN_ENTROPY_REDUCTION_THRESHOLD
        )
        self.assertTrue(is_insight_valid(threshold_insight),
                        "Insight with entropy reduction at the threshold should be valid.")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Part 2: Semantic Thermodynamics Engine
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def setUp(self):
        """Set up a SemanticThermodynamicsEngine for the tests."""
        self.thermo_engine = SemanticThermodynamicsEngine()

    def test_transformation_with_entropy_increase(self):
        """Test a transformation where entropy increases, which should be valid."""
        geoid_before = GeoidState(geoid_id='g1', semantic_state={'a': 0.5, 'b': 0.5}) # H=1.0
        geoid_after = GeoidState(geoid_id='g1', semantic_state={'a': 0.25, 'b': 0.25, 'c': 0.5}) # H=1.5
        
        entropy_before = geoid_before.calculate_entropy()
        is_valid = self.thermo_engine.validate_transformation(geoid_before, geoid_after)
        entropy_after = geoid_after.calculate_entropy()
        
        self.assertTrue(is_valid)
        self.assertGreater(entropy_after, entropy_before)

    def test_transformation_with_no_entropy_change(self):
        """Test a transformation where entropy does not change, which should be valid."""
        geoid_before = GeoidState(geoid_id='g1', semantic_state={'a': 0.5, 'b': 0.5})
        geoid_after = GeoidState(geoid_id='g1', semantic_state={'c': 0.5, 'd': 0.5})
        
        entropy_before = geoid_before.calculate_entropy()
        is_valid = self.thermo_engine.validate_transformation(geoid_before, geoid_after)
        entropy_after = geoid_after.calculate_entropy()

        self.assertTrue(is_valid)
        self.assertAlmostEqual(entropy_after, entropy_before)

    def test_transformation_with_entropy_decrease(self):
        """Test a transformation where entropy would decrease, which should be auto-corrected."""
        geoid_before = GeoidState(geoid_id='g1', semantic_state={'a': 0.25, 'b': 0.25, 'c': 0.5}) # H=1.5
        geoid_after = GeoidState(geoid_id='g1', semantic_state={'a': 0.5, 'b': 0.5}) # H=1.0
        
        entropy_before = geoid_before.calculate_entropy()
        initial_after_entropy = geoid_after.calculate_entropy()

        is_valid = self.thermo_engine.validate_transformation(geoid_before, geoid_after)
        final_after_entropy = geoid_after.calculate_entropy()
        
        self.assertTrue(is_valid)
        # The engine should modify the state to ensure entropy does not decrease.
        self.assertGreaterEqual(final_after_entropy, entropy_before)
        # Check that the state was indeed modified from its initial "after" state
        self.assertNotAlmostEqual(final_after_entropy, initial_after_entropy)

if __name__ == '__main__':
    unittest.main() 