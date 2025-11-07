"""
Document Segment Model - Fixed
Stores text chunks with embeddings
"""
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from api.models.base import Base


class DocumentSegment(Base):
    """Document Segment - Text chunks from documents"""
    __tablename__ = "document_segments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    
    # Stats
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    
    # Embeddings (stored as JSON for now)
    embedding = Column(JSON, nullable=True)
    
    # Metadata - RENAMED from 'metadata' to avoid SQLAlchemy conflict
    meta_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
