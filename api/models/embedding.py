"""
Embedding model to store vector embeddings for document segments
"""
from sqlalchemy import Column, String, Text
from .base import BaseModel


class Embedding(BaseModel):
    __tablename__ = "embeddings"
    __table_args__ = {"extend_existing": True}

    segment_id = Column(String, nullable=False, index=True)
    vector = Column(Text, nullable=False)  # JSON-encoded small vector

    def __repr__(self):
        return f"<Embedding {self.segment_id}>"
