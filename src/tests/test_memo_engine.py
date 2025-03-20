import unittest
import pandas as pd
from datetime import datetime, timedelta
from src.processing.memo_engine import MemoEngine

def setUp(self):
    self.sample_data = [
        {
            "date": datetime.utcnow() - timedelta(days=i),
            "title": f"Article {i}",
            "url": f"https://example.com/{i}",
            "bullish_signal": bool(i % 2),
            "bearish_signal": not bool(i % 2),
            "fact_check_flag": (i % 3 == 0)
        }
        for i in range(10)
    ]
    self.memo_engine = MemoEngine(period="daily", data=self.sample_data)

    def test_filter_data(self):
        """Ensure correct filtering of daily data"""
        df_daily = self.memo_engine.filter_data("daily")
        today = datetime.utcnow().date()
        self.assertTrue(all(df_daily["date"].dt.date == today))

    def test_generate_summary(self):
        """Ensure summary statistics calculation"""
        summary = self.memo_engine.generate_summary(self.df)
        self.assertIn("bullish_count", summary)
        self.assertIn("bearish_count", summary)
        self.assertIn("fact_check_flags", summary)

    def test_detect_trend(self):
        """Ensure trend detection logic is valid"""
        summary = {"bullish_count": 5, "bearish_count": 3, "fact_check_flags": 1}
        trend = self.memo_engine.detect_trend(summary)
        self.assertEqual(trend, "Bullish")

    def test_generate_memo(self):
        """Ensure memo structure is correct"""
        memo = self.memo_engine.generate_memo("daily")
        self.assertIn("period", memo)
        self.assertIn("market_trend", memo)
        self.assertIn("summary", memo)
        self.assertIn("key_articles", memo)

    def test_generate_all_memos(self):
        """Ensure all memos are generated correctly"""
        memos = self.memo_engine.generate_all_memos()
        self.assertIn("daily", memos)
        self.assertIn("weekly", memos)
        self.assertIn("monthly", memos)

if __name__ == '__main__':
    unittest.main()
