from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.routes.utils import auth_user
from app.modules.ml_budget import categorize_expenses, recommend_budgets

router = APIRouter()

class Item(BaseModel):
    description: str
    amount: float
    type: str = "expense"

@router.post("/categorize")
def categorize(items: List[Item], user = Depends(auth_user)):
    return {"items": categorize_expenses([i.model_dump() for i in items])}

@router.post("/recommend")
def recommend(history: List[Item], user = Depends(auth_user)):
    return recommend_budgets([h.model_dump() for h in history])
