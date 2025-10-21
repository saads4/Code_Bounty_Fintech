# FinEdge Pro — AI-Powered Fintech Platform

End-to-end stack: **FastAPI** + **React (Vite)** + **SQLite/Postgres**, with ML modules and Indian tax engine.

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
copy .env.example .env  # or cp on mac/linux
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm i
copy .env.example .env
npm run dev
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

> If API runs on a different host/port, set `VITE_API_BASE` in `frontend/.env`.

### Docker (optional)
```bash
docker compose up --build
```

## Modules
- Auth (JWT), Users
- Dashboard KPIs + charts
- Investments (LSTM/XGB fallback-safe)
- Budget planner (TF-IDF NLP)
- Credit scoring (RF + SHAP)
- Taxes (India old/new) + suggestions
- FinBot (LLM-ready; rule-based fallback)
- Admin endpoints
