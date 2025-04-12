import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..services.entity import EntityService
from ..schemas.entity import Entity, EntityType

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

def test_extract_entities_endpoint(client):
    # Test data
    test_data = {
        "text": "John Doe works at Acme Corp in New York.",
        "language": "en"
    }
    
    # Make request
    response = client.post("/api/entities/extract", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) > 0
    assert all("text" in entity for entity in result)
    assert all("type" in entity for entity in result)
    assert all("start" in entity for entity in result)
    assert all("end" in entity for entity in result)

def test_extract_entities_with_language(client):
    # Test data with French text
    test_data = {
        "text": "Jean Dupont travaille à Paris pour Google.",
        "language": "fr"
    }
    
    # Make request
    response = client.post("/api/entities/extract", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert len(result) > 0
    assert any(entity["type"] == EntityType.PERSON for entity in result)
    assert any(entity["type"] == EntityType.LOCATION for entity in result)
    assert any(entity["type"] == EntityType.ORGANIZATION for entity in result)

def test_extract_entities_batch_endpoint(client):
    # Test data with multiple texts
    test_data = {
        "texts": [
            "John Doe works at Acme Corp.",
            "Paris is the capital of France.",
            "Apple released a new iPhone."
        ],
        "language": "en"
    }
    
    # Make request
    response = client.post("/api/entities/extract/batch", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    assert all(isinstance(r, list) for r in results)
    assert all(len(r) > 0 for r in results)

def test_extract_entities_error_handling(client):
    # Test data with invalid input
    test_data = {
        "text": "",
        "language": "en"
    }
    
    # Make request
    response = client.post("/api/entities/extract", json=test_data)
    
    # Verify error response
    assert response.status_code == 400
    assert "error" in response.json()

def test_extract_entities_with_service(db_session):
    # Initialize service
    service = EntityService()
    
    # Test data
    text = "John Doe works at Acme Corp in New York."
    
    # Call service directly
    result = service.extract_entities(text)
    
    # Verify result
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(entity, Entity) for entity in result)
    assert any(entity.type == EntityType.PERSON for entity in result)
    assert any(entity.type == EntityType.ORGANIZATION for entity in result)
    assert any(entity.type == EntityType.LOCATION for entity in result)

def test_extract_entities_batch_with_service(db_session):
    # Initialize service
    service = EntityService()
    
    # Test data
    texts = [
        "John Doe works at Acme Corp.",
        "Paris is the capital of France.",
        "Apple released a new iPhone."
    ]
    
    # Call service directly
    results = service.extract_entities_batch(texts)
    
    # Verify results
    assert len(results) == 3
    assert all(isinstance(r, list) for r in results)
    assert all(len(r) > 0 for r in results)
    assert all(isinstance(entity, Entity) for r in results for entity in r) 