"""
Database Configuration and Session Management
Enhanced with proper health checks and connection pooling
"""

from sqlalchemy import create_engine, event, text, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./rag_enterprise.db"
)

# Create engine with optimized settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        },
        poolclass=StaticPool,
        echo=False
    )
    
    # Enable WAL mode for better concurrency
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
from api.models.base import Base

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check function
def check_database_health() -> dict:
    """
    Check database connection and health
    Returns status dict
    """
    try:
        db = SessionLocal()
        # Use text() for raw SQL
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL.split("///")[-1]
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Initialize database
def init_db():
    """
    Initialize database tables
    🔧 Fixed: Import all models before create_all
    """
    try:
        # 🔥 CRITICAL: Import ALL models here to register them with Base.metadata
        from api.models.base import Base as ModelBase, BaseModel
        from api.models.user import User
        from api.models.tenant import Tenant
        from api.models.workspace import Workspace
        from api.models.role import Role, Permission, RolePermission
        from api.models.dataset import Dataset
        from api.models.document import Document, DocumentSegment
        from api.models.app import App, AppModelConfig
        from api.models.conversation import Conversation
        from api.models.message import Message, MessageFeedback
        from api.models.workflow import Workflow, WorkflowNode
        from api.models.tool import Tool
        from api.models.tool_provider import ToolProvider
        from api.models.api_token import ApiToken
        from api.models.agent import Agent
        
    # Use ModelBase from models.base instead of local Base
        logger.info("Creating database tables...")
        ModelBase.metadata.create_all(bind=engine)
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"✅ Database initialized successfully with {len(tables)} tables")
        logger.info(f"📋 Tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Drop all tables (use with caution!)
def drop_db():
    """
    Drop all database tables
    """
    try:
        from api.models.base import Base as ModelBase
        ModelBase.metadata.drop_all(bind=engine)
        logger.warning("⚠️  All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Database drop failed: {e}")
        return False

# Reset database
def reset_db():
    """
    Reset database (drop and recreate)
    """
    try:
        drop_db()
        init_db()
        logger.info("✅ Database reset successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False
