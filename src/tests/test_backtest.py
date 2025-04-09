import unittest
import logging
from datetime import datetime
from src.processing.backtester import Backtester
from src.data.models.trading_strategy import TradingStrategy
from src.data.models.database import get_session
from src.data.models.article import Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_backtest")

class TestBacktester(unittest.TestCase):

    def setUp(self):
        # Initialize strategy and backtester
        self.strategy = TradingStrategy(bullish_ma_window=5)
        self.backtester = Backtester(
            trading_strategy=self.strategy,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        # Load Binance market data
        self.backtester.load_data(symbol="BTCUSDT")
        self.assertIsNotNone(self.backtester.df, "Market data failed to load.")

        # Fetch relevant articles from DB within an active session
        with get_session() as session:
            articles = session.query(Article).filter(
                Article.published_at.between("2024-01-01", "2024-12-31")
            ).all()

            if not articles:
                logger.info("No articles found. Seeding test article.")
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

            # Convert articles to plain dictionaries while still in the session
            articles_list = []
            for a in articles:
                articles_list.append({
                    "title": a.title,
                    "content": a.content,
                    "published_at": a.published_at
                })
            self.articles = articles_list

        logger.info(f"Articles fetched for test: {len(self.articles)}")
        
        # Apply sentiment analysis using the plain-structured articles
        self.backtester.apply_sentiment_analysis(self.articles)
        self.assertIn("bullish_signal", self.backtester.df.columns, "Sentiment signals were not applied.")

    def test_backtesting_execution(self):
        final_balance = self.backtester.execute_strategy()
        logger.info(f"Test Final Portfolio Value: ${final_balance:.2f}")
        self.assertGreater(final_balance, 0, "Final balance should always be positive after execution.")

    def test_no_articles_scenario(self):
        # Test backtesting behavior with no articles provided
        self.backtester.apply_sentiment_analysis([])
        final_balance_no_articles = self.backtester.execute_strategy()
        logger.info(f"Final Portfolio Value without Articles: ${final_balance_no_articles:.2f}")
        self.assertGreaterEqual(final_balance_no_articles, 0, "Strategy must handle no-article scenarios gracefully.")

if __name__ == "__main__":
    unittest.main()
