"""
Document Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api.models import Document, Dataset, User
from api.middleware.auth import get_current_user
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/documents")


@router.get("/")
async def list_documents(
    dataset_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List documents"""
    query = db.query(Document)
    
    if dataset_id:
        query = query.filter(Document.dataset_id == dataset_id)
    
    documents = query.all()
    return documents


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    dataset_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload document (placeholder)"""
    # TODO: Implement actual file upload and processing
    return {
        "message": "Document upload placeholder",
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
