from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.passwords import verify_password
from src.core.exceptions import unauthorized
from src.core.security import TokenPayloadError, create_access_token, create_refresh_token, decode_token
from src.models.refresh_token_session import RefreshTokenSession
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.utils.helpers.audit import log_audit_event


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)

    def login(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password) or user.status != "ACTIVE":
            log_audit_event(self.db, None, "AUTH_LOGIN", "auth", username, "FAILED")
            self.db.commit()
            raise unauthorized("Invalid username or password")

        token_id = str(uuid4())
        refresh = create_refresh_token(str(user.id), token_id)
        access = create_access_token(str(user.id))

        refresh_session = RefreshTokenSession(
            user_id=user.id,
            token_id=token_id,
            expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=settings.refresh_token_expire_minutes),
        )
        self.refresh_repo.create(refresh_session)
        log_audit_event(self.db, user.id, "AUTH_LOGIN", "auth", str(user.id), "SUCCESS")
        self.db.commit()
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    def refresh(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except TokenPayloadError as exc:
            raise unauthorized("Invalid refresh token") from exc

        if payload.get("type") != "refresh":
            raise unauthorized("Invalid token type")

        token_id = payload.get("jti")
        user_id = int(payload.get("sub"))
        now = datetime.now(UTC).replace(tzinfo=None)

        if not token_id or not self.refresh_repo.is_valid(token_id, now):
            raise unauthorized("Refresh token revoked or expired")

        user = self.user_repo.get_by_id(user_id)
        if not user or user.status != "ACTIVE":
            self.refresh_repo.revoke(token_id)
            self.db.commit()
            raise unauthorized("User is inactive or missing")

        self.refresh_repo.revoke(token_id)

        new_token_id = str(uuid4())
        new_refresh = create_refresh_token(str(user_id), new_token_id)
        new_access = create_access_token(str(user_id))

        refresh_session = RefreshTokenSession(
            user_id=user_id,
            token_id=new_token_id,
            expires_at=now + timedelta(minutes=settings.refresh_token_expire_minutes),
        )
        self.refresh_repo.create(refresh_session)
        log_audit_event(self.db, user_id, "AUTH_REFRESH", "auth", str(user_id), "SUCCESS")
        self.db.commit()
        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

    def logout(self, refresh_token: str, actor_user_id: int | None):
        try:
            payload = decode_token(refresh_token)
        except TokenPayloadError:
            raise unauthorized("Invalid refresh token")

        token_id = payload.get("jti")
        if token_id:
            self.refresh_repo.revoke(token_id)

        log_audit_event(self.db, actor_user_id, "AUTH_LOGOUT", "auth", str(actor_user_id) if actor_user_id else None, "SUCCESS")
        self.db.commit()
