import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_db, engine, Base
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Create test database
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield db
    db.rollback()
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user(test_db):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login(test_db):
    # First register
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpass123",
            "full_name": "Login User"
        }
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": "loginpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()