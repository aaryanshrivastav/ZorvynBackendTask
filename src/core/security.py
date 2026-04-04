from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from src.core.config import settings


class TokenPayloadError(Exception):
    pass


def _create_token(subject: str, token_type: str, expires_delta: timedelta, token_id: str | None = None) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": now + expires_delta,
        "iat": now,
        "jti": token_id or str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _create_token(subject, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(subject: str, token_id: str) -> str:
    return _create_token(subject, "refresh", timedelta(minutes=settings.refresh_token_expire_minutes), token_id=token_id)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenPayloadError("Invalid token") from exc
