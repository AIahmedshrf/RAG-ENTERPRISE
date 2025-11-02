"""
User Model - Enhanced with password field
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from datetime import datetime
import enum
from .base import BaseModel


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Hashed password
    name = Column(String, nullable=True)
    role = Column(String, default="user")  # user, admin, manager
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    tenant_id = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"
