from typing import Dict, List, Optional
from pydantic import BaseModel
from transformers import pipeline
from app.core.config import settings
from app.models.document import Document
from app.services.base import BaseService

class SentimentResult(BaseModel):
    label: str
    score: float
    sentiment: str
    confidence: float

class SentimentAnalysisService(BaseService):
    def __init__(self):
        self.model = pipeline(
            "sentiment-analysis",
            model=settings.SENTIMENT_MODEL_NAME,
            device=settings.DEVICE
        )
        
    async def analyze_document(self, document: Document) -> SentimentResult:
        """Analyze the sentiment of a document."""
        try:
            # Extract text from document
            text = await self._extract_text(document)
            
            # Analyze sentiment
            result = self.model(text)[0]
            
            # Map to our result format
            return SentimentResult(
                label=result['label'],
                score=result['score'],
                sentiment=self._map_sentiment(result['label']),
                confidence=result['score']
            )
        except Exception as e:
            raise Exception(f"Failed to analyze document sentiment: {str(e)}")
    
    async def analyze_batch(self, documents: List[Document]) -> Dict[str, SentimentResult]:
        """Analyze sentiment for multiple documents."""
        results = {}
        for doc in documents:
            results[doc.id] = await self.analyze_document(doc)
        return results
    
    def _map_sentiment(self, label: str) -> str:
        """Map model labels to standardized sentiment values."""
        sentiment_map = {
            "POSITIVE": "positive",
            "NEGATIVE": "negative",
            "NEUTRAL": "neutral"
        }
        return sentiment_map.get(label.upper(), "neutral")
    
    async def _extract_text(self, document: Document) -> str:
        """Extract text content from document."""
        # TODO: Implement text extraction based on document type
        # This is a placeholder implementation
        return "Sample text content" 