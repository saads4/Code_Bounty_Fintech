# backend/app/routes/users.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.utils import auth_user
from app.models.user import User

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
