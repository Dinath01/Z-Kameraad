from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# bcrypt has a maximum password length of 72 bytes
MAX_BCRYPT_LENGTH = 72


def _normalize_password(password: str) -> str:
    """
    Ensure password does not exceed bcrypt's 72-byte limit.
    Prevents hashing/verification errors.
    """
    return password.encode("utf-8")[:MAX_BCRYPT_LENGTH].decode(
        "utf-8", errors="ignore"
    )


def hash_password(password: str) -> str:
    """Hash a user's password safely."""
    password = _normalize_password(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hashed version."""
    plain_password = _normalize_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


# JWT configuration
SECRET_KEY = "zkameraad-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generate a JWT access token with an expiration time.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)