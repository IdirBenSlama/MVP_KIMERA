import unittest
from backend.engines.meta_insight import MetaInsightEngine, InsightScar

class TestMetaInsightEngine(unittest.TestCase):

    def setUp(self):
        """Set up a new MetaInsightEngine and some sample insights for each test."""
        self.meta_engine = MetaInsightEngine()
        self.sample_insights = [
            InsightScar("1", "ANALOGY", ["biology", "engineering"]),
            InsightScar("2", "ANALOGY", ["finance", "engineering"]),
            InsightScar("3", "HYPOTHESIS", ["physics"]),
            InsightScar("4", "ANALOGY", ["art", "engineering"]),
            InsightScar("5", "FRAMEWORK", ["sociology"]),
            InsightScar("6", "HYPOTHESIS", ["biology"]),
            InsightScar("7", "ANALOGY", ["history"]),
            InsightScar("8", "HYPOTHESIS", ["chemistry", "biology"]),
        ]

    def test_no_significant_patterns(self):
        """Test that no meta-insights are generated when patterns don't meet the threshold."""
        few_insights = [
            InsightScar("1", "ANALOGY", ["biology"]),
            InsightScar("2", "HYPOTHESIS", ["finance"]),
        ]
        meta_insights = self.meta_engine.scan_recent_insights(few_insights)
        self.assertEqual(len(meta_insights), 0)

    def test_detect_recurring_insight_types(self):
        """Test the detection of frequently occurring insight types."""
        patterns = self.meta_engine.detect_recurring_patterns(self.sample_insights)
        self.assertIn("ANALOGY", patterns["insight_types"])
        self.assertEqual(patterns["insight_types"]["ANALOGY"], 4)
        self.assertIn("HYPOTHESIS", patterns["insight_types"])
        self.assertEqual(patterns["insight_types"]["HYPOTHESIS"], 3)
        self.assertNotIn("FRAMEWORK", patterns["insight_types"]) # Below threshold

    def test_detect_recurring_domains(self):
        """Test the detection of frequently targeted application domains."""
        patterns = self.meta_engine.detect_recurring_patterns(self.sample_insights)
        self.assertIn("engineering", patterns["application_domains"])
        self.assertEqual(patterns["application_domains"]["engineering"], 3)
        self.assertIn("biology", patterns["application_domains"])
        self.assertEqual(patterns["application_domains"]["biology"], 3)
        self.assertNotIn("finance", patterns["application_domains"]) # Below threshold

    def test_generate_meta_insights_from_patterns(self):
        """Test the generation of meta-insight objects from detected patterns."""
        meta_insights = self.meta_engine.scan_recent_insights(self.sample_insights)
        self.assertEqual(len(meta_insights), 4)

        insight_ids = [mi.insight_id for mi in meta_insights]
        self.assertIn("META_ANALOGY_PATTERN", insight_ids)
        self.assertIn("META_HYPOTHESIS_PATTERN", insight_ids)
        self.assertIn("META_ENGINEERING_DOMAIN_FOCUS", insight_ids)
        self.assertIn("META_BIOLOGY_DOMAIN_FOCUS", insight_ids)

        for insight in meta_insights:
            self.assertEqual(insight.insight_type, "META_FRAMEWORK")

    def test_engine_with_empty_input(self):
        """Test that the engine handles an empty list of insights gracefully."""
        meta_insights = self.meta_engine.scan_recent_insights([])
        self.assertEqual(len(meta_insights), 0)

if __name__ == '__main__':
    unittest.main() 