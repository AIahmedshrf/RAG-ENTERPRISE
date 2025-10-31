"""
Enhanced Database Configuration with Connection Pooling
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from contextlib import contextmanager
import os
from typing import Generator
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    f'sqlite:///./{settings.database.name}'
)

# Engine configuration based on database type
if DATABASE_URL.startswith('sqlite'):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.database.echo
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
else:
    # PostgreSQL configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.database.echo
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session
    
    Usage:
        with get_db_context() as db:
            db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    from api.models.base import Base
    from api.models import (
        User, Workspace, Tenant, Role, Permission, RolePermission,
        Dataset, Document, DocumentSegment,
        Conversation, Message, MessageFeedback,
        App, AppModelConfig,
        Workflow, WorkflowNode,
        Tool, ToolProvider,
        ApiToken
    )
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def create_default_data():
    """Create default data (roles, permissions, etc.)"""
    from api.models import Role, Permission, RolePermission, Tenant
    
    with get_db_context() as db:
        # Check if default data already exists
        if db.query(Role).count() > 0:
            logger.info("Default data already exists")
            return
        
        # Create default tenant
        default_tenant = Tenant(
            id="default-tenant",
            name="Default Organization",
            slug="default",
            description="Default tenant for the system",
            is_active=True
        )
        db.add(default_tenant)
        
        # Create default roles
        roles_data = [
            {
                "name": "admin",
                "display_name": "Administrator",
                "description": "Full system access",
                "is_system": True
            },
            {
                "name": "manager",
                "display_name": "Manager",
                "description": "Manage users and content",
                "is_system": True
            },
            {
                "name": "user",
                "display_name": "User",
                "description": "Standard user access",
                "is_system": True
            },
            {
                "name": "viewer",
                "display_name": "Viewer",
                "description": "Read-only access",
                "is_system": True
            }
        ]
        
        roles = {}
        for role_data in roles_data:
            role = Role(**role_data)
            db.add(role)
            roles[role_data["name"]] = role
        
        db.flush()
        
        # Create default permissions
        resources = ['datasets', 'documents', 'apps', 'conversations', 'workflows', 'tools', 'users']
        actions = ['create', 'read', 'update', 'delete']
        
        permissions = {}
        for resource in resources:
            for action in actions:
                perm = Permission(
                    name=f"{resource}:{action}",
                    resource=resource,
                    action=action,
                    description=f"{action.capitalize()} {resource}"
                )
                db.add(perm)
                permissions[f"{resource}:{action}"] = perm
        
        db.flush()
        
        # Assign permissions to roles
        # Admin - all permissions
        for perm in permissions.values():
            role_perm = RolePermission(
                role_id=roles["admin"].id,
                permission_id=perm.id
            )
            db.add(role_perm)
        
        # Manager - all except user management
        for perm_name, perm in permissions.items():
            if not perm_name.startswith('users:'):
                role_perm = RolePermission(
                    role_id=roles["manager"].id,
                    permission_id=perm.id
                )
                db.add(role_perm)
        
        # User - create and read most resources
        for perm_name, perm in permissions.items():
            if perm.action in ['create', 'read'] and perm.resource != 'users':
                role_perm = RolePermission(
                    role_id=roles["user"].id,
                    permission_id=perm.id
                )
                db.add(role_perm)
        
        # Viewer - read only
        for perm_name, perm in permissions.items():
            if perm.action == 'read':
                role_perm = RolePermission(
                    role_id=roles["viewer"].id,
                    permission_id=perm.id
                )
                db.add(role_perm)
        
        db.commit()
        logger.info("Default data created successfully")


def check_db_connection():
    """Check database connection"""
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_db_health():
    """Get database health status"""
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        
        pool = engine.pool
        return {
            "status": "healthy",
            "pool_size": pool.size() if hasattr(pool, 'size') else None,
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else None,
            "overflow": pool.overflow() if hasattr(pool, 'overflow') else None,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
