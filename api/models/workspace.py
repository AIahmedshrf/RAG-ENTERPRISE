"""
Workspace Model
"""
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Workspace(BaseModel):
    """Workspace model for backward compatibility"""
    __tablename__ = 'workspaces'

    name = Column(String(255), nullable=False)
    description = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Settings
    settings = Column(JSON, default={})
    
    # Relationships
    members = relationship("User", back_populates="workspace")

    def __repr__(self):
        return f"<Workspace(id={self.id}, name={self.name})>"
