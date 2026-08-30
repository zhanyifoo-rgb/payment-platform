import pytest
from app.database import SessionLocal

@pytest.fixture
def db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()