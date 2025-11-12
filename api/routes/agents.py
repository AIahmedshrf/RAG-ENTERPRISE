"""Agents management routes backed by the database.

Endpoints:
 - GET /       : list agents (requires auth)
 - POST /      : create agent (admin only)
 - GET /{id}   : get agent details (requires auth)
 - DELETE /{id}: delete agent (admin only)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.agent import Agent
from core.auth import get_current_user, get_current_admin_user

router = APIRouter()


class AgentCreate(BaseModel):
    name: str
    description: str | None = None
    dataset_ids: List[str] | None = None


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
