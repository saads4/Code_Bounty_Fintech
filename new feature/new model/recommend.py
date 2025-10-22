import json
import pickle
import yfinance as yf
import pandas as pd
from news_sentiment import fetch_news_sentiment

# ---------- Helper Functions ----------
def load_model_and_scaler():
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    return model, scaler

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

def fetch_features_with_sentiment(ticker):
    df = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df["Return"] = df["Close"].pct_change()
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["RSI"] = compute_rsi(df["Close"])
    df["MACD"] = compute_macd(df["Close"])
    df["Volatility"] = df["Return"].rolling(10).std()
    df.dropna(inplace=True)

    latest = df.iloc[-1]
    company_name = ticker.split(".")[0]
    sentiment = fetch_news_sentiment(company_name)

    features = [[
        latest["Return"], latest["MA5"], latest["MA20"],
        latest["RSI"], latest["MACD"], latest["Volatility"], sentiment
    ]]
    return features, latest["Close"]

def recommendation(pred):
    if pred == 1:
        return "BUY 📈"
    elif pred == -1:
        return "SELL 📉"
    else:
        return "HOLD 🤔"

# ---------- Main ----------
def main():
    model, scaler = load_model_and_scaler()

    with open("portfolio.json", "r") as f:
        portfolio = json.load(f)

    for ticker, info in portfolio.items():
        features, current_price = fetch_features_with_sentiment(ticker)
        scaled_features = scaler.transform(features)
        pred = model.predict(scaled_features)[0]
        action = recommendation(pred)

        print(f"\n{ticker}")
        print(f"  Buy Price: ₹{info['buy_price']}")
        print(f"  Current Price: ₹{round(current_price,2)}")
        print(f"  Recommendation: {action}")

if __name__ == "__main__":
    main()
