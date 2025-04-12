from typing import Dict, List, Optional
from pydantic import BaseModel
from transformers import pipeline
from app.core.config import settings
from app.models.document import Document
from app.services.base import BaseService

class Entity(BaseModel):
    text: str
    type: str
    start: int
    end: int
    confidence: float

class EntityExtractionResult(BaseModel):
    entities: List[Entity]
    summary: Dict[str, int]

class EntityExtractionService(BaseService):
    def __init__(self):
        self.model = pipeline(
            "ner",
            model=settings.ENTITY_MODEL_NAME,
            device=settings.DEVICE,
            aggregation_strategy="simple"
        )
        
    async def extract_entities(self, document: Document) -> EntityExtractionResult:
        """Extract entities from a document."""
        try:
            # Extract text from document
            text = await self._extract_text(document)
            
            # Extract entities
            raw_entities = self.model(text)
            
            # Process and format entities
            entities = [
                Entity(
                    text=entity['word'],
                    type=entity['entity_group'],
                    start=entity['start'],
                    end=entity['end'],
                    confidence=entity['score']
                )
                for entity in raw_entities
            ]
            
            # Create summary
            summary = self._create_summary(entities)
            
            return EntityExtractionResult(
                entities=entities,
                summary=summary
            )
        except Exception as e:
            raise Exception(f"Failed to extract entities: {str(e)}")
    
    async def extract_batch(self, documents: List[Document]) -> Dict[str, EntityExtractionResult]:
        """Extract entities from multiple documents."""
        results = {}
        for doc in documents:
            results[doc.id] = await self.extract_entities(doc)
        return results
    
    def _create_summary(self, entities: List[Entity]) -> Dict[str, int]:
        """Create a summary of entity types and counts."""
        summary = {}
        for entity in entities:
            summary[entity.type] = summary.get(entity.type, 0) + 1
        return summary
    
    async def _extract_text(self, document: Document) -> str:
        """Extract text content from document."""
        # TODO: Implement text extraction based on document type
        # This is a placeholder implementation
        return "Sample text content" 