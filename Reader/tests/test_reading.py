import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from ..main import app
from ..models import ReadingSession, Document

client = TestClient(app)

def test_create_reading_session(test_token, test_document):
    response = client.post(
        "/api/v1/reading-sessions/",
        json={
            "document_id": test_document.id,
            "notes": "Test reading session"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == test_document.id
    assert data["notes"] == "Test reading session"
    assert "id" in data

def test_update_reading_session(test_token, test_document):
    # First create a session
    create_response = client.post(
        "/api/v1/reading-sessions/",
        json={"document_id": test_document.id},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    session_id = create_response.json()["id"]

    # Then update it
    update_data = {
        "end_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
        "duration_minutes": 30,
        "pages_read": 10,
        "notes": "Updated notes"
    }
    response = client.put(
        f"/api/v1/reading-sessions/{session_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["duration_minutes"] == 30
    assert data["pages_read"] == 10
    assert data["notes"] == "Updated notes"

def test_get_user_reading_sessions(test_token, test_document):
    # Create a session first
    client.post(
        "/api/v1/reading-sessions/",
        json={"document_id": test_document.id},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    response = client.get(
        "/api/v1/reading-sessions/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["document_id"] == test_document.id

def test_get_document_reading_sessions(test_token, test_document):
    # Create a session first
    client.post(
        "/api/v1/reading-sessions/",
        json={"document_id": test_document.id},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    response = client.get(
        f"/api/v1/documents/{test_document.id}/reading-sessions/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["document_id"] == test_document.id

def test_get_document_progress(test_token, test_document):
    # Update document with total pages
    client.put(
        f"/api/v1/documents/{test_document.id}",
        json={"total_pages": 100, "current_page": 25},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Create a reading session
    client.post(
        "/api/v1/reading-sessions/",
        json={"document_id": test_document.id},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    response = client.get(
        f"/api/v1/documents/{test_document.id}/progress",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == test_document.id
    assert data["current_page"] == 25
    assert data["total_pages"] == 100
    assert data["reading_progress"] == 25.0

def test_create_reading_session_unauthorized():
    response = client.post(
        "/api/v1/reading-sessions/",
        json={"document_id": 1}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_reading_session_unauthorized():
    response = client.put(
        "/api/v1/reading-sessions/1",
        json={"pages_read": 10}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 