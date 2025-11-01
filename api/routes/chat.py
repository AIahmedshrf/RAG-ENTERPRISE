"""
Enhanced Chat Routes with RAG Support
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import logging

from api.database import get_db
from api.models import User, Conversation, Message
from api.middleware.auth import get_current_user
from core.rag.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat")


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    dataset_id: Optional[str] = None
    use_rag: bool = True
    top_k: int = 5
    agent_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    response: str
    conversation_id: str
    sources: List[dict] = []
    used_rag: bool
    model: str


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced chat endpoint with RAG support
    
    - If use_rag=True and dataset_id provided: Uses RAG
    - If use_rag=False: Direct LLM response
    - Returns sources/citations when RAG is used
    """
    logger.info(f"Chat request from user {current_user.id}: '{request.message[:50]}...'")
    
    response_text = ""
    sources = []
    used_rag = False
    
    try:
        # RAG Mode
        if request.use_rag and request.dataset_id:
            logger.info(f"Using RAG mode with dataset {request.dataset_id}")
            
            # Initialize RAG pipeline
            rag_pipeline = RAGPipeline(db)
            
            # Process query through RAG
            rag_result = await rag_pipeline.process_query(
                query=request.message,
                top_k=request.top_k,
                dataset_id=request.dataset_id
            )
            
            if rag_result['contexts']:
                # Build RAG prompt
                prompt = rag_pipeline.build_rag_prompt(
                    query=request.message,
                    contexts=rag_result['contexts']
                )
                
                # Generate response (placeholder - will use Azure OpenAI)
                response_text = await _generate_response(prompt)
                sources = rag_result['sources']
                used_rag = True
                
                logger.info(f"RAG response generated with {len(sources)} sources")
            else:
                response_text = "عذراً، لم أجد معلومات ذات صلة في المستندات المتاحة. يرجى تحميل مستندات ذات صلة أو إعادة صياغة السؤال."
                used_rag = False
        
        # Direct LLM Mode
        else:
            logger.info("Using direct LLM mode (no RAG)")
            response_text = await _generate_response(request.message)
            used_rag = False
        
        # Create or get conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                name=request.message[:50],
                mode='chat',
                status='normal'
            )
            db.add(conversation)
            db.flush()
        
        # Save message
        message = Message(
            conversation_id=conversation.id,
            query=request.message,
            answer=response_text,
            agent_id=request.agent_id,
            model_provider='azure_openai',
            model_id='gpt-4',
            retrieval_used=used_rag,
            retrieval_count=len(sources),
            message_metadata={
                'sources': sources if sources else [],
                'dataset_id': request.dataset_id
            },
            created_by=current_user.id
        )
        db.add(message)
        
        # Update conversation
        conversation.message_count += 1
        if not conversation.first_message:
            conversation.first_message = request.message
            conversation.first_message_id = message.id
        
        db.commit()
        db.refresh(conversation)
        
        return ChatResponse(
            message=request.message,
            response=response_text,
            conversation_id=conversation.id,
            sources=sources,
            used_rag=used_rag,
            model='gpt-4'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


async def _generate_response(prompt: str) -> str:
    """
    Generate response using LLM
    
    TODO: Integrate with Azure OpenAI GPT-4
    For now, returns a placeholder
    """
    # Placeholder implementation
    # In production, use Azure OpenAI:
    # from openai import AzureOpenAI
    # client = AzureOpenAI(...)
    # response = client.chat.completions.create(...)
    
    logger.info("Generating LLM response (placeholder)")
    
    return f"""[Placeholder Response]

هذه إجابة تجريبية. في الإصدار النهائي، سيتم استخدام Azure OpenAI GPT-4 لتوليد إجابة ذكية.

السؤال المطروح: {prompt[:200]}...

للتفعيل الكامل:
1. أضف Azure OpenAI credentials في .env
2. سيتم استبدال هذه الإجابة بإجابة GPT-4 الفعلية
3. الإجابة ستكون مبنية على السياق المسترجع من المستندات"""


@router.get("/agents")
async def list_agents(current_user: User = Depends(get_current_user)):
    """List available agents"""
    return {
        "agents": [
            {
                "id": "qa",
                "name": "QA Agent",
                "description": "Question answering with RAG",
                "supports_rag": True
            },
            {
                "id": "research",
                "name": "Research Agent",
                "description": "Deep research and analysis",
                "supports_rag": True
            },
            {
                "id": "financial",
                "name": "Financial Analyst",
                "description": "Financial analysis and insights",
                "supports_rag": True
            },
            {
                "id": "investment",
                "name": "Investment Advisor",
                "description": "Investment recommendations",
                "supports_rag": True
            }
        ]
    }


@router.post("/index-dataset")
async def index_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Index a dataset for RAG
    
    This generates embeddings for all document segments
    and stores them in the vector store
    """
    try:
        logger.info(f"Indexing dataset {dataset_id} by user {current_user.id}")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(db)
        
        # Index dataset
        result = await rag_pipeline.retriever.index_dataset(dataset_id)
        
        logger.info(f"Dataset indexed: {result}")
        
        return {
            "message": "Dataset indexed successfully",
            "dataset_id": dataset_id,
            "statistics": result
        }
        
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index dataset: {str(e)}"
        )


@router.get("/retrieval-stats")
async def get_retrieval_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get RAG retrieval statistics"""
    try:
        rag_pipeline = RAGPipeline(db)
        stats = await rag_pipeline.retriever.get_stats()
        
        return {
            "statistics": stats,
            "status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "statistics": {},
            "status": "error",
            "error": str(e)
        }
