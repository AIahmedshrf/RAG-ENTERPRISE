"""
Workspace Model - Simplified
"""
from sqlalchemy import Column, String
from .base import BaseModel


class Workspace(BaseModel):
    __tablename__ = "workspaces"

    name = Column(String, nullable=False)
    tenant_id = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Workspace {self.name}>"
