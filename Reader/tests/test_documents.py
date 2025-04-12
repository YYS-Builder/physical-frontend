import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..models import Document

client = TestClient(app)

def test_create_document(test_token, test_project):
    response = client.post(
        "/api/v1/documents/",
        json={
            "title": "New Document",
            "content": "Test Content",
            "project_id": test_project.id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Document"
    assert data["content"] == "Test Content"
    assert data["project_id"] == test_project.id

def test_get_documents(test_token, test_document):
    response = client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == test_document.title

def test_get_project_documents(test_token, test_project, test_document):
    response = client.get(
        f"/api/v1/projects/{test_project.id}/documents/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == test_document.title
    assert data[0]["project_id"] == test_project.id

def test_create_document_invalid_project(test_token):
    response = client.post(
        "/api/v1/documents/",
        json={
            "title": "New Document",
            "content": "Test Content",
            "project_id": 999
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_create_document_unauthorized():
    response = client.post(
        "/api/v1/documents/",
        json={
            "title": "New Document",
            "content": "Test Content",
            "project_id": 1
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 