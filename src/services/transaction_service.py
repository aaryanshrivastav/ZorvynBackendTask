from sqlalchemy.orm import Session

from sqlalchemy import or_, select

from src.core.exceptions import forbidden, not_found
from src.models.transaction import Transaction
from src.models.transaction_risk_profile import TransactionRiskProfile
from src.models.viewer_access_scope import ViewerAccessScope
from src.repositories.transaction_repository import TransactionRepository
from src.utils.helpers.audit import log_audit_event
from src.utils.helpers.transaction_filters import apply_viewer_scope, build_transaction_filters, build_transaction_query


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)

    def create_transaction(self, payload: dict, actor_user_id: int):
        transaction = Transaction(**payload)
        self.transaction_repo.create(transaction)
        risk_profile = TransactionRiskProfile(transaction_id=transaction.id, risk_incident=False)
        self.db.add(risk_profile)
        log_audit_event(self.db, actor_user_id, "TRANSACTION_CREATE", "transaction", str(transaction.id), "SUCCESS")
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list_transactions(self, query_params: dict, current_user):
        filters = build_transaction_filters(
            start_date=query_params.get("start_date"),
            end_date=query_params.get("end_date"),
            owner_user_id=query_params.get("owner_user_id"),
            account_number=query_params.get("account_number"),
            category=query_params.get("category"),
            transaction_type=query_params.get("transaction_type"),
            payment_method=query_params.get("payment_method"),
            min_amount=query_params.get("min_amount"),
            max_amount=query_params.get("max_amount"),
            counterparty=query_params.get("counterparty"),
            include_deleted=query_params.get("include_deleted", False),
        )
        stmt = build_transaction_query(filters, query_params.get("sort_by", "occurred_at"), query_params.get("sort_order", "desc"))

        if current_user.role.name == "Viewer":
            stmt = apply_viewer_scope(stmt, current_user.id)
        elif current_user.role.name == "Analyst":
            stmt = stmt.where(Transaction.owner_user_id == current_user.id)

        return self.transaction_repo.paginate(stmt, query_params["page"], query_params["page_size"])

    def get_transaction(self, transaction_id: int, current_user):
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise not_found("Transaction not found")
        if current_user:
            if current_user.role.name == "Analyst" and transaction.owner_user_id != current_user.id:
                raise forbidden("Analyst cannot access this transaction")
            if current_user.role.name == "Viewer":
                allowed = self.db.execute(
                    select(ViewerAccessScope.id).where(
                        ViewerAccessScope.viewer_user_id == current_user.id,
                        or_(
                            (ViewerAccessScope.scope_type == "USER")
                            & (ViewerAccessScope.scoped_user_id == transaction.owner_user_id),
                            (ViewerAccessScope.scope_type == "ACCOUNT")
                            & (ViewerAccessScope.account_number == transaction.account_number),
                        ),
                    )
                ).first()
                if not allowed:
                    raise forbidden("Viewer cannot access this transaction")
        return transaction

    def soft_delete(self, transaction_id: int, actor_user_id: int):
        tx = self.get_transaction(transaction_id, current_user=None)
        tx.is_deleted = True
        tx.deleted_by_user_id = actor_user_id
        log_audit_event(self.db, actor_user_id, "TRANSACTION_SOFT_DELETE", "transaction", str(transaction_id), "SUCCESS")
