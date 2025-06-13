import unittest
import math
from backend.engines.activation_manager import ActivationManager, GeoidState

class TestActivationManager(unittest.TestCase):

    def setUp(self):
        """Set up a new ActivationManager for each test."""
        self.manager = ActivationManager()

    def test_standard_decay(self):
        """Test the standard exponential decay for a normal geoid."""
        geoids = {"GEOID_1": GeoidState(geoid_id="GEOID_1", activation_level=1.0, entropy=2.0)}
        
        # Expected decay for one step: 1.0 * e^(-0.1)
        expected_activation = math.exp(-self.manager.lambda_decay)
        
        updated_geoids = self.manager.apply_decay(geoids)
        self.assertAlmostEqual(updated_geoids["GEOID_1"].activation_level, expected_activation)

    def test_high_entropy_boost(self):
        """Test that high entropy correctly slows down the decay rate (boosts activation)."""
        high_entropy = self.manager.entropy_boost_threshold + 1.0 # 4.5
        geoids = {"GEOID_1": GeoidState(geoid_id="GEOID_1", activation_level=1.0, entropy=high_entropy)}
        
        # Standard decay rate is reduced
        expected_decay_rate = self.manager.lambda_decay / (1 + (high_entropy - self.manager.entropy_boost_threshold))
        expected_activation = math.exp(-expected_decay_rate)
        
        updated_geoids = self.manager.apply_decay(geoids)
        self.assertAlmostEqual(updated_geoids["GEOID_1"].activation_level, expected_activation)
        # Ensure it decayed less than the standard rate
        self.assertGreater(updated_geoids["GEOID_1"].activation_level, math.exp(-self.manager.lambda_decay))

    def test_low_entropy_damping(self):
        """Test that low entropy correctly speeds up the decay rate (damps activation)."""
        low_entropy = self.manager.entropy_damping_threshold - 0.5 # 0.5
        geoids = {"GEOID_1": GeoidState(geoid_id="GEOID_1", activation_level=1.0, entropy=low_entropy)}
        
        # Standard decay rate is increased
        expected_decay_rate = self.manager.lambda_decay * (1 + self.manager.damping_factor)
        expected_activation = math.exp(-expected_decay_rate)
        
        updated_geoids = self.manager.apply_decay(geoids)
        self.assertAlmostEqual(updated_geoids["GEOID_1"].activation_level, expected_activation)
        # Ensure it decayed more than the standard rate
        self.assertLess(updated_geoids["GEOID_1"].activation_level, math.exp(-self.manager.lambda_decay))

    def test_activation_floor(self):
        """Test that activation level does not drop below zero."""
        geoids = {"GEOID_1": GeoidState(geoid_id="GEOID_1", activation_level=0.001, entropy=2.0)}
        
        # Set a very high decay rate to force activation below zero if not for the floor
        self.manager.lambda_decay = 100
        
        updated_geoids = self.manager.apply_decay(geoids)
        self.assertAlmostEqual(updated_geoids["GEOID_1"].activation_level, 0)

    def test_multiple_geoids(self):
        """Test that decay is applied correctly to a dictionary of multiple geoids."""
        geoids = {
            "normal": GeoidState(geoid_id="normal", activation_level=1.0, entropy=2.0),
            "high_entropy": GeoidState(geoid_id="high_entropy", activation_level=1.0, entropy=4.0),
            "low_entropy": GeoidState(geoid_id="low_entropy", activation_level=1.0, entropy=0.5)
        }
        
        updated_geoids = self.manager.apply_decay(geoids)
        
        # Verify normal decay
        self.assertLess(updated_geoids["normal"].activation_level, 1.0)
        # Verify high entropy boost (less decay)
        self.assertGreater(updated_geoids["high_entropy"].activation_level, updated_geoids["normal"].activation_level)
        # Verify low entropy damping (more decay)
        self.assertLess(updated_geoids["low_entropy"].activation_level, updated_geoids["normal"].activation_level)

if __name__ == '__main__':
    unittest.main() 