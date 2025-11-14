"""
API Routes Package
"""

from . import (
    health,
    auth,
    admin,
    datasets,
    documents,
    chat,
    conversations,
    analytics,
    tools,
    knowledge,
    agents,
    workflows,
    financial,
    websocket
)

__all__ = [
    "health",
    "auth",
    "admin",
    "datasets",
    "documents",
    "chat",
    "conversations",
    "analytics",
    "tools",
    "knowledge",
    "agents",
    "workflows",
    "financial",
    "websocket"
]
