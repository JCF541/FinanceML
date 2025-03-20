import unittest
import pandas as pd
from datetime import datetime
from src.processing.backtester import Backtester
from src.data.models.trading_strategy import TradingStrategy
from src.data.models.agent import BullishAgent, BearishAgent
from src.scraping.scrape_data import fetch_binance_historical_data
from src.data.models.database import get_session
from src.data.models.article import Article

def setUp(self):
    self.strategy = TradingStrategy()
    self.backtester = Backtester(
        trading_strategy=self.strategy,
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    self.backtester.load_data(symbol="BTCUSDT")

    with get_session() as session:
        articles = session.query(Article).filter(
            Article.published_at.between("2024-01-01", "2024-12-31")
        ).all()

        if not articles:
            # Insert a dummy article if none exist
            dummy_article = Article(
                source="TestSource",
                title="Test Bitcoin Rally",
                url="https://test.com/article-bitcoin-rally",
                content="Bitcoin is experiencing a strong bullish rally.",
                published_at=datetime(2024, 1, 15)
            )
            session.add(dummy_article)
            session.commit()
            articles = [dummy_article]

    self.articles = [{"title": a.title, "content": a.content, "published_at": a.published_at} for a in articles]

    print(f"Articles fetched after seeding: {len(self.articles)}")

    self.backtester.apply_sentiment_analysis(self.articles)

    def test_backtesting_execution(self):
        final_balance = self.backtester.execute_strategy()
        self.assertGreater(final_balance, 0)

if __name__ == "__main__":
    unittest.main()
