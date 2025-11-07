"""
Role and Permission Models - Simplified
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import BaseModel

# Association table for role-permission many-to-many relationship
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', String, ForeignKey('permissions.id'), primary_key=True)
)


class Role(BaseModel):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}

    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    
    # Permissions relationship only (removed users relationship)
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )
    
    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(BaseModel):
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}

    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    resource = Column(String)
    action = Column(String)
    
    # Roles relationship
    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
    
    def __repr__(self):
        return f"<Permission {self.name}>"


# Deprecated - using association table instead
class RolePermission(BaseModel):
    __tablename__ = "role_permission_deprecated"
    __table_args__ = {'extend_existing': True}
    
    role_id = Column(String)
    permission_id = Column(String)
