"""
API Token Model - Simplified
"""
from sqlalchemy import Column, String, Enum as SQLEnum, DateTime
import enum
from .base import BaseModel


class TokenType(str, enum.Enum):
    API = "api"
    APP = "app"


class ApiToken(BaseModel):
    __tablename__ = "api_tokens"

    token = Column(String, unique=True, nullable=False)
    type = Column(SQLEnum(TokenType), nullable=False)
    user_id = Column(String, nullable=True)
    app_id = Column(String, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ApiToken {self.type}>"
