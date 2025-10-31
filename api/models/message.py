"""
Message and MessageFeedback Models
"""
from sqlalchemy import Column, String, JSON, ForeignKey, Text, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Message(BaseModel):
    """Message model"""
    __tablename__ = 'messages'

    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False)
    
    # Message content
    query = Column(Text, nullable=False)
    answer = Column(Text)
    
    # Agent info
    agent_id = Column(String(100))
    agent_mode = Column(String(50))
    
    # Model info
    model_provider = Column(String(100))
    model_id = Column(String(255))
    
    # Tokens
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost
    total_price = Column(Float, default=0.0)
    currency = Column(String(10), default='USD')
    
    # Latency
    provider_response_latency = Column(Float)
    total_latency = Column(Float)
    
    # RAG info
    retrieval_used = Column(Boolean, default=False)
    retrieval_count = Column(Integer, default=0)
    
    # Citations/sources (kept as message_metadata - no conflict)
    message_metadata = Column(JSON, default={})
    
    # Status
    status = Column(String(50), default='normal')
    error = Column(Text)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    feedbacks = relationship("MessageFeedback", back_populates="message", cascade="all, delete-orphan")
    
    created_by = Column(String(36), ForeignKey('users.id'))
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id})>"


class MessageFeedback(BaseModel):
    """Message feedback model"""
    __tablename__ = 'message_feedbacks'

    message_id = Column(String(36), ForeignKey('messages.id'), nullable=False)
    
    # Feedback
    rating = Column(String(10))
    content = Column(Text)
    
    # User
    user_id = Column(String(36), ForeignKey('users.id'))
    
    # Metadata (renamed from metadata to meta)
    meta = Column(JSON, default={})
    
    # Relationships
    message = relationship("Message", back_populates="feedbacks")
    user = relationship("User")

    def __repr__(self):
        return f"<MessageFeedback(id={self.id}, message_id={self.message_id}, rating={self.rating})>"
