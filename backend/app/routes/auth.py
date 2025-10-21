from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.db import Base, engine, get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

Base.metadata.create_all(bind=engine)
router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first():
        raise HTTPException(400, "Email already registered")
    u = User(email=data.email, hashed_password=hash_password(data.password), full_name=data.full_name)
    db.add(u); db.commit(); db.refresh(u)
    token = create_access_token(str(u.id))
    return TokenOut(access_token=token)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email==data.email).first()
    if not u or not verify_password(data.password, u.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(str(u.id))
    return TokenOut(access_token=token)
