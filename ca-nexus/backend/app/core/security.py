from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError
from .config import settings
import uuid


def _pwd_ctx():
    from passlib.context import CryptContext  # lazy: importable without bcrypt installed
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(p: str) -> str:
    return _pwd_ctx().hash(p)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx().verify(plain, hashed)


def create_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": sub, "jti": uuid.uuid4().hex, "iat": now,
         "exp": now + timedelta(hours=settings.JWT_EXPIRE_HOURS)},
        settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM,
    )


class TokenError(Exception):
    def __init__(self, kind: str):
        self.kind = kind  # "missing" | "expired" | "invalid" | "revoked"


def decode_token_sub(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise TokenError("expired")
    except JWTError:
        raise TokenError("invalid")
    sub = payload.get("sub")
    if not sub:
        raise TokenError("invalid")
    return str(sub)


def decode_token_jti(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise TokenError("expired")
    except JWTError:
        raise TokenError("invalid")
    return str(payload.get("jti") or "")
