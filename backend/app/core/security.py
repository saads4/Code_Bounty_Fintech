from datetime import datetime, timedelta, timezone
from fastapi import Response
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    default="pbkdf2_sha256",
    deprecated="auto",
)

def hash_password(p: str) -> str:
    try:
        if "bcrypt" in pwd_context.schemes():
            return CryptContext(schemes=["bcrypt"]).hash(p)
    except Exception:
        pass
    return CryptContext(schemes=["pbkdf2_sha256"]).hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(sub: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def add_security_headers(response: Response) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "microphone=(), geolocation=()"
