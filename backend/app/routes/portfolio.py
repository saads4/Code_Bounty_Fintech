# backend/app/routes/portfolio.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List
import json
import os
from app.routes.utils import get_current_user_id
from app.modules.model_recommendations import recommend_for_ticker, _fetch_news_sentiment

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Path to portfolio (model is handled in model_recommendations)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PORTFOLIO_PATH = os.path.join(BASE_DIR, "new feature", "new model", "portfolio.json")

# Ensure directory exists
os.makedirs(os.path.dirname(PORTFOLIO_PATH), exist_ok=True)

class StockInput(BaseModel):
    ticker: str
    buy_price: float
    quantity: int

class PortfolioUpdate(BaseModel):
    stocks: Dict[str, dict]

def _emoji_for(action: str) -> str:
    a = (action or '').upper()
    if a == 'BUY':
        return '📈'
    if a == 'SELL':
        return '📉'
    return '🤔'

@router.get("/recommendations")
async def get_recommendations(user_id: int = Depends(get_current_user_id)):
    """Get stock recommendations for user's portfolio"""
    try:
        # Load portfolio
        if not os.path.exists(PORTFOLIO_PATH):
            return {"stocks": []}
        
        with open(PORTFOLIO_PATH, "r") as f:
            portfolio = json.load(f)
        
        results = []
        for ticker, info in portfolio.items():
            try:
                rec = recommend_for_ticker(ticker)
                current_price = rec.current_price if rec.current_price is not None else 0.0
                action = rec.action
                emoji = _emoji_for(action)
                company_name = ticker.split('.')[:1][0]
                sentiment = float(_fetch_news_sentiment(company_name))
                
                buy_price = info['buy_price']
                quantity = info['quantity']
                profit_loss = (current_price - buy_price) * quantity
                profit_loss_pct = ((current_price - buy_price) / buy_price) * 100
                
                results.append({
                    "ticker": ticker,
                    "buy_price": buy_price,
                    "current_price": round(current_price, 2),
                    "quantity": quantity,
                    "profit_loss": round(profit_loss, 2),
                    "profit_loss_pct": round(profit_loss_pct, 2),
                    "recommendation": action,
                    "emoji": emoji,
                    "sentiment": round(sentiment, 3)
                })
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
                continue
        
        return {"stocks": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-stock")
async def add_stock(stock: StockInput, user_id: int = Depends(get_current_user_id)):
    """Add a stock to the portfolio"""
    try:
        print(f"Adding stock: {stock.ticker}, buy_price: {stock.buy_price}, quantity: {stock.quantity}")
        print(f"Portfolio path: {PORTFOLIO_PATH}")
        
        # Load existing portfolio
        if os.path.exists(PORTFOLIO_PATH):
            print(f"Portfolio file exists, loading...")
            with open(PORTFOLIO_PATH, "r") as f:
                portfolio = json.load(f)
        else:
            print(f"Portfolio file doesn't exist, creating new...")
            portfolio = {}
        
        # Add new stock
        portfolio[stock.ticker] = {
            "buy_price": stock.buy_price,
            "quantity": stock.quantity
        }
        
        print(f"Updated portfolio: {portfolio}")
        
        # Save portfolio
        with open(PORTFOLIO_PATH, "w") as f:
            json.dump(portfolio, f, indent=2)
        
        print(f"Portfolio saved successfully")
        
        return {"message": "Stock added successfully", "portfolio": portfolio}
    except Exception as e:
        print(f"Error adding stock: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/remove-stock/{ticker}")
async def remove_stock(ticker: str, user_id: int = Depends(get_current_user_id)):
    """Remove a stock from the portfolio"""
    try:
        if not os.path.exists(PORTFOLIO_PATH):
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        with open(PORTFOLIO_PATH, "r") as f:
            portfolio = json.load(f)
        
        if ticker not in portfolio:
            raise HTTPException(status_code=404, detail="Stock not found in portfolio")
        
        del portfolio[ticker]
        
        with open(PORTFOLIO_PATH, "w") as f:
            json.dump(portfolio, f, indent=2)
        
        return {"message": "Stock removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio")
async def get_portfolio(user_id: int = Depends(get_current_user_id)):
    """Get current portfolio"""
    try:
        if not os.path.exists(PORTFOLIO_PATH):
            return {"stocks": {}}
        
        with open(PORTFOLIO_PATH, "r") as f:
            portfolio = json.load(f)
        
        return {"stocks": portfolio}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
