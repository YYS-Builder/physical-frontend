import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..services.chunking import ChunkingService
from ..schemas.chunking import DocumentChunk, ChunkingStrategy

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

def test_create_chunks_endpoint(client):
    # Test data
    test_data = {
        "document_id": "doc1",
        "content": "This is a test document. It has multiple sentences. Each sentence should be a chunk.",
        "strategy": "sentence"
    }
    
    # Make request
    response = client.post("/api/chunking/chunks", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 3
    assert all("id" in chunk for chunk in result)
    assert all("document_id" in chunk for chunk in result)
    assert all("content" in chunk for chunk in result)
    assert all("order" in chunk for chunk in result)

def test_create_chunks_with_size_endpoint(client):
    # Test data
    test_data = {
        "document_id": "doc1",
        "content": "This is a test document that needs to be split into chunks of specific size.",
        "strategy": "size",
        "chunk_size": 10
    }
    
    # Make request
    response = client.post("/api/chunking/chunks", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) > 1
    assert all(len(chunk["content"]) <= 10 for chunk in result)

def test_create_chunks_with_overlap_endpoint(client):
    # Test data
    test_data = {
        "document_id": "doc1",
        "content": "This is a test document that needs to be split into chunks with overlap.",
        "strategy": "size",
        "chunk_size": 10,
        "overlap": 2
    }
    
    # Make request
    response = client.post("/api/chunking/chunks", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) > 1
    assert all(chunk["overlap"] == 2 for chunk in result)

def test_get_chunks_endpoint(client):
    # First create chunks
    chunk_data = {
        "document_id": "doc1",
        "content": "First chunk. Second chunk. Third chunk.",
        "strategy": "sentence"
    }
    client.post("/api/chunking/chunks", json=chunk_data)
    
    # Get chunks
    response = client.get("/api/chunking/chunks/doc1")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(chunk["document_id"] == "doc1" for chunk in result)
    assert [chunk["order"] for chunk in result] == [1, 2, 3]

def test_get_chunk_endpoint(client):
    # First create chunks
    chunk_data = {
        "document_id": "doc1",
        "content": "Test chunk",
        "strategy": "sentence"
    }
    create_response = client.post("/api/chunking/chunks", json=chunk_data)
    chunk_id = create_response.json()[0]["id"]
    
    # Get chunk
    response = client.get(f"/api/chunking/chunks/{chunk_id}")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == chunk_id
    assert result["document_id"] == "doc1"
    assert result["content"] == "Test chunk"

def test_update_chunk_endpoint(client):
    # First create chunks
    chunk_data = {
        "document_id": "doc1",
        "content": "Old content",
        "strategy": "sentence"
    }
    create_response = client.post("/api/chunking/chunks", json=chunk_data)
    chunk_id = create_response.json()[0]["id"]
    
    # Update chunk
    update_data = {
        "content": "New content"
    }
    response = client.put(f"/api/chunking/chunks/{chunk_id}", json=update_data)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == chunk_id
    assert result["content"] == "New content"

def test_delete_chunks_endpoint(client):
    # First create chunks
    chunk_data = {
        "document_id": "doc1",
        "content": "First chunk. Second chunk.",
        "strategy": "sentence"
    }
    client.post("/api/chunking/chunks", json=chunk_data)
    
    # Delete chunks
    response = client.delete("/api/chunking/chunks/doc1")
    
    # Verify response
    assert response.status_code == 200
    
    # Verify chunks are deleted
    get_response = client.get("/api/chunking/chunks/doc1")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

def test_get_chunk_count_endpoint(client):
    # First create chunks
    chunk_data = {
        "document_id": "doc1",
        "content": "First chunk. Second chunk. Third chunk.",
        "strategy": "sentence"
    }
    client.post("/api/chunking/chunks", json=chunk_data)
    
    # Get chunk count
    response = client.get("/api/chunking/chunks/doc1/count")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["count"] == 3

def test_get_chunk_range_endpoint(client):
    # First create chunks
    chunk_data = {
        "document_id": "doc1",
        "content": "First chunk. Second chunk. Third chunk. Fourth chunk.",
        "strategy": "sentence"
    }
    client.post("/api/chunking/chunks", json=chunk_data)
    
    # Get chunk range
    response = client.get("/api/chunking/chunks/doc1/range?start=1&end=3")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 3
    assert [chunk["order"] for chunk in result] == [1, 2, 3]

def test_chunking_with_service(db_session):
    # Initialize service
    service = ChunkingService(db_session)
    
    # Create chunks
    chunks = service.create_chunks("doc1", "First chunk. Second chunk.", ChunkingStrategy.SENTENCE)
    assert isinstance(chunks, list)
    assert len(chunks) == 2
    assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
    assert all(chunk.document_id == "doc1" for chunk in chunks)
    
    # Get chunks
    retrieved_chunks = service.get_chunks("doc1")
    assert len(retrieved_chunks) == 2
    assert [chunk.order for chunk in retrieved_chunks] == [1, 2]
    
    # Update chunk
    updated_chunk = service.update_chunk(chunks[0].id, "Updated content")
    assert updated_chunk.content == "Updated content"
    
    # Get chunk count
    count = service.get_chunk_count("doc1")
    assert count == 2
    
    # Delete chunks
    service.delete_chunks("doc1")
    assert service.get_chunk_count("doc1") == 0 