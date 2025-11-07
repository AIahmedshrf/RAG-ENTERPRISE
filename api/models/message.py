"""
Message and MessageFeedback Models - Fixed (metadata renamed)
"""
from sqlalchemy import Column, String, Text, JSON, Float
from .base import BaseModel


class Message(BaseModel):
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}

    conversation_id = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    message_metadata = Column(JSON, nullable=True)  # Changed from 'metadata' to 'message_metadata'
    
    def __repr__(self):
        return f"<Message {self.id}>"


class MessageFeedback(BaseModel):
    __tablename__ = "message_feedbacks"
    __table_args__ = {'extend_existing': True}

    message_id = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    content = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<MessageFeedback {self.message_id}>"
