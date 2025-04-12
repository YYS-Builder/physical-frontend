from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.document import Document
from app.services.base import BaseService

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    index: int
    total_chunks: int
    metadata: Dict

class ChunkingService(BaseService):
    def __init__(self):
        self.chunk_size = 1000  # characters per chunk
        self.overlap = 100  # characters overlap between chunks
        
    async def chunk_document(
        self,
        document: Document,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[DocumentChunk]:
        """Split a document into manageable chunks."""
        try:
            # Get document content
            content = await self._get_document_content(document)
            
            # Use provided parameters or defaults
            chunk_size = chunk_size or self.chunk_size
            overlap = overlap or self.overlap
            
            # Split content into chunks
            chunks = []
            total_length = len(content)
            current_index = 0
            
            while current_index < total_length:
                # Calculate chunk boundaries
                start = max(0, current_index - overlap)
                end = min(total_length, current_index + chunk_size)
                
                # Create chunk
                chunk_content = content[start:end]
                chunk = DocumentChunk(
                    id=f"{document.id}_{len(chunks)}",
                    document_id=document.id,
                    content=chunk_content,
                    index=len(chunks),
                    total_chunks=0,  # Will be updated after all chunks are created
                    metadata={
                        "start": start,
                        "end": end,
                        "length": len(chunk_content)
                    }
                )
                
                chunks.append(chunk)
                current_index = end
            
            # Update total chunks count
            for chunk in chunks:
                chunk.total_chunks = len(chunks)
            
            return chunks
        except Exception as e:
            raise Exception(f"Failed to chunk document: {str(e)}")
    
    async def get_chunk(
        self,
        document: Document,
        chunk_index: int
    ) -> Optional[DocumentChunk]:
        """Get a specific chunk of a document."""
        try:
            chunks = await self.chunk_document(document)
            if 0 <= chunk_index < len(chunks):
                return chunks[chunk_index]
            return None
        except Exception as e:
            raise Exception(f"Failed to get chunk: {str(e)}")
    
    async def search_chunks(
        self,
        document: Document,
        query: str
    ) -> List[DocumentChunk]:
        """Search for text across document chunks."""
        try:
            chunks = await self.chunk_document(document)
            matching_chunks = []
            
            for chunk in chunks:
                if query.lower() in chunk.content.lower():
                    matching_chunks.append(chunk)
            
            return matching_chunks
        except Exception as e:
            raise Exception(f"Failed to search chunks: {str(e)}")
    
    async def merge_chunks(
        self,
        chunks: List[DocumentChunk]
    ) -> str:
        """Merge chunks back into a single document."""
        try:
            # Sort chunks by index
            sorted_chunks = sorted(chunks, key=lambda x: x.index)
            
            # Merge content, handling overlaps
            merged_content = ""
            last_end = 0
            
            for chunk in sorted_chunks:
                start = chunk.metadata["start"]
                end = chunk.metadata["end"]
                
                if start > last_end:
                    # No overlap, add entire chunk
                    merged_content += chunk.content
                else:
                    # Handle overlap
                    overlap_length = last_end - start
                    merged_content += chunk.content[overlap_length:]
                
                last_end = end
            
            return merged_content
        except Exception as e:
            raise Exception(f"Failed to merge chunks: {str(e)}")
    
    async def _get_document_content(self, document: Document) -> str:
        """Get the text content of a document."""
        # TODO: Implement document content extraction
        # This is a placeholder implementation
        return "Sample document content" 