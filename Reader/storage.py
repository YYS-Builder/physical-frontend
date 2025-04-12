import os
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi import UploadFile
from . import logger, monitor

class FileStorage:
    def __init__(self, base_path: str = "storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.logger = logger.logger

    def _get_file_path(self, document_id: int, filename: str) -> Path:
        """Get the full path for a document file."""
        return self.base_path / str(document_id) / filename

    async def save_file(self, document_id: int, file: UploadFile) -> Optional[str]:
        """Save an uploaded file to storage."""
        try:
            # Create document directory if it doesn't exist
            doc_dir = self.base_path / str(document_id)
            doc_dir.mkdir(exist_ok=True)

            # Save file
            file_path = self._get_file_path(document_id, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            self.logger.info(f"File saved: {file_path}")
            monitor.track_request(0)  # Track storage operation
            return str(file_path)
        except Exception as e:
            self.logger.error(f"Error saving file: {str(e)}")
            monitor.track_error("FileStorage", str(e))
            return None

    def get_file(self, document_id: int, filename: str) -> Optional[BinaryIO]:
        """Retrieve a file from storage."""
        try:
            file_path = self._get_file_path(document_id, filename)
            if not file_path.exists():
                self.logger.warning(f"File not found: {file_path}")
                return None

            return open(file_path, "rb")
        except Exception as e:
            self.logger.error(f"Error retrieving file: {str(e)}")
            monitor.track_error("FileStorage", str(e))
            return None

    def delete_file(self, document_id: int, filename: str) -> bool:
        """Delete a file from storage."""
        try:
            file_path = self._get_file_path(document_id, filename)
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting file: {str(e)}")
            monitor.track_error("FileStorage", str(e))
            return False

    def get_storage_usage(self) -> float:
        """Get total storage usage in MB."""
        try:
            total_size = sum(
                f.stat().st_size for f in self.base_path.rglob("*") if f.is_file()
            )
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            self.logger.error(f"Error calculating storage usage: {str(e)}")
            return 0.0

# Create global storage instance
storage = FileStorage() 