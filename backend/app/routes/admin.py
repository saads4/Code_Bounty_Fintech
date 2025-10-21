from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.routes.utils import auth_user
from app.core.db import get_db
from app.models.user import User
from app.models.transaction import Transaction

router = APIRouter()

def ensure_admin(u: User):
    if not u.is_admin: raise HTTPException(403, "Admin only")

class TxIn(BaseModel):
    user_id: int
    category: str
    description: str
    amount: float

@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(auth_user)):
    ensure_admin(user)
    total_users = db.query(User).count()
    total_tx = db.query(Transaction).count()
    return {"total_users": total_users, "total_transactions": total_tx}

@router.post("/tx/create")
def create_tx(t: TxIn, db: Session = Depends(get_db), user: User = Depends(auth_user)):
    ensure_admin(user)
    tx = Transaction(**t.model_dump()); db.add(tx); db.commit(); db.refresh(tx)
    return {"id": tx.id}
