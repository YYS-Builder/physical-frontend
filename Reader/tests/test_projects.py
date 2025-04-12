import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..models import Project

client = TestClient(app)

def test_create_project(test_token):
    response = client.post(
        "/api/v1/projects/",
        json={"title": "New Project", "description": "Test Description"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Project"
    assert data["description"] == "Test Description"
    assert "id" in data

def test_get_projects(test_token, test_project):
    response = client.get(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == test_project.title

def test_get_project(test_token, test_project):
    response = client.get(
        f"/api/v1/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_project.title
    assert data["description"] == test_project.description

def test_get_nonexistent_project(test_token):
    response = client.get(
        "/api/v1/projects/999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_create_project_unauthorized():
    response = client.post(
        "/api/v1/projects/",
        json={"title": "New Project", "description": "Test Description"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 