"""
Document Management Routes - Complete System
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
from datetime import datetime
import mimetypes

from api.database import get_db
from api.models.document import Document, DocumentStatus
from api.models.dataset import Dataset
from api.models.user import User
from core.auth import get_current_user
from utilities.storage import save_upload_file

router = APIRouter()

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.md', '.csv', '.json'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    dataset_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document to a dataset"""
    try:
        # Validate dataset
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.tenant_id == current_user.tenant_id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Save file
        file_path = save_upload_file(content, file.filename)
        
        # Create document record
        document = Document(
            id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            name=file.filename,
            file_path=file_path,
            file_type=file_ext,
            file_size=file_size,
            status=DocumentStatus.PENDING,
            tenant_id=current_user.tenant_id,
            created_by=current_user.id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # TODO: Trigger async processing
        # For now, we'll process synchronously
        from document_processing.processors.base_processor import process_document
        
        try:
            # Process document
            result = process_document(document.id, file_path, file_ext, db)
            
            # Update status
            document.status = DocumentStatus.COMPLETED
            document.chunk_count = result.get('chunk_count', 0)
            document.word_count = result.get('word_count', 0)
            db.commit()
            
        except Exception as e:
            print(f"Processing error: {e}")
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()
        
        return {
            "id": document.id,
            "name": document.name,
            "dataset_id": dataset_id,
            "status": document.status,
            "file_size": file_size,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "message": "Document uploaded and processing started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("", response_model=dict)
async def list_documents(
    dataset_id: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents"""
    try:
        offset = (page - 1) * limit
        
        query = db.query(Document).filter(
            Document.tenant_id == current_user.tenant_id
        )
        
        if dataset_id:
            query = query.filter(Document.dataset_id == dataset_id)
        
        total = query.count()
        documents = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "data": [
                {
                    "id": doc.id,
                    "name": doc.name,
                    "dataset_id": doc.dataset_id,
                    "status": doc.status,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "chunk_count": doc.chunk_count,
                    "word_count": doc.word_count,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
                }
                for doc in documents
            ],
            "total": total,
            "page": page,
            "limit": limit,
            "has_more": (offset + limit) < total
        }
    except Exception as e:
        print(f"List documents error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document details"""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.tenant_id == current_user.tenant_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {
            "id": document.id,
            "name": document.name,
            "dataset_id": document.dataset_id,
            "status": document.status,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "file_path": document.file_path,
            "chunk_count": document.chunk_count,
            "word_count": document.word_count,
            "error_message": document.error_message,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get document error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document"""
    try:
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.tenant_id == current_user.tenant_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from storage
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                print(f"Failed to delete file: {e}")
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Delete document error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
