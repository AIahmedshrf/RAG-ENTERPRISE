"""
Enhanced User Management Routes with RBAC Support
Includes role and permission management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
import uuid

from api.database import get_db
from api.models.user import User, UserStatus
from api.models.role import Role, RolePermission, Permission
from core.auth import AuthService, get_current_user, require_admin
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/users")


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class PermissionResponse(BaseModel):
    """Permission response schema"""
    id: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Role response schema"""
    id: str
    name: str
    description: Optional[str] = None
    is_system: bool
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class UserRoleResponse(BaseModel):
    """User with role and permissions"""
    id: str
    email: str
    name: str
    is_active: bool
    is_verified: bool
    status: str
    role: Optional[RoleResponse] = None
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    """Assign role to user"""
    role_id: str = Field(..., description="Role ID to assign")


class CreateUserRequest(BaseModel):
    """Create new user"""
    email: EmailStr
    name: str
    password: str = Field(..., min_length=6)
    role_id: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Update user"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[str] = None
    is_active: Optional[bool] = None


class BulkActionRequest(BaseModel):
    """Bulk action on users"""
    user_ids: List[str]
    action: str = Field(..., description="Action: assign_role, deactivate, activate")
    role_id: Optional[str] = None


# ============================================================================
# LIST USERS WITH ROLES
# ============================================================================

@router.get("", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users with their roles and permissions
    """
    try:
        # Build query
        query = db.query(User).filter(
            User.tenant_id == current_user.tenant_id
        )
        
        # Apply filters
        if search:
            query = query.filter(
                (User.email.ilike(f"%{search}%")) |
                (User.name.ilike(f"%{search}%"))
            )
        
        if role_filter:
            query = query.filter(User.role_id == role_filter)
        
        if status_filter:
            query = query.filter(User.status == status_filter)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        users = query.offset(skip).limit(limit).all()
        
        # Build response with roles
        users_data = []
        for user in users:
            role_data = None
            if user.role:
                # Get permissions for this role
                role_perms = db.query(Permission).join(
                    RolePermission
                ).filter(
                    RolePermission.role_id == user.role_id
                ).all()
                
                role_data = {
                    "id": user.role.id,
                    "name": user.role.name,
                    "description": user.role.description,
                    "is_system": user.role.is_system,
                    "permissions": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "resource": p.resource,
                            "action": p.action,
                            "description": p.description
                        }
                        for p in role_perms
                    ]
                }
            
            users_data.append({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "status": user.status.value if user.status else "active",
                "role": role_data,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            })
        
        return {
            "data": users_data,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
    
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


# ============================================================================
# GET USER DETAILS
# ============================================================================

@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed user information with roles and permissions"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get role and permissions
        role_data = None
        if user.role:
            role_perms = db.query(Permission).join(
                RolePermission
            ).filter(
                RolePermission.role_id == user.role_id
            ).all()
            
            role_data = {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description,
                "is_system": user.role.is_system,
                "permissions": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "resource": p.resource,
                        "action": p.action,
                        "description": p.description
                    }
                    for p in role_perms
                ]
            }
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "status": user.status.value if user.status else "active",
            "role": role_data,
            "timezone": user.timezone,
            "language": user.language,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


# ============================================================================
# CREATE USER
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user"""
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Validate role if provided
        role_id = request.role_id
        if role_id:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role ID"
                )
        else:
            # Assign default 'user' role
            default_role = db.query(Role).filter(Role.name == "user").first()
            role_id = default_role.id if default_role else None
        
        # Create user
        new_user = User(
            id=str(uuid.uuid4()),
            email=request.email,
            name=request.name,
            password_hash=AuthService.get_password_hash(request.password),
            role_id=role_id,
            tenant_id=current_user.tenant_id,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created: {new_user.email}")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "role_id": new_user.role_id,
            "message": "User created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


# ============================================================================
# UPDATE USER
# ============================================================================

@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user information"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        if request.name:
            user.name = request.name
        
        if request.email:
            # Check if new email is already in use
            existing = db.query(User).filter(
                User.email == request.email,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = request.email
        
        if request.role_id:
            role = db.query(Role).filter(Role.id == request.role_id).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role ID"
                )
            user.role_id = request.role_id
        
        if request.is_active is not None:
            user.is_active = request.is_active
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.email}")
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role_id": user.role_id,
            "is_active": user.is_active,
            "message": "User updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


# ============================================================================
# ASSIGN ROLE TO USER
# ============================================================================

@router.put("/{user_id}/role", response_model=dict)
async def assign_role(
    user_id: str,
    request: AssignRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Assign a role to a user"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        role = db.query(Role).filter(Role.id == request.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found"
            )
        
        user.role_id = request.role_id
        db.commit()
        db.refresh(user)
        
        # Get role with permissions
        role_perms = db.query(Permission).join(
            RolePermission
        ).filter(
            RolePermission.role_id == role.id
        ).all()
        
        logger.info(f"Role assigned to user {user.email}: {role.name}")
        
        return {
            "id": user.id,
            "email": user.email,
            "role_id": user.role_id,
            "role_name": role.name,
            "permissions_count": len(role_perms),
            "message": f"Role '{role.name}' assigned successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error assigning role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign role: {str(e)}"
        )


# ============================================================================
# DELETE USER
# ============================================================================

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user"""
    try:
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
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
        
        logger.info(f"User deleted: {user.email}")
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


# ============================================================================
# BULK ACTIONS
# ============================================================================

@router.post("/bulk/action", response_model=dict)
async def bulk_action(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Perform bulk actions on users"""
    try:
        if not request.user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No users selected"
            )
        
        users = db.query(User).filter(
            User.id.in_(request.user_ids),
            User.tenant_id == current_user.tenant_id
        ).all()
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found"
            )
        
        count = 0
        
        if request.action == "assign_role":
            if not request.role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="role_id required for assign_role action"
                )
            
            role = db.query(Role).filter(Role.id == request.role_id).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role not found"
                )
            
            for user in users:
                user.role_id = request.role_id
                count += 1
        
        elif request.action == "deactivate":
            for user in users:
                if user.id != current_user.id:
                    user.is_active = False
                    count += 1
        
        elif request.action == "activate":
            for user in users:
                user.is_active = True
                count += 1
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action: {request.action}"
            )
        
        db.commit()
        logger.info(f"Bulk action '{request.action}' performed on {count} users")
        
        return {
            "count": count,
            "action": request.action,
            "message": f"Action performed on {count} users"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk action: {str(e)}"
        )
