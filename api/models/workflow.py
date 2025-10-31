"""
Workflow and WorkflowNode Models
"""
from sqlalchemy import Column, String, JSON, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel, TenantMixin


class Workflow(BaseModel, TenantMixin):
    """Workflow model"""
    __tablename__ = 'workflows'

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # App context
    app_id = Column(String(36), ForeignKey('apps.id'))
    
    # Version
    version = Column(String(50), default='1.0')
    
    # Status
    is_published = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    
    # Graph
    graph = Column(JSON, default={})
    features = Column(JSON, default={})
    
    # Environment variables
    environment_variables = Column(JSON, default=[])
    
    # Statistics
    run_count = Column(Integer, default=0)
    
    # Relationships
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False)
    created_by = Column(String(36), ForeignKey('users.id'))
    
    nodes = relationship("WorkflowNode", back_populates="workflow", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name}, version={self.version})>"


class WorkflowNode(BaseModel):
    """Workflow node model"""
    __tablename__ = 'workflow_nodes'

    workflow_id = Column(String(36), ForeignKey('workflows.id'), nullable=False)
    
    # Node info
    title = Column(String(255), nullable=False)
    node_type = Column(String(100), nullable=False)
    
    # Position
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    
    # Configuration
    config = Column(JSON, default={})
    
    # Relationships
    workflow = relationship("Workflow", back_populates="nodes")

    def __repr__(self):
        return f"<WorkflowNode(id={self.id}, workflow_id={self.workflow_id}, type={self.node_type})>"
