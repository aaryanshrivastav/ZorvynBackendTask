from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class TransactionRiskProfile(TimestampMixin, Base):
    __tablename__ = "transaction_risk_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False)
    risk_incident: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    risk_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    incident_severity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    system_latency: Mapped[float | None] = mapped_column(Float, nullable=True)
    login_frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failed_attempts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ip_region: Mapped[str | None] = mapped_column(String(20), nullable=True)

    transaction = relationship("Transaction", back_populates="risk_profile")
