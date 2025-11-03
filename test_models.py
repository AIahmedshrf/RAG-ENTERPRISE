#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspaces/RAG-ENTERPRISE')

print("Testing models registration...")

# Import database Base
from api.database import Base

print(f"1. Base before imports: {len(Base.metadata.tables)} tables")

# Import all models
from api.models.user import User
print(f"2. After User: {len(Base.metadata.tables)} tables")

from api.models.tenant import Tenant
print(f"3. After Tenant: {len(Base.metadata.tables)} tables")

from api.models.workspace import Workspace
print(f"4. After Workspace: {len(Base.metadata.tables)} tables")

from api.models.role import Role, Permission
print(f"5. After Role: {len(Base.metadata.tables)} tables")

from api.models.app import App, AppModelConfig
print(f"6. After App: {len(Base.metadata.tables)} tables")

from api.models.dataset import Dataset
print(f"7. After Dataset: {len(Base.metadata.tables)} tables")

from api.models.document import Document, DocumentSegment
print(f"8. After Document: {len(Base.metadata.tables)} tables")

from api.models.conversation import Conversation
print(f"9. After Conversation: {len(Base.metadata.tables)} tables")

from api.models.message import Message, MessageFeedback
print(f"10. After Message: {len(Base.metadata.tables)} tables")

from api.models.tool import Tool, ToolProvider
print(f"11. After Tool: {len(Base.metadata.tables)} tables")

from api.models.workflow import Workflow, WorkflowNode
print(f"12. After Workflow: {len(Base.metadata.tables)} tables")

from api.models.api_token import ApiToken
print(f"13. After ApiToken: {len(Base.metadata.tables)} tables")

print(f"\nFinal: {len(Base.metadata.tables)} tables registered")

if len(Base.metadata.tables) > 0:
    print("\n✅ SUCCESS! Tables:")
    for table in sorted(Base.metadata.tables.keys()):
        print(f"   ✓ {table}")
else:
    print("\n❌ FAILED! No tables registered")
    sys.exit(1)
