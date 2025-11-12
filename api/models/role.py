"""
Role and Permission Models
Enhanced with proper relationships
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from api.models.base import Base, TimestampMixin, UUIDMixin

class Role(Base, UUIDMixin, TimestampMixin):
    """Role model for RBAC"""
    
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="role", foreign_keys="User.role_id")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Role {self.name}>"

class Permission(Base, UUIDMixin, TimestampMixin):
    """Permission model"""
    
    __tablename__ = "permissions"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(50), nullable=False)  # e.g., 'dataset', 'app', 'user'
    action = Column(String(50), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    description = Column(Text, nullable=True)
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Permission {self.name}>"

class RolePermission(Base, UUIDMixin, TimestampMixin):
    """Many-to-many relationship between roles and permissions"""
    
    __tablename__ = "role_permissions"
    
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    def __repr__(self):
        return f"<RolePermission role={self.role_id} permission={self.permission_id}>"
