from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from ..main import app
from ..database import get_db, Base, engine
from ..models import User, Document, Collection, DocumentAnalytics
from ..auth import access_control
import json
from tests.utils import (
    assert_response,
    create_test_user,
    create_test_collection,
    create_test_document,
    login_user,
    get_auth_headers
)

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
def test_document(db_session, test_user):
    document = Document(
        title="Test Document",
        content="Test content",
        user_id=test_user.id
    )
    db_session.add(document)
    db_session.commit()
    return document

@pytest.fixture
def test_collection(db_session, test_user):
    collection = Collection(
        name="Test Collection",
        description="Test description",
        user_id=test_user.id
    )
    db_session.add(collection)
    db_session.commit()
    return collection

def test_create_collection(db_session, test_user):
    response = client.post(
        "/collections/",
        json={
            "name": "New Collection",
            "description": "Test description"
        },
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Collection"
    assert data["description"] == "Test description"

def test_get_collection(db_session, test_user, test_collection):
    response = client.get(
        f"/collections/{test_collection.id}",
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_collection.name
    assert data["description"] == test_collection.description

def test_add_document_to_collection(db_session, test_user, test_collection, test_document):
    response = client.post(
        f"/collections/{test_collection.id}/documents/{test_document.id}",
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document added to collection successfully"

def test_process_document(db_session, test_user, test_document):
    response = client.post(
        f"/documents/{test_document.id}/process",
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "embeddings" in data
    assert data["status"] == "success"

def test_analyze_reading_session(db_session, test_user, test_document):
    analytics = DocumentAnalytics(
        document_id=test_document.id,
        user_id=test_user.id,
        total_sessions=1,
        total_duration_minutes=30,
        total_pages_read=10
    )
    db_session.add(analytics)
    db_session.commit()
    
    response = client.post(
        f"/analytics/{analytics.id}/analyze",
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "patterns" in data
    assert "recommendations" in data
    assert data["status"] == "success"

def test_rate_limiting():
    # Test rate limiting by making multiple requests
    for _ in range(5):
        response = client.get("/collections/")
        assert response.status_code == 200
    
    # The 6th request should be rate limited
    response = client.get("/collections/")
    assert response.status_code == 429  # Too Many Requests

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert_response(response, data={"status": "ok"})

def test_metrics_endpoint(client: TestClient):
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert_response(response)
    data = response.json()
    assert "uptime" in data
    assert "requests" in data
    assert "errors" in data

def test_user_registration(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "password": "newpassword"
        }
    )
    assert_response(response, status_code=201)
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "newuser@example.com"

def test_user_login(client: TestClient):
    """Test user login."""
    # Create test user first
    create_test_user(client)
    
    response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert_response(response)
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_collection_operations(client: TestClient):
    """Test collection CRUD operations."""
    # Create user and get token
    create_test_user(client)
    token = login_user(client)
    
    # Create collection
    response = client.post(
        "/api/v1/collections/",
        headers=get_auth_headers(token),
        json={
            "name": "Test Collection",
            "description": "Test Description"
        }
    )
    assert_response(response, status_code=201)
    collection = response.json()
    
    # Get collection
    response = client.get(
        f"/api/v1/collections/{collection['id']}",
        headers=get_auth_headers(token)
    )
    assert_response(response)
    assert response.json() == collection
    
    # Update collection
    response = client.put(
        f"/api/v1/collections/{collection['id']}",
        headers=get_auth_headers(token),
        json={
            "name": "Updated Collection",
            "description": "Updated Description"
        }
    )
    assert_response(response)
    updated = response.json()
    assert updated["name"] == "Updated Collection"
    
    # Delete collection
    response = client.delete(
        f"/api/v1/collections/{collection['id']}",
        headers=get_auth_headers(token)
    )
    assert_response(response, status_code=204)

def test_document_operations(client: TestClient):
    """Test document CRUD operations."""
    # Create user and get token
    create_test_user(client)
    token = login_user(client)
    
    # Create collection
    collection = create_test_collection(client, token)
    
    # Create document
    response = client.post(
        f"/api/v1/collections/{collection['id']}/documents/",
        headers=get_auth_headers(token),
        json={
            "title": "Test Document",
            "content": "Test Content"
        }
    )
    assert_response(response, status_code=201)
    document = response.json()
    
    # Get document
    response = client.get(
        f"/api/v1/collections/{collection['id']}/documents/{document['id']}",
        headers=get_auth_headers(token)
    )
    assert_response(response)
    assert response.json() == document
    
    # Update document
    response = client.put(
        f"/api/v1/collections/{collection['id']}/documents/{document['id']}",
        headers=get_auth_headers(token),
        json={
            "title": "Updated Document",
            "content": "Updated Content"
        }
    )
    assert_response(response)
    updated = response.json()
    assert updated["title"] == "Updated Document"
    
    # Delete document
    response = client.delete(
        f"/api/v1/collections/{collection['id']}/documents/{document['id']}",
        headers=get_auth_headers(token)
    )
    assert_response(response, status_code=204)

def test_analytics_operations(client: TestClient):
    """Test analytics operations."""
    # Create user and get token
    create_test_user(client)
    token = login_user(client)
    
    # Create collection and document
    collection = create_test_collection(client, token)
    document = create_test_document(client, token, collection["id"])
    
    # Record reading session
    response = client.post(
        f"/api/v1/collections/{collection['id']}/documents/{document['id']}/read",
        headers=get_auth_headers(token),
        json={
            "duration_minutes": 30,
            "pages_read": 10
        }
    )
    assert_response(response, status_code=201)
    
    # Get analytics
    response = client.get(
        f"/api/v1/collections/{collection['id']}/documents/{document['id']}/analytics",
        headers=get_auth_headers(token)
    )
    assert_response(response)
    analytics = response.json()
    assert "total_sessions" in analytics
    assert "total_duration_minutes" in analytics
    assert "total_pages_read" in analytics
    assert analytics["total_sessions"] == 1
    assert analytics["total_duration_minutes"] == 30
    assert analytics["total_pages_read"] == 10

def test_error_handling(client: TestClient):
    """Test error handling."""
    # Test invalid token
    response = client.get(
        "/api/v1/collections/1",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert_response(response, status_code=401, error="Could not validate credentials")
    
    # Test non-existent resource
    token = login_user(client)
    response = client.get(
        "/api/v1/collections/999",
        headers=get_auth_headers(token)
    )
    assert_response(response, status_code=404, error="Collection not found")
    
    # Test invalid input
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "invalid_email",
            "password": "short"
        }
    )
    assert_response(response, status_code=422) 