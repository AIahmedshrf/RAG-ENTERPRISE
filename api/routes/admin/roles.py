"""
Role and Permission Management Routes
Complete RBAC administration interface
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from api.database import get_db
from api.models.role import Role, Permission, RolePermission
from api.models.user import User
from core.auth import get_current_user, require_admin
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/roles")


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class PermissionSchema(BaseModel):
    """Permission schema"""
    id: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleSchema(BaseModel):
    """Role schema"""
    id: str
    name: str
    description: Optional[str] = None
    is_system: bool
    permissions: List[PermissionSchema] = []
    user_count: int = 0

    class Config:
        from_attributes = True


class CreateRoleRequest(BaseModel):
    """Create role request"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = []


class UpdateRoleRequest(BaseModel):
    """Update role request"""
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None


class AssignPermissionRequest(BaseModel):
    """Assign permission to role"""
    permission_id: str


class RemovePermissionRequest(BaseModel):
    """Remove permission from role"""
    permission_id: str


# ============================================================================
# LIST ROLES
# ============================================================================

@router.get("", response_model=dict)
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all roles with their permissions"""
    try:
        query = db.query(Role)
        
        if search:
            query = query.filter(Role.name.ilike(f"%{search}%"))
        
        total = query.count()
        roles = query.offset(skip).limit(limit).all()
        
        roles_data = []
        for role in roles:
            # Get permissions for this role
            perms = db.query(Permission).join(
                RolePermission
            ).filter(
                RolePermission.role_id == role.id
            ).all()
            
            # Get user count for this role
            user_count = db.query(User).filter(User.role_id == role.id).count()
            
            roles_data.append({
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "is_system": role.is_system,
                "permissions": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "resource": p.resource,
                        "action": p.action,
                        "description": p.description
                    }
                    for p in perms
                ],
                "user_count": user_count,
                "permission_count": len(perms)
            })
        
        return {
            "data": roles_data,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
    
    except Exception as e:
        logger.error(f"Error listing roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list roles: {str(e)}"
        )


# ============================================================================
# GET ROLE DETAILS
# ============================================================================

@router.get("/{role_id}", response_model=dict)
async def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get role with all permissions and users"""
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Get permissions
        perms = db.query(Permission).join(
            RolePermission
        ).filter(
            RolePermission.role_id == role_id
        ).all()
        
        # Get users with this role
        users = db.query(User).filter(User.role_id == role_id).all()
        
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_system": role.is_system,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None,
            "permissions": [
                {
                    "id": p.id,
                    "name": p.name,
                    "resource": p.resource,
                    "action": p.action,
                    "description": p.description
                }
                for p in perms
            ],
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "name": u.name
                }
                for u in users
            ],
            "user_count": len(users),
            "permission_count": len(perms)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get role: {str(e)}"
        )


# ============================================================================
# CREATE ROLE
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_role(
    request: CreateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new role"""
    try:
        # Check if role already exists
        existing = db.query(Role).filter(Role.name == request.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{request.name}' already exists"
            )
        
        # Create role
        role = Role(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            is_system=False
        )
        
        db.add(role)
        db.commit()
        db.refresh(role)
        
        # Assign permissions if provided
        for perm_id in request.permission_ids:
            perm = db.query(Permission).filter(Permission.id == perm_id).first()
            if perm:
                role_perm = RolePermission(
                    id=str(uuid.uuid4()),
                    role_id=role.id,
                    permission_id=perm.id
                )
                db.add(role_perm)
        
        db.commit()
        logger.info(f"Role created: {request.name}")
        
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permission_count": len(request.permission_ids),
            "message": "Role created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


# ============================================================================
# UPDATE ROLE
# ============================================================================

@router.put("/{role_id}", response_model=dict)
async def update_role(
    role_id: str,
    request: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update role details and permissions"""
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        if role.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify system roles"
            )
        
        # Update description
        if request.description is not None:
            role.description = request.description
        
        # Update permissions if provided
        if request.permission_ids is not None:
            # Remove old permissions
            db.query(RolePermission).filter(
                RolePermission.role_id == role_id
            ).delete()
            
            # Add new permissions
            for perm_id in request.permission_ids:
                perm = db.query(Permission).filter(Permission.id == perm_id).first()
                if perm:
                    role_perm = RolePermission(
                        id=str(uuid.uuid4()),
                        role_id=role.id,
                        permission_id=perm.id
                    )
                    db.add(role_perm)
        
        role.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(role)
        
        logger.info(f"Role updated: {role.name}")
        
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "message": "Role updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )


# ============================================================================
# ASSIGN PERMISSION TO ROLE
# ============================================================================

@router.post("/{role_id}/permissions", status_code=status.HTTP_201_CREATED, response_model=dict)
async def assign_permission(
    role_id: str,
    request: AssignPermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Add a permission to a role"""
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        permission = db.query(Permission).filter(
            Permission.id == request.permission_id
        ).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Check if already assigned
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == request.permission_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already assigned to this role"
            )
        
        # Assign permission
        role_perm = RolePermission(
            id=str(uuid.uuid4()),
            role_id=role_id,
            permission_id=request.permission_id
        )
        db.add(role_perm)
        db.commit()
        
        logger.info(f"Permission '{permission.name}' assigned to role '{role.name}'")
        
        return {
            "role_id": role_id,
            "permission_id": request.permission_id,
            "permission_name": permission.name,
            "message": "Permission assigned successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error assigning permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign permission: {str(e)}"
        )


# ============================================================================
# REMOVE PERMISSION FROM ROLE
# ============================================================================

@router.delete("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Remove a permission from a role"""
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        role_perm = db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()
        
        if not role_perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not assigned to this role"
            )
        
        db.delete(role_perm)
        db.commit()
        
        logger.info(f"Permission removed from role '{role.name}'")
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove permission: {str(e)}"
        )


# ============================================================================
# LIST PERMISSIONS
# ============================================================================

@router.get("/permissions/list", response_model=dict)
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    resource_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available permissions"""
    try:
        query = db.query(Permission)
        
        if resource_filter:
            query = query.filter(Permission.resource == resource_filter)
        
        total = query.count()
        permissions = query.offset(skip).limit(limit).all()
        
        # Group by resource
        grouped = {}
        for perm in permissions:
            if perm.resource not in grouped:
                grouped[perm.resource] = []
            grouped[perm.resource].append({
                "id": perm.id,
                "name": perm.name,
                "action": perm.action,
                "description": perm.description
            })
        
        return {
            "data": grouped,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error listing permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list permissions: {str(e)}"
        )


# ============================================================================
# GET PERMISSION MATRIX
# ============================================================================

@router.get("/matrix/all", response_model=dict)
async def get_permission_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get complete permission matrix for all roles"""
    try:
        roles = db.query(Role).all()
        permissions = db.query(Permission).all()
        
        # Build matrix
        matrix = {}
        for role in roles:
            role_perms = db.query(Permission).join(
                RolePermission
            ).filter(
                RolePermission.role_id == role.id
            ).all()
            
            matrix[role.name] = {
                "id": role.id,
                "description": role.description,
                "is_system": role.is_system,
                "permissions": {p.name: True for p in role_perms},
                "permission_count": len(role_perms)
            }
        
        return {
            "roles": matrix,
            "total_permissions": len(permissions),
            "total_roles": len(roles),
            "resources": list(set(p.resource for p in permissions))
        }
    
    except Exception as e:
        logger.error(f"Error getting permission matrix: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get permission matrix: {str(e)}"
        )
