from fastapi import Header, HTTPException, Depends
import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.models.user import User

def get_current_user_id(authorization: str = Header(default=""))->int:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ",1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return int(payload["sub"])
    except Exception:
        raise HTTPException(401, "Invalid token")

def auth_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db))->User:
    u = db.query(User).get(user_id)
    if not u: raise HTTPException(401, "User not found")
    return u
