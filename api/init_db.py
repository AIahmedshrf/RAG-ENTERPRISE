#!/usr/bin/env python3
"""
Database Initialization Script
Fixed datetime warnings and User model compatibility
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import init_db, check_database_health, SessionLocal
from api.models.user import User
from api.models.tenant import Tenant
from api.models.workspace import Workspace
from api.models.role import Role, Permission, RolePermission
from api.models.dataset import Dataset
from api.models.app import App
from datetime import datetime, timezone
import bcrypt
from sqlalchemy import text

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_seed_data():
    """Create initial seed data"""
    db = SessionLocal()
    
    try:
        print("🌱 Creating seed data...")
        
        # 1. Create default tenant
        print("   📦 Creating tenant...")
        tenant = db.query(Tenant).filter_by(name="Default Tenant").first()
        if not tenant:
            tenant = Tenant(
                id="tenant_default",
                name="Default Tenant",
                created_at=datetime.now(timezone.utc)  # 🔧 Fixed
            )
            db.add(tenant)
            db.flush()
            print("   ✅ Tenant created")
        else:
            print("   ℹ️  Tenant already exists")
        
        # 2. Create default workspace
        print("   🏢 Creating workspace...")
        workspace = db.query(Workspace).filter_by(name="Default Workspace").first()
        if not workspace:
            workspace = Workspace(
                id="ws_default",
                name="Default Workspace",
                created_at=datetime.now(timezone.utc)  # 🔧 Fixed
            )
            db.add(workspace)
            db.flush()
            print("   ✅ Workspace created")
        else:
            print("   ℹ️  Workspace already exists")
        
        # 3. Create roles
        print("   👥 Creating roles...")
        roles_data = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "user", "description": "Regular user"},
            {"name": "viewer", "description": "Read-only access"}
        ]
        
        for role_data in roles_data:
            role = db.query(Role).filter_by(name=role_data["name"]).first()
            if not role:
                role = Role(**role_data, created_at=datetime.now(timezone.utc))  # 🔧 Fixed
                db.add(role)
                print(f"   ✅ Role '{role_data['name']}' created")
            else:
                print(f"   ℹ️  Role '{role_data['name']}' already exists")
        
        db.flush()
        
        # 4. Create users
        print("   👤 Creating users...")
        users_data = [
            {
                "email": "admin@demo.com",
                "password": "admin123",
                "name": "Admin User",
                "role": "admin"
            },
            {
                "email": "user@demo.com",
                "password": "password123",
                "name": "Demo User",
                "role": "user"
            },
            {
                "email": "viewer@demo.com",
                "password": "viewer123",
                "name": "Viewer User",
                "role": "viewer"
            }
        ]
        
        for user_data in users_data:
            user = db.query(User).filter_by(email=user_data["email"]).first()
            if not user:
                role = db.query(Role).filter_by(name=user_data["role"]).first()
                user = User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),  # 🔧 Fixed: Use password_hash
                    name=user_data["name"],
                    role_id=role.id,
                    tenant_id=tenant.id,
                    is_active=True,
                    created_at=datetime.now(timezone.utc)  # 🔧 Fixed
                )
                db.add(user)
                print(f"   ✅ User '{user_data['email']}' created")
            else:
                print(f"   ℹ️  User '{user_data['email']}' already exists")
        
        db.flush()
        
        # 5. Create sample datasets
        print("   📚 Creating sample datasets...")
        datasets_data = [
            {
                "name": "Company Knowledge Base",
                "description": "Internal company documentation and policies"
            },
            {
                "name": "Product Documentation",
                "description": "Technical product documentation"
            },
            {
                "name": "Customer Support FAQs",
                "description": "Frequently asked questions and answers"
            }
        ]
        
        admin_user = db.query(User).filter_by(email="admin@demo.com").first()
        
        for ds_data in datasets_data:
            dataset = db.query(Dataset).filter_by(name=ds_data["name"]).first()
            if not dataset:
                dataset = Dataset(
                    name=ds_data["name"],
                    description=ds_data["description"],
                    tenant_id=tenant.id,
                    created_by=admin_user.id,
                    created_at=datetime.now(timezone.utc)  # 🔧 Fixed
                )
                db.add(dataset)
                print(f"   ✅ Dataset '{ds_data['name']}' created")
            else:
                print(f"   ℹ️  Dataset '{ds_data['name']}' already exists")
        
        db.flush()
        
        # 6. Create sample apps
        print("   🤖 Creating sample apps...")
        apps_data = [
            {
                "name": "Customer Support Bot",
                "description": "AI assistant for customer support",
                "mode": "chat"
            },
            {
                "name": "Document Analyzer",
                "description": "Analyze and extract information from documents",
                "mode": "completion"
            },
            {
                "name": "Financial Advisor",
                "description": "AI-powered financial analysis and advice",
                "mode": "agent-chat"
            }
        ]
        
        for app_data in apps_data:
            app = db.query(App).filter_by(name=app_data["name"]).first()
            if not app:
                app = App(
                    name=app_data["name"],
                    description=app_data["description"],
                    mode=app_data["mode"],
                    tenant_id=tenant.id,
                    created_by=admin_user.id,
                    created_at=datetime.now(timezone.utc)  # 🔧 Fixed
                )
                db.add(app)
                print(f"   ✅ App '{app_data['name']}' created")
            else:
                print(f"   ℹ️  App '{app_data['name']}' already exists")
        
        # Commit all changes
        db.commit()
        print("\n✅ Seed data created successfully!")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Database Summary:")
        print("=" * 60)
        print(f"   Tenants: {db.query(Tenant).count()}")
        print(f"   Workspaces: {db.query(Workspace).count()}")
        print(f"   Users: {db.query(User).count()}")
        print(f"   Roles: {db.query(Role).count()}")
        print(f"   Datasets: {db.query(Dataset).count()}")
        print(f"   Apps: {db.query(App).count()}")
        print("=" * 60)
        
        # Print demo credentials
        print("\n🔑 Demo Credentials:")
        print("=" * 60)
        for user_data in users_data:
            print(f"   {user_data['role'].upper()}: {user_data['email']} / {user_data['password']}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating seed data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("🚀 RAG-ENTERPRISE Database Initialization")
    print("=" * 60)
    
    # Check database health
    print("\n1️⃣ Checking database health...")
    health = check_database_health()
    print(f"   Status: {health.get('status', 'unknown')}")
    
    # Initialize database
    print("\n2️⃣ Initializing database tables...")
    if init_db():
        print("   ✅ Tables created successfully")
    else:
        print("   ❌ Table creation failed")
        return False
    
    # Create seed data
    print("\n3️⃣ Creating seed data...")
    if create_seed_data():
        print("\n✅ Database initialization complete!")
        return True
    else:
        print("\n❌ Database initialization failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
