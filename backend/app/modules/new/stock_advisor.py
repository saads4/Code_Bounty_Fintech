import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings("ignore")

# ---------- Helper functions ---------- #
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def add_indicators(df):
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['RSI'] = compute_rsi(df['Close'])
    df['Return'] = df['Close'].pct_change()
    df['Future_Close'] = df['Close'].shift(-1)
    df['Target'] = (df['Future_Close'] > df['Close']).astype(int)  # 1=up, 0=down
    df.dropna(inplace=True)
    return df

# ---------- Main training logic ---------- #
def train_models(csv_path):
    df = pd.read_csv(csv_path)
    if 'Symbol' not in df.columns:
        raise ValueError("CSV must contain a 'Symbol' column for stock names.")
    
    # Add indicators once for the entire dataset
    df = df.sort_values(['Symbol','Date']).reset_index(drop=True)
    df = add_indicators(df)

    models = {}
    symbols = df['Symbol'].unique()

    for sym in symbols:
        data = df[df['Symbol'] == sym].copy()
        features = ['SMA_5','SMA_10','EMA_10','EMA_20','RSI','Return']
        X = data[features]
        y = data['Target']

        if len(X) < 100:
            print(f"Skipping {sym} (not enough data)")
            continue  # not enough data to train

        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)
        acc = accuracy_score(y_test, model.predict(X_test))
        models[sym] = (model, features)
        print(f"Trained model for {sym} | Accuracy: {acc:.2f}")

    return models, df

# ---------- Decision logic ---------- #
def get_recommendation(model, df, symbol, buy_price, quantity):
    recent = df[df['Symbol'] == symbol].copy().tail(1)
    features = model[1]
    X_last = recent[features]
    prob = model[0].predict_proba(X_last)[0][1]  # prob of price going UP

    if prob > 0.6:
        decision = "BUY ✅"
    elif prob < 0.4:
        decision = "SELL ❌"
    else:
        decision = "HOLD ⚖️"

    latest_close = float(recent['Close'].iloc[-1])
    profit_loss = (latest_close - buy_price) * quantity

    print(f"\nStock: {symbol}")
    print(f"Predicted Up Probability: {prob:.2f}")
    print(f"Latest Close Price: ₹{latest_close:.2f}")
    print(f"Your Buy Price: ₹{buy_price:.2f}")
    print(f"Quantity: {quantity}")
    print(f"Unrealized P/L: ₹{profit_loss:.2f}")
    print(f"Recommendation: {decision}\n")

# ---------- Main flow ---------- #
if __name__ == "__main__":
    print("📈 Training Stock Advisor model...\n")
    models, data = train_models("new\stock_data_7stocks.csv")  # replace with your CSV path

    if not models:
        print("No models trained. Check your CSV or data quality.")
        exit()

    while True:
        sym = input("\nEnter stock symbol (or 'exit' to quit): ").strip().upper()
        if sym == "EXIT":
            break
        if sym not in models:
            print("Symbol not found in data.")
            continue
        try:
            buy_price = float(input("Enter your buy price: "))
            quantity = int(input("Enter quantity: "))
            get_recommendation(models[sym], data, sym, buy_price, quantity)
        except Exception as e:
            print("❌ Error:", e)
