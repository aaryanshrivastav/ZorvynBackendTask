from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user, require_roles
from src.core.constants import RoleName
from src.db.session import get_db
from src.schemas.transaction import TransactionCreate, TransactionResponse, TransactionsListResponse
from src.services.transaction_service import TransactionService

router = APIRouter()


@router.post("", response_model=TransactionResponse)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ANALYST, RoleName.ADMIN)),
):
    tx = TransactionService(db).create_transaction(payload.model_dump(), current_user.id)
    return {
        "id": tx.id,
        "transaction_id": tx.transaction_id,
        "occurred_at": tx.occurred_at,
        "account_number": tx.account_number,
        "transaction_type": tx.transaction_type,
        "amount": tx.amount,
        "currency": tx.currency,
        "counterparty": tx.counterparty,
        "category": tx.category,
        "payment_method": tx.payment_method,
        "owner_user_id": tx.owner_user_id,
        "is_deleted": tx.is_deleted,
    }


@router.get("", response_model=TransactionsListResponse)
def list_transactions(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    owner_user_id: int | None = None,
    account_number: str | None = None,
    category: str | None = None,
    transaction_type: str | None = None,
    payment_method: str | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    counterparty: str | None = None,
    include_deleted: bool = False,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = "occurred_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items, total = TransactionService(db).list_transactions(
        {
            "start_date": start_date,
            "end_date": end_date,
            "owner_user_id": owner_user_id,
            "account_number": account_number,
            "category": category,
            "transaction_type": transaction_type,
            "payment_method": payment_method,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "counterparty": counterparty,
            "include_deleted": include_deleted,
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
        current_user,
    )
    return {
        "items": [
            {
                "id": tx.id,
                "transaction_id": tx.transaction_id,
                "occurred_at": tx.occurred_at,
                "account_number": tx.account_number,
                "transaction_type": tx.transaction_type,
                "amount": tx.amount,
                "currency": tx.currency,
                "counterparty": tx.counterparty,
                "category": tx.category,
                "payment_method": tx.payment_method,
                "owner_user_id": tx.owner_user_id,
                "is_deleted": tx.is_deleted,
            }
            for tx in items
        ],
        "total": total,
    }


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tx = TransactionService(db).get_transaction(transaction_id, current_user)
    return {
        "id": tx.id,
        "transaction_id": tx.transaction_id,
        "occurred_at": tx.occurred_at,
        "account_number": tx.account_number,
        "transaction_type": tx.transaction_type,
        "amount": tx.amount,
        "currency": tx.currency,
        "counterparty": tx.counterparty,
        "category": tx.category,
        "payment_method": tx.payment_method,
        "owner_user_id": tx.owner_user_id,
        "is_deleted": tx.is_deleted,
    }
