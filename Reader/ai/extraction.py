from typing import List, Dict, Any, Optional
from . import logger, monitor, model, pipeline

class ExtractionSystem:
    def __init__(self):
        self.logger = logger.logger
        self.initialized = False

    async def initialize(self):
        """Initialize the extraction system."""
        try:
            await pipeline.initialize()
            self.initialized = True
            self.logger.info("Extraction system initialized")
        except Exception as e:
            self.logger.error(f"Error initializing extraction system: {str(e)}")
            monitor.track_error("ExtractionSystem", str(e))
            raise

    async def extract_from_document(self, document_path: str) -> Dict[str, Any]:
        """Extract information from a document."""
        if not self.initialized:
            raise RuntimeError("Extraction system not initialized")

        try:
            # Process document with AI model
            document_data = await model.process_document(document_path)
            
            # Process text with embedding pipeline
            text_data = await pipeline.process_text(document_data["text"])

            result = {
                "document": document_data,
                "text": text_data,
                "metadata": {
                    **document_data["metadata"],
                    **text_data["metadata"]
                }
            }

            self.logger.info(f"Document extracted: {document_path}")
            monitor.track_request(0)  # Track extraction operation
            return result
        except Exception as e:
            self.logger.error(f"Error extracting document: {str(e)}")
            monitor.track_error("ExtractionSystem", str(e))
            raise

    async def batch_extract(self, document_paths: List[str]) -> List[Dict[str, Any]]:
        """Extract information from multiple documents."""
        if not self.initialized:
            raise RuntimeError("Extraction system not initialized")

        try:
            results = []
            for path in document_paths:
                result = await self.extract_from_document(path)
                results.append(result)
            return results
        except Exception as e:
            self.logger.error(f"Error in batch extraction: {str(e)}")
            monitor.track_error("ExtractionSystem", str(e))
            raise

    async def validate_extraction(self, extraction_result: Dict[str, Any]) -> bool:
        """Validate the quality of extraction results."""
        try:
            # Check if required fields are present
            required_fields = ["document", "text", "metadata"]
            if not all(field in extraction_result for field in required_fields):
                return False

            # Check if embeddings are valid
            embeddings = extraction_result["text"]["embeddings"]
            if not embeddings or len(embeddings) == 0:
                return False

            # Check if summary is meaningful
            summary = extraction_result["text"]["summary"]
            if not summary or len(summary.strip()) == 0:
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error validating extraction: {str(e)}")
            monitor.track_error("ExtractionSystem", str(e))
            return False

# Create global extraction system instance
extractor = ExtractionSystem() 