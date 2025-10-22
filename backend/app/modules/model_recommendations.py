# backend/app/modules/model_recommendations.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

# External deps (declared in backend/requirements.txt)
import yfinance as yf
import feedparser
from textblob import TextBlob
import pickle
import json


@dataclass
class TickerRecommendation:
    ticker: str
    action: str
    current_price: float | None = None
    buy_price: float | None = None
    features: Dict[str, Any] | None = None


# Resolve repository root and new-model directory
_THIS_FILE = Path(__file__).resolve()
# modules -> app -> backend -> repo_root
_REPO_ROOT = _THIS_FILE.parents[3]
_MODEL_DIR = _REPO_ROOT / "new feature" / "new model"
_MODEL_FILE = _MODEL_DIR / "model.pkl"
_PORTFOLIO_FILE = _MODEL_DIR / "portfolio.json"


def _load_model():
    if not _MODEL_FILE.exists():
        raise FileNotFoundError(f"Model file not found: {_MODEL_FILE}")
    with open(_MODEL_FILE, "rb") as f:
        return pickle.load(f)


def _fetch_news_sentiment(company_name: str) -> float:
    rss_url = f"https://news.google.com/rss/search?q={company_name}+stock+price"
    try:
        feed = feedparser.parse(rss_url)
        if not getattr(feed, "entries", None):
            return 0.0
        sentiments = []
        for entry in feed.entries[:5]:
            analysis = TextBlob(entry.title)
            sentiments.append(analysis.sentiment.polarity)
        return float(sum(sentiments) / len(sentiments)) if sentiments else 0.0
    except Exception:
        return 0.0


def _build_features_with_sentiment(ticker: str):
    # Try primary download
    try:
        df = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True, progress=False, threads=False)
    except Exception:
        df = pd.DataFrame()

    # Fallback using Ticker().history if needed
    if isinstance(df, pd.DataFrame) and df.empty:
        try:
            hist = yf.Ticker(ticker).history(period="1mo")
            df = hist.reset_index()
        except Exception:
            df = pd.DataFrame()

    if isinstance(df, pd.DataFrame) and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df is None or len(df) == 0 or 'Close' not in df.columns:
        # Sentiment-only fallback: zeroed price-derived features
        company_name = ticker.split(".")[0]
        sentiment = _fetch_news_sentiment(company_name)
        features = [[0.0, 0.0, 0.0, float(sentiment)]]
        return features, None

    df['Return'] = df['Close'].pct_change()
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df = df.dropna()
    if len(df) == 0:
        company_name = ticker.split(".")[0]
        sentiment = _fetch_news_sentiment(company_name)
        features = [[0.0, 0.0, 0.0, float(sentiment)]]
        return features, None

    latest = df.iloc[-1]
    company_name = ticker.split(".")[0]
    sentiment = _fetch_news_sentiment(company_name)
    features = [[float(latest['Return']), float(latest['MA5']), float(latest['MA20']), float(sentiment)]]
    return features, float(latest['Close'])

def _map_prediction_to_action(pred) -> str:
    # Handle numpy arrays / lists of probabilities or scores
    try:
        import numpy as np
        arr = np.array(pred)
        if arr.ndim > 0:
            flat = arr.ravel()
            if flat.size > 1:
                # Assume last element is positive class prob
                p1 = float(flat[-1])
                if p1 >= 0.6:
                    return "BUY"
                elif p1 <= 0.4:
                    return "SELL"
                return "HOLD"
            else:
                # Single score/regression
                val = float(flat[0])
                if val >= 0.02:
                    return "BUY"
                if val <= -0.02:
                    return "SELL"
                return "HOLD"
    except Exception:
        pass

    # Try direct float
    try:
        val = float(pred)
        if val >= 0.02:
            return "BUY"
        if val <= -0.02:
            return "SELL"
        return "HOLD"
    except Exception:
        pass

    # Try integer class {-1,0,1}
    try:
        ival = int(pred)
        return _classify_action(ival)
    except Exception:
        return "HOLD"


def _classify_action(pred_val: int) -> str:
    if pred_val == 1:
        return "BUY"
    if pred_val == -1:
        return "SELL"
    return "HOLD"


def recommend_for_ticker(ticker: str) -> TickerRecommendation:
    try:
        model = _load_model()
        features, current_price = _build_features_with_sentiment(ticker)
        pred = model.predict(features)[0]
        action = _map_prediction_to_action(pred)
        return TickerRecommendation(
            ticker=ticker,
            action=action,
            current_price=current_price,
            features={"sentiment_included": True}
        )
    except Exception as e:
        # Graceful fallback: return HOLD with explanation (JSON-safe values)
        return TickerRecommendation(
            ticker=ticker,
            action="HOLD",
            current_price=None,
            features={"fallback": True, "error": str(e)}
        )


def recommend_for_portfolio() -> List[TickerRecommendation]:
    if not _PORTFOLIO_FILE.exists():
        # No portfolio: return an empty list rather than erroring out
        return []
    with open(_PORTFOLIO_FILE, "r", encoding="utf-8") as f:
        portfolio = json.load(f)

    out: List[TickerRecommendation] = []
    for ticker, info in portfolio.items():
        rec = recommend_for_ticker(ticker)
        rec.buy_price = float(info.get("buy_price")) if isinstance(info, dict) and "buy_price" in info else None
        out.append(rec)
    return out
