import pytest
from unittest.mock import Mock, patch
from ..services.version import VersionService
from ..schemas.version import VersionCreate, VersionResponse, VersionDiff

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def version_service(mock_db):
    return VersionService(mock_db)

def test_create_version(version_service, mock_db):
    # Mock database query
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    
    # Test input
    document_id = "doc1"
    version = VersionCreate(content="Test content", metadata={"key": "value"})
    user_id = "user1"
    
    # Call the service
    result = version_service.create_version(document_id, version, user_id)
    
    # Verify the result
    assert isinstance(result, VersionResponse)
    assert result.document_id == document_id
    assert result.version_number == 1
    assert result.content == "Test content"
    assert result.metadata == {"key": "value"}
    assert result.created_by == user_id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_create_version_with_existing(version_service, mock_db):
    # Mock database query
    mock_version = Mock(version_number=2)
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_version
    
    # Test input
    document_id = "doc1"
    version = VersionCreate(content="Test content")
    user_id = "user1"
    
    # Call the service
    result = version_service.create_version(document_id, version, user_id)
    
    # Verify the result
    assert isinstance(result, VersionResponse)
    assert result.version_number == 3

def test_get_versions(version_service, mock_db):
    # Mock database query
    mock_versions = [
        Mock(id="v1", document_id="doc1", version_number=1, content="Content 1"),
        Mock(id="v2", document_id="doc1", version_number=2, content="Content 2")
    ]
    mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_versions
    
    # Call the service
    result = version_service.get_versions("doc1", skip=0, limit=10)
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(v, VersionResponse) for v in result)
    assert [v.version_number for v in result] == [1, 2]

def test_get_version(version_service, mock_db):
    # Mock database query
    mock_version = Mock(id="v1", document_id="doc1", version_number=1, content="Test content")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_version
    
    # Call the service
    result = version_service.get_version("doc1", "v1")
    
    # Verify the result
    assert isinstance(result, VersionResponse)
    assert result.id == "v1"
    assert result.document_id == "doc1"
    assert result.version_number == 1
    assert result.content == "Test content"

def test_restore_version(version_service, mock_db):
    # Mock database queries
    mock_version = Mock(id="v1", document_id="doc1", version_number=1, content="Old content")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_version
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = Mock(version_number=3)
    
    # Call the service
    result = version_service.restore_version("doc1", "v1")
    
    # Verify the result
    assert isinstance(result, VersionResponse)
    assert result.version_number == 4
    assert result.content == "Old content"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_compare_versions(version_service, mock_db):
    # Mock database queries
    mock_version1 = Mock(content="This is version 1")
    mock_version2 = Mock(content="This is version 2")
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_version1, mock_version2]
    
    # Call the service
    result = version_service.compare_versions("doc1", "v1", "v2")
    
    # Verify the result
    assert isinstance(result, VersionDiff)
    assert result.version1_id == "v1"
    assert result.version2_id == "v2"
    assert "diff" in result.diff
    assert len(result.changes) > 0

def test_get_version_count(version_service, mock_db):
    # Mock database query
    mock_db.query.return_value.filter.return_value.count.return_value = 5
    
    # Call the service
    result = version_service.get_version_count("doc1")
    
    # Verify the result
    assert result == 5

def test_delete_version(version_service, mock_db):
    # Mock database query
    mock_version = Mock(id="v1")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_version
    
    # Call the service
    version_service.delete_version("doc1", "v1")
    
    # Verify the result
    mock_db.delete.assert_called_once_with(mock_version)
    mock_db.commit.assert_called_once()

def test_get_latest_version(version_service, mock_db):
    # Mock database query
    mock_version = Mock(id="v3", document_id="doc1", version_number=3, content="Latest content")
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_version
    
    # Call the service
    result = version_service.get_latest_version("doc1")
    
    # Verify the result
    assert isinstance(result, VersionResponse)
    assert result.id == "v3"
    assert result.version_number == 3
    assert result.content == "Latest content" 