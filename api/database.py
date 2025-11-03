"""
Database Configuration
SQLAlchemy setup with session management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = getattr(settings, 'DATABASE_URL', 'sqlite:///./data/rag_enterprise.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
    pool_pre_ping=True,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    """
    try:
        # Import all models to register them with Base
        from api.models import (
            user, tenant, workspace, app, dataset, document,
            conversation, message, tool, workflow, role, api_token
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


__all__ = ['engine', 'SessionLocal', 'Base', 'get_db', 'init_db', 'DATABASE_URL']
