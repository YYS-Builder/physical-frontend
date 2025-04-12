import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..services.classification import ClassificationService
from ..schemas.classification import DocumentCategory

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

def test_classify_document_endpoint(client):
    # Test data
    test_data = {
        "text": "This is a business document about market analysis and financial projections.",
        "subcategories": ["finance", "marketing"],
        "tags": ["market", "analysis", "report"]
    }
    
    # Make request
    response = client.post("/api/classification/classify", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert "category" in result
    assert "confidence" in result
    assert "subcategories" in result
    assert "tags" in result
    assert result["category"] in ["business", "technical", "legal", "other"]
    assert 0 <= result["confidence"] <= 1
    assert len(result["subcategories"]) > 0
    assert len(result["tags"]) > 0

def test_classify_document_with_subcategories(client):
    # Test data with specific subcategories
    test_data = {
        "text": "This is a technical document about software development.",
        "subcategories": ["programming", "devops"],
        "tags": ["code", "development"]
    }
    
    # Make request
    response = client.post("/api/classification/classify", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["category"] == "technical"
    assert "programming" in result["subcategories"]
    assert "devops" in result["subcategories"]

def test_classify_document_batch_endpoint(client):
    # Test data with multiple documents
    test_data = {
        "documents": [
            {
                "text": "This is a business document.",
                "subcategories": ["finance"],
                "tags": ["report"]
            },
            {
                "text": "This is a technical document.",
                "subcategories": ["programming"],
                "tags": ["code"]
            }
        ]
    }
    
    # Make request
    response = client.post("/api/classification/classify/batch", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert all("category" in r for r in results)
    assert all("confidence" in r for r in results)
    assert all("subcategories" in r for r in results)
    assert all("tags" in r for r in results)

def test_classify_document_error_handling(client):
    # Test data with invalid input
    test_data = {
        "text": "",
        "subcategories": [],
        "tags": []
    }
    
    # Make request
    response = client.post("/api/classification/classify", json=test_data)
    
    # Verify error response
    assert response.status_code == 400
    assert "error" in response.json()

def test_classify_document_with_service(db_session):
    # Initialize service
    service = ClassificationService()
    
    # Test data
    text = "This is a business document about market analysis."
    subcategories = ["finance", "marketing"]
    tags = ["market", "analysis", "report"]
    
    # Call service directly
    result = service.classify_document(text, subcategories, tags)
    
    # Verify result
    assert isinstance(result, DocumentCategory)
    assert result.category in ["business", "technical", "legal", "other"]
    assert 0 <= result.confidence <= 1
    assert len(result.subcategories) > 0
    assert len(result.tags) > 0
    assert all(sc in result.subcategories for sc in subcategories)
    assert all(tag in result.tags for tag in tags)

def test_classify_document_batch_with_service(db_session):
    # Initialize service
    service = ClassificationService()
    
    # Test data
    documents = [
        {
            "text": "This is a business document.",
            "subcategories": ["finance"],
            "tags": ["report"]
        },
        {
            "text": "This is a technical document.",
            "subcategories": ["programming"],
            "tags": ["code"]
        }
    ]
    
    # Call service directly
    results = service.classify_document_batch(documents)
    
    # Verify results
    assert len(results) == 2
    assert all(isinstance(r, DocumentCategory) for r in results)
    assert all(r.category in ["business", "technical", "legal", "other"] for r in results)
    assert all(0 <= r.confidence <= 1 for r in results)
    assert all(len(r.subcategories) > 0 for r in results)
    assert all(len(r.tags) > 0 for r in results) 