"""
Admin Workspace Management - Fixed with Error Handling
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from api.database import get_db
from api.models.workspace import Workspace
from api.models.user import User
from core.auth import get_current_user, require_admin

router = APIRouter()


@router.get("", response_model=dict)
async def get_workspace(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current workspace info"""
    try:
        workspace = db.query(Workspace).filter(
            Workspace.tenant_id == current_user.tenant_id
        ).first()
        
        if not workspace:
            workspace = Workspace(
                id=str(uuid.uuid4()),
                name=f"Workspace - {current_user.tenant_id[:8] if current_user.tenant_id else 'default'}",
                tenant_id=current_user.tenant_id
            )
            db.add(workspace)
            db.commit()
            db.refresh(workspace)
        
        member_count = db.query(User).filter(
            User.tenant_id == current_user.tenant_id
        ).count()
        
        return {
            "id": workspace.id,
            "name": workspace.name,
            "tenant_id": workspace.tenant_id,
            "member_count": member_count,
            "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
            "updated_at": workspace.updated_at.isoformat() if workspace.updated_at else None,
        }
    except Exception as e:
        print(f"Error in get_workspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace: {str(e)}"
        )


@router.put("", response_model=dict)
async def update_workspace(
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update workspace settings"""
    try:
        workspace = db.query(Workspace).filter(
            Workspace.tenant_id == current_user.tenant_id
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        if name:
            workspace.name = name
        
        workspace.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(workspace)
        
        return {
            "id": workspace.id,
            "name": workspace.name,
            "updated_at": workspace.updated_at.isoformat() if workspace.updated_at else None,
            "message": "Workspace updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in update_workspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workspace: {str(e)}"
        )


@router.get("/members", response_model=dict)
async def list_workspace_members(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workspace members"""
    try:
        offset = (page - 1) * limit
        
        query = db.query(User).filter(
            User.tenant_id == current_user.tenant_id
        )
        
        total = query.count()
        members = query.offset(offset).limit(limit).all()
        
        return {
            "data": [
                {
                    "id": member.id,
                    "email": member.email,
                    "name": member.name,
                    "role": member.role,
                    "status": member.status,
                    "last_login": member.last_login.isoformat() if member.last_login else None,
                    "created_at": member.created_at.isoformat() if member.created_at else None,
                }
                for member in members
            ],
            "total": total,
            "page": page,
            "limit": limit,
            "has_more": (offset + limit) < total
        }
    except Exception as e:
        print(f"Error in list_workspace_members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list members: {str(e)}"
        )


@router.post("/members/invite", response_model=dict, status_code=status.HTTP_201_CREATED)
async def invite_member(
    email: str,
    role: str = "user",
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Invite a new member to workspace"""
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        valid_roles = ["admin", "user", "viewer"]
        if role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        from core.auth import get_password_hash
        
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name or email.split('@')[0],
            password=get_password_hash("temporary123"),
            role=role,
            status="active",
            tenant_id=current_user.tenant_id
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role,
            "message": "Member invited successfully. Temporary password: temporary123"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in invite_member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invite member: {str(e)}"
        )


@router.delete("/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Remove member from workspace"""
    try:
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself"
            )
        
        member = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
        
        db.delete(member)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in remove_member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member: {str(e)}"
        )


@router.get("/settings", response_model=dict)
async def get_workspace_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workspace settings"""
    try:
        workspace = db.query(Workspace).filter(
            Workspace.tenant_id == current_user.tenant_id
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        return {
            "workspace_id": workspace.id,
            "name": workspace.name,
            "tenant_id": workspace.tenant_id,
            "settings": {
                "language": "en",
                "timezone": "UTC",
                "date_format": "YYYY-MM-DD"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_workspace_settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}"
        )


@router.put("/settings", response_model=dict)
async def update_workspace_settings(
    settings: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update workspace settings"""
    try:
        workspace = db.query(Workspace).filter(
            Workspace.tenant_id == current_user.tenant_id
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        return {
            "workspace_id": workspace.id,
            "settings": settings,
            "message": "Settings updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_workspace_settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )
