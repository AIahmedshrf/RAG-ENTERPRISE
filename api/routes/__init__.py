from .health import router as health_router
from .auth import router as auth_router
from .datasets import router as datasets_router
from .documents import router as documents_router
from .conversations import router as conversations_router
from .chat import router as chat_router
from .financial import router as financial_router
from .tools import router as tools_router
from .analytics import router as analytics_router
from .admin import admin_router

__all__ = [
    'health_router',
    'auth_router',
    'datasets_router',
    'documents_router',
    'conversations_router',
    'chat_router',
    'financial_router',
    'tools_router',
    'analytics_router',
    'admin_router',
]
