"""
Enhanced Authentication Middleware
"""
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
from functools import wraps

from api.database import get_db
from api.models import User, ApiToken
from core.config import settings
from utilities.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.security.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.security.secret_key,
            algorithm=settings.security.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.security.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.security.secret_key,
            algorithm=settings.security.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.security.secret_key,
                algorithms=[settings.security.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    
    # Try JWT token first
    try:
        payload = AuthMiddleware.decode_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        
    except HTTPException:
        # Try API token
        api_token = db.query(ApiToken).filter(
            ApiToken.token == token,
            ApiToken.is_active == True,
            ApiToken.type == 'user'
        ).first()
        
        if not api_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        api_token.last_used_at = datetime.utcnow().isoformat()
        db.commit()
        
        user = db.query(User).filter(User.id == api_token.user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_permissions(required_permissions: List[str]):
    """Decorator to require specific permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user') or kwargs.get('user')
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            for permission in required_permissions:
                resource, action = permission.split(':')
                if not user.has_permission(resource, action):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required permission: {permission}"
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class PermissionChecker:
    """Permission checker dependency"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    async def __call__(self, user: User = Depends(get_current_user)):
        for permission in self.required_permissions:
            resource, action = permission.split(':')
            if not user.has_permission(resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}"
                )
        return user
