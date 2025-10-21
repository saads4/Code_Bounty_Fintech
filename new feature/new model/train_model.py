# train_model.py
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
from news_sentiment import fetch_news_sentiment
import numpy as np


TICKERS = ["RELIANCE.NS", "INFY.NS", "TCS.NS"]

def fetch_data(ticker):
    """Fetch historical price data and compute features."""
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    
    # Flatten MultiIndex columns if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df['Return'] = df['Close'].pct_change()
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df.dropna(inplace=True)
    return df

def label_data(df):
    """Label: 1=next day rise, 0=hold, -1=next day fall"""
    df = df.copy()
    df['Label'] = 0
    df.loc[df['Close'].shift(-1) > df['Close'], 'Label'] = 1
    df.loc[df['Close'].shift(-1) < df['Close'], 'Label'] = -1
    return df.dropna()

def add_sentiment(df, ticker):
    """Add news sentiment as a column (same sentiment for all rows)."""
    company_name = ticker.split(".")[0]
    sentiment = fetch_news_sentiment(company_name)
    df['Sentiment'] = sentiment
    return df

def main():
    Xs, ys = [], []
    for ticker in TICKERS:
        df = fetch_data(ticker)
        df = label_data(df)
        df = add_sentiment(df, ticker)
        features = df[['Return', 'MA5', 'MA20', 'Sentiment']].values
        labels = df['Label'].values
        Xs.append(features)
        ys.append(labels)

    X = np.vstack(Xs)
    y = np.concatenate(ys)


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print(f"✅ Model trained with accuracy: {model.score(X_test, y_test):.2f}")
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("💾 Model saved as model.pkl")

if __name__ == "__main__":
    main()
