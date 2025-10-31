"""
Conversation Model
"""
from sqlalchemy import Column, String, JSON, ForeignKey, Enum, Text, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class ConversationStatus(str, enum.Enum):
    """Conversation status"""
    NORMAL = "normal"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Conversation(BaseModel):
    """Conversation model"""
    __tablename__ = 'conversations'

    # App context
    app_id = Column(String(36), ForeignKey('apps.id'))
    
    # User info
    user_id = Column(String(36), ForeignKey('users.id'))
    
    # Conversation info
    name = Column(String(255))
    status = Column(Enum(ConversationStatus), default=ConversationStatus.NORMAL)
    
    # Summary
    summary = Column(Text)
    summary_model = Column(String(255))
    
    # Statistics
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # First message
    first_message = Column(Text)
    first_message_id = Column(String(36))
    
    # Metadata (renamed from metadata to meta)
    meta = Column(JSON, default={})
    
    # Agent/mode
    mode = Column(String(50))
    agent_id = Column(String(100))
    
    # Relationships
    app = relationship("App", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, messages={self.message_count})>"
