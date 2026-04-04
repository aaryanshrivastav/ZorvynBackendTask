from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.core.constants import TransactionType


class TransactionCreate(BaseModel):
    transaction_id: str = Field(min_length=3, max_length=50)
    occurred_at: datetime
    account_number: str
    transaction_type: TransactionType
    amount: Decimal
    currency: str
    counterparty: str
    category: str
    notes: str | None = None
    payment_method: str
    owner_user_id: int


class TransactionUpdate(BaseModel):
    occurred_at: datetime | None = None
    account_number: str | None = None
    transaction_type: TransactionType | None = None
    amount: Decimal | None = None
    currency: str | None = None
    counterparty: str | None = None
    category: str | None = None
    notes: str | None = None
    payment_method: str | None = None
    owner_user_id: int | None = None


class TransactionFilterQuery(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    owner_user_id: int | None = None
    account_number: str | None = None
    category: str | None = None
    transaction_type: TransactionType | None = None
    payment_method: str | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    counterparty: str | None = None
    include_deleted: bool = False
    page: int = 1
    page_size: int = 20
    sort_by: str = "occurred_at"
    sort_order: str = "desc"


class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    occurred_at: datetime
    account_number: str
    transaction_type: TransactionType
    amount: Decimal
    currency: str
    counterparty: str
    category: str
    notes: str | None
    payment_method: str
    owner_user_id: int
    is_deleted: bool


class TransactionsListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int


def transaction_to_response(transaction) -> dict:
    return {
        "id": transaction.id,
        "transaction_id": transaction.transaction_id,
        "occurred_at": transaction.occurred_at,
        "account_number": transaction.account_number,
        "transaction_type": transaction.transaction_type,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "counterparty": transaction.counterparty,
        "category": transaction.category,
        "notes": transaction.notes,
        "payment_method": transaction.payment_method,
        "owner_user_id": transaction.owner_user_id,
        "is_deleted": transaction.is_deleted,
    }


def transactions_list_to_response(items: list, total: int) -> dict:
    return {"items": [transaction_to_response(tx) for tx in items], "total": total}
