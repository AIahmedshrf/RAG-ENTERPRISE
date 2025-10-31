"""
Tenant Model for Multi-tenancy
"""
from sqlalchemy import Column, String, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel


class Tenant(BaseModel):
    """Tenant model for multi-tenant support"""
    __tablename__ = 'tenants'

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)
    
    # Limits
    max_users = Column(Integer, default=10)
    max_datasets = Column(Integer, default=50)
    max_documents = Column(Integer, default=1000)
    max_storage_gb = Column(Integer, default=10)
    
    # Settings
    settings = Column(JSON, default={})
    
    # Metadata (renamed from metadata to meta)
    meta = Column(JSON, default={})
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    datasets = relationship("Dataset", back_populates="tenant")
    apps = relationship("App", back_populates="tenant")

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, slug={self.slug})>"
