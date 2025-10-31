"""
Enhanced User Model
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class UserStatus(str, enum.Enum):
    """User status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(BaseModel):
    """Enhanced User model"""
    __tablename__ = 'users'

    # Basic info
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255))
    avatar = Column(String(500))
    phone = Column(String(50))
    
    # Multi-tenancy
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    tenant = relationship("Tenant", back_populates="users")
    
    # Role
    role_id = Column(String(36), ForeignKey('roles.id'))
    role = relationship("Role", back_populates="users")
    
    # Workspace (backwards compatibility)
    workspace_id = Column(String(36), ForeignKey('workspaces.id'))
    workspace = relationship("Workspace", back_populates="members")
    
    # Status
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Preferences
    preferences = Column(JSON, default={})
    language = Column(String(10), default='en')
    timezone = Column(String(50), default='UTC')
    
    # Security
    last_login_at = Column(String(50))
    last_login_ip = Column(String(50))
    failed_login_attempts = Column(String(10), default='0')
    
    # Metadata (renamed from metadata to meta)
    meta = Column(JSON, default={})
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission"""
        if not self.role:
            return False
        
        for role_permission in self.role.permissions:
            permission = role_permission.permission
            if permission.resource == resource and permission.action == action:
                return True
        
        return False
