from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.utils import auth_user
from app.modules.tax_india import compute_tax, suggest_deductions_old_regime

router = APIRouter()

class TaxIn(BaseModel):
    income: float
    deductions: float = 0.0
    use_new: bool = True

@router.post("/compute")
def compute(t: TaxIn, user = Depends(auth_user)):
    return compute_tax(t.income, t.deductions, t.use_new)

@router.get("/suggestions/old")
def suggestions_old(user = Depends(auth_user)):
    return suggest_deductions_old_regime()
