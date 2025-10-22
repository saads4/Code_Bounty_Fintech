# backend/app/routes/stockmind.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import time
import os
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.routes.utils import auth_user

router = APIRouter(prefix="/api/stockmind", tags=["stockmind"])


def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    })
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST"]) 
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

_SESS = _make_session()

def _get_sentiment(stock: str) -> float:
    try:
        query = stock.split(".")[0] + " stock news"
        url = f"https://www.google.com/search?q={query}"
        r = _SESS.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        headlines = [h.get_text() for h in soup.select('div[role="heading"]')[:5]]
        if not headlines:
            return 0.0
        scores = [TextBlob(h).sentiment.polarity for h in headlines]
        return float(np.mean(scores)) if scores else 0.0
    except Exception:
        return 0.0


def _calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Return'] = df['Close'].pct_change()
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    df['RSI'] = 100 - (100 / (1 + rs))
    df.dropna(inplace=True)
    return df


class StockMindRequest(BaseModel):
    ticker: str = Field(..., description="Ticker symbol, e.g. RELIANCE.NS")
    buy_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)


def _fetch_ohlcv_yf(ticker: str, attempts: int = 3) -> pd.DataFrame:
    last_err = None
    for i in range(attempts):
        try:
            df = yf.download(
                ticker,
                period="180d",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
                repair=True,
                session=_SESS,
                timeout=20,
            )
            if df is not None and not df.empty and 'Close' in df.columns:
                return df
        except Exception as e:
            last_err = e
        # Backoff on rate-limit or unknown errors
        time.sleep(2 * (i + 1))
        # Try alternate path
        try:
            hist = yf.Ticker(ticker, session=_SESS).history(period="6mo", interval="1d")
            if hist is not None and not hist.empty:
                return hist
        except Exception as e2:
            last_err = e2
            time.sleep(1)
    if last_err:
        raise last_err
    return pd.DataFrame()


def _map_ns_symbol_for_twelvedata(ticker: str) -> str:
    # RELIANCE.NS -> RELIANCE:NS, TCS.NS -> TCS:NS
    if ticker.upper().endswith('.NS'):
        return ticker.upper().replace('.NS', ':NS')
    return ticker

def _fetch_ohlcv_twelvedata(ticker: str, apikey: str) -> pd.DataFrame:
    try:
        symbol = _map_ns_symbol_for_twelvedata(ticker)
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': 500,
            'format': 'JSON',
            'apikey': apikey,
        }
        r = _SESS.get('https://api.twelvedata.com/time_series', params=params, timeout=15)
        j = r.json()
        if 'values' not in j:
            return pd.DataFrame()
        df = pd.DataFrame(j['values'])
        # Expect columns: datetime, open, high, low, close, volume
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')
        df.rename(columns={
            'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume',
        }, inplace=True)
        df.set_index('datetime', inplace=True)
        # Ensure numeric
        for c in ['Open','High','Low','Close','Volume']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df.dropna(inplace=True)
        return df
    except Exception:
        return pd.DataFrame()


# Simple local cache to mitigate rate limits
_CACHE_DIR = Path(__file__).resolve().parents[3] / 'backend' / '.cache' / 'stockmind'
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_path(ticker: str) -> Path:
    safe = ticker.replace('/', '_').replace('\\', '_')
    return _CACHE_DIR / f"{safe}.csv"

def _load_cache(ticker: str, max_age_sec: int = 24*3600) -> Optional[pd.DataFrame]:
    p = _cache_path(ticker)
    if not p.exists():
        return None
    try:
        mtime = p.stat().st_mtime
        if (time.time() - mtime) > max_age_sec:
            # Stale but still usable as last-resort
            return pd.read_csv(p)
        return pd.read_csv(p)
    except Exception:
        return None

def _save_cache(ticker: str, df: pd.DataFrame) -> None:
    try:
        if df is not None and not df.empty:
            # Ensure index is a column for CSV
            out = df.copy()
            if not isinstance(out.index, pd.RangeIndex):
                out = out.reset_index()
            out.to_csv(_cache_path(ticker), index=False)
    except Exception:
        pass


@router.post("/recommend")
def recommend(req: StockMindRequest, user = Depends(auth_user)):
    try:
        df = pd.DataFrame()
        key = os.getenv('TWELVE_DATA_KEY')
        if key:
            td = _fetch_ohlcv_twelvedata(req.ticker, key)
            if isinstance(td, pd.DataFrame) and not td.empty and 'Close' in td.columns:
                df = td
        if df is None or df.empty or 'Close' not in df.columns:
            try:
                df = _fetch_ohlcv_yf(req.ticker, attempts=3)
            except Exception:
                df = pd.DataFrame()

        used_cache = False
        if df is None or df.empty or 'Close' not in df.columns:
            cached = _load_cache(req.ticker)
            if isinstance(cached, pd.DataFrame) and not cached.empty and 'Close' in cached.columns:
                df = cached
                used_cache = True

        if df is None or df.empty or 'Close' not in df.columns:
            # Degraded mode: sentiment-only output to avoid 400s on rate limits
            sentiment = _get_sentiment(req.ticker)
            return {
                "ticker": req.ticker,
                "current_price": None,
                "predicted_price": None,
                "adjusted_predicted_price": None,
                "sentiment": round(float(sentiment), 3),
                "rsi": None,
                "advice": "HOLD — Data temporarily unavailable; showing sentiment only.",
                "metrics": {"r2": None, "mae": None},
                "potential_profit_loss": None,
                "degraded": True,
                "degraded_from_cache": used_cache,
            }

        # Indicators
        df = _calculate_indicators(df)
        if df.empty:
            sentiment = _get_sentiment(req.ticker)
            return {
                "ticker": req.ticker,
                "current_price": None,
                "predicted_price": None,
                "adjusted_predicted_price": None,
                "sentiment": round(float(sentiment), 3),
                "rsi": None,
                "advice": "HOLD — Insufficient data after indicators; showing sentiment only.",
                "metrics": {"r2": None, "mae": None},
                "potential_profit_loss": None,
                "degraded": True,
                "degraded_from_cache": used_cache,
            }

        X = df[['Return', 'SMA_5', 'SMA_20', 'RSI']]
        y = df['Close'].shift(-1).dropna()
        X = X.iloc[:-1]
        if len(X) < 50:
            sentiment = _get_sentiment(req.ticker)
            current_price = float(df['Close'].iloc[-1]) if 'Close' in df.columns else None
            return {
                "ticker": req.ticker,
                "current_price": round(current_price, 2) if current_price else None,
                "predicted_price": None,
                "adjusted_predicted_price": None,
                "sentiment": round(float(sentiment), 3),
                "rsi": float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else None,
                "advice": "HOLD — Not enough samples to train; sentiment-only.",
                "metrics": {"r2": None, "mae": None},
                "potential_profit_loss": None,
                "degraded": True,
                "degraded_from_cache": used_cache,
            }

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = RandomForestRegressor(n_estimators=150, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        r2 = float(r2_score(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))

        sentiment = _get_sentiment(req.ticker)
        sentiment_factor = 1 + (sentiment / 5.0)

        next_day_pred = float(model.predict([X.iloc[-1]])[0])
        current_price = float(df['Close'].iloc[-1])
        adjusted_pred = float(next_day_pred * sentiment_factor)
        potential_pl = float((adjusted_pred - req.buy_price) * req.quantity)
        last_rsi = float(df['RSI'].iloc[-1])

        if last_rsi < 30:
            advice = "BUY — Oversold condition."
        elif last_rsi > 70:
            advice = "SELL — Overbought condition."
        elif adjusted_pred > current_price * 1.01:
            advice = "HOLD — Predicted rise expected soon."
        else:
            advice = "SELL — Weak momentum detected."

        # Save cache for future resilience
        _save_cache(req.ticker, df)

        return {
            "ticker": req.ticker,
            "current_price": round(current_price, 2),
            "predicted_price": round(next_day_pred, 2),
            "adjusted_predicted_price": round(adjusted_pred, 2),
            "sentiment": round(float(sentiment), 3),
            "rsi": round(last_rsi, 2),
            "advice": advice,
            "metrics": {"r2": round(r2, 3), "mae": round(mae, 3)},
            "potential_profit_loss": round(potential_pl, 2),
            "degraded": False,
            "degraded_from_cache": False,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
