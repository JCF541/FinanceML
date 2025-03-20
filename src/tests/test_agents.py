import unittest
from src.data.models.agent import BullishAgent, BearishAgent, AnalyticalAgent

class TestAnalyticalAgents(unittest.TestCase):
    
    def setUp(self):
        """Create sample dataset for testing"""
        self.sample_articles = [
            {"title": "Bitcoin Surges to New Highs", "content": "Bitcoin reaches new record levels with strong market demand.", "published_at": "2025-03-15"},
            {"title": "Market Panic: Crash Incoming", "content": "Economists predict a severe downturn in the markets.", "published_at": "2025-03-16"},
            {"title": "Breaking: Unconfirmed Rumors About Major Sell-Off", "content": "Unconfirmed reports suggest a major Bitcoin holder is selling assets.", "published_at": "2025-03-17"}
        ]
    
    def test_bullish_agent(self):
        """Ensure BullishAgent correctly identifies bullish sentiment."""
        agent = BullishAgent(self.sample_articles)
        df = agent.analyze()
        self.assertTrue(df.iloc[0]['bullish_signal'])  # First article should be bullish
        self.assertFalse(df.iloc[1]['bullish_signal'])  # Second article should not be bullish
    
    def test_bearish_agent(self):
        """Ensure BearishAgent correctly identifies bearish sentiment."""
        negative_article = "Bitcoin crashes heavily due to regulatory fears."
        self.sample_articles[1]["content"] = negative_article

        agent = BearishAgent(self.sample_articles)
        df = agent.analyze()
        self.assertTrue(df.iloc[1]['bearish_signal'])

    #def test_fact_checker_agent(self):
    #    """Ensure FactCheckerAgent correctly flags low credibility sources."""
    #    agent = AnalyticalAgent(self.sample_articles)
    #    df = agent.analyze()
    #    self.assertEqual(df.iloc[2]['credibility_score'], "Low")  # Third article contains 'unconfirmed', should be low credibility
    #    self.assertEqual(df.iloc[0]['credibility_score'], "High")  # First article should be high credibility

if __name__ == '__main__':
    unittest.main()
