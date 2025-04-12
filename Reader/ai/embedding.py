from typing import List, Dict, Any, Optional
import numpy as np
from . import logger, monitor, model

class EmbeddingPipeline:
    def __init__(self):
        self.logger = logger.logger
        self.initialized = False

    async def initialize(self):
        """Initialize the embedding pipeline."""
        try:
            await model.initialize()
            self.initialized = True
            self.logger.info("Embedding pipeline initialized")
        except Exception as e:
            self.logger.error(f"Error initializing embedding pipeline: {str(e)}")
            monitor.track_error("EmbeddingPipeline", str(e))
            raise

    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process text and generate embeddings and metadata."""
        if not self.initialized:
            raise RuntimeError("Pipeline not initialized")

        try:
            # Generate embeddings
            embeddings = await model.generate_embeddings(text)
            
            # Extract entities
            entities = await model.extract_entities(text)
            
            # Generate summary
            summary = await model.generate_summary(text)

            result = {
                "embeddings": embeddings,
                "entities": entities,
                "summary": summary,
                "metadata": {
                    "text_length": len(text),
                    "entity_count": len(entities),
                    "embedding_dimension": len(embeddings)
                }
            }

            self.logger.info("Text processed successfully")
            monitor.track_request(0)  # Track pipeline operation
            return result
        except Exception as e:
            self.logger.error(f"Error processing text: {str(e)}")
            monitor.track_error("EmbeddingPipeline", str(e))
            raise

    async def batch_process(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Process multiple texts in batch."""
        if not self.initialized:
            raise RuntimeError("Pipeline not initialized")

        try:
            results = []
            for text in texts:
                result = await self.process_text(text)
                results.append(result)
            return results
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            monitor.track_error("EmbeddingPipeline", str(e))
            raise

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            monitor.track_error("EmbeddingPipeline", str(e))
            raise

# Create global pipeline instance
pipeline = EmbeddingPipeline() 