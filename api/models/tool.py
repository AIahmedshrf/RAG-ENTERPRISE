"""
Tool and ToolProvider Models
"""
from sqlalchemy import Column, String, JSON, Text, Boolean, Integer, Enum
from .base import BaseModel, TenantMixin
import enum


class ToolType(str, enum.Enum):
    """Tool type"""
    BUILTIN = "builtin"
    CUSTOM = "custom"
    API = "api"


class Tool(BaseModel, TenantMixin):
    """Tool model"""
    __tablename__ = 'tools'

    # Basic info
    name = Column(String(255), nullable=False)
    label = Column(JSON, nullable=False)
    description = Column(JSON)
    icon = Column(String(255))
    
    # Type
    type = Column(Enum(ToolType), default=ToolType.CUSTOM, nullable=False)
    
    # Provider
    provider_id = Column(String(100))
    provider_type = Column(String(100))
    
    # Parameters
    parameters = Column(JSON, default=[])
    
    # Configuration
    config = Column(JSON, default={})
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Privacy
    privacy_policy = Column(String(500))
    
    # Statistics
    usage_count = Column(Integer, default=0)
    
    # Relationships
    tenant_id = Column(String(36), nullable=True)

    def __repr__(self):
        return f"<Tool(id={self.id}, name={self.name}, type={self.type})>"


class ToolProvider(BaseModel):
    """Tool provider model"""
    __tablename__ = 'tool_providers'

    # Basic info
    name = Column(String(100), nullable=False, unique=True)
    label = Column(JSON, nullable=False)
    description = Column(JSON)
    icon = Column(String(255))
    
    # Type
    type = Column(String(50), default='api')
    
    # Credentials
    credentials_schema = Column(JSON, default={})
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Tools list
    tools = Column(JSON, default=[])

    def __repr__(self):
        return f"<ToolProvider(id={self.id}, name={self.name})>"
