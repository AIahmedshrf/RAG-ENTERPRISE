"""
Tool Provider Model
"""
from sqlalchemy import Column, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from api.models.base import Base


class ToolProvider(Base):
    """Tool Provider"""
    __tablename__ = "tool_providers"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    credentials = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
