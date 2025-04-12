import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..services.collaboration import CollaborationService
from ..schemas.collaboration import CollaborationSession, UserPresence

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_session_endpoint(client):
    # Test data
    test_data = {
        "document_id": "doc1",
        "user_id": "user1"
    }
    
    # Make request
    response = client.post("/api/collaboration/sessions", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    assert result["document_id"] == "doc1"
    assert result["host_id"] == "user1"
    assert len(result["participants"]) == 1
    assert result["participants"][0]["user_id"] == "user1"

def test_join_session_endpoint(client):
    # First create a session
    session_data = {
        "document_id": "doc1",
        "user_id": "user1"
    }
    session_response = client.post("/api/collaboration/sessions", json=session_data)
    session_id = session_response.json()["id"]
    
    # Test data
    test_data = {
        "user_id": "user2"
    }
    
    # Make request
    response = client.post(f"/api/collaboration/sessions/{session_id}/join", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == session_id
    assert len(result["participants"]) == 2
    assert any(p["user_id"] == "user2" for p in result["participants"])

def test_leave_session_endpoint(client):
    # First create a session and join it
    session_data = {
        "document_id": "doc1",
        "user_id": "user1"
    }
    session_response = client.post("/api/collaboration/sessions", json=session_data)
    session_id = session_response.json()["id"]
    
    client.post(f"/api/collaboration/sessions/{session_id}/join", json={"user_id": "user2"})
    
    # Leave session
    response = client.post(f"/api/collaboration/sessions/{session_id}/leave", json={"user_id": "user2"})
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == session_id
    assert len(result["participants"]) == 1
    assert result["participants"][0]["user_id"] == "user1"

def test_update_presence_endpoint(client):
    # First create a session
    session_data = {
        "document_id": "doc1",
        "user_id": "user1"
    }
    session_response = client.post("/api/collaboration/sessions", json=session_data)
    session_id = session_response.json()["id"]
    
    # Update presence
    test_data = {
        "user_id": "user1",
        "status": "typing"
    }
    response = client.post(f"/api/collaboration/sessions/{session_id}/presence", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["user_id"] == "user1"
    assert result["status"] == "typing"

def test_get_session_endpoint(client):
    # First create a session
    session_data = {
        "document_id": "doc1",
        "user_id": "user1"
    }
    session_response = client.post("/api/collaboration/sessions", json=session_data)
    session_id = session_response.json()["id"]
    
    # Get session
    response = client.get(f"/api/collaboration/sessions/{session_id}")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == session_id
    assert result["document_id"] == "doc1"
    assert result["host_id"] == "user1"

def test_end_session_endpoint(client):
    # First create a session
    session_data = {
        "document_id": "doc1",
        "user_id": "user1"
    }
    session_response = client.post("/api/collaboration/sessions", json=session_data)
    session_id = session_response.json()["id"]
    
    # End session
    response = client.post(f"/api/collaboration/sessions/{session_id}/end")
    
    # Verify response
    assert response.status_code == 200
    
    # Verify session is ended
    get_response = client.get(f"/api/collaboration/sessions/{session_id}")
    assert get_response.status_code == 404

def test_get_active_sessions_endpoint(client):
    # Create some sessions
    sessions_data = [
        {"document_id": "doc1", "user_id": "user1"},
        {"document_id": "doc1", "user_id": "user2"},
        {"document_id": "doc2", "user_id": "user1"}
    ]
    for session_data in sessions_data:
        client.post("/api/collaboration/sessions", json=session_data)
    
    # Get active sessions for doc1
    response = client.get("/api/collaboration/sessions/active/doc1")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert len(result) >= 2
    assert all(s["document_id"] == "doc1" for s in result)

def test_get_user_sessions_endpoint(client):
    # Create some sessions
    sessions_data = [
        {"document_id": "doc1", "user_id": "user1"},
        {"document_id": "doc2", "user_id": "user1"}
    ]
    for session_data in sessions_data:
        client.post("/api/collaboration/sessions", json=session_data)
    
    # Get user sessions
    response = client.get("/api/collaboration/sessions/user/user1")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert len(result) >= 2
    assert all(s["host_id"] == "user1" for s in result)

def test_collaboration_with_service(db_session):
    # Initialize service
    service = CollaborationService(db_session)
    
    # Create session
    session = service.create_session("doc1", "user1")
    assert isinstance(session, CollaborationSession)
    assert session.document_id == "doc1"
    assert session.host_id == "user1"
    assert len(session.participants) == 1
    
    # Join session
    updated_session = service.join_session(session.id, "user2")
    assert len(updated_session.participants) == 2
    assert any(p.user_id == "user2" for p in updated_session.participants)
    
    # Update presence
    presence = service.update_presence(session.id, "user1", "typing")
    assert isinstance(presence, UserPresence)
    assert presence.user_id == "user1"
    assert presence.status == "typing"
    
    # Leave session
    updated_session = service.leave_session(session.id, "user2")
    assert len(updated_session.participants) == 1
    assert updated_session.participants[0].user_id == "user1"
    
    # End session
    service.end_session(session.id)
    assert service.get_session(session.id) is None 