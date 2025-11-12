#!/usr/bin/env python3
"""
Create database and all tables
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.database import Base, engine

# Import ALL models explicitly to register them
from api.models.base import BaseModel
from api.models.user import User, UserStatus
from api.models.tenant import Tenant
from api.models.workspace import Workspace
from api.models.role import Role, Permission, RolePermission
from api.models.app import App, AppMode, AppModelConfig
from api.models.dataset import Dataset, IndexingTechnique
from api.models.document import Document, DocumentSegment, DocumentStatus, DocumentType
from api.models.embedding import Embedding
from api.models.agent import Agent
from api.models.conversation import Conversation, ConversationStatus
from api.models.message import Message, MessageFeedback
from api.models.tool import Tool, ToolProvider, ToolType
from api.models.workflow import Workflow, WorkflowNode
from api.models.api_token import ApiToken, TokenType

def main():
    print("="*60)
    print("Creating Database Tables")
    print("="*60)
    
    # Check metadata
    print(f"\nModels registered: {len(Base.metadata.tables)}")
    
    if len(Base.metadata.tables) == 0:
        print("ERROR: No models registered!")
        return False
    
    print("\nTables to create:")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"  - {table_name}")
    
    # Create tables
    print("\nCreating tables...")
    Base.metadata.create_all(bind=engine)
    
    # Verify
    from sqlalchemy import inspect
    inspector = inspect(engine)
    actual_tables = inspector.get_table_names()
    
    print(f"\nTables created: {len(actual_tables)}")
    for table in sorted(actual_tables):
        print(f"  ✓ {table}")
    
    if len(actual_tables) == 0:
        print("\nERROR: No tables were created!")
        return False
    
    print("\n✅ Database created successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
