"""
Workspace Model
"""

from sqlalchemy import Column, String, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from api.models.base import Base, TimestampMixin, UUIDMixin

class Workspace(Base, UUIDMixin, TimestampMixin):
    """Workspace model for organizing users and resources"""
    
    __tablename__ = "workspaces"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    
    # Limits
    max_users = Column(Integer, default=10, nullable=False)
    max_datasets = Column(Integer, default=50, nullable=False)
    max_apps = Column(Integer, default=20, nullable=False)
    
    # Settings
    settings = Column(Text, nullable=True)  # JSON string
    
    def __repr__(self):
        return f"<Workspace {self.name}>"
