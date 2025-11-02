"""
Admin Routes Module
Adapted from Dify for RAG-ENTERPRISE
"""
from fastapi import APIRouter
from .apps import router as apps_router
from .datasets import router as datasets_router
from .workspace import router as workspace_router

# Create main admin router
admin_router = APIRouter()

# Include sub-routers
admin_router.include_router(apps_router, prefix="/apps", tags=["Admin - Apps"])
admin_router.include_router(datasets_router, prefix="/datasets", tags=["Admin - Datasets"])
admin_router.include_router(workspace_router, prefix="/workspace", tags=["Admin - Workspace"])

# Export both names for compatibility
router = admin_router

__all__ = ['admin_router', 'router']
