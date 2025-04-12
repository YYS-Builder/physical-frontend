import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..services.sentiment import SentimentService
from ..schemas.sentiment import SentimentAnalysis

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

def test_analyze_sentiment_endpoint(client):
    # Test data
    test_data = {
        "text": "This is a positive test sentence.",
        "language": "en"
    }
    
    # Make request
    response = client.post("/api/sentiment/analyze", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert "overall_sentiment" in result
    assert "confidence" in result
    assert "sentences" in result
    assert result["overall_sentiment"] in ["positive", "negative", "neutral"]
    assert 0 <= result["confidence"] <= 1
    assert len(result["sentences"]) > 0

def test_analyze_sentiment_with_language(client):
    # Test data with French text
    test_data = {
        "text": "Ceci est une phrase positive.",
        "language": "fr"
    }
    
    # Make request
    response = client.post("/api/sentiment/analyze", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["language"] == "fr"
    assert result["overall_sentiment"] in ["positive", "negative", "neutral"]

def test_analyze_sentiment_batch_endpoint(client):
    # Test data with multiple texts
    test_data = {
        "texts": [
            "This is a positive sentence.",
            "This is a negative sentence.",
            "This is a neutral sentence."
        ],
        "language": "en"
    }
    
    # Make request
    response = client.post("/api/sentiment/analyze/batch", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    assert all("overall_sentiment" in r for r in results)
    assert all("confidence" in r for r in results)

def test_analyze_sentiment_error_handling(client):
    # Test data with invalid input
    test_data = {
        "text": "",
        "language": "en"
    }
    
    # Make request
    response = client.post("/api/sentiment/analyze", json=test_data)
    
    # Verify error response
    assert response.status_code == 400
    assert "error" in response.json()

def test_analyze_sentiment_with_service(db_session):
    # Initialize service
    service = SentimentService()
    
    # Test data
    text = "This is a positive test sentence."
    
    # Call service directly
    result = service.analyze_sentiment(text)
    
    # Verify result
    assert isinstance(result, SentimentAnalysis)
    assert result.overall_sentiment in ["positive", "negative", "neutral"]
    assert 0 <= result.confidence <= 1
    assert len(result.sentences) > 0

def test_analyze_sentiment_batch_with_service(db_session):
    # Initialize service
    service = SentimentService()
    
    # Test data
    texts = [
        "This is a positive sentence.",
        "This is a negative sentence.",
        "This is a neutral sentence."
    ]
    
    # Call service directly
    results = service.analyze_sentiment_batch(texts)
    
    # Verify results
    assert len(results) == 3
    assert all(isinstance(r, SentimentAnalysis) for r in results)
    assert all(r.overall_sentiment in ["positive", "negative", "neutral"] for r in results) 