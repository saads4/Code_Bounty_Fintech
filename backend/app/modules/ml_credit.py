import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

try:
    import shap  # optional
except Exception:
    shap = None

class CreditModel:
    def __init__(self):
        self.lr = LogisticRegression(max_iter=200)
        self.rf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
        self.explainer = None

    def _synthetic(self, n=1000):
        rng = np.random.default_rng(42)
        income = rng.normal(600000, 150000, n)
        age = rng.integers(21, 65, n)
        utilization = rng.uniform(0, 1, n)
        late_pay = rng.poisson(0.2, n)
        dti = rng.uniform(0, 1, n)
        X = np.column_stack([income, age, utilization, late_pay, dti])
        p = 1/(1+np.exp(-( -2.5 + 0.015*(utilization*100) + 0.5*late_pay + 2*dti - income/1.2e6 - (age-21)/80 )))
        y = (rng.uniform(0,1,n) < p).astype(int)
        cols = ["income","age","utilization","late_pay","dti"]
        return pd.DataFrame(X, columns=cols), y

    def train(self):
        X, y = self._synthetic()
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.lr.fit(Xtr, ytr)
        self.rf.fit(Xtr, ytr)
        if shap:
            try:
                self.explainer = shap.TreeExplainer(self.rf)
            except Exception:
                self.explainer = None
        auc_lr = roc_auc_score(yte, self.lr.predict_proba(Xte)[:,1])
        auc_rf = roc_auc_score(yte, self.rf.predict_proba(Xte)[:,1])
        return {"auc_lr": float(auc_lr), "auc_rf": float(auc_rf)}

    def score(self, features: dict):
        cols = ["income","age","utilization","late_pay","dti"]
        x = np.array([[features.get(c,0) for c in cols]])
        prob = float(self.rf.predict_proba(x)[0,1])
        shap_vals = []
        if self.explainer and shap:
            try:
                # Try legacy API (list for binary classification)
                sv = self.explainer.shap_values(x)
                if isinstance(sv, list):
                    # Use class 1 if available
                    if len(sv) > 1:
                        shap_vals = sv[1][0].tolist()
                    else:
                        shap_vals = sv[0][0].tolist()
                else:
                    # Array returned
                    shap_vals = sv[0].tolist()
            except Exception:
                try:
                    # Try newer API returning Explanation object
                    ex = self.explainer(x)
                    shap_vals = getattr(ex, 'values', None)
                    if shap_vals is not None:
                        shap_vals = np.array(shap_vals)[0].tolist()
                    else:
                        shap_vals = []
                except Exception:
                    shap_vals = []
        # Fallback: if no SHAP values, provide feature importances as proxy
        if not shap_vals:
            try:
                importances = getattr(self.rf, 'feature_importances_', None)
                if importances is not None:
                    shap_vals = importances.tolist()
                else:
                    # Fallback to logistic coefficients aligned to cols
                    coefs = getattr(self.lr, 'coef_', None)
                    shap_vals = coefs[0].tolist() if coefs is not None else [0]*len(cols)
            except Exception:
                shap_vals = [0]*len(cols)
        return {"prob_default": prob, "shap": {"features": cols, "values": shap_vals}}
