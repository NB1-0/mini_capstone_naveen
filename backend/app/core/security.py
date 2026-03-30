from __future__ import annotations

from datetime import timedelta

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import get_settings
from app.exceptions.custom_exceptions import UnauthorizedException
from app.utils.helpers import utc_now

settings = get_settings()
# Use pbkdf2_sha256 to avoid bcrypt backend incompatibilities on fresh Windows
# environments while keeping password hashing strong and portable.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
http_bearer_scheme = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    sub: str
    role: str | None = None
    exp: int | None = None


def extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise UnauthorizedException("Authentication required.")
    return credentials.credentials


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str) -> str:
    expires_at = utc_now() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return TokenPayload.model_validate(payload)
    except JWTError as exc:
        raise UnauthorizedException("Invalid or expired authentication token.") from exc
