from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import ScopeType
from src.db.base import Base, TimestampMixin


class ViewerAccessScope(TimestampMixin, Base):
    __tablename__ = "viewer_access_scopes"

    id: Mapped[int] = mapped_column(primary_key=True)
    viewer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(20), nullable=False)
    scoped_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint(
            f"scope_type IN ('{ScopeType.USER.value}','{ScopeType.ACCOUNT.value}')",
            name="ck_viewer_scope_type",
        ),
        CheckConstraint(
            "(scope_type = 'USER' AND scoped_user_id IS NOT NULL AND account_number IS NULL) OR "
            "(scope_type = 'ACCOUNT' AND account_number IS NOT NULL AND scoped_user_id IS NULL)",
            name="ck_viewer_scope_mapping",
        ),
        UniqueConstraint("viewer_user_id", "scope_type", "scoped_user_id", "account_number", name="uq_viewer_scope_unique"),
        Index("ix_viewer_scope_lookup", "viewer_user_id", "scope_type"),
    )
