"""
Storage Utilities
Handle file uploads and storage
"""
import os
import uuid
from pathlib import Path
from typing import Union


def get_upload_dir() -> Path:
    """Get or create upload directory"""
    upload_dir = Path("/tmp/rag-enterprise/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_upload_file(content: bytes, filename: str) -> str:
    """
    Save uploaded file to storage
    Returns: full file path
    """
    upload_dir = get_upload_dir()
    
    # Generate unique filename
    file_ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    file_path = upload_dir / unique_filename
    
    # Write file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return str(file_path)


def delete_file(file_path: str) -> bool:
    """Delete file from storage"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
