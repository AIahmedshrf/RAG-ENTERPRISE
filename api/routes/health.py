"""
Health Check Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from api.database import get_db, get_db_health
from core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Basic health check endpoint
    
    Returns system health status
    """
    db_health = get_db_health()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "components": {
            "api": {"status": "healthy"},
            "database": db_health
        }
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with system information
    """
    from api.models import User, Tenant, Role, Dataset
    
    db_health = get_db_health()
    
    # Get database statistics
    try:
        user_count = db.query(User).count()
        tenant_count = db.query(Tenant).count()
        role_count = db.query(Role).count()
        dataset_count = db.query(Dataset).count()
        
        db_stats = {
            "users": user_count,
            "tenants": tenant_count,
            "roles": role_count,
            "datasets": dataset_count
        }
    except Exception as e:
        db_stats = {"error": str(e)}
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "app": {
            "name": settings.app_name,
            "debug": settings.debug,
            "metrics_enabled": settings.enable_metrics,
            "tracing_enabled": settings.enable_tracing
        },
        "components": {
            "api": {"status": "healthy"},
            "database": {**db_health, "statistics": db_stats}
        },
        "features": {
            "multi_tenancy": True,
            "rbac": True,
            "rate_limiting": settings.rate_limit.enabled
        }
    }


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check for Kubernetes/container orchestration
    """
    db_health = get_db_health()
    
    if db_health["status"] != "healthy":
        return {
            "ready": False,
            "reason": "Database not ready"
        }, 503
    
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
