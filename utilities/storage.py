"""
Storage Utilities
File storage management
"""
import os
from pathlib import Path
from typing import Optional
import shutil
from datetime import datetime


def get_storage_path() -> str:
    """
    Get storage path for uploaded files
    Creates directory if it doesn't exist
    """
    # Use /tmp for codespaces
    storage_path = os.getenv('STORAGE_PATH', '/tmp/rag-enterprise/storage')
    
    # Create directory if it doesn't exist
    os.makedirs(storage_path, exist_ok=True)
    
    return storage_path


def get_upload_path(filename: str, user_id: Optional[str] = None) -> str:
    """
    Get full path for uploaded file
    """
    storage_path = get_storage_path()
    
    # Create user subfolder if provided
    if user_id:
        user_path = os.path.join(storage_path, user_id)
        os.makedirs(user_path, exist_ok=True)
        return os.path.join(user_path, filename)
    
    return os.path.join(storage_path, filename)


def save_uploaded_file(file_content: bytes, filename: str, user_id: Optional[str] = None) -> str:
    """
    Save uploaded file to storage
    Returns: file path
    """
    file_path = get_upload_path(filename, user_id)
    
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return file_path


def delete_file(file_path: str) -> bool:
    """
    Delete file from storage
    Returns: True if deleted, False if not found
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_file_info(file_path: str) -> dict:
    """
    Get file information
    """
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    
    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "size": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def cleanup_old_files(days: int = 30):
    """
    Cleanup files older than specified days
    """
    storage_path = get_storage_path()
    now = datetime.now().timestamp()
    cutoff = now - (days * 24 * 60 * 60)
    
    deleted_count = 0
    
    for root, dirs, files in os.walk(storage_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getmtime(file_path) < cutoff:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    return deleted_count


# Initialize storage on import
get_storage_path()
