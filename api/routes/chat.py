"""
Chat Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.models import User
from api.middleware.auth import get_current_user
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat")


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None
    agent_id: str = None


@router.post("/")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat endpoint (placeholder)
    
    TODO: Implement actual chat logic with agents
    """
    return {
        "message": "Chat endpoint placeholder",
        "user_message": request.message,
        "agent_response": "This is a placeholder response. Implement actual agent logic.",
        "conversation_id": request.conversation_id,
        "agent_id": request.agent_id
    }


@router.get("/agents")
async def list_agents(current_user: User = Depends(get_current_user)):
    """List available agents"""
    return {
        "agents": [
            {
                "id": "qa",
                "name": "QA Agent",
                "description": "Question answering agent"
            },
            {
                "id": "research",
                "name": "Research Agent",
                "description": "Research and analysis agent"
            },
            {
                "id": "financial",
                "name": "Financial Analyst",
                "description": "Financial analysis agent"
            },
            {
                "id": "investment",
                "name": "Investment Advisor",
                "description": "Investment advisory agent"
            }
        ]
    }
