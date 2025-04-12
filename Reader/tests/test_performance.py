from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
import time
from ..main import app
from ..database import get_db, Base, engine
from ..models import User, Document, Collection
from ..auth import access_control

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

@pytest.fixture
def test_token(test_user):
    return "test_token"

def test_response_time():
    """Test API response time under normal load."""
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 0.1  # Response should be under 100ms

def test_concurrent_requests():
    """Test API performance under concurrent requests."""
    import concurrent.futures
    
    def make_request():
        response = client.get("/health")
        return response.status_code
    
    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in futures]
    
    assert all(code == 200 for code in results)

def test_large_payload():
    """Test API performance with large payloads."""
    # Create a large document
    large_content = "Test content " * 10000  # ~120KB
    
    start_time = time.time()
    response = client.post(
        "/documents/",
        json={
            "title": "Large Document",
            "content": large_content
        },
        headers={"Authorization": "Bearer test_token"}
    )
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 1.0  # Should process within 1 second

def test_database_performance(db_session, test_user, test_token):
    """Test database operation performance."""
    # Create multiple collections
    start_time = time.time()
    
    for i in range(100):
        response = client.post(
            "/collections/",
            json={
                "name": f"Collection {i}",
                "description": f"Description {i}"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Average time per operation should be under 50ms
    assert total_time / 100 < 0.05

def test_rate_limiting_performance():
    """Test rate limiting performance."""
    # Make requests up to the rate limit
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
    
    # The next request should be rate limited
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    assert response.status_code == 429
    # Rate limiting response should be fast
    assert end_time - start_time < 0.1 