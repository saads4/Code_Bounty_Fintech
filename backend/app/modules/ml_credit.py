import numpy as np, pandas as pd, shap
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

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
        self.lr.fit(Xtr, ytr); self.rf.fit(Xtr, ytr)
        self.explainer = shap.TreeExplainer(self.rf)
        auc_lr = roc_auc_score(yte, self.lr.predict_proba(Xte)[:,1])
        auc_rf = roc_auc_score(yte, self.rf.predict_proba(Xte)[:,1])
        return {"auc_lr": float(auc_lr), "auc_rf": float(auc_rf)}

    def score(self, features: dict):
        cols = ["income","age","utilization","late_pay","dti"]
        import numpy as np
        x = np.array([[features.get(c,0) for c in cols]])
        prob = float(self.rf.predict_proba(x)[0,1])
        shap_vals = self.explainer.shap_values(x)[1][0].tolist() if self.explainer else []
        return {"prob_default": prob, "shap": {"features": cols, "values": shap_vals}}
