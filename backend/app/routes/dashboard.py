from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.routes.utils import auth_user
from app.models.transaction import Transaction
import pandas as pd

router = APIRouter()

@router.get("/kpis")
def kpis(db: Session = Depends(get_db), user = Depends(auth_user)):
    tx = db.query(Transaction).filter(Transaction.user_id==user.id).all()
    df = pd.DataFrame([{"amount":t.amount, "category":t.category} for t in tx]) if tx else pd.DataFrame(columns=["amount","category"])
    total_spend = float(df["amount"].clip(lower=0).sum()) if not df.empty else 0.0
    savings = 100000.0 - total_spend
    credit_score = 740
    returns = 0.06
    tax_liability = 25000.0
    return {"savings": savings, "credit_score": credit_score, "returns": returns, "tax_liability": tax_liability}
