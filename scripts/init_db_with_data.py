#!/usr/bin/env python3
"""
Initialize database with required data (tenants, roles, permissions, admin user)
"""

import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/workspaces/RAG-ENTERPRISE')

from api.database import SessionLocal
from api.models.tenant import Tenant
from api.models.role import Role, Permission, RolePermission
from api.models.user import User, UserStatus
from core.auth import AuthService
from core.rbac import RoleEnum, PermissionEnum


def init_database():
    """Initialize database with seed data"""
    db = SessionLocal()
    
    try:
        print("🔧 Initializing database with seed data...\n")
        
        # ============================================================================
        # 1. CREATE TENANT
        # ============================================================================
        print("📦 Creating Tenant...")
        tenant = Tenant(
            id=str(uuid.uuid4()),
            name="Default Tenant",
            plan="enterprise",
            status="active"
        )
        db.add(tenant)
        db.commit()
        print(f"✅ Tenant created: {tenant.name}")
        
        # ============================================================================
        # 2. CREATE ROLES
        # ============================================================================
        print("\n📋 Creating Roles...")
        roles_dict = {}
        role_descriptions = {
            'super_admin': 'Has all permissions and can manage everything',
            'admin': 'Can manage users, agents, knowledge, and settings',
            'manager': 'Can create and manage agents and knowledge',
            'editor': 'Can create and edit content',
            'viewer': 'Can only view content (read-only)',
            'user': 'Regular user with basic permissions'
        }
        
        for role_enum in RoleEnum:
            role_name = role_enum.value
            role = Role(
                id=str(uuid.uuid4()),
                name=role_name,
                description=role_descriptions.get(role_name, f"{role_name} role"),
                is_system=True
            )
            db.add(role)
            db.commit()
            roles_dict[role_name] = role
            print(f"  ✅ {role_name.upper()}")
        
        # ============================================================================
        # 3. CREATE PERMISSIONS
        # ============================================================================
        print("\n🔐 Creating Permissions...")
        permissions_dict = {}
        
        for perm_enum in PermissionEnum:
            perm_name = perm_enum.value  # e.g., "user:create"
            resource, action = perm_name.split(':')
            
            permission = Permission(
                id=str(uuid.uuid4()),
                name=perm_name,
                resource=resource,
                action=action,
                description=f"{action.upper()} on {resource.upper()}"
            )
            db.add(permission)
            db.commit()
            permissions_dict[perm_name] = permission
        
        print(f"  ✅ Created {len(permissions_dict)} permissions")
        
        # ============================================================================
        # 4. ASSIGN PERMISSIONS TO ROLES (from core.rbac ROLE_PERMISSIONS)
        # ============================================================================
        print("\n🔗 Assigning Permissions to Roles...")
        from core.rbac import ROLE_PERMISSIONS
        
        for role_enum, perms_list in ROLE_PERMISSIONS.items():
            role_name = role_enum.value
            role = roles_dict[role_name]
            
            for perm_enum in perms_list:
                perm_name = perm_enum.value
                if perm_name in permissions_dict:
                    permission = permissions_dict[perm_name]
                    
                    # Check if relationship already exists
                    existing = db.query(RolePermission).filter(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    
                    if not existing:
                        role_perm = RolePermission(
                            id=str(uuid.uuid4()),
                            role_id=role.id,
                            permission_id=permission.id
                        )
                        db.add(role_perm)
            
            db.commit()
            perm_count = db.query(RolePermission).filter(RolePermission.role_id == role.id).count()
            print(f"  ✅ {role_name.upper()}: {perm_count} permissions")
        
        # ============================================================================
        # 5. CREATE ADMIN USER
        # ============================================================================
        print("\n👤 Creating Admin User...")
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@admin.com",
            password_hash=AuthService.get_password_hash("admin123"),
            name="Admin User",
            is_active=True,
            is_verified=True,
            status=UserStatus.ACTIVE,
            role_id=roles_dict['super_admin'].id,
            tenant_id=tenant.id,
            timezone="UTC",
            language="en"
        )
        db.add(admin_user)
        db.commit()
        print(f"✅ Admin created: admin@admin.com / admin123")
        
        # ============================================================================
        # 6. CREATE DEMO USER
        # ============================================================================
        print("\n👤 Creating Demo User...")
        demo_user = User(
            id=str(uuid.uuid4()),
            email="user@demo.com",
            password_hash=AuthService.get_password_hash("demo123"),
            name="Demo User",
            is_active=True,
            is_verified=True,
            status=UserStatus.ACTIVE,
            role_id=roles_dict['user'].id,
            tenant_id=tenant.id,
            timezone="UTC",
            language="en"
        )
        db.add(demo_user)
        db.commit()
        print(f"✅ Demo user created: user@demo.com / demo123")
        
        # ============================================================================
        # SUMMARY
        # ============================================================================
        print("\n" + "="*60)
        print("✅ DATABASE INITIALIZATION COMPLETED!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"  • Tenants: 1")
        print(f"  • Roles: {len(roles_dict)}")
        print(f"  • Permissions: {len(permissions_dict)}")
        print(f"  • Users: 2")
        print("\n🔐 Login Credentials:")
        print("  Admin: admin@admin.com / admin123")
        print("  User:  user@demo.com / demo123")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
