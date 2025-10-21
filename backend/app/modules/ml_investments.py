import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any
from loguru import logger

# Optional heavy deps
try:
    import torch
    import torch.nn as nn
except Exception:
    torch = None
    nn = None

try:
    from xgboost import XGBRegressor
except Exception:
    XGBRegressor = None


@dataclass
class PredictionResult:
    model: str
    next_return: float
    details: Dict[str, Any]


class SimpleLSTM(nn.Module if nn else object):
    def __init__(self, input_size=1, hidden=16, layers=1):
        if nn:
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden, num_layers=layers, batch_first=True)
            self.fc = nn.Linear(hidden, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)


class InvestmentPredictor:
    def __init__(self):
        self.lstm = None
        self.xgb = None

    def _gen_sine_series(self, n=300, noise=0.05):
        t = np.arange(n)
        y = np.sin(0.05 * t) + np.random.normal(0, noise, size=n)
        return pd.Series(y)

    def train_baselines(self):
        """Train lightweight baselines on a synthetic series.
        Works even if torch/xgboost are not installed (graceful fallbacks).
        """
        series = self._gen_sine_series()
        returns = series.pct_change().fillna(0)

        # LSTM if torch available
        if torch and nn:
            seq_len = 20
            X, Y = [], []
            arr = returns.values.astype(np.float32).reshape(-1, 1)
            for i in range(len(arr) - seq_len):
                X.append(arr[i : i + seq_len])
                Y.append(arr[i + seq_len])
            X = np.stack(X)
            Y = np.stack(Y)
            X_t = torch.tensor(X)
            Y_t = torch.tensor(Y)
            model = SimpleLSTM(1, 16, 1)
            optim = torch.optim.Adam(model.parameters(), lr=0.01)
            loss_fn = nn.MSELoss()
            for _ in range(30):
                optim.zero_grad()
                pred = model(X_t)
                loss = loss_fn(pred, Y_t)
                loss.backward()
                optim.step()
            self.lstm = model
        else:
            logger.warning("Torch not available; skipping LSTM training.")

        # XGBoost (optional)
        if XGBRegressor:
            X_feat = np.arange(len(returns)).reshape(-1, 1)
            y = returns.values
            model = XGBRegressor(
                n_estimators=200,
                max_depth=3,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
            )
            model.fit(X_feat, y)
            self.xgb = model
        else:
            logger.warning("xgboost not installed; skipping XGBoost model.")

    def predict_next(self) -> PredictionResult:
        """Predict the next period return with whichever model is available."""
        if self.xgb:
            n = 400
            pred = float(self.xgb.predict(np.array([[n]])).item())
            return PredictionResult(model="xgboost", next_return=pred, details={"note": "synthetic series"})

        if self.lstm and torch:
            seq = torch.zeros((1, 20, 1), dtype=torch.float32)
            with torch.no_grad():
                pred = float(self.lstm(seq).item())
            return PredictionResult(model="lstm", next_return=pred, details={"note": "zero-seq input"})

        # Naive fallback if no models available
        pred = float(np.random.normal(0, 0.01))
        return PredictionResult(model="naive", next_return=pred, details={"fallback": True})
