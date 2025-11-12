"""
Base Models and Mixins
Fixed datetime warnings and added BaseModel
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class UUIDMixin:
    """Mixin for UUID primary key"""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

class TimestampMixin:
    """Mixin for timestamp columns"""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

# BaseModel combines Base, UUIDMixin, and TimestampMixin
class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model class that includes:
    - SQLAlchemy Base
    - UUID primary key
    - Timestamp columns (created_at, updated_at)
    """
    __abstract__ = True  # This prevents SQLAlchemy from creating a table for BaseModel
    
    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
