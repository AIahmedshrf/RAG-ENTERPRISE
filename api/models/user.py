"""
User Model
Enhanced with proper password handling and relationships
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from api.models.base import Base, TimestampMixin, UUIDMixin
from datetime import datetime, timezone
import enum

# User Status Enum
class UserStatus(str, enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class User(Base, UUIDMixin, TimestampMixin):
    """User model with authentication and authorization"""
    
    __tablename__ = "users"
    
    # Basic Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    avatar = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Role and Permissions
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    
    # Tenant and Workspace
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=True)
    
    # Additional Info
    phone = Column(String(50), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Authentication
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    
    # Metadata
    bio = Column(Text, nullable=True)
    user_metadata = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    role = relationship("Role", back_populates="users", foreign_keys=[role_id])
    tenant = relationship("Tenant", back_populates="users", foreign_keys=[tenant_id])
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "status": self.status.value if self.status else None,
            "role_id": self.role_id,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "timezone": self.timezone,
            "language": self.language,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
