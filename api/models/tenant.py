"""
Tenant Model - Simplified
"""
from sqlalchemy import Column, String, JSON
from .base import BaseModel


class Tenant(BaseModel):
    __tablename__ = "tenants"

    name = Column(String, nullable=False)
    plan = Column(String, default="free")
    settings = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Tenant {self.name}>"
