"""
Workflow and WorkflowNode Models - Simplified
"""
from sqlalchemy import Column, String, Text, JSON
from .base import BaseModel


class Workflow(BaseModel):
    __tablename__ = "workflows"

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tenant_id = Column(String, nullable=True)
    graph = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Workflow {self.name}>"


class WorkflowNode(BaseModel):
    __tablename__ = "workflow_nodes"

    workflow_id = Column(String, nullable=False)
    node_type = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    position_x = Column(String, nullable=True)
    position_y = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<WorkflowNode {self.workflow_id}:{self.node_type}>"
