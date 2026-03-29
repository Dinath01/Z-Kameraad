from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt

#Hashes
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

MAX_BCRYPT_LENGTH = 72


def _normalize_password(password: str) -> str:
    """
    bcrypt hard-limits passwords to 72 bytes.
    Truncate safely to avoid runtime crashes.
    """
    return password.encode("utf-8")[:MAX_BCRYPT_LENGTH].decode(
        "utf-8", errors="ignore"
    )


def hash_password(password: str) -> str:
    password = _normalize_password(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _normalize_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


#jwt-tokens

SECRET_KEY = "zkameraad-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
