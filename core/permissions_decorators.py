"""
Permission-based decorators for FastAPI endpoints
"""

from functools import wraps
from typing import Callable, List, Optional
from fastapi import Depends, HTTPException, status
from core.rbac import PermissionEnum, RoleEnum, has_permission, has_any_permission, has_all_permissions


def require_permission(required_permission: PermissionEnum):
    """
    Decorator to require a specific permission
    Usage:
    @app.get("/protected")
    @require_permission(PermissionEnum.AGENT_CREATE)
    async def protected_endpoint(current_user: User = Depends(get_current_user)):
        ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_role = RoleEnum(current_user.role_id or "user")
            
            if not has_permission(user_role, required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {required_permission}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_any_permission(required_permissions: List[PermissionEnum]):
    """
    Decorator to require any of the specified permissions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_role = RoleEnum(current_user.role_id or "user")
            
            if not has_any_permission(user_role, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required any of: {[p.value for p in required_permissions]}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(required_permissions: List[PermissionEnum]):
    """
    Decorator to require all of the specified permissions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_role = RoleEnum(current_user.role_id or "user")
            
            if not has_all_permissions(user_role, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required all of: {[p.value for p in required_permissions]}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_role(*roles: RoleEnum):
    """
    Decorator to require one of the specified roles
    Usage:
    @app.get("/admin")
    @require_role(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)
    async def admin_endpoint(current_user: User = Depends(get_current_user)):
        ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_role = RoleEnum(current_user.role_id or "user")
            
            if user_role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Forbidden. Required roles: {[r.value for r in roles]}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
