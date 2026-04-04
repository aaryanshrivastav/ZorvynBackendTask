from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import UserStatus
from src.db.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[UserStatus] = mapped_column(String(20), nullable=False, default=UserStatus.ACTIVE.value)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)

    role = relationship("Role", back_populates="users")
    transactions = relationship(
        "Transaction",
        back_populates="owner",
        foreign_keys="Transaction.owner_user_id",
    )
    deleted_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.deleted_by_user_id",
    )

    __table_args__ = (Index("ix_users_role_status", "role_id", "status"),)
