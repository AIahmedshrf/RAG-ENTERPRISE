"""
Admin Routes for Role and Permission Management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.database import get_db
from core.rbac import PermissionEnum, RoleEnum, has_permission, ROLE_PERMISSIONS
from api.models.user import User
from core.auth import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ==================== Role Management ====================

@router.get("/roles")
async def list_roles(current_user: User = Depends(get_current_user)):
    """List all available roles with their permissions"""
    if not has_permission(current_user.role or "USER", PermissionEnum.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list roles"
        )
    
    roles_data = []
    for role_enum in RoleEnum:
        permissions = ROLE_PERMISSIONS.get(role_enum, [])
        roles_data.append({
            "id": role_enum.value,
            "name": role_enum.name,
            "display_name": role_enum.name.replace("_", " ").title(),
            "permissions": [p.value for p in permissions],
            "permission_count": len(permissions)
        })
    
    return {
        "success": True,
        "data": roles_data,
        "total": len(roles_data)
    }


@router.get("/roles/{role_id}")
async def get_role_details(role_id: str, current_user: User = Depends(get_current_user)):
    """Get detailed information about a specific role"""
    if not has_permission(current_user.role or "USER", PermissionEnum.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        role_enum = RoleEnum(role_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_id}' not found"
        )
    
    permissions = ROLE_PERMISSIONS.get(role_enum, [])
    
    return {
        "success": True,
        "data": {
            "id": role_enum.value,
            "name": role_enum.name,
            "display_name": role_enum.name.replace("_", " ").title(),
            "permissions": [p.value for p in permissions],
            "description": get_role_description(role_enum)
        }
    }


# ==================== Permission Management ====================

@router.get("/permissions")
async def list_permissions(current_user: User = Depends(get_current_user)):
    """List all available permissions grouped by resource"""
    if not has_permission(current_user.role or "USER", PermissionEnum.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Group permissions by resource type
    permission_groups = {
        "user": [],
        "agent": [],
        "knowledge": [],
        "model": [],
        "dataset": [],
        "chat": [],
        "settings": [],
        "system": []
    }
    
    for perm in PermissionEnum:
        resource = perm.value.split(":")[0]
        action = perm.value.split(":")[1] if ":" in perm.value else ""
        
        if resource in permission_groups:
            permission_groups[resource].append({
                "id": perm.value,
                "name": perm.name,
                "display_name": f"{resource}:{action}",
                "resource": resource,
                "action": action
            })
    
    return {
        "success": True,
        "data": permission_groups,
        "total": len(PermissionEnum)
    }


# ==================== User-Role Assignment ====================

@router.get("/users/{user_id}/role")
async def get_user_role(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current role of a user"""
    if not has_permission(current_user.role or "USER", PermissionEnum.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_role = user.role or "USER"
    permissions = ROLE_PERMISSIONS.get(RoleEnum(user_role), [])
    
    return {
        "success": True,
        "data": {
            "user_id": user.id,
            "user_email": user.email,
            "role": user_role,
            "permissions": [p.value for p in permissions]
        }
    }


@router.put("/users/{user_id}/role")
async def assign_user_role(
    user_id: str,
    role_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a role to a user"""
    if not has_permission(current_user.role or "USER", PermissionEnum.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Validate role
    try:
        new_role = role_data.get("role", "USER").upper()
        RoleEnum(new_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {new_role}"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_role = user.role
    user.role = new_role
    db.commit()
    
    return {
        "success": True,
        "message": f"User role updated from {old_role} to {new_role}",
        "data": {
            "user_id": user.id,
            "user_email": user.email,
            "old_role": old_role,
            "new_role": new_role
        }
    }


# ==================== User Permissions ====================

@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions for a user based on their role"""
    if not has_permission(current_user.role or "USER", PermissionEnum.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_role = user.role or "USER"
    try:
        role_enum = RoleEnum(user_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {user_role}"
        )
    
    permissions = ROLE_PERMISSIONS.get(role_enum, [])
    
    # Group permissions by resource
    grouped_perms = {}
    for perm in permissions:
        resource = perm.value.split(":")[0]
        if resource not in grouped_perms:
            grouped_perms[resource] = []
        grouped_perms[resource].append(perm.value)
    
    return {
        "success": True,
        "data": {
            "user_id": user.id,
            "user_email": user.email,
            "role": user_role,
            "all_permissions": [p.value for p in permissions],
            "grouped_permissions": grouped_perms,
            "total_permissions": len(permissions)
        }
    }


# ==================== Role Statistics ====================

@router.get("/statistics/roles")
async def get_role_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics about user distribution across roles"""
    if not has_permission(current_user.role or "USER", PermissionEnum.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Count users by role
    role_stats = {}
    for role_enum in RoleEnum:
        count = db.query(User).filter(User.role == role_enum.value).count()
        role_stats[role_enum.name] = count
    
    total_users = db.query(User).count()
    
    return {
        "success": True,
        "data": {
            "total_users": total_users,
            "by_role": role_stats,
            "role_breakdown": [
                {
                    "role": role,
                    "count": count,
                    "percentage": round((count / total_users * 100) if total_users > 0 else 0, 2)
                }
                for role, count in role_stats.items()
            ]
        }
    }


# ==================== Helper Functions ====================

def get_role_description(role: RoleEnum) -> str:
    """Get a description for each role"""
    descriptions = {
        RoleEnum.SUPER_ADMIN: "Full system access with all permissions",
        RoleEnum.ADMIN: "System administration and management",
        RoleEnum.MANAGER: "Team and content management",
        RoleEnum.EDITOR: "Content creation and editing",
        RoleEnum.VIEWER: "Read-only access to system resources",
        RoleEnum.USER: "Basic user access"
    }
    return descriptions.get(role, "")
