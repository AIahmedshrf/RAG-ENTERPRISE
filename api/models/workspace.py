"""
Workspace Model - Fixed
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class Workspace(BaseModel):
    __tablename__ = "workspaces"

    name = Column(String, nullable=False)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    
    # Relationships (without members - will be accessed through User.tenant_id)
    # members relationship removed to fix the error
    
    def __repr__(self):
        return f"<Workspace {self.name}>"
