import pytest
from unittest.mock import Mock, patch
from ..services.permissions import PermissionsService
from ..schemas.permissions import Permission, Role, UserRole

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def permissions_service(mock_db):
    return PermissionsService(mock_db)

def test_create_role(permissions_service, mock_db):
    # Test input
    name = "editor"
    permissions = [Permission.READ, Permission.WRITE]
    
    # Call the service
    result = permissions_service.create_role(name, permissions)
    
    # Verify the result
    assert isinstance(result, Role)
    assert result.name == name
    assert set(result.permissions) == set(permissions)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_get_role(permissions_service, mock_db):
    # Mock database query
    mock_role = Mock()
    mock_role.id = 1
    mock_role.name = "editor"
    mock_role.permissions = [Permission.READ, Permission.WRITE]
    mock_db.query.return_value.filter.return_value.first.return_value = mock_role
    
    # Call the service
    result = permissions_service.get_role(1)
    
    # Verify the result
    assert isinstance(result, Role)
    assert result.id == 1
    assert result.name == "editor"
    assert set(result.permissions) == {Permission.READ, Permission.WRITE}

def test_assign_role(permissions_service, mock_db):
    # Test input
    user_id = "user1"
    role_id = 1
    
    # Call the service
    result = permissions_service.assign_role(user_id, role_id)
    
    # Verify the result
    assert isinstance(result, UserRole)
    assert result.user_id == user_id
    assert result.role_id == role_id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_check_permission(permissions_service, mock_db):
    # Mock database queries
    mock_role = Mock()
    mock_role.permissions = [Permission.READ, Permission.WRITE]
    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_role
    
    # Test with valid permission
    assert permissions_service.check_permission("user1", Permission.READ) is True
    
    # Test with invalid permission
    assert permissions_service.check_permission("user1", Permission.ADMIN) is False

def test_get_user_permissions(permissions_service, mock_db):
    # Mock database queries
    mock_role = Mock()
    mock_role.permissions = [Permission.READ, Permission.WRITE]
    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_role
    
    # Call the service
    result = permissions_service.get_user_permissions("user1")
    
    # Verify the result
    assert isinstance(result, list)
    assert all(isinstance(p, Permission) for p in result)
    assert set(result) == {Permission.READ, Permission.WRITE}

def test_update_role_permissions(permissions_service, mock_db):
    # Mock database query
    mock_role = Mock()
    mock_role.id = 1
    mock_role.name = "editor"
    mock_role.permissions = [Permission.READ]
    mock_db.query.return_value.filter.return_value.first.return_value = mock_role
    
    # Test input
    new_permissions = [Permission.READ, Permission.WRITE]
    
    # Call the service
    result = permissions_service.update_role_permissions(1, new_permissions)
    
    # Verify the result
    assert isinstance(result, Role)
    assert result.id == 1
    assert set(result.permissions) == set(new_permissions)
    mock_db.commit.assert_called_once()

def test_remove_role(permissions_service, mock_db):
    # Mock database query
    mock_role = Mock()
    mock_role.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_role
    
    # Call the service
    permissions_service.remove_role(1)
    
    # Verify the result
    mock_db.delete.assert_called_once_with(mock_role)
    mock_db.commit.assert_called_once()

def test_get_all_roles(permissions_service, mock_db):
    # Mock database query
    mock_roles = [
        Mock(id=1, name="editor", permissions=[Permission.READ, Permission.WRITE]),
        Mock(id=2, name="viewer", permissions=[Permission.READ])
    ]
    mock_db.query.return_value.all.return_value = mock_roles
    
    # Call the service
    result = permissions_service.get_all_roles()
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(r, Role) for r in result)
    assert {r.name for r in result} == {"editor", "viewer"} 