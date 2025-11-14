"""
API Routes Package
"""

from . import (
    health,
    auth,
    admin,
    admin_roles,
    datasets,
    documents,
    chat,
    conversations,
    analytics,
    tools,
    knowledge,
    agents,
    financial,
    websocket
)

__all__ = [
    "health",
    "auth",
    "admin",
    "admin_roles",
    "datasets",
    "documents",
    "chat",
    "conversations",
    "analytics",
    "tools",
    "knowledge",
    "agents",
    "financial",
    "websocket"
]
