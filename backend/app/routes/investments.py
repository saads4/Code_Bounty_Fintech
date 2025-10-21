from fastapi import APIRouter, Depends
from app.routes.utils import auth_user
from app.modules.ml_investments import InvestmentPredictor

router = APIRouter()
_model = InvestmentPredictor(); _model.train_baselines()

@router.get("/predict")
def predict(user = Depends(auth_user)):
    res = _model.predict_next()
    return res.__dict__
