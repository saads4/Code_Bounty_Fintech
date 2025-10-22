import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

# -------------------------------
# Helper Functions
# -------------------------------
def get_sentiment(stock):
    """Scrape recent news headlines for sentiment."""
    query = stock.split(".")[0] + " stock news"
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = [h.get_text() for h in soup.select('div[role="heading"]')[:5]]
    if not headlines:
        return 0
    sentiment_scores = [TextBlob(h).sentiment.polarity for h in headlines]
    return np.mean(sentiment_scores)

def calculate_indicators(df):
    """Add SMA, RSI, and returns to dataframe."""
    df['Return'] = df['Close'].pct_change()
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df.dropna(inplace=True)
    return df

# -------------------------------
# Main Model
# -------------------------------
def stock_recommendation():
    stock = input("Enter stock symbol (e.g. RELIANCE.NS): ")
    buy_price = float(input("Enter your buying price: "))
    qty = int(input("Enter quantity: "))

    # Fetch data
    data = yf.download(stock, period="180d", interval="1d", progress=False)
    if data.empty:
        print("❌ Failed to fetch data. Check symbol or internet connection.")
        return

    df = calculate_indicators(data)

    # Prepare ML data
    X = df[['Return', 'SMA_5', 'SMA_20', 'RSI']]
    y = df['Close'].shift(-1).dropna()
    X = X.iloc[:-1]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"\n📊 Model R²: {acc:.2f} | MAE: {mae:.2f}")

    # Sentiment weighting
    sentiment = get_sentiment(stock)
    sentiment_factor = 1 + sentiment / 5

    next_day_pred = model.predict([X.iloc[-1]])[0]
    current_price = float(df['Close'].iloc[-1])
    adjusted_pred = next_day_pred * sentiment_factor

    print(f"\nCurrent Price: ₹{current_price:.2f}")
    print(f"Predicted Next Day Price (adj): ₹{adjusted_pred:.2f}")
    profit = (adjusted_pred - buy_price) * qty
    print(f"Potential Profit/Loss: ₹{profit:.2f}")

    # Auto-adjust logic
    last_rsi = df['RSI'].iloc[-1]
    if last_rsi < 30:
        advice = "BUY — Oversold condition."
    elif last_rsi > 70:
        advice = "SELL — Overbought condition."
    elif adjusted_pred > current_price * 1.01:
        advice = "HOLD — Predicted rise expected soon."
    else:
        advice = "SELL — Weak momentum detected."

    print("\n🧠 Recommendation Summary:")
    print(f"RSI: {last_rsi:.2f}")
    print(f"Sentiment Score: {sentiment:.2f}")
    print(f"Recommendation: {advice}")
    print(f"Backtest Accuracy (R²): {acc:.2f}, MAE: {mae:.2f}")

if __name__ == "__main__":
    stock_recommendation()
