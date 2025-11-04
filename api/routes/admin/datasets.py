"""
Admin Dataset Management - Fixed Response Format
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from api.database import get_db
from api.models.dataset import Dataset
from api.models.document import Document
from api.models.user import User
from core.auth import get_current_user, require_admin

router = APIRouter()


@router.get("", response_model=dict)
async def list_datasets(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all datasets with pagination"""
    try:
        offset = (page - 1) * limit
        
        query = db.query(Dataset)
        if current_user.tenant_id:
            query = query.filter(Dataset.tenant_id == current_user.tenant_id)
        
        total = query.count()
        datasets = query.offset(offset).limit(limit).all()
        
        dataset_list = []
        for dataset in datasets:
            dataset_list.append({
                "id": dataset.id,
                "name": dataset.name,
                "description": dataset.description,
                "indexing_technique": dataset.indexing_technique,
                "tenant_id": dataset.tenant_id,
                "created_by": dataset.created_by,
                "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
                "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
            })
        
        return {
            "data": dataset_list,
            "total": total,
            "page": page,
            "limit": limit,
            "has_more": (offset + limit) < total
        }
    except Exception as e:
        print(f"Error in list_datasets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets: {str(e)}"
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    name: str,
    description: Optional[str] = None,
    indexing_technique: str = "high_quality",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new dataset"""
    try:
        existing = db.query(Dataset).filter(
            Dataset.name == name,
            Dataset.tenant_id == current_user.tenant_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset with name '{name}' already exists"
            )
        
        dataset = Dataset(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            indexing_technique=indexing_technique,
            tenant_id=current_user.tenant_id,
            created_by=current_user.id
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "indexing_technique": dataset.indexing_technique,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            "message": "Dataset created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in create_dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dataset: {str(e)}"
        )


@router.get("/{dataset_id}", response_model=dict)
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset details"""
    try:
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.tenant_id == current_user.tenant_id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        document_count = db.query(Document).filter(
            Document.dataset_id == dataset_id
        ).count()
        
        return {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "indexing_technique": dataset.indexing_technique,
            "document_count": document_count,
            "tenant_id": dataset.tenant_id,
            "created_by": dataset.created_by,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dataset: {str(e)}"
        )


@router.put("/{dataset_id}", response_model=dict)
async def update_dataset(
    dataset_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update dataset"""
    try:
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.tenant_id == current_user.tenant_id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        if name:
            dataset.name = name
        if description:
            dataset.description = description
        
        dataset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(dataset)
        
        return {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
            "message": "Dataset updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in update_dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dataset: {str(e)}"
        )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete dataset"""
    try:
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.tenant_id == current_user.tenant_id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        db.query(Document).filter(Document.dataset_id == dataset_id).delete()
        db.delete(dataset)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in delete_dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataset: {str(e)}"
        )


@router.get("/{dataset_id}/documents", response_model=dict)
async def list_dataset_documents(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents in a dataset"""
    try:
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.tenant_id == current_user.tenant_id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        documents = db.query(Document).filter(
            Document.dataset_id == dataset_id
        ).all()
        
        return {
            "data": [
                {
                    "id": doc.id,
                    "name": doc.name,
                    "status": doc.status,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                }
                for doc in documents
            ],
            "total": len(documents)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in list_dataset_documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/{dataset_id}/statistics", response_model=dict)
async def get_dataset_statistics(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset statistics"""
    try:
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.tenant_id == current_user.tenant_id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        document_count = db.query(Document).filter(
            Document.dataset_id == dataset_id
        ).count()
        
        return {
            "dataset_id": dataset_id,
            "document_count": document_count,
            "indexing_technique": dataset.indexing_technique,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_dataset_statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
