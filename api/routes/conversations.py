"""
Conversation Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from api.database import get_db
from api.models import Conversation, Message, User, App
from api.middleware.auth import get_current_user
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/conversations")


# Request/Response Models
class ConversationCreate(BaseModel):
    app_id: Optional[str] = None
    name: Optional[str] = None
    mode: Optional[str] = "chat"
    agent_id: Optional[str] = None


class MessageCreate(BaseModel):
    query: str = Field(..., min_length=1)
    agent_id: Optional[str] = None


class RenameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class MessageResponse(BaseModel):
    id: str
    query: str
    answer: Optional[str]
    agent_id: Optional[str]
    agent_mode: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    total_price: float
    retrieval_used: bool
    retrieval_count: int
    message_metadata: dict
    created_at: str
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    name: Optional[str]
    status: str
    message_count: int
    total_tokens: int
    first_message: Optional[str]
    mode: Optional[str]
    agent_id: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user conversations"""
    query = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    )
    
    if status:
        query = query.filter(Conversation.status == status)
    
    conversations = query.order_by(
        Conversation.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return conversations


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new conversation"""
    if conversation_data.app_id:
        app = db.query(App).filter(App.id == conversation_data.app_id).first()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App not found"
            )
    
    conversation = Conversation(
        app_id=conversation_data.app_id,
        user_id=current_user.id,
        name=conversation_data.name or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        mode=conversation_data.mode,
        agent_id=conversation_data.agent_id,
        status="normal"
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    logger.info(f"Conversation created: {conversation.id} by user {current_user.id}")
    
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation details"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.status = "deleted"
    db.commit()
    
    logger.info(f"Conversation deleted: {conversation_id} by user {current_user.id}")
    
    return None


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    
    return messages


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message in conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    message = Message(
        conversation_id=conversation_id,
        query=message_data.query,
        answer="[Placeholder - implement agent logic]",
        agent_id=message_data.agent_id or conversation.agent_id,
        agent_mode=conversation.mode,
        model_provider="azure_openai",
        model_id="gpt-4",
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        total_price=0.0,
        retrieval_used=False,
        retrieval_count=0,
        message_metadata={},
        created_by=current_user.id
    )
    
    db.add(message)
    
    conversation.message_count += 1
    if not conversation.first_message:
        conversation.first_message = message_data.query
        conversation.first_message_id = message.id
    
    db.commit()
    db.refresh(message)
    
    logger.info(f"Message created in conversation {conversation_id}")
    
    return message


@router.post("/{conversation_id}/rename")
async def rename_conversation(
    conversation_id: str,
    request: RenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rename conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.name = request.name
    db.commit()
    
    return {"message": "Conversation renamed successfully"}


@router.post("/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.status = "archived"
    db.commit()
    
    return {"message": "Conversation archived successfully"}
