import pytest
from unittest.mock import Mock, patch
from ..services.entity import EntityService
from ..schemas.entity import Entity, EntityType

@pytest.fixture
def mock_nlp():
    with patch('spacy.load') as mock_load:
        mock_nlp = Mock()
        mock_nlp.return_value = mock_nlp
        mock_load.return_value = mock_nlp
        yield mock_nlp

@pytest.fixture
def entity_service(mock_nlp):
    return EntityService()

def test_extract_entities(entity_service, mock_nlp):
    # Mock the NLP processing
    mock_ent = Mock()
    mock_ent.text = "John Doe"
    mock_ent.label_ = "PERSON"
    mock_ent.start_char = 0
    mock_ent.end_char = 8
    
    mock_doc = Mock()
    mock_doc.ents = [mock_ent]
    mock_nlp.return_value = mock_doc

    # Test input
    text = "John Doe works at Acme Corp."
    
    # Call the service
    result = entity_service.extract_entities(text)
    
    # Verify the result
    assert len(result) == 1
    entity = result[0]
    assert isinstance(entity, Entity)
    assert entity.text == "John Doe"
    assert entity.type == EntityType.PERSON
    assert entity.start == 0
    assert entity.end == 8
    assert entity.confidence > 0.5

def test_extract_entities_with_language(entity_service, mock_nlp):
    # Mock the NLP processing
    mock_ent = Mock()
    mock_ent.text = "Paris"
    mock_ent.label_ = "GPE"
    mock_ent.start_char = 0
    mock_ent.end_char = 5
    
    mock_doc = Mock()
    mock_doc.ents = [mock_ent]
    mock_nlp.return_value = mock_doc

    # Test input with language
    text = "Paris est la capitale de la France."
    language = "fr"
    
    # Call the service
    result = entity_service.extract_entities(text, language)
    
    # Verify the result
    assert len(result) == 1
    entity = result[0]
    assert entity.text == "Paris"
    assert entity.type == EntityType.LOCATION
    assert entity.language == language

def test_extract_entities_error_handling(entity_service, mock_nlp):
    # Mock an error in NLP processing
    mock_nlp.side_effect = Exception("NLP processing error")
    
    # Test input
    text = "This is a test sentence."
    
    # Call the service and expect an error
    with pytest.raises(Exception) as exc_info:
        entity_service.extract_entities(text)
    
    assert "Error extracting entities" in str(exc_info.value)

def test_get_entity_type(entity_service):
    # Test PERSON type
    assert entity_service._get_entity_type("PERSON") == EntityType.PERSON
    
    # Test ORG type
    assert entity_service._get_entity_type("ORG") == EntityType.ORGANIZATION
    
    # Test GPE type
    assert entity_service._get_entity_type("GPE") == EntityType.LOCATION
    
    # Test DATE type
    assert entity_service._get_entity_type("DATE") == EntityType.DATE
    
    # Test default type
    assert entity_service._get_entity_type("UNKNOWN") == EntityType.OTHER

def test_calculate_confidence(entity_service):
    # Test high confidence
    confidence = entity_service._calculate_confidence(0.9)
    assert confidence > 0.8
    
    # Test low confidence
    confidence = entity_service._calculate_confidence(0.4)
    assert confidence < 0.5 