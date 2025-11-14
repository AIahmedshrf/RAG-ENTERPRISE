"""
App and AppModelConfig Models - Simplified
"""
from sqlalchemy import Column, String, Text, JSON, Enum as SQLEnum
import enum
from .base import BaseModel


class AppMode(str, enum.Enum):
    CHAT = "chat"
    AGENT = "agent"
    AGENT_CHAT = "agent-chat"
    WORKFLOW = "workflow"
    COMPLETION = "completion"


class App(BaseModel):
    __tablename__ = "apps"
    __table_args__ = {'extend_existing': True}

    name = Column(String, nullable=False)
    mode = Column(SQLEnum(AppMode), nullable=False)
    icon = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tenant_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    model_config = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<App {self.name}>"


class AppModelConfig(BaseModel):
    __tablename__ = "app_model_configs"
    __table_args__ = {'extend_existing': True}

    app_id = Column(String, nullable=False)
    provider = Column(String)
    model_name = Column(String)
    configs = Column(JSON)
    
    def __repr__(self):
        return f"<AppModelConfig {self.app_id}>"
