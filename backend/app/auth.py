"""Auth: password hashing and JWT issue/verify.

Uses pbkdf2_sha256 (pure-Python, no native build) for portability across runners,
and a short-lived signed JWT as the bearer token. The signing secret comes from the
environment in production; a dev default keeps local runs frictionless.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("AGENT_OPS_SECRET", "dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_TTL_MINUTES = int(os.environ.get("AGENT_OPS_TOKEN_TTL", "60"))

_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)


def create_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    """Return the subject (username) if the token is valid, else None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None
