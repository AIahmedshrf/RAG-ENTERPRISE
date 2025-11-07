"""
Document Models - Complete with all file types
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, Enum as SQLEnum
import enum
from .base import BaseModel


class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class DocumentType(str, enum.Enum):
    """All supported document types"""
    TEXT = "text"
    TXT = "txt"
    PDF = "pdf"
    WORD = "word"
    DOC = "doc"
    DOCX = "docx"
    EXCEL = "excel"
    XLS = "xls"
    XLSX = "xlsx"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"
    MD = "md"
    HTML = "html"
    XML = "xml"


class Document(BaseModel):
    __tablename__ = "documents"
    __table_args__ = {'extend_existing': True}

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
    __table_args__ = {'extend_existing': True}

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
