import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..services.version import VersionService
from ..schemas.version import VersionCreate, VersionResponse, VersionDiff

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

def test_create_version_endpoint(client):
    # Test data
    test_data = {
        "content": "Initial version content",
        "metadata": {"key": "value"}
    }
    
    # Make request
    response = client.post("/api/versions/doc1", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    assert result["document_id"] == "doc1"
    assert result["version_number"] == 1
    assert result["content"] == "Initial version content"
    assert result["metadata"] == {"key": "value"}

def test_get_versions_endpoint(client):
    # First create some versions
    versions_data = [
        {"content": "Version 1 content"},
        {"content": "Version 2 content"},
        {"content": "Version 3 content"}
    ]
    for version_data in versions_data:
        client.post("/api/versions/doc1", json=version_data)
    
    # Get versions
    response = client.get("/api/versions/doc1")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 3
    assert [v["version_number"] for v in result] == [1, 2, 3]

def test_get_version_endpoint(client):
    # First create a version
    version_data = {"content": "Test version content"}
    create_response = client.post("/api/versions/doc1", json=version_data)
    version_id = create_response.json()["id"]
    
    # Get version
    response = client.get(f"/api/versions/doc1/{version_id}")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == version_id
    assert result["document_id"] == "doc1"
    assert result["version_number"] == 1
    assert result["content"] == "Test version content"

def test_restore_version_endpoint(client):
    # First create a version
    version_data = {"content": "Old version content"}
    create_response = client.post("/api/versions/doc1", json=version_data)
    version_id = create_response.json()["id"]
    
    # Restore version
    response = client.post(f"/api/versions/doc1/{version_id}/restore")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["version_number"] == 2
    assert result["content"] == "Old version content"

def test_compare_versions_endpoint(client):
    # First create two versions
    version1_data = {"content": "First version content"}
    version2_data = {"content": "Second version content"}
    version1_response = client.post("/api/versions/doc1", json=version1_data)
    version2_response = client.post("/api/versions/doc1", json=version2_data)
    version1_id = version1_response.json()["id"]
    version2_id = version2_response.json()["id"]
    
    # Compare versions
    response = client.get(f"/api/versions/doc1/compare?version1_id={version1_id}&version2_id={version2_id}")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["version1_id"] == version1_id
    assert result["version2_id"] == version2_id
    assert "diff" in result
    assert len(result["changes"]) > 0

def test_get_version_count_endpoint(client):
    # First create some versions
    versions_data = [
        {"content": "Version 1 content"},
        {"content": "Version 2 content"},
        {"content": "Version 3 content"}
    ]
    for version_data in versions_data:
        client.post("/api/versions/doc1", json=version_data)
    
    # Get version count
    response = client.get("/api/versions/doc1/count")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["count"] == 3

def test_delete_version_endpoint(client):
    # First create a version
    version_data = {"content": "Test version content"}
    create_response = client.post("/api/versions/doc1", json=version_data)
    version_id = create_response.json()["id"]
    
    # Delete version
    response = client.delete(f"/api/versions/doc1/{version_id}")
    
    # Verify response
    assert response.status_code == 200
    
    # Verify version is deleted
    get_response = client.get(f"/api/versions/doc1/{version_id}")
    assert get_response.status_code == 404

def test_get_latest_version_endpoint(client):
    # First create some versions
    versions_data = [
        {"content": "Version 1 content"},
        {"content": "Version 2 content"},
        {"content": "Version 3 content"}
    ]
    for version_data in versions_data:
        client.post("/api/versions/doc1", json=version_data)
    
    # Get latest version
    response = client.get("/api/versions/doc1/latest")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["version_number"] == 3
    assert result["content"] == "Version 3 content"

def test_versioning_with_service(db_session):
    # Initialize service
    service = VersionService(db_session)
    
    # Create version
    version = service.create_version("doc1", VersionCreate(content="Test content"), "user1")
    assert isinstance(version, VersionResponse)
    assert version.document_id == "doc1"
    assert version.version_number == 1
    assert version.content == "Test content"
    
    # Get versions
    versions = service.get_versions("doc1")
    assert len(versions) == 1
    assert versions[0].version_number == 1
    
    # Get version
    retrieved_version = service.get_version("doc1", version.id)
    assert retrieved_version.id == version.id
    assert retrieved_version.content == "Test content"
    
    # Restore version
    restored_version = service.restore_version("doc1", version.id)
    assert restored_version.version_number == 2
    assert restored_version.content == "Test content"
    
    # Compare versions
    diff = service.compare_versions("doc1", version.id, restored_version.id)
    assert isinstance(diff, VersionDiff)
    assert diff.version1_id == version.id
    assert diff.version2_id == restored_version.id
    
    # Get version count
    count = service.get_version_count("doc1")
    assert count == 2
    
    # Delete version
    service.delete_version("doc1", version.id)
    assert service.get_version("doc1", version.id) is None
    
    # Get latest version
    latest = service.get_latest_version("doc1")
    assert latest.version_number == 2 