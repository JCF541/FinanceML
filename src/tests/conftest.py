import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.data.models.base import Base

@pytest.fixture(scope='module')
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)  # Create all tables
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()

@pytest.fixture(scope='module')
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()
