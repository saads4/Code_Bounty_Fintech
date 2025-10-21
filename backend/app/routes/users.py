# backend/app/routes/users.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.routes.utils import auth_user
from app.models.user import User
from app.core.db import get_db
from app.core.security import hash_password

router = APIRouter()

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool
    class Config:
        from_attributes = True

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(auth_user)):
    return user

class UpdateIn(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

@router.put("/me", response_model=UserOut)
def update_me(data: UpdateIn, user: User = Depends(auth_user), db: Session = Depends(get_db)):
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.password:
        user.hashed_password = hash_password(data.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
