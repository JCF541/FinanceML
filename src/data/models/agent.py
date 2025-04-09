import pandas as pd
from textblob import TextBlob
from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker
from src.data.models.database import engine
from src.data.models.analysis_summary import AnalysisSummary
from src.data.models.article import Article
import logging

logger = logging.getLogger(__name__)

class AnalyticalAgent(ABC):
    """Base class for analytical agents handling sentiment and credibility analysis."""
    
    def __init__(self, articles):
        self.df = pd.DataFrame(articles)
        self.session = sessionmaker(bind=engine)()
    
    @abstractmethod
    def analyze(self):
        pass

    def clean_text(self, text):
        """Removes HTML and special characters."""
        import re
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text.lower().strip()

    def preprocess_articles(self):
        """Prepares the text for sentiment analysis."""
        if self.df.empty:
            logger.warning("Empty DataFrame provided; skipping preprocessing.")
            return
        if "content" not in self.df.columns:
            raise KeyError("Missing 'content' column in DataFrame.")
        self.df["clean_content"] = self.df["content"].apply(self.clean_text)
        self.df["date_parsed"] = pd.to_datetime(self.df["published_at"], errors='coerce')

    def save_analysis(self, article_id, sentiment, key_points, credibility_issues):
        """Save or update analysis results in the database."""
        existing_analysis = self.session.query(AnalysisSummary).filter_by(article_id=article_id).first()
        if existing_analysis:
            existing_analysis.sentiment = sentiment
            existing_analysis.key_points = key_points
            existing_analysis.credibility_issues = credibility_issues
        else:
            analysis = AnalysisSummary(
                article_id=article_id,
                sentiment=sentiment,
                key_points=key_points,
                credibility_issues=credibility_issues
            )
            self.session.add(analysis)
        try:
            self.session.commit()
        except Exception as e:
            logger.error(f"Error saving analysis for article_id {article_id}: {e}")
            self.session.rollback()

class BullishAgent(AnalyticalAgent):
    """Detects bullish trends based on sentiment and key phrases."""
    
    def analyze(self):
        self.preprocess_articles()
        if self.df.empty or "clean_content" not in self.df.columns:
            logger.info("No articles to analyze for bullish sentiment.")
            return self.df
        self.df["sentiment_score"] = self.df["clean_content"].apply(lambda x: TextBlob(x).sentiment.polarity)
        self.df["bullish_signal"] = self.df["sentiment_score"].apply(lambda x: x > 0.1)
        
        for _, row in self.df.iterrows():
            article = self.session.query(Article).filter_by(title=row["title"]).first()
            if article:
                self.save_analysis(
                    article.id,
                    "Bullish" if row["bullish_signal"] else "Neutral",
                    key_points=[], 
                    credibility_issues=None
                )
        return self.df

class BearishAgent(AnalyticalAgent):
    """Detects bearish trends based on sentiment and key phrases."""
    
    def analyze(self):
        self.preprocess_articles()
        if self.df.empty or "clean_content" not in self.df.columns:
            logger.info("No articles to analyze for bearish sentiment.")
            return self.df
        self.df["sentiment_score"] = self.df["clean_content"].apply(lambda x: TextBlob(x).sentiment.polarity)
        self.df["bearish_signal"] = self.df["sentiment_score"].apply(lambda x: x < -0.1)
        
        for _, row in self.df.iterrows():
            article = self.session.query(Article).filter_by(title=row["title"]).first()
            if article:
                self.save_analysis(
                    article.id,
                    "Bearish" if row["bearish_signal"] else "Neutral",
                    key_points=[], 
                    credibility_issues=None
                )
        return self.df
