"""
Storage Manager for File Uploads
"""
import os
import hashlib
from pathlib import Path
from typing import BinaryIO, Optional
from datetime import datetime

from core.config import settings
from utilities.logger import get_logger

logger = get_logger(__name__)


class StorageManager:
    """Manage file storage (local or Azure Blob)"""
    
    def __init__(self):
        self.provider = settings.storage.provider
        self.local_path = Path(settings.storage.local_path)
        
        # Create local storage directory
        if self.provider == "local":
            self.local_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Local storage initialized: {self.local_path}")
    
    def save_file(
        self,
        file: BinaryIO,
        filename: str,
        subfolder: str = "documents"
    ) -> tuple[str, str, int]:
        """
        Save file and return (file_path, file_hash, file_size)
        
        Args:
            file: File binary stream
            filename: Original filename
            subfolder: Subfolder name (documents, images, etc.)
        
        Returns:
            Tuple of (file_path, file_hash, file_size)
        """
        # Read file content
        content = file.read()
        file.seek(0)  # Reset for potential re-read
        
        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()
        file_size = len(content)
        
        # Generate storage path
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        safe_filename = self._sanitize_filename(filename)
        relative_path = f"{subfolder}/{timestamp}/{file_hash[:8]}_{safe_filename}"
        
        if self.provider == "local":
            # Save to local storage
            full_path = self.local_path / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"File saved locally: {relative_path}")
            return str(relative_path), file_hash, file_size
        
        elif self.provider == "azure":
            # TODO: Implement Azure Blob Storage
            logger.warning("Azure Blob Storage not implemented yet, using local fallback")
            return self.save_file(file, filename, subfolder)
        
        else:
            raise ValueError(f"Unknown storage provider: {self.provider}")
    
    def get_file_path(self, relative_path: str) -> Path:
        """Get full file path"""
        if self.provider == "local":
            return self.local_path / relative_path
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
    
    def file_exists(self, relative_path: str) -> bool:
        """Check if file exists"""
        if self.provider == "local":
            return (self.local_path / relative_path).exists()
        return False
    
    def delete_file(self, relative_path: str) -> bool:
        """Delete file"""
        try:
            if self.provider == "local":
                file_path = self.local_path / relative_path
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"File deleted: {relative_path}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {relative_path}: {e}")
            return False
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path components
        filename = os.path.basename(filename)
        # Remove dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        return ''.join(c if c in safe_chars else '_' for c in filename)


# Global storage instance
storage_manager = StorageManager()
