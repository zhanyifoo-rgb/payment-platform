import pytest
from app.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.model import Users, UserRoles
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

    # Register testuser if not in db 
    testuser = db.scalar(select(Users).where(Users.username == "admin"))

    if not testuser:

        try:
            test_user = Users(
                username = "admin",
                password_hash = hash_password("testpassword"),
                role = UserRoles.ADMIN
            )

            db.add(test_user)
            db.commit()

        except Exception:
            db.rollback()
            raise

    response = client.post(
                    "/login",
                    data = {
                        "username": "admin",
                        "password": "testpassword"
                    }
                )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }