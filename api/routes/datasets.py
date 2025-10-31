"""
Dataset Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from api.database import get_db
from api.models import Dataset, User, Tenant, Document
from api.middleware.auth import get_current_user
from api.middleware.tenant import get_current_tenant
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/datasets")


# Request/Response Models
class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = "#1C64F2"
    indexing_technique: str = Field(default="high_quality")
    embedding_model: Optional[str] = "text-embedding-ada-002"
    embedding_model_provider: Optional[str] = "azure_openai"


class DatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None


class DatasetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    icon_background: Optional[str]
    indexing_technique: str
    document_count: int
    word_count: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    List all datasets for current tenant
    """
    datasets = db.query(Dataset).filter(
        Dataset.tenant_id == current_tenant.id
    ).offset(skip).limit(limit).all()
    
    return datasets


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset_data: DatasetCreate,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Create new dataset
    """
    # Check user permission
    if not current_user.has_permission("datasets", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to create datasets"
        )
    
    # Create dataset
    dataset = Dataset(
        name=dataset_data.name,
        description=dataset_data.description,
        icon=dataset_data.icon,
        icon_background=dataset_data.icon_background,
        indexing_technique=dataset_data.indexing_technique,
        embedding_model=dataset_data.embedding_model,
        embedding_model_provider=dataset_data.embedding_model_provider,
        tenant_id=current_tenant.id,
        created_by=current_user.id
    )
    
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    
    logger.info(f"Dataset created: {dataset.id} by user {current_user.id}")
    
    return dataset


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get dataset details
    """
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.tenant_id == current_tenant.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return dataset


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    dataset_data: DatasetUpdate,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Update dataset
    """
    # Check permission
    if not current_user.has_permission("datasets", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to update datasets"
        )
    
    # Get dataset
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.tenant_id == current_tenant.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Update fields
    update_data = dataset_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dataset, field, value)
    
    db.commit()
    db.refresh(dataset)
    
    logger.info(f"Dataset updated: {dataset.id} by user {current_user.id}")
    
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Delete dataset
    """
    # Check permission
    if not current_user.has_permission("datasets", "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete datasets"
        )
    
    # Get dataset
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.tenant_id == current_tenant.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Delete dataset (cascade will delete documents and segments)
    db.delete(dataset)
    db.commit()
    
    logger.info(f"Dataset deleted: {dataset_id} by user {current_user.id}")
    
    return None


@router.get("/{dataset_id}/statistics")
async def get_dataset_statistics(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get dataset statistics
    """
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.tenant_id == current_tenant.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Get documents statistics
    documents = db.query(Document).filter(Document.dataset_id == dataset_id).all()
    
    total_documents = len(documents)
    completed_documents = sum(1 for doc in documents if doc.status == "completed")
    processing_documents = sum(1 for doc in documents if doc.status in ["parsing", "splitting", "indexing"])
    error_documents = sum(1 for doc in documents if doc.status == "error")
    
    return {
        "dataset_id": dataset.id,
        "name": dataset.name,
        "document_count": dataset.document_count,
        "word_count": dataset.word_count,
        "documents": {
            "total": total_documents,
            "completed": completed_documents,
            "processing": processing_documents,
            "error": error_documents
        },
        "indexing_technique": dataset.indexing_technique,
        "embedding_model": dataset.embedding_model
    }
