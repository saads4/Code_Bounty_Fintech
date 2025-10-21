from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.routes.utils import auth_user
from app.modules.model_recommendations import (
    recommend_for_ticker,
    recommend_for_portfolio as _recommend_for_portfolio,
)

router = APIRouter()


def _with_emoji(action: str) -> str:
    a = (action or "").upper()
    if a == "BUY":
        return "BUY \U0001F4C8"  # 📈
    if a == "SELL":
        return "SELL \U0001F4C9"  # 📉
    return "HOLD \U0001F914"     # 🤔


@router.get("/{ticker}")
def recommend_single(ticker: str, user = Depends(auth_user)):
    try:
        rec = recommend_for_ticker(ticker)
        return {
            "ticker": rec.ticker,
            "current_price": rec.current_price,  # may be null on fallback
            "recommendation": _with_emoji(rec.action),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Recommendation failed: {e}")


@router.get("/portfolio")
def recommend_portfolio(user = Depends(auth_user)):
    try:
        recs = _recommend_for_portfolio()
        return [
            {
                "ticker": r.ticker,
                "current_price": r.current_price,
                "recommendation": _with_emoji(r.action),
            }
            for r in recs
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Portfolio recommendation failed: {e}")
