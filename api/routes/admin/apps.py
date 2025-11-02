"""
Admin Apps Management - Adapted from Dify
Manages applications, configurations, and workflows
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.database import get_db
from api.models.app import App, AppMode, AppModelConfig
from api.models.user import User
from core.auth import get_current_user, require_admin

router = APIRouter()


# === Apps Management ===

@router.get("/apps", response_model=List[dict])
async def list_apps(
    page: int = 1,
    limit: int = 20,
    mode: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all applications with pagination"""
    query = db.query(App)
    
    # Filter by mode if specified
    if mode:
        query = query.filter(App.mode == mode)
    
    # Apply pagination
    offset = (page - 1) * limit
    apps = query.offset(offset).limit(limit).all()
    
    return [
        {
            "id": app.id,
            "name": app.name,
            "mode": app.mode,
            "icon": app.icon,
            "description": app.description,
            "created_at": app.created_at.isoformat(),
            "updated_at": app.updated_at.isoformat(),
        }
        for app in apps
    ]


@router.post("/apps", status_code=status.HTTP_201_CREATED)
async def create_app(
    name: str,
    mode: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new application"""
    # Validate mode
    try:
        app_mode = AppMode(mode)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid app mode: {mode}"
        )
    
    # Create app
    new_app = App(
        name=name,
        mode=app_mode,
        description=description,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id
    )
    
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return {
        "id": new_app.id,
        "name": new_app.name,
        "mode": new_app.mode,
        "created_at": new_app.created_at.isoformat()
    }


@router.get("/apps/{app_id}")
async def get_app(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get application details"""
    app = db.query(App).filter(App.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return {
        "id": app.id,
        "name": app.name,
        "mode": app.mode,
        "icon": app.icon,
        "description": app.description,
        "model_config": app.model_config,
        "created_at": app.created_at.isoformat(),
        "updated_at": app.updated_at.isoformat(),
    }


@router.put("/apps/{app_id}")
async def update_app(
    app_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update application"""
    app = db.query(App).filter(App.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update fields
    if name:
        app.name = name
    if description is not None:
        app.description = description
    if icon:
        app.icon = icon
    
    app.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(app)
    
    return {
        "id": app.id,
        "name": app.name,
        "updated_at": app.updated_at.isoformat()
    }


@router.delete("/apps/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete application"""
    app = db.query(App).filter(App.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    db.delete(app)
    db.commit()
    
    return None


# === App Configuration ===

@router.get("/apps/{app_id}/model-config")
async def get_model_config(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app model configuration"""
    app = db.query(App).filter(App.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return app.model_config or {}


@router.post("/apps/{app_id}/model-config")
async def update_model_config(
    app_id: str,
    config: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update app model configuration"""
    app = db.query(App).filter(App.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update config
    app.model_config = config
    app.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Configuration updated successfully"}


# === Statistics ===

@router.get("/apps/{app_id}/statistics")
async def get_app_statistics(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get application usage statistics"""
    from api.models.conversation import Conversation
    from api.models.message import Message
    from sqlalchemy import func
    
    # Get conversation count
    conversation_count = db.query(func.count(Conversation.id))\
        .filter(Conversation.app_id == app_id)\
        .scalar()
    
    # Get message count
    message_count = db.query(func.count(Message.id))\
        .join(Conversation)\
        .filter(Conversation.app_id == app_id)\
        .scalar()
    
    return {
        "app_id": app_id,
        "conversations": conversation_count,
        "messages": message_count,
        "updated_at": datetime.utcnow().isoformat()
    }

