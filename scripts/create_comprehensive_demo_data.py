#!/usr/bin/env python3
"""
Create comprehensive demo data for RAG-ENTERPRISE
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from api.database import get_db, engine
from api.models.app import App
from api.models.dataset import Dataset
from api.models.workspace import Workspace
from api.models.conversation import Conversation
from api.models.user import User
import uuid
import json
from datetime import datetime

def create_demo_data():
    """Create comprehensive demo data"""
    db = next(get_db())
    
    try:
        print("🚀 Creating Demo Data for RAG-ENTERPRISE\n")
        
        # Get admin user
        admin = db.query(User).filter(User.email == "admin@demo.com").first()
        if not admin:
            print("❌ Admin user not found!")
            return
        
        tenant_id = admin.tenant_id
        print(f"✅ Using tenant: {tenant_id or 'default'}\n")
        
        # 1. Create Demo Apps
        print("📱 Creating Demo Apps...")
        apps_data = [
            {
                "name": "Customer Support Bot",
                "mode": "chat",
                "icon": "🎧",
                "description": "AI-powered customer support assistant",
                "model_config": json.dumps({
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000
                })
            },
            {
                "name": "Financial Advisor",
                "mode": "agent",
                "icon": "💰",
                "description": "Intelligent financial analysis and advisory",
                "model_config": json.dumps({
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.5,
                    "max_tokens": 3000
                })
            },
            {
                "name": "Research Assistant",
                "mode": "workflow",
                "icon": "🔬",
                "description": "Advanced research and analysis tool",
                "model_config": json.dumps({
                    "provider": "openai",
                    "model": "gpt-4-turbo",
                    "temperature": 0.3,
                    "max_tokens": 4000
                })
            }
        ]
        
        created_apps = 0
        for app_data in apps_data:
            existing = db.query(App).filter(
                App.name == app_data["name"],
                App.tenant_id == tenant_id
            ).first()
            
            if not existing:
                app = App(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    created_by=admin.id,
                    **app_data
                )
                db.add(app)
                created_apps += 1
                print(f"  ✅ Created: {app_data['name']}")
            else:
                print(f"  ⏭️  Skipped: {app_data['name']} (already exists)")
        
        # 2. Create Demo Datasets
        print("\n📊 Creating Demo Datasets...")
        datasets_data = [
            {
                "name": "Product Documentation",
                "description": "Complete product documentation and guides",
                "indexing_technique": "high_quality"
            },
            {
                "name": "Financial Reports",
                "description": "Company financial reports and analysis",
                "indexing_technique": "high_quality"
            },
            {
                "name": "Research Papers",
                "description": "Academic and industry research papers",
                "indexing_technique": "economy"
            }
        ]
        
        created_datasets = 0
        for ds_data in datasets_data:
            existing = db.query(Dataset).filter(
                Dataset.name == ds_data["name"],
                Dataset.tenant_id == tenant_id
            ).first()
            
            if not existing:
                dataset = Dataset(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    created_by=admin.id,
                    **ds_data
                )
                db.add(dataset)
                created_datasets += 1
                print(f"  ✅ Created: {ds_data['name']}")
            else:
                print(f"  ⏭️  Skipped: {ds_data['name']} (already exists)")
        
        # 3. Ensure Workspace exists
        print("\n🏢 Setting up Workspace...")
        workspace = db.query(Workspace).filter(
            Workspace.tenant_id == tenant_id
        ).first()
        
        if not workspace:
            workspace = Workspace(
                id=str(uuid.uuid4()),
                name="RAG-ENTERPRISE Workspace",
                tenant_id=tenant_id
            )
            db.add(workspace)
            print("  ✅ Created workspace")
        else:
            workspace.name = "RAG-ENTERPRISE Workspace"
            print("  ✅ Updated workspace")
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print("\n" + "="*50)
        print("🎉 Demo Data Creation Complete!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"  • Apps created: {created_apps}")
        print(f"  • Datasets created: {created_datasets}")
        print(f"  • Workspace: ✅")
        print(f"\n🌐 Access your system at:")
        print(f"  • Frontend: http://localhost:3000")
        print(f"  • Admin Panel: http://localhost:3000/admin")
        print(f"  • API Docs: http://localhost:8000/docs")
        print(f"\n👤 Login with:")
        print(f"  • Email: admin@demo.com")
        print(f"  • Password: admin123")
        print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
