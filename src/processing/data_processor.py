import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob

class DataProcessor:
    def __init__(self, articles):
        """Initialize with a list of articles (from DB or Scrapy)."""
        self.df = pd.DataFrame(articles)

    def clean_text(self, text):
        """Clean article text: remove HTML, symbols, and lowercasing."""
        text = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
        return text.lower().strip()

    def preprocess_articles(self):
        """Applies preprocessing steps to all articles."""
        self.df["clean_content"] = self.df["content"].apply(self.clean_text)
        self.df["title_length"] = self.df["title"].apply(lambda x: len(str(x)))
        self.df["content_length"] = self.df["clean_content"].apply(lambda x: len(str(x)))
        self.df["word_count"] = self.df["clean_content"].apply(lambda x: len(x.split()))
        self.df["date_parsed"] = pd.to_datetime(self.df["published_at"], errors='coerce')

    def analyze_sentiment(self):
        """Apply sentiment analysis using TextBlob."""
        self.df["sentiment_score"] = self.df["clean_content"].apply(lambda x: TextBlob(x).sentiment.polarity)
        self.df["sentiment_label"] = self.df["sentiment_score"].apply(lambda x: "Bullish" if x > 0.1 else ("Bearish" if x < -0.1 else "Neutral"))

    def feature_engineering(self):
        """Apply TF-IDF for keyword extraction."""
        vectorizer = TfidfVectorizer(stop_words="english", max_features=100)
        tfidf_matrix = vectorizer.fit_transform(self.df["clean_content"])
        feature_names = vectorizer.get_feature_names_out()
        self.df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    def process(self):
        """Full execution pipeline."""
        self.preprocess_articles()
        self.analyze_sentiment()
        self.feature_engineering()
        return self.df, self.df_tfidf  # Return both main and feature-engineered DataFrames
