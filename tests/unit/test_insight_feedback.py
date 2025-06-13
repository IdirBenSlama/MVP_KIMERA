import unittest
from backend.engines.insight_feedback import InsightFeedbackEngine

class TestInsightFeedbackEngine(unittest.TestCase):

    def setUp(self):
        """Set up a new InsightFeedbackEngine for each test."""
        self.feedback_engine = InsightFeedbackEngine()

    def test_track_engagement_new_insight(self):
        """Test tracking engagement for a previously unseen insight."""
        self.feedback_engine.track_insight_engagement("insight_001", "explored")
        self.assertIn("insight_001", self.feedback_engine.engagement_data)
        self.assertEqual(self.feedback_engine.engagement_data["insight_001"]["explored"], 1)
        self.assertEqual(self.feedback_engine.engagement_data["insight_001"]["dismissed"], 0)

    def test_track_engagement_existing_insight(self):
        """Test tracking multiple engagement actions for the same insight."""
        self.feedback_engine.track_insight_engagement("insight_001", "explored")
        self.feedback_engine.track_insight_engagement("insight_001", "explored")
        self.feedback_engine.track_insight_engagement("insight_001", "dismissed")
        self.assertEqual(self.feedback_engine.engagement_data["insight_001"]["explored"], 2)
        self.assertEqual(self.feedback_engine.engagement_data["insight_001"]["dismissed"], 1)

    def test_track_engagement_unknown_action(self):
        """Test that unknown engagement actions are handled gracefully."""
        # This test primarily ensures no exception is raised.
        # The engine logs a warning, which we can't easily check here.
        self.feedback_engine.track_insight_engagement("insight_001", "liked")
        self.assertNotIn("liked", self.feedback_engine.engagement_data["insight_001"])

    def test_adjust_parameters_default(self):
        """Test that default parameters are returned when there is no feedback."""
        params = self.feedback_engine.adjust_synthesis_parameters({})
        self.assertEqual(params['exploration_factor'], 1.0)

    def test_adjust_parameters_increased_exploration(self):
        """Test if exploration factor increases when insights are mostly dismissed."""
        self.feedback_engine.track_insight_engagement("insight_001", "dismissed")
        self.feedback_engine.track_insight_engagement("insight_002", "dismissed")
        self.feedback_engine.track_insight_engagement("insight_003", "explored")
        params = self.feedback_engine.adjust_synthesis_parameters({})
        self.assertEqual(params['exploration_factor'], 1.2)

    def test_adjust_parameters_decreased_exploration(self):
        """Test if exploration factor decreases when insights are mostly explored."""
        self.feedback_engine.track_insight_engagement("insight_001", "explored")
        self.feedback_engine.track_insight_engagement("insight_002", "explored")
        self.feedback_engine.track_insight_engagement("insight_003", "explored")
        self.feedback_engine.track_insight_engagement("insight_004", "dismissed")
        params = self.feedback_engine.adjust_synthesis_parameters({})
        self.assertEqual(params['exploration_factor'], 0.8)

    def test_adjust_parameters_balanced_feedback(self):
        """Test if exploration factor remains default with balanced feedback."""
        self.feedback_engine.track_insight_engagement("insight_001", "explored")
        self.feedback_engine.track_insight_engagement("insight_002", "dismissed")
        params = self.feedback_engine.adjust_synthesis_parameters({})
        self.assertEqual(params['exploration_factor'], 1.0)

if __name__ == '__main__':
    unittest.main() 