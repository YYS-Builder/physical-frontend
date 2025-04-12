import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..services.permissions import PermissionsService
from ..schemas.permissions import Permission, Role, UserRole

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

def test_create_role_endpoint(client):
    # Test data
    test_data = {
        "name": "editor",
        "permissions": ["read", "write"]
    }
    
    # Make request
    response = client.post("/api/permissions/roles", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    assert result["name"] == "editor"
    assert set(result["permissions"]) == {"read", "write"}

def test_assign_role_endpoint(client):
    # First create a role
    role_data = {
        "name": "viewer",
        "permissions": ["read"]
    }
    role_response = client.post("/api/permissions/roles", json=role_data)
    role_id = role_response.json()["id"]
    
    # Test data
    test_data = {
        "user_id": "user1",
        "role_id": role_id
    }
    
    # Make request
    response = client.post("/api/permissions/assign", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["user_id"] == "user1"
    assert result["role_id"] == role_id

def test_check_permission_endpoint(client):
    # First create a role and assign it
    role_data = {
        "name": "admin",
        "permissions": ["read", "write", "admin"]
    }
    role_response = client.post("/api/permissions/roles", json=role_data)
    role_id = role_response.json()["id"]
    
    # Assign role
    client.post("/api/permissions/assign", json={
        "user_id": "user1",
        "role_id": role_id
    })
    
    # Test permission check
    response = client.get(f"/api/permissions/check/user1/read")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["has_permission"] is True

def test_get_user_permissions_endpoint(client):
    # First create a role and assign it
    role_data = {
        "name": "editor",
        "permissions": ["read", "write"]
    }
    role_response = client.post("/api/permissions/roles", json=role_data)
    role_id = role_response.json()["id"]
    
    # Assign role
    client.post("/api/permissions/assign", json={
        "user_id": "user1",
        "role_id": role_id
    })
    
    # Get user permissions
    response = client.get("/api/permissions/user1")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"read", "write"}

def test_update_role_permissions_endpoint(client):
    # First create a role
    role_data = {
        "name": "viewer",
        "permissions": ["read"]
    }
    role_response = client.post("/api/permissions/roles", json=role_data)
    role_id = role_response.json()["id"]
    
    # Update role permissions
    update_data = {
        "permissions": ["read", "write"]
    }
    response = client.put(f"/api/permissions/roles/{role_id}", json=update_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert set(result["permissions"]) == {"read", "write"}

def test_remove_role_endpoint(client):
    # First create a role
    role_data = {
        "name": "temp",
        "permissions": ["read"]
    }
    role_response = client.post("/api/permissions/roles", json=role_data)
    role_id = role_response.json()["id"]
    
    # Remove role
    response = client.delete(f"/api/permissions/roles/{role_id}")
    
    # Verify response
    assert response.status_code == 200
    
    # Verify role is removed
    get_response = client.get(f"/api/permissions/roles/{role_id}")
    assert get_response.status_code == 404

def test_get_all_roles_endpoint(client):
    # Create some roles
    roles_data = [
        {"name": "admin", "permissions": ["read", "write", "admin"]},
        {"name": "editor", "permissions": ["read", "write"]},
        {"name": "viewer", "permissions": ["read"]}
    ]
    for role_data in roles_data:
        client.post("/api/permissions/roles", json=role_data)
    
    # Get all roles
    response = client.get("/api/permissions/roles")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert len(result) >= 3
    assert all("id" in role for role in result)
    assert all("name" in role for role in result)
    assert all("permissions" in role for role in result)

def test_permissions_with_service(db_session):
    # Initialize service
    service = PermissionsService(db_session)
    
    # Create role
    role = service.create_role("test_role", [Permission.READ, Permission.WRITE])
    assert isinstance(role, Role)
    assert role.name == "test_role"
    assert set(role.permissions) == {Permission.READ, Permission.WRITE}
    
    # Assign role
    user_role = service.assign_role("user1", role.id)
    assert isinstance(user_role, UserRole)
    assert user_role.user_id == "user1"
    assert user_role.role_id == role.id
    
    # Check permission
    assert service.check_permission("user1", Permission.READ) is True
    assert service.check_permission("user1", Permission.ADMIN) is False
    
    # Get user permissions
    permissions = service.get_user_permissions("user1")
    assert set(permissions) == {Permission.READ, Permission.WRITE}
    
    # Update role permissions
    updated_role = service.update_role_permissions(role.id, [Permission.READ])
    assert set(updated_role.permissions) == {Permission.READ}
    
    # Remove role
    service.remove_role(role.id)
    assert service.get_role(role.id) is None 