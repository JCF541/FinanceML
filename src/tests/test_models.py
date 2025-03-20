import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.data.models.base import Base
from src.data.models.article import Article
from src.data.models.market_data import MarketData
from src.data.models.analysis_summary import AnalysisSummary

@pytest.fixture(scope='module')
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()

def test_article_creation(test_session):
    article = Article(
        source="CoinDesk",
        title="Bitcoin reaches all-time high",
        url="https://example.com/bitcoin-all-time-high",
        content="Bitcoin hits new highs on institutional buying...",
        published_at=datetime(2023, 3, 13, 10, 0, 0)
    )
    test_session.add(article)
    test_session.commit()

    result = test_session.query(Article).filter_by(url="https://example.com/bitcoin-all-time-high").first()
    assert result is not None
    assert result.title == "Bitcoin reaches all-time high"

def test_market_data_creation(test_session):
    market_data = MarketData(
        symbol="BTCUSDT",
        open_time=datetime(2023, 3, 12, 0, 0, 0),
        close_time=datetime(2023, 3, 12, 23, 59, 59),
        open_price=40000.0,
        high_price=42000.0,
        low_price=39500.0,
        close_price=41500.0,
        volume=1234.567,
        trades_count=3456
    )
    test_session.add(market_data)
    test_session.commit()

    result = test_session.query(MarketData).filter_by(symbol="BTCUSDT", open_time=datetime(2023, 3, 12, 0, 0, 0)).first()
    assert result is not None
    assert result.symbol == "BTCUSDT"

def test_analysis_summary_creation(test_session):
    article = Article(
        source="CoinTelegraph",
        title="BTC surges amid positive sentiment",
        url="https://example.com/btc-sentiment"
    )
    test_session.add(article)
    test_session.commit()

    summary = AnalysisSummary(
        article_id=article.id,
        sentiment="Bullish",
        key_points=["Increased investment"],
        potential_impact="Positive",
        credibility_issues=None
    )
    test_session.add(summary)
    test_session.commit()

    result = test_session.query(AnalysisSummary).filter_by(article_id=article.id).first()
    assert result is not None
    assert result.sentiment == "Bullish"

def test_article_unique_constraint(test_session):
    article1 = Article(
        source="NewsBTC",
        title="BTC testing resistance",
        url="https://example.com/btc-resistance"
    )
    test_session.add(article1)
    test_session.commit()

    article_duplicate = Article(
        source="NewsBTC",
        title="Duplicate Article",
        url="https://example.com/btc-resistance"
    )
    test_session.add(article_duplicate)
    with pytest.raises(Exception):
        test_session.commit()
    test_session.rollback()

def test_marketdata_unique_constraint(test_session):
    market_data1 = MarketData(
        symbol="BTCUSDT",
        open_time=datetime(2023, 3, 11, 0, 0, 0),
        close_time=datetime(2023, 3, 11, 23, 59, 59),
        open_price=39000.0,
        high_price=40500.0,
        low_price=38500.0,
        close_price=40000.0,
        volume=987.654,
        trades_count=1234
    )
    test_session.add(market_data1)
    test_session.commit()

    market_data_duplicate = MarketData(
        symbol="BTCUSDT",
        open_time=datetime(2023, 3, 11, 0, 0, 0),
        close_time=datetime(2023, 3, 11, 23, 59, 59),
        open_price=39000.0,
        high_price=40500.0,
        low_price=38500.0,
        close_price=40000.0,
        volume=987.654,
        trades_count=1234
    )
    test_session.add(market_data_duplicate)
    with pytest.raises(Exception):
        test_session.commit()
    test_session.rollback()

def test_analysis_summary_unique_constraint(test_session):
    article = Article(
        source="CryptoSlate",
        title="BTC stability at new levels",
        url="https://example.com/btc-stability"
    )
    test_session.add(article)
    test_session.commit()

    summary1 = AnalysisSummary(article_id=article.id, sentiment="Neutral")
    test_session.add(summary1)
    test_session.commit()

    summary_duplicate = AnalysisSummary(article_id=article.id, sentiment="Bearish")
    test_session.add(summary_duplicate)

    with pytest.raises(Exception):
        test_session.commit()
    test_session.rollback()
