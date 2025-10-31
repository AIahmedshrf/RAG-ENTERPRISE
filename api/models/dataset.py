"""
Dataset Model - inspired by Dify
"""
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from .base import BaseModel, TenantMixin
import enum


class IndexingTechnique(str, enum.Enum):
    """Indexing technique for dataset"""
    HIGH_QUALITY = "high_quality"
    ECONOMY = "economy"


class Dataset(BaseModel, TenantMixin):
    """Dataset model for document collections"""
    __tablename__ = 'datasets'

    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    icon_background = Column(String(50))
    
    # Configuration
    indexing_technique = Column(
        Enum(IndexingTechnique),
        default=IndexingTechnique.HIGH_QUALITY,
        nullable=False
    )
    embedding_model = Column(String(255))
    embedding_model_provider = Column(String(100))
    
    # Metadata
    data_source_type = Column(String(50))
    
    # Statistics
    document_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    
    # Settings
    retrieval_model = Column(JSON, default={})
    
    # Relationships
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    tenant = relationship("Tenant", back_populates="datasets")
    
    created_by = Column(String(36), ForeignKey('users.id'))
    creator = relationship("User", foreign_keys=[created_by])
    
    documents = relationship("Document", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, documents={self.document_count})>"
