"""
Agent model for managing AI agents
"""
from sqlalchemy import Column, String, Text, Boolean
from .base import BaseModel
import json


class Agent(BaseModel):
    __tablename__ = "agents"
    __table_args__ = {"extend_existing": True}

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    dataset_ids = Column(Text, nullable=True)  # JSON array of dataset ids
    owner_id = Column(String(36), nullable=True)
    is_active = Column(Boolean, default=True)

    def get_dataset_ids(self):
        try:
            return json.loads(self.dataset_ids) if self.dataset_ids else []
        except Exception:
            return []

    def set_dataset_ids(self, ids):
        self.dataset_ids = json.dumps(ids or [])

    def __repr__(self):
        return f"<Agent {self.name}>"
