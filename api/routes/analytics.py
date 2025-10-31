"""
Analytics and Metrics Routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, timedelta

from api.database import get_db
from api.models import (
    User, Dataset, Document, Conversation, Message, 
    MessageFeedback, Tenant
)
from api.middleware.auth import get_current_user
from api.middleware.tenant import get_current_tenant
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analytics")


@router.get("/usage")
async def get_usage_analytics(
    period: str = Query("7d", pattern="^(24h|7d|30d|90d)$"),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get usage analytics
    
    Period options: 24h, 7d, 30d, 90d
    """
    # Calculate date range
    now = datetime.utcnow()
    period_map = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90)
    }
    start_date = now - period_map[period]
    
    # Get statistics
    stats = {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "tenant_id": current_tenant.id,
        "datasets": {
            "total": db.query(Dataset).filter(
                Dataset.tenant_id == current_tenant.id
            ).count(),
            "created_in_period": db.query(Dataset).filter(
                Dataset.tenant_id == current_tenant.id,
                Dataset.created_at >= start_date.isoformat()
            ).count()
        },
        "documents": {
            "total": db.query(Document).join(Dataset).filter(
                Dataset.tenant_id == current_tenant.id
            ).count(),
            "uploaded_in_period": db.query(Document).join(Dataset).filter(
                Dataset.tenant_id == current_tenant.id,
                Document.created_at >= start_date.isoformat()
            ).count(),
            "by_status": {}
        },
        "conversations": {
            "total": db.query(Conversation).join(User).filter(
                User.tenant_id == current_tenant.id
            ).count(),
            "created_in_period": db.query(Conversation).join(User).filter(
                User.tenant_id == current_tenant.id,
                Conversation.created_at >= start_date.isoformat()
            ).count()
        },
        "messages": {
            "total": db.query(Message).join(Conversation).join(User).filter(
                User.tenant_id == current_tenant.id
            ).count(),
            "sent_in_period": db.query(Message).join(Conversation).join(User).filter(
                User.tenant_id == current_tenant.id,
                Message.created_at >= start_date.isoformat()
            ).count()
        },
        "users": {
            "total": db.query(User).filter(
                User.tenant_id == current_tenant.id
            ).count(),
            "active_in_period": db.query(User).filter(
                User.tenant_id == current_tenant.id,
                User.last_login_at >= start_date.isoformat()
            ).count()
        }
    }
    
    # Document status breakdown
    status_counts = db.query(
        Document.status,
        func.count(Document.id)
    ).join(Dataset).filter(
        Dataset.tenant_id == current_tenant.id
    ).group_by(Document.status).all()
    
    stats["documents"]["by_status"] = {
        status: count for status, count in status_counts
    }
    
    return stats


@router.get("/costs")
async def get_cost_analytics(
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get cost analytics (tokens and pricing)
    """
    # Calculate date range
    now = datetime.utcnow()
    period_map = {"7d": 7, "30d": 30, "90d": 90}
    start_date = now - timedelta(days=period_map[period])
    
    # Get message costs
    messages = db.query(Message).join(Conversation).join(User).filter(
        User.tenant_id == current_tenant.id,
        Message.created_at >= start_date.isoformat()
    ).all()
    
    total_tokens = sum(msg.total_tokens for msg in messages)
    total_cost = sum(msg.total_price for msg in messages)
    total_messages = len(messages)
    
    # Calculate averages
    avg_tokens = total_tokens / total_messages if total_messages > 0 else 0
    avg_cost = total_cost / total_messages if total_messages > 0 else 0
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "total_messages": total_messages,
        "tokens": {
            "total": total_tokens,
            "average_per_message": round(avg_tokens, 2)
        },
        "cost": {
            "total": round(total_cost, 4),
            "currency": "USD",
            "average_per_message": round(avg_cost, 6)
        },
        "retrieval": {
            "messages_with_retrieval": sum(1 for msg in messages if msg.retrieval_used),
            "total_retrievals": sum(msg.retrieval_count for msg in messages)
        }
    }


@router.get("/performance")
async def get_performance_analytics(
    period: str = Query("7d", pattern="^(24h|7d|30d)$"),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get performance analytics (latency, response times)
    """
    # Calculate date range
    now = datetime.utcnow()
    period_map = {"24h": 1, "7d": 7, "30d": 30}
    start_date = now - timedelta(days=period_map[period])
    
    # Get messages with latency data
    messages = db.query(Message).join(Conversation).join(User).filter(
        User.tenant_id == current_tenant.id,
        Message.created_at >= start_date.isoformat(),
        Message.total_latency.isnot(None)
    ).all()
    
    if not messages:
        return {
            "period": period,
            "message_count": 0,
            "latency": None
        }
    
    latencies = [msg.total_latency for msg in messages if msg.total_latency]
    provider_latencies = [msg.provider_response_latency for msg in messages if msg.provider_response_latency]
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "message_count": len(messages),
        "latency": {
            "total": {
                "average": round(sum(latencies) / len(latencies), 3) if latencies else 0,
                "min": round(min(latencies), 3) if latencies else 0,
                "max": round(max(latencies), 3) if latencies else 0
            },
            "provider": {
                "average": round(sum(provider_latencies) / len(provider_latencies), 3) if provider_latencies else 0,
                "min": round(min(provider_latencies), 3) if provider_latencies else 0,
                "max": round(max(provider_latencies), 3) if provider_latencies else 0
            }
        },
        "retrieval_performance": {
            "messages_with_retrieval": sum(1 for msg in messages if msg.retrieval_used),
            "average_retrieval_count": round(
                sum(msg.retrieval_count for msg in messages) / len(messages), 2
            ) if messages else 0
        }
    }


@router.get("/feedback")
async def get_feedback_analytics(
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get user feedback analytics
    """
    # Calculate date range
    now = datetime.utcnow()
    period_map = {"7d": 7, "30d": 30, "90d": 90}
    start_date = now - timedelta(days=period_map[period])
    
    # Get feedbacks
    feedbacks = db.query(MessageFeedback).join(Message).join(Conversation).join(User).filter(
        User.tenant_id == current_tenant.id,
        MessageFeedback.created_at >= start_date.isoformat()
    ).all()
    
    total_feedbacks = len(feedbacks)
    likes = sum(1 for f in feedbacks if f.rating == "like")
    dislikes = sum(1 for f in feedbacks if f.rating == "dislike")
    neutral = sum(1 for f in feedbacks if f.rating == "neutral")
    
    # Calculate satisfaction score (0-100)
    satisfaction_score = (likes / total_feedbacks * 100) if total_feedbacks > 0 else 0
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "total_feedbacks": total_feedbacks,
        "ratings": {
            "like": likes,
            "dislike": dislikes,
            "neutral": neutral
        },
        "percentages": {
            "like": round(likes / total_feedbacks * 100, 1) if total_feedbacks > 0 else 0,
            "dislike": round(dislikes / total_feedbacks * 100, 1) if total_feedbacks > 0 else 0,
            "neutral": round(neutral / total_feedbacks * 100, 1) if total_feedbacks > 0 else 0
        },
        "satisfaction_score": round(satisfaction_score, 1)
    }


@router.get("/agents")
async def get_agent_analytics(
    period: str = Query("7d", pattern="^(7d|30d|90d)$"),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get agent usage analytics
    """
    # Calculate date range
    now = datetime.utcnow()
    period_map = {"7d": 7, "30d": 30, "90d": 90}
    start_date = now - timedelta(days=period_map[period])
    
    # Get messages by agent
    messages = db.query(Message).join(Conversation).join(User).filter(
        User.tenant_id == current_tenant.id,
        Message.created_at >= start_date.isoformat(),
        Message.agent_id.isnot(None)
    ).all()
    
    # Group by agent
    agent_stats = {}
    for msg in messages:
        agent_id = msg.agent_id
        if agent_id not in agent_stats:
            agent_stats[agent_id] = {
                "message_count": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "retrieval_used": 0
            }
        
        agent_stats[agent_id]["message_count"] += 1
        agent_stats[agent_id]["total_tokens"] += msg.total_tokens
        agent_stats[agent_id]["total_cost"] += msg.total_price
        if msg.retrieval_used:
            agent_stats[agent_id]["retrieval_used"] += 1
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "total_messages": len(messages),
        "agents": agent_stats
    }
