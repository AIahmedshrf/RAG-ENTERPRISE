"""
Conversation Model - Simplified
"""
from sqlalchemy import Column, String, Enum as SQLEnum
import enum
from .base import BaseModel


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Conversation(BaseModel):
    __tablename__ = "conversations"
    __table_args__ = {'extend_existing': True}

    app_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    summary = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Conversation {self.id}>"
