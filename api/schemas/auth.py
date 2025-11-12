"""
Authentication Schemas
Pydantic models for request/response serialization
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ============================================================================
# Role Schemas
# ============================================================================

class RoleBase(BaseModel):
    """Base role schema"""
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    """Role response schema"""
    id: str
    
    class Config:
        from_attributes = True

# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    """User response schema"""
    id: str
    is_active: bool
    is_verified: bool
    status: Optional[str] = None
    role_id: Optional[str] = None
    tenant_id: str
    workspace_id: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    # Nested role (optional)
    role: Optional[RoleResponse] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    avatar: Optional[str] = None

# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str

class RefreshResponse(BaseModel):
    """Token refresh response"""
    access_token: str
    token_type: str = "bearer"

class RegisterRequest(UserCreate):
    """Registration request schema"""
    pass

class RegisterResponse(BaseModel):
    """Registration response schema"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
