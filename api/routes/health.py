"""
Health Check Routes
Enhanced with detailed system information
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db, check_database_health
from datetime import datetime
import psutil
import os

# 🔧 Fixed: Remove prefix (it's added in main.py)
router = APIRouter()

@router.get("/health/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Enhanced health check endpoint
    Returns detailed system status
    """
    try:
        # Database health
        db_health = check_database_health()
        
        # System information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application info
        app_info = {
            "version": "2.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Overall status
        is_healthy = db_health["status"] == "healthy"
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": app_info["timestamp"],
            "version": app_info["version"],
            "environment": app_info["environment"],
            "database": {
                "status": db_health["status"],
                "connection": db_health.get("database", "unknown"),
                "url": db_health.get("url", "unknown")
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "database": "error",
            "version": "2.1.0"
        }

@router.get("/health/db")
async def database_health(db: Session = Depends(get_db)):
    """
    Detailed database health check
    """
    try:
        # Test query
        result = db.execute(text("SELECT 1 as test")).fetchone()
        
        # Get table count
        if "sqlite" in str(db.bind.url):
            tables_result = db.execute(text(
                "SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'"
            )).fetchone()
        else:
            tables_result = db.execute(text(
                "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema='public'"
            )).fetchone()
        
        return {
            "status": "healthy",
            "connection": "active",
            "test_query": "passed",
            "tables_count": tables_result[0] if tables_result else 0,
            "database_url": str(db.bind.url).split("@")[-1] if "@" in str(db.bind.url) else str(db.bind.url).split("///")[-1]
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "connection": "failed",
            "error": str(e)
        }

@router.get("/health/stats")
async def system_stats(db: Session = Depends(get_db)):
    """
    Get system statistics
    """
    try:
        from api.models.user import User
        from api.models.dataset import Dataset
        from api.models.app import App
        from api.models.document import Document
        from api.models.conversation import Conversation
        from api.models.message import Message
        
        stats = {
            "users": db.query(User).count(),
            "datasets": db.query(Dataset).count(),
            "apps": db.query(App).count(),
            "documents": db.query(Document).count(),
            "conversations": db.query(Conversation).count(),
            "messages": db.query(Message).count()
        }
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
