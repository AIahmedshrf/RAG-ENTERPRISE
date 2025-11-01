"""
Document Management Routes with File Upload
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import mimetypes

from api.database import get_db
from api.models import Document, Dataset, User, DocumentStatus, DocumentType
from api.middleware.auth import get_current_user
from utilities.storage import storage_manager
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/documents")


# File type mapping
ALLOWED_EXTENSIONS = {
    '.pdf': DocumentType.PDF,
    '.docx': DocumentType.DOCX,
    '.xlsx': DocumentType.XLSX,
    '.pptx': DocumentType.PPTX,
    '.txt': DocumentType.TEXT,
    '.md': DocumentType.MARKDOWN,
    '.html': DocumentType.HTML,
    '.csv': DocumentType.CSV
}


@router.get("/")
async def list_documents(
    dataset_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List documents"""
    query = db.query(Document)
    
    if dataset_id:
        query = query.filter(Document.dataset_id == dataset_id)
    
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    dataset_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload document to dataset
    
    Supported formats: PDF, DOCX, XLSX, PPTX, TXT, MD, HTML, CSV
    """
    # Verify dataset exists and user has access
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.tenant_id == current_user.tenant_id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Check file extension
    file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )
    
    file_type = ALLOWED_EXTENSIONS[file_ext]
    
    # Check file size
    max_size = settings.storage.max_file_size_mb * 1024 * 1024
    
    try:
        # Save file to storage
        file_path, file_hash, file_size = storage_manager.save_file(
            file.file,
            file.filename,
            subfolder=f"datasets/{dataset_id}"
        )
        
        if file_size > max_size:
            storage_manager.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.storage.max_file_size_mb}MB"
            )
        
        # Check for duplicates
        existing_doc = db.query(Document).filter(
            Document.dataset_id == dataset_id,
            Document.file_hash == file_hash
        ).first()
        
        if existing_doc:
            storage_manager.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document already exists: {existing_doc.name}"
            )
        
        # Create document record
        document = Document(
            dataset_id=dataset_id,
            name=file.filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            file_hash=file_hash,
            status=DocumentStatus.WAITING,
            created_by=current_user.id
        )
        
        db.add(document)
        
        # Update dataset stats
        dataset.document_count += 1
        
        db.commit()
        db.refresh(document)
        
        logger.info(f"Document uploaded: {document.id} - {file.filename}")
        
        # TODO: Trigger async processing
        
        return {
            "id": document.id,
            "name": document.name,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "status": document.status,
            "message": "Document uploaded successfully. Processing will start shortly."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )


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


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    
    # Delete file from storage
    if document.file_path:
        storage_manager.delete_file(document.file_path)
    
    # Delete from database
    db.delete(document)
    
    # Update dataset stats
    dataset = db.query(Dataset).filter(Dataset.id == document.dataset_id).first()
    if dataset:
        dataset.document_count = max(0, dataset.document_count - 1)
    
    db.commit()
    
    logger.info(f"Document deleted: {document_id}")
    
    return None


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download document (placeholder)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # TODO: Implement actual file download
    from fastapi.responses import FileResponse
    
    file_path = storage_manager.get_file_path(document.file_path)
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=document.name,
        media_type='application/octet-stream'
    )
