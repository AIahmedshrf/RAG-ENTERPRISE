"""
Advanced Role-Based Access Control System
Supports granular permissions and role hierarchy
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PermissionEnum(str, Enum):
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Agents Management
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_DEPLOY = "agent:deploy"
    
    # Knowledge Management
    KNOWLEDGE_CREATE = "knowledge:create"
    KNOWLEDGE_READ = "knowledge:read"
    KNOWLEDGE_UPDATE = "knowledge:update"
    KNOWLEDGE_DELETE = "knowledge:delete"
    KNOWLEDGE_PUBLISH = "knowledge:publish"
    
    # Models Management
    MODEL_CREATE = "model:create"
    MODEL_READ = "model:read"
    MODEL_UPDATE = "model:update"
    MODEL_DELETE = "model:delete"
    
    # Datasets Management
    DATASET_CREATE = "dataset:create"
    DATASET_READ = "dataset:read"
    DATASET_UPDATE = "dataset:update"
    DATASET_DELETE = "dataset:delete"
    
    # Chat Management
    CHAT_CREATE = "chat:create"
    CHAT_READ = "chat:read"
    CHAT_DELETE = "chat:delete"
    
    # Settings & Administration
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"
    SYSTEM_ADMIN = "system:admin"


class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    EDITOR = "editor"
    VIEWER = "viewer"
    USER = "user"


# Role Permissions Mapping
ROLE_PERMISSIONS = {
    RoleEnum.SUPER_ADMIN: [permission for permission in PermissionEnum],  # All permissions
    
    RoleEnum.ADMIN: [
        PermissionEnum.USER_CREATE,
        PermissionEnum.USER_READ,
        PermissionEnum.USER_UPDATE,
        PermissionEnum.USER_DELETE,
        PermissionEnum.AGENT_CREATE,
        PermissionEnum.AGENT_READ,
        PermissionEnum.AGENT_UPDATE,
        PermissionEnum.AGENT_DELETE,
        PermissionEnum.AGENT_DEPLOY,
        PermissionEnum.KNOWLEDGE_CREATE,
        PermissionEnum.KNOWLEDGE_READ,
        PermissionEnum.KNOWLEDGE_UPDATE,
        PermissionEnum.KNOWLEDGE_DELETE,
        PermissionEnum.KNOWLEDGE_PUBLISH,
        PermissionEnum.MODEL_READ,
        PermissionEnum.MODEL_UPDATE,
        PermissionEnum.DATASET_READ,
        PermissionEnum.DATASET_UPDATE,
        PermissionEnum.CHAT_READ,
        PermissionEnum.SETTINGS_READ,
        PermissionEnum.SETTINGS_UPDATE,
    ],
    
    RoleEnum.MANAGER: [
        PermissionEnum.USER_READ,
        PermissionEnum.AGENT_CREATE,
        PermissionEnum.AGENT_READ,
        PermissionEnum.AGENT_UPDATE,
        PermissionEnum.KNOWLEDGE_CREATE,
        PermissionEnum.KNOWLEDGE_READ,
        PermissionEnum.KNOWLEDGE_UPDATE,
        PermissionEnum.KNOWLEDGE_PUBLISH,
        PermissionEnum.MODEL_READ,
        PermissionEnum.DATASET_READ,
        PermissionEnum.CHAT_READ,
        PermissionEnum.SETTINGS_READ,
    ],
    
    RoleEnum.EDITOR: [
        PermissionEnum.AGENT_READ,
        PermissionEnum.KNOWLEDGE_CREATE,
        PermissionEnum.KNOWLEDGE_READ,
        PermissionEnum.KNOWLEDGE_UPDATE,
        PermissionEnum.MODEL_READ,
        PermissionEnum.DATASET_READ,
        PermissionEnum.CHAT_CREATE,
        PermissionEnum.CHAT_READ,
    ],
    
    RoleEnum.VIEWER: [
        PermissionEnum.AGENT_READ,
        PermissionEnum.KNOWLEDGE_READ,
        PermissionEnum.MODEL_READ,
        PermissionEnum.DATASET_READ,
        PermissionEnum.CHAT_READ,
        PermissionEnum.SETTINGS_READ,
    ],
    
    RoleEnum.USER: [
        PermissionEnum.CHAT_CREATE,
        PermissionEnum.CHAT_READ,
        PermissionEnum.KNOWLEDGE_READ,
    ],
}


# Pydantic Models
class PermissionSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: PermissionEnum
    description: str
    resource: str
    action: str
    
    class Config:
        use_enum_values = True


class RoleSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: RoleEnum
    description: str
    permissions: List[PermissionEnum]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class RoleAssignmentSchema(BaseModel):
    user_id: str
    role_id: str
    assigned_at: datetime = Field(default_factory=datetime.now)
    assigned_by: str
    reason: Optional[str] = None


# Permission Check Functions
def has_permission(user_role: RoleEnum, required_permission: PermissionEnum) -> bool:
    """Check if user role has required permission"""
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in permissions


def has_any_permission(user_role: RoleEnum, required_permissions: List[PermissionEnum]) -> bool:
    """Check if user role has any of the required permissions"""
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    return any(perm in permissions for perm in required_permissions)


def has_all_permissions(user_role: RoleEnum, required_permissions: List[PermissionEnum]) -> bool:
    """Check if user role has all of the required permissions"""
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    return all(perm in permissions for perm in required_permissions)


if __name__ == "__main__":
    import uuid
    print("RBAC System initialized")
