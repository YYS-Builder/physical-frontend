import pytest
from unittest.mock import Mock, patch
from ..services.sentiment import SentimentService
from ..schemas.sentiment import SentimentAnalysis, SentimentScore

@pytest.fixture
def mock_nlp():
    with patch('spacy.load') as mock_load:
        mock_nlp = Mock()
        mock_nlp.return_value = mock_nlp
        mock_load.return_value = mock_nlp
        yield mock_nlp

@pytest.fixture
def sentiment_service(mock_nlp):
    return SentimentService()

def test_analyze_sentiment(sentiment_service, mock_nlp):
    # Mock the NLP processing
    mock_doc = Mock()
    mock_doc._.sentiment = {'pos': 0.7, 'neg': 0.1, 'neu': 0.2}
    mock_nlp.return_value = mock_doc

    # Test input
    text = "This is a positive test sentence."
    
    # Call the service
    result = sentiment_service.analyze_sentiment(text)
    
    # Verify the result
    assert isinstance(result, SentimentAnalysis)
    assert result.overall_sentiment == "positive"
    assert result.confidence > 0.5
    assert len(result.sentences) > 0
    assert all(isinstance(s.score, SentimentScore) for s in result.sentences)

def test_analyze_sentiment_with_language(sentiment_service, mock_nlp):
    # Mock the NLP processing
    mock_doc = Mock()
    mock_doc._.sentiment = {'pos': 0.6, 'neg': 0.2, 'neu': 0.2}
    mock_nlp.return_value = mock_doc

    # Test input with language
    text = "Ceci est une phrase positive."
    language = "fr"
    
    # Call the service
    result = sentiment_service.analyze_sentiment(text, language)
    
    # Verify the result
    assert isinstance(result, SentimentAnalysis)
    assert result.overall_sentiment in ["positive", "negative", "neutral"]
    assert result.language == language

def test_analyze_sentiment_error_handling(sentiment_service, mock_nlp):
    # Mock an error in NLP processing
    mock_nlp.side_effect = Exception("NLP processing error")
    
    # Test input
    text = "This is a test sentence."
    
    # Call the service and expect an error
    with pytest.raises(Exception) as exc_info:
        sentiment_service.analyze_sentiment(text)
    
    assert "Error analyzing sentiment" in str(exc_info.value)

def test_get_sentiment_label(sentiment_service):
    # Test positive sentiment
    score = SentimentScore(positive=0.7, negative=0.1, neutral=0.2)
    label = sentiment_service._get_sentiment_label(score)
    assert label == "positive"
    
    # Test negative sentiment
    score = SentimentScore(positive=0.1, negative=0.7, neutral=0.2)
    label = sentiment_service._get_sentiment_label(score)
    assert label == "negative"
    
    # Test neutral sentiment
    score = SentimentScore(positive=0.3, negative=0.3, neutral=0.4)
    label = sentiment_service._get_sentiment_label(score)
    assert label == "neutral"

def test_calculate_confidence(sentiment_service):
    # Test high confidence
    score = SentimentScore(positive=0.8, negative=0.1, neutral=0.1)
    confidence = sentiment_service._calculate_confidence(score)
    assert confidence > 0.7
    
    # Test low confidence
    score = SentimentScore(positive=0.4, negative=0.3, neutral=0.3)
    confidence = sentiment_service._calculate_confidence(score)
    assert confidence < 0.5 