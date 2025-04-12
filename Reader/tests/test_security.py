from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
import jwt
from ..main import app
from ..database import get_db, Base, engine
from ..models import User
from ..config import settings

client = TestClient(app)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    yield session
    session.rollback()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_jwt_security():
    """Test JWT token security."""
    # Test token expiration
    expired_token = jwt.encode(
        {"sub": "testuser", "exp": 0},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    response = client.get(
        "/collections/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    
    # Test invalid signature
    invalid_token = jwt.encode(
        {"sub": "testuser"},
        "wrong_secret",
        algorithm=settings.ALGORITHM
    )
    response = client.get(
        "/collections/",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    
    # Test missing token
    response = client.get("/collections/")
    assert response.status_code == 401

def test_sql_injection(db_session, test_user):
    """Test SQL injection prevention."""
    # Attempt SQL injection in collection name
    response = client.post(
        "/collections/",
        json={
            "name": "'; DROP TABLE users; --",
            "description": "Test description"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 422  # Should be caught by validation
    
    # Verify users table still exists
    users = db_session.query(User).all()
    assert len(users) > 0

def test_xss_prevention():
    """Test XSS prevention."""
    # Attempt XSS in document content
    xss_content = "<script>alert('xss')</script>"
    response = client.post(
        "/documents/",
        json={
            "title": "Test Document",
            "content": xss_content
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    document = response.json()
    assert xss_content not in document["content"]  # Should be sanitized

def test_csrf_protection():
    """Test CSRF protection."""
    # Attempt request without CSRF token
    response = client.post(
        "/collections/",
        json={
            "name": "Test Collection",
            "description": "Test description"
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "invalid_token"
        }
    )
    assert response.status_code == 403

def test_rate_limiting_security():
    """Test rate limiting security."""
    # Make rapid requests to test rate limiting
    for _ in range(10):
        response = client.get("/health")
        if response.status_code == 429:
            break
    else:
        pytest.fail("Rate limiting not working")

def test_input_validation():
    """Test input validation security."""
    # Test oversized input
    large_input = "a" * (settings.MAX_FILE_SIZE + 1)
    response = client.post(
        "/documents/",
        json={
            "title": "Test Document",
            "content": large_input
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 413  # Payload Too Large
    
    # Test malformed JSON
    response = client.post(
        "/documents/",
        data="invalid json",
        headers={
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 422  # Unprocessable Entity 