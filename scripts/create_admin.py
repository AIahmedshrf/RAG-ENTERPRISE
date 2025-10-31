#!/usr/bin/env python3
"""
Create Admin User Script
"""
import sys
import os
import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.database import get_db_context
from api.models import User, Role, Tenant
from passlib.context import CryptContext
from utilities.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user(
    email: str,
    username: str,
    password: str,
    full_name: str = "System Administrator"
):
    """Create admin user"""
    
    with get_db_context() as db:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            logger.error(f"❌ User already exists: {existing_user.email}")
            return False
        
        # Get admin role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            logger.error("❌ Admin role not found. Please run init_db.py first.")
            return False
        
        # Get default tenant
        default_tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
        if not default_tenant:
            logger.error("❌ Default tenant not found. Please run init_db.py first.")
            return False
        
        # Hash password
        hashed_password = pwd_context.hash(password)
        
        # Create user
        admin_user = User(
            email=email,
            username=username,
            password_hash=hashed_password,
            full_name=full_name,
            tenant_id=default_tenant.id,
            role_id=admin_role.id,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info("✅ Admin user created successfully!")
        logger.info(f"   - Email: {admin_user.email}")
        logger.info(f"   - Username: {admin_user.username}")
        logger.info(f"   - Role: {admin_role.display_name}")
        
        return True


def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("👤 Create Admin User")
    logger.info("=" * 60)
    
    # Interactive input
    print("\nEnter admin user details:")
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    full_name = input("Full Name [System Administrator]: ").strip() or "System Administrator"
    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm Password: ")
    
    # Validate
    if not email or not username or not password:
        logger.error("❌ All fields are required")
        sys.exit(1)
    
    if password != password_confirm:
        logger.error("❌ Passwords do not match")
        sys.exit(1)
    
    if len(password) < 8:
        logger.error("❌ Password must be at least 8 characters")
        sys.exit(1)
    
    # Create user
    print()
    success = create_admin_user(email, username, password, full_name)
    
    if success:
        logger.info("\n🎉 Admin user created successfully!")
        logger.info("\n🎯 You can now login with:")
        logger.info(f"   - Email: {email}")
        logger.info(f"   - Password: ******")
        logger.info("")
    else:
        logger.error("\n❌ Failed to create admin user")
        sys.exit(1)


if __name__ == "__main__":
    main()
