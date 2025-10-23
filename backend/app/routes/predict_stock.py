# backend/app/routes/predict_stock.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.linear_model import Ridge
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import time
from pathlib import Path

# Reuse helpers from the provided module
from app.modules.Stock_recomendation import calculate_indicators, get_sentiment

router = APIRouter(prefix="/api", tags=["prediction"])


class PredictStockRequest(BaseModel):
    symbol: str = Field(..., description="Ticker symbol, e.g. RELIANCE.NS")
    buy_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)


@router.post("/predict_stock")
def predict_stock(req: PredictStockRequest):
    try:
        if not req.symbol or not isinstance(req.symbol, str):
            raise HTTPException(status_code=400, detail="Invalid symbol")

        # Build resilient HTTP session
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        })
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"]) 
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        sess.mount("http://", adapter)
        sess.mount("https://", adapter)

        # Simple local cache to mitigate provider flakiness
        cache_dir = Path(__file__).resolve().parents[3] / 'backend' / '.cache' / 'predict_stock'
        cache_dir.mkdir(parents=True, exist_ok=True)

        def _cache_path(sym: str) -> Path:
            safe = sym.replace('/', '_').replace('\\', '_').upper()
            return cache_dir / f"{safe}.csv"

        def _load_cache(sym: str, max_age_sec: int = 24*3600):
            p = _cache_path(sym)
            if not p.exists():
                return None
            try:
                if (time.time() - p.stat().st_mtime) <= max_age_sec:
                    return pd.read_csv(p)
            except Exception:
                return None
            return None

        def _save_cache(sym: str, df: pd.DataFrame):
            try:
                if df is not None and not df.empty:
                    out = df.copy()
                    if not isinstance(out.index, pd.RangeIndex):
                        out = out.reset_index()
                    _cache_path(sym).write_text(out.to_csv(index=False))
            except Exception:
                pass

        # Prefer TwelveData first if API key provided. If it fails, return degraded without Yahoo (to avoid 429 noise).
        last_err = None
        df = pd.DataFrame()
        used_twelvedata = False
        try:
            api_key = os.getenv('TWELVE_DATA_KEY')
            if api_key:
                used_twelvedata = True
                sym0 = req.symbol.upper()
                base = sym0.replace('.NS', '') if sym0.endswith('.NS') else sym0
                candidates = []
                candidates.append(f"{base}:NS")
                candidates.append(f"NSE:{base}")
                candidates.append(f"{base}:NSE")
                candidates.append(sym0)  # last resort
                for symbol_td in candidates:
                    params = {
                        'symbol': symbol_td,
                        'interval': '1day',
                        'outputsize': 500,
                        'format': 'JSON',
                        'apikey': api_key,
                    }
                    r = sess.get('https://api.twelvedata.com/time_series', params=params, timeout=15)
                    j = r.json()
                    if isinstance(j, dict) and 'status' in j and j.get('status') == 'error':
                        continue
                    if isinstance(j, dict) and 'values' in j and isinstance(j['values'], list) and len(j['values']) > 0:
                        tdf = pd.DataFrame(j['values'])
                        if not tdf.empty:
                            tdf['datetime'] = pd.to_datetime(tdf['datetime'])
                            tdf = tdf.sort_values('datetime')
                            tdf.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'}, inplace=True)
                            tdf.set_index('datetime', inplace=True)
                            for c in ['Open','High','Low','Close','Volume']:
                                tdf[c] = pd.to_numeric(tdf[c], errors='coerce')
                            tdf.dropna(inplace=True)
                            if not tdf.empty and 'Close' in tdf.columns:
                                df = tdf
                                break
        except Exception as e3:
            last_err = e3

        # If TwelveData was attempted but failed, return degraded directly
        if used_twelvedata and (df is None or df.empty or 'Close' not in df.columns):
            # Try cache before degraded
            cached = _load_cache(req.symbol)
            if isinstance(cached, pd.DataFrame) and not cached.empty:
                df = cached
            else:
                sentiment = float(get_sentiment(req.symbol))
                return {
                    "symbol": req.symbol,
                    "current_price": None,
                    "predicted_price": None,
                    "potential_profit": None,
                    "rsi": None,
                    "sentiment": round(sentiment, 3),
                    "recommendation": "HOLD — Data temporarily unavailable; showing sentiment only.",
                    "r2": None,
                    "mae": None,
                    "degraded": True,
                }

        # Fall back to Yahoo variants only if TwelveData was not used
        if (not used_twelvedata) and (df is None or df.empty or 'Close' not in df.columns):
            variants = [req.symbol, req.symbol.upper()]
            if req.symbol.upper().endswith('.NS'):
                variants.append(req.symbol.upper().replace('.NS', ''))
                variants.append(req.symbol.upper().replace('.NS', '.BO'))

            for sym in variants:
                # First attempt: download API (no session support), safer flags and shorter period
                for _ in range(2):
                    try:
                        df = yf.download(sym, period="120d", interval="1d", progress=False, auto_adjust=True, threads=False, repair=True)
                        if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                            break
                    except Exception as e:
                        last_err = e
                if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                    break
                # Second attempt: Ticker().history with our session
                try:
                    hist = yf.Ticker(sym, session=sess).history(period="6mo", interval="1d", auto_adjust=True)
                    if isinstance(hist, pd.DataFrame) and not hist.empty:
                        df = hist
                        break
                except Exception as e2:
                    last_err = e2

        if df is None or df.empty or 'Close' not in df.columns:
            # Try cache before degraded
            cached = _load_cache(req.symbol)
            if isinstance(cached, pd.DataFrame) and not cached.empty:
                df = cached
            else:
                # Degraded fallback: return sentiment-only
                sentiment = float(get_sentiment(req.symbol))
                return {
                    "symbol": req.symbol,
                    "current_price": None,
                    "predicted_price": None,
                    "potential_profit": None,
                    "rsi": None,
                    "sentiment": round(sentiment, 3),
                    "recommendation": "HOLD — Data temporarily unavailable; showing sentiment only.",
                    "r2": None,
                    "mae": None,
                    "degraded": True,
                }

        # Indicators
        df = calculate_indicators(df)
        if df is None or df.empty or 'Close' not in df.columns:
            raise HTTPException(status_code=400, detail="Insufficient data after indicators")

        # Features/labels
        X = df[['Return', 'SMA_5', 'SMA_20', 'RSI']]
        y = df['Close'].shift(-1).dropna()
        X = X.iloc[:-1]

        # Lightweight ML fallback when data is limited
        if len(X) < 50:
            sentiment = float(get_sentiment(req.symbol))
            current_price = float(df['Close'].iloc[-1])
            last_rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df.columns and not pd.isna(df['RSI'].iloc[-1]) else None

            # If we have at least 20 samples, fit a Ridge model to provide metrics
            if len(X) >= 20:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
                ridge = Ridge(alpha=1.0, random_state=42)
                ridge.fit(X_train, y_train)
                y_pred = ridge.predict(X_test)
                r2 = float(r2_score(y_test, y_pred))
                mae = float(mean_absolute_error(y_test, y_pred))
                next_day_pred = float(ridge.predict([X.iloc[-1]])[0])
            else:
                # Too few samples for ML; use SMA_5 as baseline
                sma5 = float(df['SMA_5'].iloc[-1]) if 'SMA_5' in df.columns and not pd.isna(df['SMA_5'].iloc[-1]) else current_price
                next_day_pred = sma5
                r2 = None
                mae = None

            sentiment_factor = 1 + (sentiment / 5.0)
            adjusted_pred = float(next_day_pred * sentiment_factor)
            potential_profit = float((adjusted_pred - req.buy_price) * req.quantity)

            if last_rsi is not None and last_rsi < 30:
                recommendation = "BUY — Oversold condition."
            elif last_rsi is not None and last_rsi > 70:
                recommendation = "SELL — Overbought condition."
            elif adjusted_pred > current_price * 1.01:
                recommendation = "HOLD — Predicted rise expected soon."
            else:
                recommendation = "SELL — Weak momentum detected."

            return {
                "symbol": req.symbol,
                "current_price": round(current_price, 2),
                "predicted_price": round(adjusted_pred, 2),
                "potential_profit": round(potential_profit, 2),
                "rsi": round(last_rsi, 2) if last_rsi is not None else None,
                "sentiment": round(sentiment, 3),
                "recommendation": recommendation,
                "r2": round(r2, 3) if r2 is not None else None,
                "mae": round(mae, 3) if mae is not None else None,
                "degraded": False,
            }

        # Train/test split and model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = RandomForestRegressor(n_estimators=150, random_state=42)
        model.fit(X_train, y_train)

        # Metrics
        y_pred = model.predict(X_test)
        r2 = float(r2_score(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))

        # Sentiment and predictions
        sentiment = float(get_sentiment(req.symbol))
        sentiment_factor = 1 + (sentiment / 5.0)
        next_day_pred = float(model.predict([X.iloc[-1]])[0])
        current_price = float(df['Close'].iloc[-1])
        adjusted_pred = float(next_day_pred * sentiment_factor)
        potential_profit = float((adjusted_pred - req.buy_price) * req.quantity)
        last_rsi = float(df['RSI'].iloc[-1])

        # Recommendation logic (mirrors module behavior)
        if last_rsi < 30:
            recommendation = "BUY — Oversold condition."
        elif last_rsi > 70:
            recommendation = "SELL — Overbought condition."
        elif adjusted_pred > current_price * 1.01:
            recommendation = "HOLD — Predicted rise expected soon."
        else:
            recommendation = "SELL — Weak momentum detected."

        # Save cache for resilience
        _save_cache(req.symbol, df)
        return {
            "symbol": req.symbol,
            "current_price": round(current_price, 2),
            "predicted_price": round(adjusted_pred, 2),
            "potential_profit": round(potential_profit, 2),
            "rsi": round(last_rsi, 2),
            "sentiment": round(sentiment, 3),
            "recommendation": recommendation,
            "r2": round(r2, 3),
            "mae": round(mae, 3),
            "degraded": False,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
