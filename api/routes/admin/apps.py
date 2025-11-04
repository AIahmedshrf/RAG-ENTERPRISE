"""
Admin App Management - Fixed (No Invalid Imports)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

from api.database import get_db
from api.models.app import App
from api.models.user import User
from core.auth import get_current_user, require_admin

router = APIRouter()


@router.get("", response_model=dict)
async def list_apps(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all applications with pagination"""
    offset = (page - 1) * limit
    
    query = db.query(App)
    if current_user.tenant_id:
        query = query.filter(App.tenant_id == current_user.tenant_id)
    
    total = query.count()
    apps = query.offset(offset).limit(limit).all()
    
    return {
        "data": [
            {
                "id": app.id,
                "name": app.name,
                "mode": app.mode,
                "icon": app.icon,
                "description": app.description,
                "tenant_id": app.tenant_id,
                "created_by": app.created_by,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "updated_at": app.updated_at.isoformat() if app.updated_at else None,
            }
            for app in apps
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": (offset + limit) < total
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_app(
    name: str,
    mode: str = "chat",
    icon: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new application"""
    
    valid_modes = ["chat", "agent", "workflow", "completion"]
    if mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
        )
    
    existing = db.query(App).filter(
        App.name == name,
        App.tenant_id == current_user.tenant_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"App with name '{name}' already exists"
        )
    
    app = App(
        id=str(uuid.uuid4()),
        name=name,
        mode=mode,
        icon=icon or "🤖",
        description=description,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        model_config=json.dumps({"provider": "openai", "model": "gpt-4"})
    )
    
    db.add(app)
    db.commit()
    db.refresh(app)
    
    return {
        "id": app.id,
        "name": app.name,
        "mode": app.mode,
        "icon": app.icon,
        "description": app.description,
        "created_at": app.created_at.isoformat(),
        "message": "App created successfully"
    }


@router.get("/{app_id}", response_model=dict)
async def get_app(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app details"""
    app = db.query(App).filter(
        App.id == app_id,
        App.tenant_id == current_user.tenant_id
    ).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    return {
        "id": app.id,
        "name": app.name,
        "mode": app.mode,
        "icon": app.icon,
        "description": app.description,
        "model_config": json.loads(app.model_config) if app.model_config else None,
        "tenant_id": app.tenant_id,
        "created_by": app.created_by,
        "created_at": app.created_at.isoformat() if app.created_at else None,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None,
    }


@router.put("/{app_id}", response_model=dict)
async def update_app(
    app_id: str,
    name: Optional[str] = None,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update app"""
    app = db.query(App).filter(
        App.id == app_id,
        App.tenant_id == current_user.tenant_id
    ).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    if name:
        app.name = name
    if icon:
        app.icon = icon
    if description:
        app.description = description
    
    app.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(app)
    
    return {
        "id": app.id,
        "name": app.name,
        "icon": app.icon,
        "description": app.description,
        "updated_at": app.updated_at.isoformat(),
        "message": "App updated successfully"
    }


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete app"""
    app = db.query(App).filter(
        App.id == app_id,
        App.tenant_id == current_user.tenant_id
    ).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    db.delete(app)
    db.commit()
    
    return None


@router.get("/{app_id}/model-config", response_model=dict)
async def get_app_model_config(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app model configuration"""
    app = db.query(App).filter(
        App.id == app_id,
        App.tenant_id == current_user.tenant_id
    ).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    return {
        "app_id": app_id,
        "model_config": json.loads(app.model_config) if app.model_config else {}
    }


@router.post("/{app_id}/model-config", response_model=dict)
async def update_app_model_config(
    app_id: str,
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update app model configuration"""
    app = db.query(App).filter(
        App.id == app_id,
        App.tenant_id == current_user.tenant_id
    ).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    app.model_config = json.dumps(config)
    app.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "app_id": app_id,
        "model_config": config,
        "message": "Model config updated successfully"
    }


@router.get("/{app_id}/statistics", response_model=dict)
async def get_app_statistics(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app statistics"""
    app = db.query(App).filter(
        App.id == app_id,
        App.tenant_id == current_user.tenant_id
    ).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    return {
        "app_id": app_id,
        "total_conversations": 0,
        "total_messages": 0,
        "created_at": app.created_at.isoformat() if app.created_at else None,
    }
