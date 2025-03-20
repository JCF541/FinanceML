from datetime import datetime
import unittest
import pandas as pd
from src.processing.data_processor import DataProcessor

class TestDataProcessor(unittest.TestCase):

    def setUp(self):
        self.sample_articles = [
            {"title": "Bullish News", "content": "Bitcoin rallies strongly, prices soaring and market optimistic.", "published_at": datetime.now()},
            {"title": "Bearish News", "content": "Bitcoin crashes, market fearful and negative outlook prevails.", "published_at": datetime.now()},
            {"title": "Neutral News", "content": "Bitcoin price remained stable with minor fluctuations.", "published_at": datetime.now()}
        ]
        self.processor = DataProcessor(self.sample_articles)
        self.processor.preprocess_articles()


    def test_clean_text(self):
        """Ensure text cleaning removes HTML and unwanted characters"""
        cleaned_text = self.processor.clean_text("<p>Hello! This is a test.</p>")
        self.assertEqual(cleaned_text, "hello this is a test")

    def test_preprocess_articles(self):
        """Ensure preprocessing adds necessary columns"""
        self.assertIn("clean_content", self.processor.df.columns)
        self.assertIn("title_length", self.processor.df.columns)
        self.assertIn("word_count", self.processor.df.columns)

    def test_sentiment_analysis(self):
        """Ensure sentiment classification is working correctly"""
        self.processor.analyze_sentiment()
        self.assertIn("sentiment_score", self.processor.df.columns)
        self.assertIn("sentiment_label", self.processor.df.columns)
        sentiments = self.processor.df["sentiment_label"].tolist()
        self.assertEqual(sentiments[0], "Bullish")  # Bitcoin rally is positive
        self.assertEqual(sentiments[1], "Bearish")  # Market crash is negative
        self.assertEqual(sentiments[2], "Neutral")  # Stable market is neutral

    def test_feature_engineering(self):
        """Ensure TF-IDF feature extraction is working"""
        self.processor.feature_engineering()
        self.assertGreater(len(self.processor.df_tfidf.columns), 0)  # Should have extracted features

    def test_full_pipeline(self):
        """Ensure full pipeline runs without errors"""
        df, df_tfidf = self.processor.process()
        self.assertFalse(df.empty)
        self.assertFalse(df_tfidf.empty)

if __name__ == '__main__':
    unittest.main()
