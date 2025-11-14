"""
Workflows Management Routes
Handles agent workflow creation, execution, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from api.database import get_db
from api.models.user import User
from core.auth import get_current_user, require_admin
from agents.workflow import (
    AgentWorkflow, WorkflowStep, WorkflowStatus, 
    WorkflowTemplates, PipelineBuilder
)
from agents.agent_factory import get_agent_factory
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflows"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class WorkflowStepRequest(BaseModel):
    """Workflow step request"""
    name: str = Field(..., min_length=1)
    agent_type: str = Field(..., description="Type of agent to use")


class WorkflowTemplateRequest(BaseModel):
    """Request to create workflow from template"""
    template_type: str = Field(
        ..., 
        description="Template type: portfolio_review, compliance_review, market_analysis"
    )


class WorkflowExecutionRequest(BaseModel):
    """Workflow execution request"""
    workflow_id: str
    context: Optional[dict] = None


class WorkflowResponse(BaseModel):
    """Workflow response model"""
    workflow_id: str
    name: str
    status: str
    steps: int
    created_at: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# WORKFLOW MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/from-template", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_workflow_from_template(
    request: WorkflowTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create workflow from predefined template
    """
    try:
        template_type = request.template_type.lower()
        
        # Create workflow from template
        if template_type == "portfolio_review":
            workflow = WorkflowTemplates.create_portfolio_review_workflow()
        elif template_type == "compliance_review":
            workflow = WorkflowTemplates.create_compliance_review_workflow()
        elif template_type == "market_analysis":
            workflow = WorkflowTemplates.create_market_analysis_workflow()
        else:
            raise ValueError(f"Unknown template type: {template_type}")
        
        logger.info(f"Workflow created from template: {template_type} (ID: {workflow.workflow_id})")
        
        return {
            "data": {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "steps": len(workflow.steps),
                "template_type": template_type
            },
            "message": "Workflow created from template"
        }
    
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.post("/custom", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_custom_workflow(
    workflow_name: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create custom workflow
    """
    try:
        workflow_id = str(uuid.uuid4())
        workflow = AgentWorkflow(workflow_id, workflow_name)
        
        logger.info(f"Custom workflow created: {workflow_name} (ID: {workflow_id})")
        
        return {
            "data": {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "steps": 0
            },
            "message": "Custom workflow created"
        }
    
    except Exception as e:
        logger.error(f"Error creating custom workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.post("/{workflow_id}/add-step", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_workflow_step(
    workflow_id: str,
    request: WorkflowStepRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add step to workflow
    Note: In production, workflows would be stored in database
    """
    try:
        # In a real implementation, you would fetch the workflow from DB
        # For now, we return a response structure
        
        logger.info(f"Step added to workflow: {workflow_id}")
        
        return {
            "data": {
                "workflow_id": workflow_id,
                "step_name": request.name,
                "agent_type": request.agent_type,
                "status": "added"
            },
            "message": "Step added to workflow"
        }
    
    except Exception as e:
        logger.error(f"Error adding step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add step: {str(e)}"
        )


@router.post("/{workflow_id}/execute", response_model=dict)
async def execute_workflow(
    workflow_id: str,
    request: WorkflowExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute workflow with provided context
    """
    try:
        start_time = datetime.now()
        
        # Get appropriate workflow template for demo
        # In production, this would be fetched from DB
        context = request.context or {}
        
        # Execute based on workflow_id pattern
        if "portfolio" in workflow_id.lower():
            workflow = WorkflowTemplates.create_portfolio_review_workflow()
        elif "compliance" in workflow_id.lower():
            workflow = WorkflowTemplates.create_compliance_review_workflow()
        elif "market" in workflow_id.lower():
            workflow = WorkflowTemplates.create_market_analysis_workflow()
        else:
            workflow = AgentWorkflow(workflow_id, "Custom Workflow")
        
        # Execute workflow
        results = await workflow.execute(context)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        report = workflow.get_execution_report()
        
        logger.info(f"Workflow executed: {workflow_id} ({duration:.2f}ms)")
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "duration_ms": int(duration),
            "timestamp": datetime.now().isoformat(),
            "report": report,
            "results": results,
            "message": "Workflow executed successfully"
        }
    
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )


@router.get("/{workflow_id}/status", response_model=dict)
async def get_workflow_status(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get workflow execution status
    """
    try:
        # In production, fetch from database
        return {
            "data": {
                "workflow_id": workflow_id,
                "status": "ready",
                "message": "Workflow available for execution"
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {str(e)}"
        )


# ============================================================================
# TEMPLATES ENDPOINTS
# ============================================================================

@router.get("/templates/available", response_model=dict)
async def get_available_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available workflow templates
    """
    try:
        templates = {
            "portfolio_review": {
                "name": "Portfolio Review",
                "description": "Complete portfolio analysis with risk, market, and compliance checks",
                "steps": 5,
                "agents": ["portfolio", "risk", "market", "compliance", "summarizer"]
            },
            "compliance_review": {
                "name": "Compliance Review",
                "description": "Compliance verification with risk assessment",
                "steps": 3,
                "agents": ["compliance", "risk", "summarizer"]
            },
            "market_analysis": {
                "name": "Market Analysis",
                "description": "Market trends and analysis with summary",
                "steps": 2,
                "agents": ["market", "summarizer"]
            }
        }
        
        return {
            "data": templates,
            "total": len(templates),
            "message": "Available templates retrieved"
        }
    
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}"
        )


@router.get("/templates/{template_type}/preview", response_model=dict)
async def preview_template(
    template_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview workflow template
    """
    try:
        template_type = template_type.lower()
        
        if template_type == "portfolio_review":
            workflow = WorkflowTemplates.create_portfolio_review_workflow()
        elif template_type == "compliance_review":
            workflow = WorkflowTemplates.create_compliance_review_workflow()
        elif template_type == "market_analysis":
            workflow = WorkflowTemplates.create_market_analysis_workflow()
        else:
            raise ValueError(f"Unknown template: {template_type}")
        
        steps_preview = [
            {
                "name": step.name,
                "agent_type": step.agent_type,
                "order": idx + 1
            }
            for idx, step in enumerate(workflow.steps)
        ]
        
        return {
            "data": {
                "template_type": template_type,
                "name": workflow.name,
                "total_steps": len(workflow.steps),
                "steps": steps_preview
            },
            "message": "Template preview"
        }
    
    except Exception as e:
        logger.error(f"Error previewing template: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found: {str(e)}"
        )
