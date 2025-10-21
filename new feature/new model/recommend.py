# recommend.py
import json
import pickle
import yfinance as yf
import pandas as pd
from news_sentiment import fetch_news_sentiment

def load_model():
    with open("model.pkl", "rb") as f:
        return pickle.load(f)

def fetch_features_with_sentiment(ticker):
    df = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True)
    
    # Flatten MultiIndex if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df['Return'] = df['Close'].pct_change()
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df.dropna(inplace=True)
    latest = df.iloc[-1]
    company_name = ticker.split(".")[0]
    sentiment = fetch_news_sentiment(company_name)
    features = [[latest['Return'], latest['MA5'], latest['MA20'], sentiment]]
    return features, latest['Close']

def recommendation(model, features):
    pred = model.predict(features)[0]
    if pred == 1:
        return "BUY 📈"
    elif pred == -1:
        return "SELL 📉"
    else:
        return "HOLD 🤔"

def main():
    model = load_model()
    with open("portfolio.json", "r") as f:
        portfolio = json.load(f)

    for ticker, info in portfolio.items():
        features, current_price = fetch_features_with_sentiment(ticker)
        action = recommendation(model, features)
        print(f"\n{ticker}")
        print(f"  Buy Price: ₹{info['buy_price']}")
        print(f"  Current Price: ₹{round(current_price,2)}")
        print(f"  Recommendation: {action}")

if __name__ == "__main__":
    main()
