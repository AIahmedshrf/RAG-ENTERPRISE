"""
API Token Model
"""
from sqlalchemy import Column, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class TokenType(str, enum.Enum):
    """Token type"""
    APP = "app"
    DATASET = "dataset"
    USER = "user"


class ApiToken(BaseModel):
    """API Token model"""
    __tablename__ = 'api_tokens'

    # Token
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Type
    type = Column(Enum(TokenType), nullable=False)
    
    # Context
    app_id = Column(String(36), ForeignKey('apps.id'))
    dataset_id = Column(String(36), ForeignKey('datasets.id'))
    user_id = Column(String(36), ForeignKey('users.id'))
    
    # Info
    name = Column(String(255))
    last_used_at = Column(String(50))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    app = relationship("App")
    dataset = relationship("Dataset")
    user = relationship("User")

    def __repr__(self):
        return f"<ApiToken(id={self.id}, type={self.type}, is_active={self.is_active})>"
