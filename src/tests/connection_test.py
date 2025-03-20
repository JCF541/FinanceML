from sqlalchemy import text
from data.models.database import SessionLocal

try:
    session = SessionLocal()
    session.execute(text('SELECT 1'))  # simple test query
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
finally:
    session.close()
