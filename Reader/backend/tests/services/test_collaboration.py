import pytest
from unittest.mock import Mock, patch
from ..services.collaboration import CollaborationService
from ..schemas.collaboration import CollaborationSession, UserPresence

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def collaboration_service(mock_db):
    return CollaborationService(mock_db)

def test_create_session(collaboration_service, mock_db):
    # Test input
    document_id = "doc1"
    user_id = "user1"
    
    # Call the service
    result = collaboration_service.create_session(document_id, user_id)
    
    # Verify the result
    assert isinstance(result, CollaborationSession)
    assert result.document_id == document_id
    assert result.host_id == user_id
    assert len(result.participants) == 1
    assert result.participants[0].user_id == user_id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_join_session(collaboration_service, mock_db):
    # Mock database query
    mock_session = Mock()
    mock_session.id = "session1"
    mock_session.document_id = "doc1"
    mock_session.host_id = "user1"
    mock_session.participants = []
    mock_db.query.return_value.filter.return_value.first.return_value = mock_session
    
    # Test input
    session_id = "session1"
    user_id = "user2"
    
    # Call the service
    result = collaboration_service.join_session(session_id, user_id)
    
    # Verify the result
    assert isinstance(result, CollaborationSession)
    assert result.id == session_id
    assert len(result.participants) == 1
    assert result.participants[0].user_id == user_id
    mock_db.commit.assert_called_once()

def test_leave_session(collaboration_service, mock_db):
    # Mock database query
    mock_session = Mock()
    mock_session.id = "session1"
    mock_session.participants = [Mock(user_id="user1"), Mock(user_id="user2")]
    mock_db.query.return_value.filter.return_value.first.return_value = mock_session
    
    # Test input
    session_id = "session1"
    user_id = "user2"
    
    # Call the service
    result = collaboration_service.leave_session(session_id, user_id)
    
    # Verify the result
    assert isinstance(result, CollaborationSession)
    assert result.id == session_id
    assert len(result.participants) == 1
    assert result.participants[0].user_id == "user1"
    mock_db.commit.assert_called_once()

def test_update_presence(collaboration_service, mock_db):
    # Mock database query
    mock_session = Mock()
    mock_session.id = "session1"
    mock_participant = Mock(user_id="user1")
    mock_session.participants = [mock_participant]
    mock_db.query.return_value.filter.return_value.first.return_value = mock_session
    
    # Test input
    session_id = "session1"
    user_id = "user1"
    status = "typing"
    
    # Call the service
    result = collaboration_service.update_presence(session_id, user_id, status)
    
    # Verify the result
    assert isinstance(result, UserPresence)
    assert result.user_id == user_id
    assert result.status == status
    mock_db.commit.assert_called_once()

def test_get_session(collaboration_service, mock_db):
    # Mock database query
    mock_session = Mock()
    mock_session.id = "session1"
    mock_session.document_id = "doc1"
    mock_session.host_id = "user1"
    mock_session.participants = [Mock(user_id="user1")]
    mock_db.query.return_value.filter.return_value.first.return_value = mock_session
    
    # Call the service
    result = collaboration_service.get_session("session1")
    
    # Verify the result
    assert isinstance(result, CollaborationSession)
    assert result.id == "session1"
    assert result.document_id == "doc1"
    assert result.host_id == "user1"
    assert len(result.participants) == 1

def test_end_session(collaboration_service, mock_db):
    # Mock database query
    mock_session = Mock()
    mock_session.id = "session1"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_session
    
    # Call the service
    collaboration_service.end_session("session1")
    
    # Verify the result
    mock_db.delete.assert_called_once_with(mock_session)
    mock_db.commit.assert_called_once()

def test_get_active_sessions(collaboration_service, mock_db):
    # Mock database query
    mock_sessions = [
        Mock(id="session1", document_id="doc1", host_id="user1", participants=[]),
        Mock(id="session2", document_id="doc2", host_id="user2", participants=[])
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_sessions
    
    # Call the service
    result = collaboration_service.get_active_sessions("doc1")
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(s, CollaborationSession) for s in result)
    assert {s.id for s in result} == {"session1", "session2"}

def test_get_user_sessions(collaboration_service, mock_db):
    # Mock database query
    mock_sessions = [
        Mock(id="session1", document_id="doc1", host_id="user1", participants=[]),
        Mock(id="session2", document_id="doc2", host_id="user1", participants=[])
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_sessions
    
    # Call the service
    result = collaboration_service.get_user_sessions("user1")
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(s, CollaborationSession) for s in result)
    assert all(s.host_id == "user1" for s in result) 