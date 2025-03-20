from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .base import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Article(title={self.title}, source={self.source})>"
