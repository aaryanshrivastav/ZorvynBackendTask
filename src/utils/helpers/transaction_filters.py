from datetime import datetime, timedelta

from sqlalchemy import Select, and_, asc, desc, or_, select

from src.models.transaction import Transaction
from src.models.viewer_access_scope import ViewerAccessScope


SORT_FIELDS = {
    "occurred_at": Transaction.occurred_at,
    "amount": Transaction.amount,
    "category": Transaction.category,
    "transaction_type": Transaction.transaction_type,
}


def normalize_end_date(end_date: datetime | None) -> datetime | None:
    if not end_date:
        return None
    return end_date + timedelta(days=1)


def build_transaction_filters(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    owner_user_id: int | None = None,
    account_number: str | None = None,
    category: str | None = None,
    transaction_type: str | None = None,
    payment_method: str | None = None,
    min_amount=None,
    max_amount=None,
    counterparty: str | None = None,
    include_deleted: bool = False,
) -> list:
    filters = []
    if not include_deleted:
        filters.append(Transaction.is_deleted.is_(False))
    if start_date:
        filters.append(Transaction.occurred_at >= start_date)
    normalized_end = normalize_end_date(end_date)
    if normalized_end:
        filters.append(Transaction.occurred_at < normalized_end)
    if owner_user_id is not None:
        filters.append(Transaction.owner_user_id == owner_user_id)
    if account_number:
        filters.append(Transaction.account_number == account_number)
    if category:
        filters.append(Transaction.category == category)
    if transaction_type:
        filters.append(Transaction.transaction_type == transaction_type)
    if payment_method:
        filters.append(Transaction.payment_method == payment_method)
    if min_amount is not None:
        filters.append(Transaction.amount >= min_amount)
    if max_amount is not None:
        filters.append(Transaction.amount <= max_amount)
    if counterparty:
        filters.append(Transaction.counterparty == counterparty)
    return filters


def apply_viewer_scope(base_stmt: Select, viewer_user_id: int) -> Select:
    user_scope_subq = (
        select(ViewerAccessScope.scoped_user_id)
        .where(
            ViewerAccessScope.viewer_user_id == viewer_user_id,
            ViewerAccessScope.scope_type == "USER",
        )
        .subquery()
    )
    account_scope_subq = (
        select(ViewerAccessScope.account_number)
        .where(
            ViewerAccessScope.viewer_user_id == viewer_user_id,
            ViewerAccessScope.scope_type == "ACCOUNT",
        )
        .subquery()
    )

    return base_stmt.where(
        or_(
            Transaction.owner_user_id.in_(select(user_scope_subq.c.scoped_user_id)),
            Transaction.account_number.in_(select(account_scope_subq.c.account_number)),
        )
    )


def build_transaction_query(filters: list, sort_by: str = "occurred_at", sort_order: str = "desc") -> Select:
    stmt = select(Transaction).where(and_(*filters)) if filters else select(Transaction)
    sort_column = SORT_FIELDS.get(sort_by, Transaction.occurred_at)
    if sort_order.lower() == "asc":
        return stmt.order_by(asc(sort_column))
    return stmt.order_by(desc(sort_column))
