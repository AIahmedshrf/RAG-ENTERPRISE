"""
Base Model
All models inherit from this
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
import uuid

# Import Base from database - THIS IS CRITICAL
from api.database import Base


class BaseModel(Base):
    """
    Base model with common fields
    All models inherit from this
    """
    __abstract__ = True
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class TenantMixin:
    """Mixin for tenant isolation"""
    # This is just a marker, actual tenant_id is in individual models
    pass
