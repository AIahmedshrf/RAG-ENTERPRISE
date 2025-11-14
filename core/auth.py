"""
Authentication and Authorization Service
Enhanced with proper password handling and FastAPI dependencies
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.models.user import User
from api.database import get_db
import os

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-use-strong-secret")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()

class AuthService:
    """Authentication service"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
        """Verify JWT token"""
        try:
            secret = REFRESH_SECRET_KEY if token_type == "refresh" else SECRET_KEY
            payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
            
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        
        return user
    
    @staticmethod
    def get_user_from_token(db: Session, token: str) -> Optional[User]:
        """Get current user from token"""
        payload = AuthService.verify_token(token, token_type="access")
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        payload = AuthService.verify_token(refresh_token, token_type="refresh")
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Verify user still exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return None
        
        # Create new access token
        access_token = AuthService.create_access_token(data={"sub": user.id})
        return access_token
    
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        name: Optional[str] = None,
        tenant_id: str = None
    ) -> User:
        """Create new user"""
        # Hash password
        hashed_password = AuthService.get_password_hash(password)
        
        # Create user
        user = User(
            email=email,
            password_hash=hashed_password,
            name=name,
            tenant_id=tenant_id,
            is_active=True,
            is_verified=False,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user


# ============================================================================
# FastAPI Dependencies
# ============================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        user = AuthService.get_user_from_token(db, token)
        
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception:
        raise credentials_exception


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency to get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get current admin user
    """
    # Check if user has admin role
    if current_user.role and current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to require admin permissions
    Checks for super_admin or admin role
    """
    # Check if user has admin or super_admin role
    if not current_user.role or current_user.role.name not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    
    return current_user


# Optional: Simple dependency without bearer token (for endpoints that accept optional auth)
def get_optional_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    FastAPI dependency to get optional current user
    Returns None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = AuthService.get_user_from_token(db, token)
        return user
    except Exception:
        return None


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "AuthService",
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "require_admin",
    "get_optional_current_user",
    "security",
]
