from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, UniqueConstraint
from datetime import datetime
from .base import Base

class AnalysisSummary(Base):
    __tablename__ = "analysis_summaries"
    __table_args__ = (UniqueConstraint('article_id', name='uix_article_id'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, nullable=False)
    sentiment = Column(String(20), nullable=False)
    key_points = Column(JSON, nullable=True)
    potential_impact = Column(Text, nullable=True)
    credibility_issues = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalysisSummary(article_id={self.article_id}, sentiment={self.sentiment})>"