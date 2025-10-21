from typing import List, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DEFAULT_LABELS = ["groceries","rent","utilities","transport","entertainment","health","education","shopping","travel","other"]

def default_training_data()->Tuple[List[str], List[str]]:
    X = [
        "milk eggs vegetables at supermarket",
        "monthly house rent payment",
        "electricity bill and water charges",
        "uber ride to office",
        "movie tickets and popcorn",
        "doctor visit and medicines",
        "college tuition fees",
        "new shoes and t-shirt online",
        "flight tickets and hotel booking",
        "miscellaneous expense",
    ]
    y = DEFAULT_LABELS[:-1] + ["other"]
    return X, y

def build_text_classifier()->Pipeline:
    X, y = default_training_data()
    model = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1,2), stop_words="english")), ("clf", LogisticRegression(max_iter=1000))])
    model.fit(X, y); return model

def normalize_text(s: str)->str:
    s = s.lower(); s = re.sub(r"[^a-z0-9\s]", " ", s); s = re.sub(r"\s+", " ", s); return s.strip()
