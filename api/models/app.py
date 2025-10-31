"""
App and AppModelConfig Models
"""
from sqlalchemy import Column, String, JSON, ForeignKey, Enum, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel, TenantMixin
import enum


class AppMode(str, enum.Enum):
    """App mode"""
    CHAT = "chat"
    AGENT_CHAT = "agent-chat"
    COMPLETION = "completion"
    WORKFLOW = "workflow"


class App(BaseModel, TenantMixin):
    """App model"""
    __tablename__ = 'apps'

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    icon_background = Column(String(50))
    
    # Mode
    mode = Column(Enum(AppMode), default=AppMode.CHAT, nullable=False)
    
    # Status
    enable_site = Column(Boolean, default=True)
    enable_api = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Model config
    model_config_id = Column(String(36))
    
    # Statistics
    conversation_count = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    
    # Relationships
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    tenant = relationship("Tenant", back_populates="apps")
    
    created_by = Column(String(36), ForeignKey('users.id'))
    creator = relationship("User", foreign_keys=[created_by])
    
    conversations = relationship("Conversation", back_populates="app", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<App(id={self.id}, name={self.name}, mode={self.mode})>"


class AppModelConfig(BaseModel):
    """App model configuration"""
    __tablename__ = 'app_model_configs'

    app_id = Column(String(36), ForeignKey('apps.id'), nullable=False)
    
    # Model
    provider = Column(String(100), nullable=False)
    model_id = Column(String(255), nullable=False)
    
    # Model parameters
    temperature = Column(Integer, default=1)
    top_p = Column(Integer, default=1)
    max_tokens = Column(Integer, default=2048)
    presence_penalty = Column(Integer, default=0)
    frequency_penalty = Column(Integer, default=0)
    
    # System prompt
    pre_prompt = Column(Text)
    
    # Agent/Tools
    agent_mode = Column(JSON, default={})
    tools = Column(JSON, default=[])
    
    # RAG settings
    retrieval_model = Column(JSON, default={})
    dataset_configs = Column(JSON, default={})
    
    # Citation
    citation = Column(Boolean, default=False)
    
    # Memory
    conversation_history_enabled = Column(Boolean, default=True)
    conversation_history_num = Column(Integer, default=5)
    
    # More settings
    more_like_this = Column(JSON, default={})
    suggested_questions = Column(JSON, default=[])
    
    # Opening statement
    opening_statement = Column(Text)
    
    # Relationships
    app = relationship("App")

    def __repr__(self):
        return f"<AppModelConfig(id={self.id}, app_id={self.app_id}, model_id={self.model_id})>"
