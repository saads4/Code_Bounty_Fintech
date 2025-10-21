from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.utils import auth_user
from app.modules.ml_credit import CreditModel

router = APIRouter()
_model = CreditModel(); metrics = _model.train()

class Features(BaseModel):
    income: float
    age: int
    utilization: float
    late_pay: int
    dti: float

@router.get("/metrics")
def model_metrics(user = Depends(auth_user)):
    return metrics

@router.post("/score")
def score(f: Features, user = Depends(auth_user)):
    return _model.score(f.model_dump())
