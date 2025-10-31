#!/usr/bin/env python3
"""
Database Initialization Script
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.database import init_db, create_default_data, check_db_connection
from utilities.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Initialize database with tables and default data"""
    logger.info("=" * 60)
    logger.info("🚀 Database Initialization")
    logger.info("=" * 60)
    
    # Step 1: Check connection
    logger.info("Step 1: Checking database connection...")
    if not check_db_connection():
        logger.error("❌ Database connection failed")
        sys.exit(1)
    logger.info("✅ Database connection successful")
    
    # Step 2: Create tables
    logger.info("\nStep 2: Creating database tables...")
    try:
        init_db()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        sys.exit(1)
    
    # Step 3: Create default data
    logger.info("\nStep 3: Creating default data (roles, permissions, tenant)...")
    try:
        create_default_data()
        logger.info("✅ Default data created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating default data: {e}")
        sys.exit(1)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Database initialization completed successfully!")
    logger.info("=" * 60)
    
    # Display summary
    from api.database import get_db_context
    from api.models import Tenant, Role, Permission
    
    with get_db_context() as db:
        tenant_count = db.query(Tenant).count()
        role_count = db.query(Role).count()
        permission_count = db.query(Permission).count()
        
        logger.info("\n📊 Summary:")
        logger.info(f"   - Tenants: {tenant_count}")
        logger.info(f"   - Roles: {role_count}")
        logger.info(f"   - Permissions: {permission_count}")
    
    logger.info("\n🎯 Next steps:")
    logger.info("   1. Run: python scripts/create_admin.py (to create admin user)")
    logger.info("   2. Run: uvicorn api.main:app --reload (to start the API)")
    logger.info("")


if __name__ == "__main__":
    main()
