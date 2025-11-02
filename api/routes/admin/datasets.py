"""
Admin Dataset Management - Adapted from Dify
Manages datasets, documents, and knowledge base
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.database import get_db
from api.models.dataset import Dataset, IndexingTechnique
from api.models.document import Document, DocumentStatus
from api.models.user import User
from core.auth import get_current_user, require_admin

router = APIRouter()


# === Dataset Management ===

@router.get("/datasets", response_model=List[dict])
async def list_datasets(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all datasets with pagination"""
    offset = (page - 1) * limit
    
    datasets = db.query(Dataset)\
        .filter(Dataset.tenant_id == current_user.tenant_id)\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "indexing_technique": dataset.indexing_technique,
            "document_count": len(dataset.documents) if hasattr(dataset, 'documents') else 0,
            "created_at": dataset.created_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
        }
        for dataset in datasets
    ]


@router.post("/datasets", status_code=status.HTTP_201_CREATED)
async def create_dataset(
    name: str,
    description: Optional[str] = None,
    indexing_technique: str = "high_quality",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new dataset"""
    # Validate indexing technique
    try:
        technique = IndexingTechnique(indexing_technique)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid indexing technique: {indexing_technique}"
        )
    
    # Create dataset
    new_dataset = Dataset(
        name=name,
        description=description,
        indexing_technique=technique,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id
    )
    
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    
    return {
        "id": new_dataset.id,
        "name": new_dataset.name,
        "indexing_technique": new_dataset.indexing_technique,
        "created_at": new_dataset.created_at.isoformat()
    }


@router.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset details"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "indexing_technique": dataset.indexing_technique,
        "created_at": dataset.created_at.isoformat(),
        "updated_at": dataset.updated_at.isoformat(),
    }


@router.put("/datasets/{dataset_id}")
async def update_dataset(
    dataset_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Update fields
    if name:
        dataset.name = name
    if description is not None:
        dataset.description = description
    
    dataset.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(dataset)
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "updated_at": dataset.updated_at.isoformat()
    }


@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete dataset and all related documents"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Delete all documents first
    db.query(Document).filter(Document.dataset_id == dataset_id).delete()
    
    # Delete dataset
    db.delete(dataset)
    db.commit()
    
    return None


# === Document Management ===

@router.get("/datasets/{dataset_id}/documents")
async def list_dataset_documents(
    dataset_id: str,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents in a dataset"""
    offset = (page - 1) * limit
    
    documents = db.query(Document)\
        .filter(Document.dataset_id == dataset_id)\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": doc.id,
            "name": doc.name,
            "type": doc.type,
            "status": doc.status,
            "word_count": doc.word_count,
            "created_at": doc.created_at.isoformat(),
        }
        for doc in documents
    ]


@router.get("/datasets/{dataset_id}/statistics")
async def get_dataset_statistics(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset statistics"""
    from sqlalchemy import func
    
    # Get document count by status
    doc_stats = db.query(
        Document.status,
        func.count(Document.id)
    ).filter(
        Document.dataset_id == dataset_id
    ).group_by(Document.status).all()
    
    # Get total word count
    total_words = db.query(func.sum(Document.word_count))\
        .filter(Document.dataset_id == dataset_id)\
        .scalar() or 0
    
    stats_dict = {status.value: count for status, count in doc_stats}
    
    return {
        "dataset_id": dataset_id,
        "total_documents": sum(stats_dict.values()),
        "by_status": stats_dict,
        "total_words": total_words,
        "updated_at": datetime.utcnow().isoformat()
    }

