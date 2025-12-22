from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt

from app.auth.jw import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# bcrypt context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_password_hash(password: str):
    """
    Hash a plaintext password.
    Used when creating a user.
    """
    return pwd_context.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str
                    ):
    """
    Verify a plaintext password against its hash.
    Used during login.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False


def create_access_token(data: dict):
    """
    Create a signed JWT access token.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)