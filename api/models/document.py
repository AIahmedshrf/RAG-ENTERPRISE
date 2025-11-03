"""
Document and DocumentSegment Models - Simplified
"""
from sqlalchemy import Column, String, Text, Integer, Float, Enum as SQLEnum, Boolean
import enum
from .base import BaseModel


class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class DocumentType(str, enum.Enum):
    TEXT = "text"
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class Document(BaseModel):
    __tablename__ = "documents"

    name = Column(String, nullable=False)
    type = Column(SQLEnum(DocumentType), nullable=False)
    dataset_id = Column(String, nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADING)
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    file_path = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Document {self.name}>"


class DocumentSegment(BaseModel):
    __tablename__ = "document_segments"

    document_id = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    tokens = Column(Integer, default=0)
    index_node_id = Column(String, nullable=True)
    index_node_hash = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<DocumentSegment {self.document_id}:{self.position}>"
