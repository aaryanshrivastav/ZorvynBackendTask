import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from src.db.init_db import create_tables, seed_roles
from src.db.session import SessionLocal
from src.core.passwords import hash_password
from src.models.transaction import Transaction
from src.models.transaction_risk_profile import TransactionRiskProfile
from src.models.user import User
from src.repositories.role_repository import RoleRepository

CSV_PATH = Path("accounting_dataset.csv")


def none_to_null(value: str | None):
    if value is None:
        return None
    v = value.strip()
    if v == "" or v.lower() == "none":
        return None
    return v


def parse_datetime(value: str) -> datetime:
    raw = none_to_null(value)
    if not raw:
        return datetime.utcnow()
    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return datetime.fromisoformat(raw)


def parse_bool(value: str | None) -> bool:
    raw = none_to_null(value)
    if raw is None:
        return False
    return raw in {"1", "true", "True", "YES", "yes"}


def get_or_create_dataset_user(db: Session, dataset_user_id: str, analyst_role_id: int) -> int:
    username = f"dataset_{dataset_user_id.lower()}"
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user.id

    user = User(username=username, password=hash_password("changeme"), role_id=analyst_role_id, status="ACTIVE")
    db.add(user)
    db.flush()
    return user.id


def import_csv_to_db(csv_path: Path) -> None:
    create_tables()
    db: Session = SessionLocal()
    try:
        seed_roles(db)
        role_repo = RoleRepository(db)
        analyst = role_repo.get_by_name("Analyst")
        if not analyst:
            raise RuntimeError("Analyst role missing")

        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tx_id = none_to_null(row.get("Transaction_ID"))
                if not tx_id:
                    continue

                owner_user_id = get_or_create_dataset_user(db, row.get("User_ID", "UNKNOWN"), analyst.id)

                transaction = db.query(Transaction).filter(Transaction.transaction_id == tx_id).first()
                payload = {
                    "transaction_id": tx_id,
                    "occurred_at": parse_datetime(row.get("Date", "")),
                    "account_number": none_to_null(row.get("Account_Number")) or "UNKNOWN",
                    "transaction_type": none_to_null(row.get("Transaction_Type")) or "UNKNOWN",
                    "amount": Decimal(none_to_null(row.get("Amount")) or "0"),
                    "currency": none_to_null(row.get("Currency")) or "USD",
                    "counterparty": none_to_null(row.get("Counterparty")) or "UNKNOWN",
                    "category": none_to_null(row.get("Category")) or "Uncategorized",
                    "notes": none_to_null(row.get("Description")) or none_to_null(row.get("Notes")),
                    "payment_method": none_to_null(row.get("Payment_Method")) or "UNKNOWN",
                    "owner_user_id": owner_user_id,
                }

                if transaction:
                    for key, value in payload.items():
                        setattr(transaction, key, value)
                else:
                    transaction = Transaction(**payload)
                    db.add(transaction)
                    db.flush()

                risk = db.query(TransactionRiskProfile).filter(TransactionRiskProfile.transaction_id == transaction.id).first()
                risk_payload = {
                    "risk_incident": parse_bool(row.get("Risk_Incident")),
                    "risk_type": none_to_null(row.get("Risk_Type")),
                    "incident_severity": none_to_null(row.get("Incident_Severity")),
                    "error_code": none_to_null(row.get("Error_Code")),
                    "system_latency": float(none_to_null(row.get("System_Latency")) or 0) if none_to_null(row.get("System_Latency")) else None,
                    "login_frequency": int(none_to_null(row.get("Login_Frequency")) or 0) if none_to_null(row.get("Login_Frequency")) else None,
                    "failed_attempts": int(none_to_null(row.get("Failed_Attempts")) or 0) if none_to_null(row.get("Failed_Attempts")) else None,
                    "ip_region": none_to_null(row.get("IP_Region")),
                }
                if risk:
                    for key, value in risk_payload.items():
                        setattr(risk, key, value)
                else:
                    db.add(TransactionRiskProfile(transaction_id=transaction.id, **risk_payload))

        db.commit()
        print("CSV import completed")
    finally:
        db.close()


if __name__ == "__main__":
    import_csv_to_db(CSV_PATH)
