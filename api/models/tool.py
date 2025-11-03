"""
Tool and ToolProvider Models - Simplified
"""
from sqlalchemy import Column, String, Text, JSON, Enum as SQLEnum
import enum
from .base import BaseModel


class ToolType(str, enum.Enum):
    BUILTIN = "builtin"
    API = "api"
    WORKFLOW = "workflow"


class Tool(BaseModel):
    __tablename__ = "tools"

    name = Column(String, nullable=False)
    type = Column(SQLEnum(ToolType), nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    tenant_id = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Tool {self.name}>"


class ToolProvider(BaseModel):
    __tablename__ = "tool_providers"

    name = Column(String, nullable=False)
    credentials = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<ToolProvider {self.name}>"
