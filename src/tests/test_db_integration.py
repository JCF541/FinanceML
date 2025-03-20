import pytest
from datetime import datetime

from sqlalchemy import create_engine
from src.data.models.article import Article
from src.data.models.analysis_summary import AnalysisSummary
from src.data.models.base import Base
from src.data.models.database import SessionLocal as sessionmaker

def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)

def test_article_and_analysis_persistence(db_session):
    article = Article(
        source="TestSource",
        title="Test Article",
        url="https://example.com/article",
        content="Sample content.",
        published_at=datetime.utcnow()
    )
    db_session.add(article)
    db_session.flush()

    analysis = AnalysisSummary(
        article_id=article.id,
        sentiment="Bullish",
        key_points=["Point 1", "Point 2"],
        potential_impact="Positive",
        credibility_issues=None
    )

    db_session.add(analysis)
    db_session.commit()

    retrieved_article = db_session.query(Article).filter_by(id=article.id).first()
    retrieved_analysis = db_session.query(AnalysisSummary).filter_by(article_id=article.id).first()

    assert retrieved_article.title == "Test Article"
    assert retrieved_analysis.sentiment == "Bullish"
