import pytest
from unittest.mock import Mock, patch
from ..services.chunking import ChunkingService
from ..schemas.chunking import DocumentChunk, ChunkingStrategy

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def chunking_service(mock_db):
    return ChunkingService(mock_db)

def test_create_chunks(chunking_service, mock_db):
    # Test input
    document_id = "doc1"
    content = "This is a test document. It has multiple sentences. Each sentence should be a chunk."
    strategy = ChunkingStrategy.SENTENCE
    
    # Call the service
    result = chunking_service.create_chunks(document_id, content, strategy)
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(chunk, DocumentChunk) for chunk in result)
    assert all(chunk.document_id == document_id for chunk in result)
    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()

def test_create_chunks_with_size(chunking_service, mock_db):
    # Test input
    document_id = "doc1"
    content = "This is a test document that needs to be split into chunks of specific size."
    strategy = ChunkingStrategy.SIZE
    chunk_size = 10
    
    # Call the service
    result = chunking_service.create_chunks(document_id, content, strategy, chunk_size)
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) > 1
    assert all(isinstance(chunk, DocumentChunk) for chunk in result)
    assert all(len(chunk.content) <= chunk_size for chunk in result)
    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()

def test_create_chunks_with_overlap(chunking_service, mock_db):
    # Test input
    document_id = "doc1"
    content = "This is a test document that needs to be split into chunks with overlap."
    strategy = ChunkingStrategy.SIZE
    chunk_size = 10
    overlap = 2
    
    # Call the service
    result = chunking_service.create_chunks(document_id, content, strategy, chunk_size, overlap)
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) > 1
    assert all(isinstance(chunk, DocumentChunk) for chunk in result)
    assert all(chunk.overlap == overlap for chunk in result)
    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()

def test_get_chunks(chunking_service, mock_db):
    # Mock database query
    mock_chunks = [
        Mock(id="chunk1", document_id="doc1", content="First chunk", order=1),
        Mock(id="chunk2", document_id="doc1", content="Second chunk", order=2)
    ]
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_chunks
    
    # Call the service
    result = chunking_service.get_chunks("doc1")
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(chunk, DocumentChunk) for chunk in result)
    assert [chunk.order for chunk in result] == [1, 2]

def test_get_chunk(chunking_service, mock_db):
    # Mock database query
    mock_chunk = Mock(id="chunk1", document_id="doc1", content="Test chunk", order=1)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_chunk
    
    # Call the service
    result = chunking_service.get_chunk("chunk1")
    
    # Verify the result
    assert isinstance(result, DocumentChunk)
    assert result.id == "chunk1"
    assert result.document_id == "doc1"
    assert result.content == "Test chunk"

def test_update_chunk(chunking_service, mock_db):
    # Mock database query
    mock_chunk = Mock(id="chunk1", document_id="doc1", content="Old content", order=1)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_chunk
    
    # Test input
    new_content = "New content"
    
    # Call the service
    result = chunking_service.update_chunk("chunk1", new_content)
    
    # Verify the result
    assert isinstance(result, DocumentChunk)
    assert result.id == "chunk1"
    assert result.content == new_content
    mock_db.commit.assert_called_once()

def test_delete_chunks(chunking_service, mock_db):
    # Mock database query
    mock_chunks = [
        Mock(id="chunk1", document_id="doc1"),
        Mock(id="chunk2", document_id="doc1")
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_chunks
    
    # Call the service
    chunking_service.delete_chunks("doc1")
    
    # Verify the result
    assert mock_db.delete.call_count == 2
    mock_db.commit.assert_called_once()

def test_get_chunk_count(chunking_service, mock_db):
    # Mock database query
    mock_db.query.return_value.filter.return_value.count.return_value = 5
    
    # Call the service
    result = chunking_service.get_chunk_count("doc1")
    
    # Verify the result
    assert result == 5

def test_get_chunk_range(chunking_service, mock_db):
    # Mock database query
    mock_chunks = [
        Mock(id="chunk1", document_id="doc1", content="Chunk 1", order=1),
        Mock(id="chunk2", document_id="doc1", content="Chunk 2", order=2),
        Mock(id="chunk3", document_id="doc1", content="Chunk 3", order=3)
    ]
    mock_db.query.return_value.filter.return_value.order_by.return_value.slice.return_value.all.return_value = mock_chunks
    
    # Call the service
    result = chunking_service.get_chunk_range("doc1", 0, 3)
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(chunk, DocumentChunk) for chunk in result)
    assert [chunk.order for chunk in result] == [1, 2, 3] 