"""
Tools Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from api.database import get_db
from api.models import Tool, ToolProvider, User, Tenant
from api.middleware.auth import get_current_user
from api.middleware.tenant import get_current_tenant
from utilities.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/tools")


# Request/Response Models
class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    label: dict = Field(..., description="Multi-language labels")
    description: Optional[dict] = None
    icon: Optional[str] = None
    type: str = Field(default="custom", pattern="^(builtin|custom|api)$")
    provider_id: Optional[str] = None
    parameters: List[dict] = Field(default=[])
    config: dict = Field(default={})
    privacy_policy: Optional[str] = None


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    label: Optional[dict] = None
    description: Optional[dict] = None
    icon: Optional[str] = None
    parameters: Optional[List[dict]] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class ToolResponse(BaseModel):
    id: str
    name: str
    label: dict
    description: Optional[dict]
    icon: Optional[str]
    type: str
    provider_id: Optional[str]
    parameters: List[dict]
    is_active: bool
    usage_count: int
    created_at: str
    
    class Config:
        from_attributes = True


class ToolProviderResponse(BaseModel):
    id: str
    name: str
    label: dict
    description: Optional[dict]
    icon: Optional[str]
    type: str
    is_active: bool
    tools: List[dict]
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ToolResponse])
async def list_tools(
    skip: int = 0,
    limit: int = 50,
    type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    List all available tools
    """
    query = db.query(Tool)
    
    # Filter by type
    if type:
        query = query.filter(Tool.type == type)
    
    # Filter by active status
    if is_active is not None:
        query = query.filter(Tool.is_active == is_active)
    
    # Get builtin tools + tenant tools
    tools = query.filter(
        (Tool.tenant_id == current_tenant.id) | (Tool.tenant_id.is_(None))
    ).offset(skip).limit(limit).all()
    
    return tools


@router.post("", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_data: ToolCreate,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Create custom tool
    """
    # Check permission
    if not current_user.has_permission("tools", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to create tools"
        )
    
    # Verify provider if provided
    if tool_data.provider_id:
        provider = db.query(ToolProvider).filter(
            ToolProvider.id == tool_data.provider_id
        ).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool provider not found"
            )
    
    # Create tool
    tool = Tool(
        name=tool_data.name,
        label=tool_data.label,
        description=tool_data.description,
        icon=tool_data.icon,
        type=tool_data.type,
        provider_id=tool_data.provider_id,
        parameters=tool_data.parameters,
        config=tool_data.config,
        privacy_policy=tool_data.privacy_policy,
        tenant_id=current_tenant.id,
        is_active=True
    )
    
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    logger.info(f"Tool created: {tool.id} by user {current_user.id}")
    
    return tool


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get tool details
    """
    tool = db.query(Tool).filter(
        Tool.id == tool_id,
        (Tool.tenant_id == current_tenant.id) | (Tool.tenant_id.is_(None))
    ).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    return tool


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: str,
    tool_data: ToolUpdate,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Update custom tool
    """
    # Check permission
    if not current_user.has_permission("tools", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to update tools"
        )
    
    # Get tool
    tool = db.query(Tool).filter(
        Tool.id == tool_id,
        Tool.tenant_id == current_tenant.id
    ).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found or not editable"
        )
    
    # Cannot update builtin tools
    if tool.type == "builtin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update builtin tools"
        )
    
    # Update fields
    update_data = tool_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tool, field, value)
    
    db.commit()
    db.refresh(tool)
    
    logger.info(f"Tool updated: {tool.id} by user {current_user.id}")
    
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Delete custom tool
    """
    # Check permission
    if not current_user.has_permission("tools", "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete tools"
        )
    
    # Get tool
    tool = db.query(Tool).filter(
        Tool.id == tool_id,
        Tool.tenant_id == current_tenant.id
    ).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Cannot delete builtin tools
    if tool.type == "builtin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete builtin tools"
        )
    
    db.delete(tool)
    db.commit()
    
    logger.info(f"Tool deleted: {tool_id} by user {current_user.id}")
    
    return None


@router.get("/providers/", response_model=List[ToolProviderResponse])
async def list_tool_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all tool providers
    """
    providers = db.query(ToolProvider).filter(
        ToolProvider.is_active == True
    ).all()
    
    return providers


@router.post("/{tool_id}/invoke")
async def invoke_tool(
    tool_id: str,
    parameters: dict,
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Invoke/Execute a tool
    
    Note: This is a placeholder. Actual implementation should:
    1. Validate parameters against tool schema
    2. Execute the tool logic
    3. Return results
    4. Update usage statistics
    """
    # Get tool
    tool = db.query(Tool).filter(
        Tool.id == tool_id,
        (Tool.tenant_id == current_tenant.id) | (Tool.tenant_id.is_(None))
    ).first()
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    if not tool.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool is not active"
        )
    
    # Increment usage count
    tool.usage_count += 1
    db.commit()
    
    # TODO: Implement actual tool execution logic
    logger.info(f"Tool invoked: {tool_id} by user {current_user.id}")
    
    return {
        "tool_id": tool_id,
        "tool_name": tool.name,
        "status": "success",
        "result": "[Tool execution placeholder - implement actual logic]",
        "parameters": parameters
    }
