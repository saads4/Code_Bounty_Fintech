# backend/app/routes/advisor.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path
import pandas as pd
from app.modules.new.stock_advisor import train_models

router = APIRouter(prefix="/api/advisor", tags=["advisor"])

# Global cache for models and dataframe
_MODELS = None
_DF = None
_CSV_PATH = Path(__file__).resolve().parents[1] / 'modules' / 'new' / 'stock_data_7stocks.csv'


def _ensure_models():
    global _MODELS, _DF
    if _MODELS is None or _DF is None:
        if not _CSV_PATH.exists():
            raise HTTPException(status_code=500, detail=f"Dataset not found: {_CSV_PATH}")
        models, df = train_models(str(_CSV_PATH))
        if not models:
            raise HTTPException(status_code=500, detail="No models trained from dataset")
        # Normalize keys to uppercase for stable lookups
        _MODELS = {str(k).upper(): v for k, v in models.items()}
        # Also store a normalized uppercase symbol column for filtering
        df = df.copy()
        df['__SYMBOL_UPPER__'] = df['Symbol'].astype(str).str.upper()
        _DF = df


@router.get('/symbols', response_model=List[str])
def list_symbols():
    _ensure_models()
    return sorted([str(s) for s in _DF['__SYMBOL_UPPER__'].unique()])


class RecommendRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol present in dataset")
    buy_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)


@router.post('/recommend')
def recommend(req: RecommendRequest):
    _ensure_models()
    sym = req.symbol.upper()
    if sym not in _MODELS:
        raise HTTPException(status_code=400, detail="Symbol not found in dataset")

    model, features = _MODELS[sym]
    recent = _DF[_DF['__SYMBOL_UPPER__'] == sym].copy().tail(1)
    if recent.empty:
        raise HTTPException(status_code=400, detail="No recent data for symbol")

    X_last = recent[features]
    # For binary RF, ensure predict_proba exists
    if not hasattr(model, 'predict_proba'):
        raise HTTPException(status_code=500, detail="Model doesn't support probability predictions")

    prob_up = float(model.predict_proba(X_last)[0][1])
    if prob_up > 0.6:
        decision = "BUY"
    elif prob_up < 0.4:
        decision = "SELL"
    else:
        decision = "HOLD"

    latest_close = float(recent['Close'].iloc[-1])
    profit_loss = float((latest_close - req.buy_price) * req.quantity)

    return {
        "symbol": sym,
        "latest_close": round(latest_close, 2),
        "prob_up": round(prob_up, 3),
        "decision": decision,
        "profit_loss": round(profit_loss, 2),
    }
