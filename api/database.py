"""
Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import config
import os

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/rag_enterprise.db"  # SQLite للتطوير
)

# Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=config.debug
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base
Base = declarative_base()


def get_db():
    """Dependency للحصول على database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """إنشاء جميع الجداول"""
    Base.metadata.create_all(bind=engine)
