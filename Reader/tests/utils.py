import json
from typing import Any, Dict, Optional

from fastapi.testclient import TestClient

def assert_response(
    response,
    status_code: int = 200,
    content_type: str = "application/json",
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> None:
    """Assert response matches expected values."""
    assert response.status_code == status_code
    assert response.headers["content-type"] == content_type
    
    if content_type == "application/json":
        response_data = response.json()
        if data:
            assert response_data == data
        if error:
            assert "detail" in response_data
            assert response_data["detail"] == error

def create_test_user(
    client: TestClient,
    email: str = "test@example.com",
    password: str = "testpassword"
) -> Dict[str, Any]:
    """Create a test user."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "password": password
        }
    )
    assert response.status_code == 201
    return response.json()

def get_auth_headers(token: str) -> Dict[str, str]:
    """Get authentication headers."""
    return {"Authorization": f"Bearer {token}"}

def create_test_collection(
    client: TestClient,
    token: str,
    name: str = "Test Collection",
    description: str = "Test Description"
) -> Dict[str, Any]:
    """Create a test collection."""
    response = client.post(
        "/api/v1/collections/",
        headers=get_auth_headers(token),
        json={
            "name": name,
            "description": description
        }
    )
    assert response.status_code == 201
    return response.json()

def create_test_document(
    client: TestClient,
    token: str,
    collection_id: int,
    title: str = "Test Document",
    content: str = "Test Content"
) -> Dict[str, Any]:
    """Create a test document."""
    response = client.post(
        f"/api/v1/collections/{collection_id}/documents/",
        headers=get_auth_headers(token),
        json={
            "title": title,
            "content": content
        }
    )
    assert response.status_code == 201
    return response.json()

def login_user(
    client: TestClient,
    email: str = "test@example.com",
    password: str = "testpassword"
) -> str:
    """Login user and return token."""
    response = client.post(
        "/api/v1/token",
        data={
            "username": email,
            "password": password
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"] 