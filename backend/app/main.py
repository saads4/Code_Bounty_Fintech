from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.security import add_security_headers
from app.routes import auth, users, dashboard, investments, budget, credit, taxes, finbot, admin

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.APP_NAME, version="0.1.0")

origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    add_security_headers(response)
    return response

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests"})

app.state.limiter = limiter
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(investments.router, prefix="/api/investments", tags=["investments"])
app.include_router(budget.router, prefix="/api/budget", tags=["budget"])
app.include_router(credit.router, prefix="/api/credit", tags=["credit"])
app.include_router(taxes.router, prefix="/api/taxes", tags=["taxes"])
app.include_router(finbot.router, prefix="/api/finbot", tags=["finbot"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/health")
def health():
    return {"status":"ok"}
