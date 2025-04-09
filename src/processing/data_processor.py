import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, articles):
        """Initialize with a list of articles (from DB or Scrapy)."""
        self.df = pd.DataFrame(articles)
        logger.info(f"DataProcessor initialized with {len(self.df)} articles.")

    def clean_text(self, text):
        """Clean article text: remove HTML, symbols, and lowercasing."""
        cleaned = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned)  # Remove special characters
        cleaned = cleaned.lower().strip()
        return cleaned

    def preprocess_articles(self):
        """Applies preprocessing steps to all articles."""
        try:
            self.df["clean_content"] = self.df["content"].apply(self.clean_text)
            self.df["title_length"] = self.df["title"].apply(lambda x: len(str(x)))
            self.df["content_length"] = self.df["clean_content"].apply(lambda x: len(str(x)))
            self.df["word_count"] = self.df["clean_content"].apply(lambda x: len(x.split()))
            self.df["date_parsed"] = pd.to_datetime(self.df["published_at"], errors='coerce')
            logger.info("Article preprocessing completed.")
        except Exception as e:
            logger.error(f"Error during preprocessing: {e}")
            raise

    def analyze_sentiment(self):
        """Apply sentiment analysis using TextBlob."""
        try:
            self.df["sentiment_score"] = self.df["clean_content"].apply(lambda x: TextBlob(x).sentiment.polarity)
            self.df["sentiment_label"] = self.df["sentiment_score"].apply(
                lambda x: "Bullish" if x > 0.1 else ("Bearish" if x < -0.1 else "Neutral")
            )
            logger.info("Sentiment analysis completed.")
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            raise

    def feature_engineering(self):
        """Apply TF-IDF for keyword extraction."""
        try:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=100)
            tfidf_matrix = vectorizer.fit_transform(self.df["clean_content"])
            feature_names = vectorizer.get_feature_names_out()
            self.df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
            logger.info("TF-IDF feature engineering completed.")
        except Exception as e:
            logger.error(f"Error during feature engineering: {e}")
            raise

    def process(self):
        """Full execution pipeline."""
        logger.info("Starting full data processing pipeline.")
        self.preprocess_articles()
        self.analyze_sentiment()
        self.feature_engineering()
        logger.info("Data processing pipeline completed.")
        return self.df, self.df_tfidf
