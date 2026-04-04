from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.refresh_token_session import RefreshTokenSession


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session: RefreshTokenSession) -> RefreshTokenSession:
        self.db.add(session)
        self.db.flush()
        return session

    def get_by_token_id(self, token_id: str) -> RefreshTokenSession | None:
        return self.db.scalar(select(RefreshTokenSession).where(RefreshTokenSession.token_id == token_id))

    def revoke(self, token_id: str) -> None:
        session = self.get_by_token_id(token_id)
        if session:
            session.is_revoked = True

    def is_valid(self, token_id: str, now: datetime) -> bool:
        session = self.get_by_token_id(token_id)
        return bool(session and not session.is_revoked and session.expires_at > now)
