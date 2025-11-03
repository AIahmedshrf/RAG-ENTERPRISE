"""
Document Management Routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import aiofiles
from datetime import datetime

from api.database import get_db
from api.models.document import Document, DocumentType, DocumentStatus
from api.models.user import User
from core.auth import get_current_user
from utilities.storage import get_storage_path

router = APIRouter()

# File type mapping
FILE_TYPE_MAPPING = {
    '.txt': DocumentType.TXT,
    '.pdf': DocumentType.PDF,
    '.doc': DocumentType.DOC,
    '.docx': DocumentType.DOCX,
    '.xls': DocumentType.XLS,
    '.xlsx': DocumentType.XLSX,
    '.csv': DocumentType.CSV,
    '.json': DocumentType.JSON,
    '.md': DocumentType.MD,
    '.html': DocumentType.HTML,
    '.xml': DocumentType.XML,
}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    dataset_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document
    """
    # Get file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # Check if supported
    if file_ext not in FILE_TYPE_MAPPING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}"
        )
    
    # Create document record
    document = Document(
        name=file.filename,
        type=FILE_TYPE_MAPPING[file_ext],
        dataset_id=dataset_id or "default",
        status=DocumentStatus.UPLOADING,
        created_by=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Save file
    try:
        storage_path = get_storage_path()
        file_path = os.path.join(storage_path, f"{document.id}_{file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Update document
        document.file_path = file_path
        document.status = DocumentStatus.COMPLETED
        db.commit()
        
        return {
            "id": document.id,
            "name": document.name,
            "type": document.type,
            "status": document.status,
            "created_at": document.created_at.isoformat()
        }
        
    except Exception as e:
        document.status = DocumentStatus.ERROR
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


@router.get("/documents")
async def list_documents(
    dataset_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents"""
    query = db.query(Document)
    
    if dataset_id:
        query = query.filter(Document.dataset_id == dataset_id)
    
    documents = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": doc.id,
            "name": doc.name,
            "type": doc.type,
            "status": doc.status,
            "word_count": doc.word_count,
            "created_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "id": document.id,
        "name": document.name,
        "type": document.type,
        "status": document.status,
        "word_count": document.word_count,
        "file_path": document.file_path,
        "created_at": document.created_at.isoformat()
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file if exists
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
