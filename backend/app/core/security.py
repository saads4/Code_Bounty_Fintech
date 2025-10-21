# backend/app/core/security.py
from passlib.context import CryptContext

# Prefer bcrypt if present, but default to pbkdf2_sha256 so Windows works without bcrypt wheels
pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    default="pbkdf2_sha256",
    deprecated="auto",
)

def hash_password(p: str) -> str:
    # If bcrypt is available, you can switch default at runtime like this:
    if "bcrypt" in pwd_context.schemes():
        try:
            # Try bcrypt first
            return CryptContext(schemes=["bcrypt"]).hash(p)
        except Exception:
            pass
    # Fallback
    return CryptContext(schemes=["pbkdf2_sha256"]).hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    # Verifies either bcrypt or pbkdf2 hashes
    return pwd_context.verify(plain, hashed)
