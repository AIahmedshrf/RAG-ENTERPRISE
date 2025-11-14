"""
Admin App Management - Fixed with Pydantic Models
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
import json

from api.database import get_db
from api.models.app import App
from api.models.user import User
from core.auth import get_current_user, require_admin

router = APIRouter()


# Pydantic Models for Request/Response
class CreateAppRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    mode: str = Field(default="chat", pattern="^(chat|agent|agent-chat|workflow|completion)$")
    icon: Optional[str] = Field(default="🤖", max_length=10)
    description: Optional[str] = Field(default=None, max_length=500)
    model_config: Optional[Dict[str, Any]] = None


class UpdateAppRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = Field(None, max_length=500)


@router.get("", response_model=dict)
async def list_apps(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all applications with pagination"""
    try:
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
    except Exception as e:
        print(f"Error in list_apps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list apps: {str(e)}"
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_app(
    request: CreateAppRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new application"""
    try:
        # Check if app name already exists for this tenant
        existing = db.query(App).filter(
            App.name == request.name,
            App.tenant_id == current_user.tenant_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"App with name '{request.name}' already exists"
            )
        
        # Prepare model config
        model_config = request.model_config or {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        app = App(
            id=str(uuid.uuid4()),
            name=request.name,
            mode=request.mode,
            icon=request.icon or "🤖",
            description=request.description,
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            model_config=json.dumps(model_config)
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in create_app: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create app: {str(e)}"
        )


@router.get("/{app_id}", response_model=dict)
async def get_app(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app details"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_app: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get app: {str(e)}"
        )


@router.put("/{app_id}", response_model=dict)
async def update_app(
    app_id: str,
    request: UpdateAppRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update app"""
    try:
        app = db.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.tenant_id
        ).first()
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App not found"
            )
        
        if request.name:
            app.name = request.name
        if request.icon:
            app.icon = request.icon
        if request.description:
            app.description = request.description
        
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in update_app: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update app: {str(e)}"
        )


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete app"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in delete_app: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete app: {str(e)}"
        )


@router.get("/{app_id}/model-config", response_model=dict)
async def get_app_model_config(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app model configuration"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_app_model_config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model config: {str(e)}"
        )


@router.post("/{app_id}/model-config", response_model=dict)
async def update_app_model_config(
    app_id: str,
    config: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update app model configuration"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in update_app_model_config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update model config: {str(e)}"
        )


@router.get("/{app_id}/statistics", response_model=dict)
async def get_app_statistics(
    app_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app statistics"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_app_statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
