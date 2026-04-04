from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    transaction_id: str = Field(min_length=3, max_length=50)
    occurred_at: datetime
    account_number: str
    transaction_type: str
    amount: Decimal
    currency: str
    counterparty: str
    category: str
    payment_method: str
    owner_user_id: int


class TransactionFilterQuery(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    owner_user_id: int | None = None
    account_number: str | None = None
    category: str | None = None
    transaction_type: str | None = None
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
    transaction_type: str
    amount: Decimal
    currency: str
    counterparty: str
    category: str
    payment_method: str
    owner_user_id: int
    is_deleted: bool


class TransactionsListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
