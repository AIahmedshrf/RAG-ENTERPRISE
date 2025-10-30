"""
User Management APIs
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr

from api.database import get_db
from api.models.user import User
from utilities.logger import logger

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "user"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """قائمة جميع المستخدمين"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """الحصول على مستخدم محدد"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """إنشاء مستخدم جديد"""
    
    # التحقق من وجود المستخدم
    existing = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # إنشاء المستخدم
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=f"hashed_{user.password}",  # TODO: hash properly
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"Created user: {db_user.username}")
    return db_user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """حذف مستخدم"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    logger.info(f"Deleted user: {user.username}")
    return {"success": True, "message": "User deleted"}


@router.get("/stats/summary")
async def get_user_stats(db: Session = Depends(get_db)):
    """إحصائيات المستخدمين"""
    total = db.query(User).count()
    active = db.query(User).filter(User.is_active == True).count()
    admins = db.query(User).filter(User.role == "admin").count()
    
    return {
        "total_users": total,
        "active_users": active,
        "admin_users": admins,
        "inactive_users": total - active
    }
