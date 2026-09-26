import pytest
from app.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.model import User, UserRoles
from fastapi.testclient import TestClient
from app.main import app
from app.utils.security import hash_password


@pytest.fixture
def db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture
def auth_headers(db: Session):

    # Register test user if not in database
    test_user = db.scalar(
        select(User).where(User.username == "admin")
    )

    if not test_user:

        try:
            test_user = User(
                account_number="000000000001",
                username="admin",
                first_name="Test",
                last_name="Admin",
                email="admin@test.com",
                phone="0123456789",
                available_balance=0,
                password_hash=hash_password("testpassword"),
                role=UserRoles.ADMIN
            )

            db.add(test_user)
            db.commit()

        except Exception:
            db.rollback()
            raise

    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "testpassword"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }