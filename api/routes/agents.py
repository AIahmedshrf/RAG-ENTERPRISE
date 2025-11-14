"""
Agent Management Routes with Dify Integration
Handles agent creation, execution, and management via Dify workflow engine
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from api.database import get_db
from api.models.user import User
from core.auth import get_current_user, require_admin
from core.dify_service import get_dify_client, DifyServiceManager
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class AgentConfigRequest(BaseModel):
    """Agent configuration"""
    name: str = Field(..., min_length=1, max_length=255)
    agent_type: str = Field(..., description="Agent type: portfolio, risk, market, compliance, summarizer")
    description: Optional[str] = None
    config: Optional[dict] = None


class AgentExecutionRequest(BaseModel):
    """Agent execution request"""
    inputs: dict = Field(..., description="Input parameters for agent")
    user_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent response model"""
    id: str
    name: str
    agent_type: str
    description: Optional[str]
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True


class AgentExecutionResponse(BaseModel):
    """Agent execution response"""
    execution_id: str
    agent_id: str
    status: str
    output: Optional[dict]
    duration_ms: Optional[int]
    created_at: str


# ============================================================================
# AGENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_agent(
    request: AgentConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create new agent in Dify
    Requires admin permissions
    """
    try:
        dify_client = get_dify_client()
        manager = DifyServiceManager(dify_client)
        
        # Create agent in Dify
        app_id = await manager.create_agent(
            name=request.name,
            agent_type=request.agent_type,
            description=request.description,
            config=request.config
        )
        
        logger.info(f"Agent created: {request.name} (ID: {app_id})")
        
        return {
            "data": {
                "id": app_id,
                "name": request.name,
                "agent_type": request.agent_type,
                "description": request.description,
                "status": "created"
            },
            "message": "Agent created successfully"
        }
    
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("", response_model=dict)
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all agents accessible to user
    """
    try:
        dify_client = get_dify_client()
        manager = DifyServiceManager(dify_client)
        
        # Get agents from Dify
        agents = await manager.list_agents(limit=limit, offset=skip)
        
        return {
            "data": agents,
            "skip": skip,
            "limit": limit,
            "total": len(agents),
            "message": f"Retrieved {len(agents)} agents"
        }
    
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=dict)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get agent details by ID
    """
    try:
        dify_client = get_dify_client()
        
        # Get agent from Dify
        agent = dify_client.get_app(agent_id)
        
        return {
            "data": agent,
            "message": "Agent details retrieved"
        }
    
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {str(e)}"
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete agent from Dify
    Requires admin permissions
    """
    try:
        dify_client = get_dify_client()
        manager = DifyServiceManager(dify_client)
        
        # Delete agent
        await manager.delete_agent(agent_id)
        
        logger.info(f"Agent deleted: {agent_id}")
        return None
    
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


# ============================================================================
# AGENT EXECUTION ENDPOINTS
# ============================================================================

@router.post("/{agent_id}/execute", response_model=dict)
async def execute_agent(
    agent_id: str,
    request: AgentExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute agent with provided inputs
    Returns execution result immediately
    """
    try:
        start_time = datetime.now()
        dify_client = get_dify_client()
        manager = DifyServiceManager(dify_client)
        
        # Execute agent
        user_id = request.user_id or str(current_user.id)
        result = await manager.execute_agent(
            app_id=agent_id,
            inputs=request.inputs,
            user_id=user_id
        )
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(f"Agent executed: {agent_id} ({duration:.2f}ms)")
        
        return {
            "execution_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "status": "completed",
            "output": result,
            "duration_ms": int(duration),
            "timestamp": datetime.now().isoformat(),
            "message": "Agent executed successfully"
        }
    
    except Exception as e:
        logger.error(f"Error executing agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute agent: {str(e)}"
        )


@router.post("/{agent_id}/execute-async", response_model=dict)
async def execute_agent_async(
    agent_id: str,
    request: AgentExecutionRequest,
    webhook_url: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute agent asynchronously
    Returns task ID for tracking
    """
    try:
        dify_client = get_dify_client()
        
        # Execute async
        user_id = request.user_id or str(current_user.id)
        result = dify_client.run_workflow_async(
            app_id=agent_id,
            inputs=request.inputs,
            webhook_url=webhook_url,
            user_id=user_id
        )
        
        task_id = result.get('task_id')
        logger.info(f"Agent async execution started: {agent_id} (Task: {task_id})")
        
        return {
            "task_id": task_id,
            "agent_id": agent_id,
            "status": "pending",
            "message": "Agent execution started",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error starting async execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start execution: {str(e)}"
        )


@router.get("/{agent_id}/task/{task_id}", response_model=dict)
async def get_execution_status(
    agent_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get status of async task execution
    """
    try:
        dify_client = get_dify_client()
        
        # Get task status
        status_result = dify_client.get_execution_status(agent_id, task_id)
        
        return {
            "data": status_result,
            "message": "Task status retrieved"
        }
    
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {str(e)}"
        )


# ============================================================================
# AGENT LOGS & ANALYTICS
# ============================================================================

@router.get("/{agent_id}/logs", response_model=dict)
async def get_agent_logs(
    agent_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get execution logs for agent
    """
    try:
        dify_client = get_dify_client()
        
        # Get logs
        logs = dify_client.get_execution_logs(agent_id, limit=limit, offset=skip)
        
        return {
            "data": logs,
            "skip": skip,
            "limit": limit,
            "message": "Logs retrieved"
        }
    
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve logs: {str(e)}"
        )


@router.get("/{agent_id}/analytics", response_model=dict)
async def get_agent_analytics(
    agent_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get agent performance analytics
    """
    try:
        dify_client = get_dify_client()
        
        # Get analytics
        analytics = dify_client.get_app_analytics(
            agent_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "data": analytics,
            "message": "Analytics retrieved"
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )


# ============================================================================
# MODELS & TOOLS
# ============================================================================

@router.get("/available/models", response_model=dict)
async def get_available_models(
    model_type: str = Query("llm"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available LLM models for agents
    """
    try:
        dify_client = get_dify_client()
        
        # Get models
        models = dify_client.list_models(model_type=model_type)
        
        return {
            "data": models,
            "message": "Available models retrieved"
        }
    
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve models: {str(e)}"
        )


@router.get("/available/tools", response_model=dict)
async def get_available_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available tools for agent workflows
    """
    try:
        dify_client = get_dify_client()
        
        # Get tools
        tools = dify_client.list_tools()
        
        return {
            "data": tools,
            "message": "Available tools retrieved"
        }
    
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tools: {str(e)}"
        )



@router.get("/", summary="List agents")
def list_agents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # For now, list all agents for authenticated users; later add tenant/owner filtering
    agents = db.query(Agent).all()
    result = []
    for a in agents:
        result.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "dataset_ids": a.get_dataset_ids(),
            "is_active": a.is_active,
            "owner_id": a.owner_id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })
    return {"agents": result}


@router.post("/", summary="Create an agent")
def create_agent(payload: AgentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    agent = Agent(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
        is_active=True
    )
    agent.set_dataset_ids(payload.dataset_ids or [])
    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "dataset_ids": agent.get_dataset_ids(),
        "is_active": agent.is_active,
        "owner_id": agent.owner_id,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
    }


@router.get("/{agent_id}", summary="Get agent details")
def get_agent(agent_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "dataset_ids": agent.get_dataset_ids(),
        "is_active": agent.is_active,
        "owner_id": agent.owner_id,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
    }


@router.delete("/{agent_id}", summary="Delete an agent")
def delete_agent(agent_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"status": "deleted"}
