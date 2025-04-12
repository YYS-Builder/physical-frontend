import pytest
from unittest.mock import Mock, patch
from ..services.classification import ClassificationService
from ..schemas.classification import DocumentCategory, CategoryConfidence

@pytest.fixture
def mock_model():
    with patch('transformers.pipeline') as mock_pipeline:
        mock_model = Mock()
        mock_pipeline.return_value = mock_model
        yield mock_model

@pytest.fixture
def classification_service(mock_model):
    return ClassificationService()

def test_classify_document(classification_service, mock_model):
    # Mock the model prediction
    mock_model.return_value = [{
        'label': 'business',
        'score': 0.9
    }]

    # Test input
    text = "This is a business document about market analysis."
    
    # Call the service
    result = classification_service.classify_document(text)
    
    # Verify the result
    assert isinstance(result, DocumentCategory)
    assert result.category == "business"
    assert result.confidence > 0.8
    assert len(result.subcategories) == 0
    assert len(result.tags) == 0

def test_classify_document_with_subcategories(classification_service, mock_model):
    # Mock the model prediction
    mock_model.return_value = [{
        'label': 'business',
        'score': 0.9
    }]

    # Test input with subcategories
    text = "This is a business document about market analysis."
    subcategories = ["finance", "marketing"]
    
    # Call the service
    result = classification_service.classify_document(text, subcategories)
    
    # Verify the result
    assert isinstance(result, DocumentCategory)
    assert result.category == "business"
    assert len(result.subcategories) == 2
    assert "finance" in result.subcategories
    assert "marketing" in result.subcategories

def test_classify_document_with_tags(classification_service, mock_model):
    # Mock the model prediction
    mock_model.return_value = [{
        'label': 'business',
        'score': 0.9
    }]

    # Test input with tags
    text = "This is a business document about market analysis."
    tags = ["market", "analysis", "report"]
    
    # Call the service
    result = classification_service.classify_document(text, tags=tags)
    
    # Verify the result
    assert isinstance(result, DocumentCategory)
    assert result.category == "business"
    assert len(result.tags) == 3
    assert all(tag in result.tags for tag in tags)

def test_classify_document_error_handling(classification_service, mock_model):
    # Mock an error in model prediction
    mock_model.side_effect = Exception("Model prediction error")
    
    # Test input
    text = "This is a test document."
    
    # Call the service and expect an error
    with pytest.raises(Exception) as exc_info:
        classification_service.classify_document(text)
    
    assert "Error classifying document" in str(exc_info.value)

def test_get_category_confidence(classification_service):
    # Test high confidence
    confidence = classification_service._get_category_confidence(0.9)
    assert confidence > 0.8
    
    # Test medium confidence
    confidence = classification_service._get_category_confidence(0.6)
    assert 0.5 < confidence < 0.7
    
    # Test low confidence
    confidence = classification_service._get_category_confidence(0.3)
    assert confidence < 0.4

def test_validate_subcategories(classification_service):
    # Test valid subcategories
    subcategories = ["finance", "marketing"]
    assert classification_service._validate_subcategories(subcategories) == subcategories
    
    # Test invalid subcategories
    subcategories = ["invalid", "finance"]
    assert classification_service._validate_subcategories(subcategories) == ["finance"]
    
    # Test empty subcategories
    assert classification_service._validate_subcategories([]) == []

def test_validate_tags(classification_service):
    # Test valid tags
    tags = ["market", "analysis", "report"]
    assert classification_service._validate_tags(tags) == tags
    
    # Test invalid tags
    tags = ["invalid", "market"]
    assert classification_service._validate_tags(tags) == ["market"]
    
    # Test empty tags
    assert classification_service._validate_tags([]) == [] 