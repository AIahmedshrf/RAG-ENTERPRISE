"""
User Model - Simplified (No complex relationships)
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
    __table_args__ = {'extend_existing': True}

    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, default="user")  # Simple string: "user", "admin", "manager"
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    tenant_id = Column(String, nullable=True)  # Simple reference, no FK
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == "admin"
    
    def is_active(self):
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE
