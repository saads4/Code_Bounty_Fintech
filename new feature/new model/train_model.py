import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import numpy as np
from news_sentiment import fetch_news_sentiment


# Stocks to train on
TICKERS = ["RELIANCE.NS", "INFY.NS", "TCS.NS"]

# ---------- Helper Functions ----------
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, short=12, long=26):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    return short_ema - long_ema

def fetch_data(ticker):
    """Fetch historical price data and compute features."""
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)

    # Flatten MultiIndex columns if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df["Return"] = df["Close"].pct_change()
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["RSI"] = compute_rsi(df["Close"])
    df["MACD"] = compute_macd(df["Close"])
    df["Volatility"] = df["Return"].rolling(10).std()
    df.dropna(inplace=True)
    return df

def label_data(df, threshold=0.002):
    """Label: 1 = rise, -1 = fall, 0 = hold"""
    df = df.copy()
    df["Label"] = 0
    df.loc[df["Close"].pct_change().shift(-1) > threshold, "Label"] = 1
    df.loc[df["Close"].pct_change().shift(-1) < -threshold, "Label"] = -1
    return df.dropna()

def add_sentiment(df, ticker):
    """Add sentiment as a feature."""
    company_name = ticker.split(".")[0]
    sentiment = fetch_news_sentiment(company_name)
    df["Sentiment"] = sentiment
    return df

# ---------- Main Training ----------
def main():
    Xs, ys = [], []
    for ticker in TICKERS:
        df = fetch_data(ticker)
        df = label_data(df)
        df = add_sentiment(df, ticker)
        features = df[["Return", "MA5", "MA20", "RSI", "MACD", "Volatility", "Sentiment"]].values
        labels = df["Label"].values
        Xs.append(features)
        ys.append(labels)

    X = np.vstack(Xs)
    y = np.concatenate(ys)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train model with class balancing
    model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    print(f"✅ Model trained successfully with accuracy: {acc:.2f}")

    # Save model & scaler
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print("💾 Model and scaler saved (model.pkl, scaler.pkl)")

if __name__ == "__main__":
    main()
