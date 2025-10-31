"""
Document and DocumentSegment Models
"""
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Enum, Text, Boolean, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    WAITING = "waiting"
    PARSING = "parsing"
    CLEANING = "cleaning"
    SPLITTING = "splitting"
    INDEXING = "indexing"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"


class DocumentType(str, enum.Enum):
    """Document type"""
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"


class Document(BaseModel):
    """Document model"""
    __tablename__ = 'documents'

    dataset_id = Column(String(36), ForeignKey('datasets.id'), nullable=False)
    
    # File info
    name = Column(String(255), nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)
    file_size = Column(Integer)
    file_path = Column(String(500))
    file_hash = Column(String(64))
    
    # Processing
    status = Column(Enum(DocumentStatus), default=DocumentStatus.WAITING, nullable=False)
    error_message = Column(Text)
    processing_started_at = Column(String(50))
    processing_completed_at = Column(String(50))
    
    # Content
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    
    # Indexing
    indexing_latency = Column(Float)
    segment_count = Column(Integer, default=0)
    
    # Metadata (renamed from metadata to meta)
    meta = Column(JSON, default={})
    
    # Batch info
    batch_id = Column(String(36))
    position = Column(Integer)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="documents")
    segments = relationship("DocumentSegment", back_populates="document", cascade="all, delete-orphan")
    
    created_by = Column(String(36), ForeignKey('users.id'))
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Document(id={self.id}, name={self.name}, status={self.status})>"


class DocumentSegment(BaseModel):
    """Document segment (chunk) model"""
    __tablename__ = 'document_segments'

    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False)
    dataset_id = Column(String(36), ForeignKey('datasets.id'), nullable=False)
    
    # Position
    position = Column(Integer, nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    word_count = Column(Integer)
    character_count = Column(Integer)
    
    # Tokens
    tokens = Column(Integer)
    
    # Vector
    index_node_id = Column(String(255))
    index_node_hash = Column(String(64))
    
    # Status
    status = Column(String(50), default='completed')
    enabled = Column(Boolean, default=True)
    disabled_at = Column(String(50))
    disabled_by = Column(String(36), ForeignKey('users.id'))
    
    # Metadata (renamed from metadata to meta)
    meta = Column(JSON, default={})
    
    # Hit count
    hit_count = Column(Integer, default=0)
    
    # Relationships
    document = relationship("Document", back_populates="segments")
    dataset = relationship("Dataset")

    def __repr__(self):
        return f"<DocumentSegment(id={self.id}, document_id={self.document_id}, position={self.position})>"
