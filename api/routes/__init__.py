"""
API Routes Package
"""
from .auth import router as auth_router
from .documents import router as documents_router
from .datasets import router as datasets_router
from .chat import router as chat_router
from .conversations import router as conversations_router
from .financial import router as financial_router
from .tools import router as tools_router
from .analytics import router as analytics_router
from .admin import router as admin_router
from .health import router as health_router

__all__ = [
    'auth_router',
    'documents_router',
    'datasets_router',
    'chat_router',
    'conversations_router',
    'financial_router',
    'tools_router',
    'analytics_router',
    'admin_router',
    'health_router'
]