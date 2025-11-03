"""
Dataset Model - Simplified
"""
from sqlalchemy import Column, String, Text, Enum as SQLEnum
import enum
from .base import BaseModel


class IndexingTechnique(str, enum.Enum):
    HIGH_QUALITY = "high_quality"
    ECONOMY = "economy"


class Dataset(BaseModel):
    __tablename__ = "datasets"

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    indexing_technique = Column(SQLEnum(IndexingTechnique), default=IndexingTechnique.HIGH_QUALITY)
    tenant_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Dataset {self.name}>"
