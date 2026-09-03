import pytest
from app.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.model import Users
from fastapi.testclient import TestClient
from app.main import app

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
    testuser = db.scalar(select(Users).where(Users.username == "testuser"))

    if not testuser:
        response = client.post(
                "/register",
                json = {
                    "username": "testuser",
                    "password": "testpassword",
                    "role": "admin"
                }
            )

        assert response.status_code == 201

    response = client.post(
                    "/login",
                    data = {
                        "username": "testuser",
                        "password": "testpassword"
                    }
                )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }