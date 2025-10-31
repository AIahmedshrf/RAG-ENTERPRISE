"""
Role and Permission Models for RBAC
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Role(BaseModel):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(String(500))
    is_system = Column(Boolean, default=False)
    
    # Relationships
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(BaseModel):
    """Permission model"""
    __tablename__ = 'permissions'

    name = Column(String(100), nullable=False, unique=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(String(500))
    
    # Relationships
    roles = relationship("RolePermission", back_populates="permission")

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name})>"


class RolePermission(BaseModel):
    """Many-to-many relationship between roles and permissions"""
    __tablename__ = 'role_permissions'

    role_id = Column(String(36), ForeignKey('roles.id'), nullable=False)
    permission_id = Column(String(36), ForeignKey('permissions.id'), nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
