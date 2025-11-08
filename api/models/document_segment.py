from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from api.models.base import Base

class DocumentSegment(Base):
    __tablename__ = "document_segments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    embedding = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
