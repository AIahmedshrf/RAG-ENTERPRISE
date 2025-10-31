"""
Base Model with common fields
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class TenantMixin:
    """Mixin for multi-tenant models"""
    tenant_id = Column(String(36), nullable=False, index=True)
