from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user, require_roles
from src.core.constants import RoleName, TransactionType
from src.db.session import get_db
from src.schemas.common import APIMessage
from src.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionsListResponse,
    TransactionUpdate,
    transaction_to_response,
    transactions_list_to_response,
)
from src.services.transaction_service import TransactionService

router = APIRouter()


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ANALYST, RoleName.ADMIN)),
):
    payload_dict = payload.model_dump()
    if current_user.role.name == RoleName.ANALYST.value:
        payload_dict["owner_user_id"] = current_user.id

    tx = TransactionService(db).create_transaction(payload_dict, current_user.id)
    return transaction_to_response(tx)


@router.get("", response_model=TransactionsListResponse)
def list_transactions(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    owner_user_id: int | None = None,
    account_number: str | None = None,
    category: str | None = None,
    transaction_type: TransactionType | None = None,
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
    return transactions_list_to_response(items, total)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tx = TransactionService(db).get_transaction(transaction_id, current_user)
    return transaction_to_response(tx)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ADMIN)),
):
    tx = TransactionService(db).update_transaction(
        transaction_id=transaction_id,
        payload=payload.model_dump(exclude_unset=True),
        actor_user_id=current_user.id,
    )
    return transaction_to_response(tx)


@router.delete("/{transaction_id}", response_model=APIMessage)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ADMIN)),
):
    TransactionService(db).delete_transaction(transaction_id=transaction_id, actor_user_id=current_user.id)
    return {"message": "Transaction soft-deleted"}
