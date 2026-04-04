from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import RequestStatus, RequestType
from src.db.base import Base, TimestampMixin


class RecordChangeRequest(TimestampMixin, Base):
    __tablename__ = "record_change_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    request_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=RequestStatus.PENDING.value)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    requester_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reviewer_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    transaction = relationship("Transaction", back_populates="change_requests")

    __table_args__ = (
        CheckConstraint(
            f"request_type IN ('{RequestType.UPDATE.value}','{RequestType.DELETE.value}')",
            name="ck_change_request_type",
        ),
        CheckConstraint(
            f"status IN ('{RequestStatus.PENDING.value}','{RequestStatus.APPROVED.value}','{RequestStatus.REJECTED.value}')",
            name="ck_change_request_status",
        ),
        CheckConstraint("length(trim(reason)) > 0", name="ck_change_request_reason_required"),
        Index("ix_change_requests_pending", "status", "request_type", "transaction_id"),
        Index(
            "uq_active_delete_request_per_txn",
            "transaction_id",
            unique=True,
            sqlite_where=text("request_type = 'DELETE' AND status = 'PENDING'"),
        ),
    )
