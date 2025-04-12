from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from ..main import app
from ..database import get_db, Base, engine
from ..models import User, Document, Collection, DocumentAnalytics
from ..auth import access_control
import time

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
    # In a real scenario, this would use the actual token generation
    return "test_token"

def test_full_collection_workflow(db_session, test_user, test_token):
    """Test the complete collection workflow."""
    # Create collection
    response = client.post(
        "/collections/",
        json={
            "name": "Test Collection",
            "description": "Test description"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    collection = response.json()
    
    # Create document
    response = client.post(
        "/documents/",
        json={
            "title": "Test Document",
            "content": "Test content"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    document = response.json()
    
    # Add document to collection
    response = client.post(
        f"/collections/{collection['id']}/documents/{document['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    
    # Process document
    response = client.post(
        f"/documents/{document['id']}/process",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    
    # Get collection with documents
    response = client.get(
        f"/collections/{collection['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()["documents"]) == 1

def test_reading_analytics_workflow(db_session, test_user, test_token):
    """Test the complete reading analytics workflow."""
    # Create document
    response = client.post(
        "/documents/",
        json={
            "title": "Test Document",
            "content": "Test content"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    document = response.json()
    
    # Start reading session
    response = client.post(
        f"/documents/{document['id']}/start-reading",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    session = response.json()
    
    # Update reading progress
    response = client.put(
        f"/documents/{document['id']}/reading-progress",
        json={
            "pages_read": 10,
            "duration_minutes": 30
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    
    # End reading session
    response = client.post(
        f"/documents/{document['id']}/end-reading",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    
    # Get analytics
    response = client.get(
        f"/documents/{document['id']}/analytics",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    analytics = response.json()
    assert analytics["total_pages_read"] == 10
    assert analytics["total_duration_minutes"] == 30

def test_error_handling(db_session, test_user, test_token):
    """Test error handling scenarios."""
    # Test non-existent resource
    response = client.get(
        "/collections/999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404
    
    # Test invalid input
    response = client.post(
        "/collections/",
        json={
            "name": "",  # Invalid empty name
            "description": "Test description"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 422
    
    # Test unauthorized access
    response = client.get(
        "/collections/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401 