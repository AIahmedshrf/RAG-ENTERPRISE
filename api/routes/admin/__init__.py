"""
Admin Routes Module
Adapted from Dify for RAG-ENTERPRISE
"""
from fastapi import APIRouter
from .apps import router as apps_router
from .datasets import router as datasets_router
from .workspace import router as workspace_router
from .users import router as users_router
from .roles import router as roles_router

# Create main admin router
admin_router = APIRouter()

# Include sub-routers with proper prefixes
admin_router.include_router(apps_router, prefix="/apps", tags=["Admin - Apps"])
admin_router.include_router(datasets_router, prefix="/datasets", tags=["Admin - Datasets"])
admin_router.include_router(workspace_router, prefix="/workspace", tags=["Admin - Workspace"])
admin_router.include_router(users_router, tags=["Admin - Users"])  # Users router already has /users prefix
admin_router.include_router(roles_router, tags=["Admin - Roles"])  # Roles router already has /roles prefix

# Export both names for compatibility
router = admin_router

__all__ = ['admin_router', 'router']
