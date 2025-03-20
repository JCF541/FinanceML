from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models for easy accessibility
from .article import Article
from .market_data import MarketData
from .analysis_summary import AnalysisSummary
from .database import get_session, get_db_config

__all__ = [
    'Base',
    'Article',
    'AnalysisSummary',
    'MarketData',
    'get_session',
    'get_db_config'
]