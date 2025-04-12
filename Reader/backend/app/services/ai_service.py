from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from app.models.document import Document
from app.core.config import settings

class AIService(ABC):
    """Abstract base class for AI services."""
    
    @abstractmethod
    async def summarize_document(self, document: Document, max_length: int = 500) -> str:
        """Generate a summary of the document content."""
        pass
    
    @abstractmethod
    async def extract_keywords(self, document: Document, num_keywords: int = 10) -> List[str]:
        """Extract key terms from the document."""
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, document: Document) -> Dict[str, float]:
        """Analyze the sentiment of the document content."""
        pass
    
    @abstractmethod
    async def classify_document(self, document: Document) -> List[Dict[str, float]]:
        """Classify the document into categories."""
        pass
    
    @abstractmethod
    async def get_entities(self, document: Document) -> List[Dict[str, str]]:
        """Extract named entities from the document."""
        pass

class OpenAIService(AIService):
    """Implementation of AIService using OpenAI's API."""
    
    def __init__(self):
        import openai
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def summarize_document(self, document: Document, max_length: int = 500) -> str:
        """Generate a summary using OpenAI's GPT model."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
                    {"role": "user", "content": f"Please summarize the following document in {max_length} characters or less:\n\n{document.content}"}
                ],
                max_tokens=max_length
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    async def extract_keywords(self, document: Document, num_keywords: int = 10) -> List[str]:
        """Extract keywords using OpenAI's GPT model."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts keywords from documents."},
                    {"role": "user", "content": f"Please extract {num_keywords} key terms from the following document:\n\n{document.content}"}
                ],
                max_tokens=100
            )
            keywords = response.choices[0].message.content.split(',')
            return [kw.strip() for kw in keywords]
        except Exception as e:
            raise Exception(f"Failed to extract keywords: {str(e)}")
    
    async def analyze_sentiment(self, document: Document) -> Dict[str, float]:
        """Analyze sentiment using OpenAI's GPT model."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes document sentiment."},
                    {"role": "user", "content": f"Please analyze the sentiment of the following document and return a JSON object with scores for positive, negative, and neutral sentiment (0-1):\n\n{document.content}"}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to analyze sentiment: {str(e)}")
    
    async def classify_document(self, document: Document) -> List[Dict[str, float]]:
        """Classify document using OpenAI's GPT model."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies documents."},
                    {"role": "user", "content": f"Please classify the following document and return a JSON array of categories with confidence scores (0-1):\n\n{document.content}"}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to classify document: {str(e)}")
    
    async def get_entities(self, document: Document) -> List[Dict[str, str]]:
        """Extract named entities using OpenAI's GPT model."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts named entities from documents."},
                    {"role": "user", "content": f"Please extract named entities from the following document and return a JSON array of objects with 'type' and 'text' fields:\n\n{document.content}"}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to extract entities: {str(e)}")

# Create a singleton instance
ai_service = OpenAIService() 