from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin


class RefreshTokenSession(TimestampMixin, Base):
    __tablename__ = "refresh_token_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)

    __table_args__ = (Index("ix_refresh_tokens_user_active", "user_id", "is_revoked", "expires_at"),)
