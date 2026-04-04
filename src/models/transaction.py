from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    occurred_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    counterparty: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    deleted_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    owner = relationship("User", foreign_keys=[owner_user_id], back_populates="transactions")
    risk_profile = relationship("TransactionRiskProfile", back_populates="transaction", uselist=False)
    flags = relationship("Flag", back_populates="transaction")
    change_requests = relationship("RecordChangeRequest", back_populates="transaction")

    __table_args__ = (
        Index("ix_transactions_active_occurred", "is_deleted", "occurred_at"),
        Index("ix_transactions_active_owner", "is_deleted", "owner_user_id"),
    )
