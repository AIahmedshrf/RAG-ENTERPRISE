"""
Admin Workspace Management - Adapted from Dify
Manages workspace, members, and settings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.database import get_db
from api.models.workspace import Workspace
from api.models.user import User, UserStatus
from api.models.tenant import Tenant
from core.auth import get_current_user, require_admin

router = APIRouter()


# === Workspace Info ===

@router.get("/workspace")
async def get_workspace(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current workspace information"""
    workspace = db.query(Workspace)\
        .filter(Workspace.tenant_id == current_user.tenant_id)\
        .first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    return {
        "id": workspace.id,
        "name": workspace.name,
        "tenant_id": workspace.tenant_id,
        "created_at": workspace.created_at.isoformat(),
        "updated_at": workspace.updated_at.isoformat(),
    }


@router.put("/workspace")
async def update_workspace(
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update workspace information"""
    workspace = db.query(Workspace)\
        .filter(Workspace.tenant_id == current_user.tenant_id)\
        .first()
    
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
        "updated_at": workspace.updated_at.isoformat()
    }


# === Members Management ===

@router.get("/workspace/members")
async def list_members(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workspace members"""
    offset = (page - 1) * limit
    
    members = db.query(User)\
        .filter(User.tenant_id == current_user.tenant_id)\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": member.id,
            "email": member.email,
            "name": member.name,
            "status": member.status,
            "role": member.role,
            "created_at": member.created_at.isoformat(),
        }
        for member in members
    ]


@router.post("/workspace/members/invite")
async def invite_member(
    email: str,
    role: str = "member",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Invite new member to workspace"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create invitation (simplified - in production, send email)
    new_user = User(
        email=email,
        name=email.split('@')[0],
        tenant_id=current_user.tenant_id,
        role=role,
        status=UserStatus.PENDING
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "status": "invited",
        "message": "Invitation sent successfully"
    }


@router.delete("/workspace/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Remove member from workspace"""
    # Cannot remove self
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself"
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == current_user.tenant_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return None


# === Settings ===

@router.get("/workspace/settings")
async def get_workspace_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workspace settings"""
    tenant = db.query(Tenant)\
        .filter(Tenant.id == current_user.tenant_id)\
        .first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return {
        "tenant_id": tenant.id,
        "name": tenant.name,
        "plan": tenant.plan if hasattr(tenant, 'plan') else "free",
        "settings": tenant.settings if hasattr(tenant, 'settings') else {},
    }


@router.put("/workspace/settings")
async def update_workspace_settings(
    settings: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update workspace settings"""
    tenant = db.query(Tenant)\
        .filter(Tenant.id == current_user.tenant_id)\
        .first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update settings (if column exists)
    if hasattr(tenant, 'settings'):
        tenant.settings = settings
        tenant.updated_at = datetime.utcnow()
        db.commit()
    
    return {"message": "Settings updated successfully"}

