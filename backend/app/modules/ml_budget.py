from typing import List, Dict, Any
from app.utils.classifier import build_text_classifier, normalize_text

clf = build_text_classifier()

def categorize_expenses(items: List[Dict[str, Any]]):
    results = []
    for it in items:
        if it.get("type", "expense") != "expense":
            continue
        text = normalize_text(it.get("description", ""))
        # Simple rule-based overrides for common merchants/keywords
        category = None
        if text:
            rules = {
                "uber": "transport", "ola": "transport", "fuel": "transport", "petrol": "transport", "diesel": "transport", "bus": "transport", "metro": "transport",
                "rent": "rent", "landlord": "rent",
                "electricity": "utilities", "water": "utilities", "gas": "utilities", "internet": "utilities", "wifi": "utilities", "broadband": "utilities", "mobile": "utilities", "recharge": "utilities", "airtel": "utilities", "jio": "utilities", "vodafone": "utilities",
                "movie": "entertainment", "netflix": "entertainment", "prime": "entertainment", "spotify": "entertainment", "hotstar": "entertainment",
                "doctor": "health", "medicine": "health", "pharmacy": "health", "hospital": "health", "clinic": "health", "apollo": "health",
                "tuition": "education", "school": "education", "college": "education", "course": "education", "udemy": "education", "coursera": "education",
                "shoes": "shopping", "tshirt": "shopping", "clothes": "shopping", "apparel": "shopping", "myntra": "shopping", "flipkart": "shopping", "amazon": "shopping",
                "flight": "travel", "hotel": "travel", "booking": "travel", "train": "travel", "makemytrip": "travel", "irctc": "travel",
                "supermarket": "groceries", "grocery": "groceries", "groceries": "groceries", "bigbasket": "groceries", "milk": "groceries", "vegetables": "groceries", "zomato": "groceries", "swiggy": "groceries", "restaurant": "groceries", "food": "groceries",
            }
            for k, v in rules.items():
                if k in text:
                    category = v
                    break
        if not category:
            if not text:
                category = "other"
            else:
                # Use model with a confidence threshold; fallback to 'other' for low confidence
                probs = clf.predict_proba([text])[0]
                pred = clf.predict([text])[0]
                maxp = float(max(probs))
                category = pred if maxp >= 0.35 else "other"
        results.append({**it, "category_pred": category})
    return results

def recommend_budgets(history: List[Dict[str, Any]]):
    income = sum(h.get("amount",0) for h in history if h.get("type")=="income")
    essentials = 0.5*income; wants = 0.3*income; savings = 0.2*income
    return {"monthly_income": income, "suggested": {"essentials": essentials, "wants": wants, "savings": savings}}
