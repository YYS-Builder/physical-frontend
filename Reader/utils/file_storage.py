import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, BinaryIO
import magic
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class FileStorage:
    def __init__(self, base_path: str = "storage"):
        self.base_path = Path(base_path)
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.base_path / "uploads",
            self.base_path / "processed",
            self.base_path / "temp"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename using UUID."""
        ext = Path(original_filename).suffix
        return f"{uuid.uuid4()}{ext}"
    
    def _validate_file_type(self, file_path: Path) -> bool:
        """Validate file type using python-magic."""
        try:
            file_type = magic.from_file(str(file_path), mime=True)
            allowed_types = {
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp'
            }
            return file_type in allowed_types
        except Exception as e:
            logger.error(f"Error validating file type: {e}")
            return False
    
    async def save_upload(self, file: UploadFile) -> Optional[str]:
        """Save an uploaded file and return its path."""
        try:
            # Generate unique filename
            filename = self._generate_unique_filename(file.filename)
            file_path = self.base_path / "uploads" / filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Validate file type
            if not self._validate_file_type(file_path):
                os.remove(file_path)
                return None
            
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving upload: {e}")
            return None
    
    def save_processed(self, source_path: str, filename: str) -> Optional[str]:
        """Save a processed file and return its path."""
        try:
            source = Path(source_path)
            if not source.exists():
                return None
                
            dest_path = self.base_path / "processed" / filename
            shutil.copy2(source, dest_path)
            return str(dest_path)
        except Exception as e:
            logger.error(f"Error saving processed file: {e}")
            return None
    
    def get_file_path(self, filename: str, processed: bool = False) -> Optional[str]:
        """Get the full path of a file."""
        try:
            directory = "processed" if processed else "uploads"
            file_path = self.base_path / directory / filename
            return str(file_path) if file_path.exists() else None
        except Exception as e:
            logger.error(f"Error getting file path: {e}")
            return None
    
    def delete_file(self, filename: str, processed: bool = False) -> bool:
        """Delete a file."""
        try:
            directory = "processed" if processed else "uploads"
            file_path = self.base_path / directory / filename
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def cleanup_temp(self) -> None:
        """Clean up temporary files."""
        try:
            temp_dir = self.base_path / "temp"
            for file in temp_dir.iterdir():
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"Error deleting temp file {file}: {e}")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {e}")
    
    def get_file_size(self, filename: str, processed: bool = False) -> Optional[int]:
        """Get the size of a file in bytes."""
        try:
            directory = "processed" if processed else "uploads"
            file_path = self.base_path / directory / filename
            return file_path.stat().st_size if file_path.exists() else None
        except Exception as e:
            logger.error(f"Error getting file size: {e}")
            return None
    
    def get_file_metadata(self, filename: str, processed: bool = False) -> Optional[dict]:
        """Get metadata about a file."""
        try:
            directory = "processed" if processed else "uploads"
            file_path = self.base_path / directory / filename
            if not file_path.exists():
                return None
                
            return {
                "size": file_path.stat().st_size,
                "created": file_path.stat().st_ctime,
                "modified": file_path.stat().st_mtime,
                "type": magic.from_file(str(file_path), mime=True)
            }
        except Exception as e:
            logger.error(f"Error getting file metadata: {e}")
            return None 