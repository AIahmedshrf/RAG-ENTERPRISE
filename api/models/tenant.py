"""
Tenant Model for Multi-tenancy Support
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from api.models.base import Base, TimestampMixin, UUIDMixin

class Tenant(Base, UUIDMixin, TimestampMixin):
    """Tenant model for multi-tenancy"""
    
    __tablename__ = "tenants"
    
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="free", nullable=False)  # free, pro, enterprise
    status = Column(String(50), default="active", nullable=False)  # active, suspended, deleted
    
    # Configuration
    settings = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    users = relationship("User", back_populates="tenant", foreign_keys="User.tenant_id")
    
    def __repr__(self):
        return f"<Tenant {self.name}>"
