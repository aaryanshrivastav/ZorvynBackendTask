from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from src.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        return self.db.scalar(select(Transaction).where(Transaction.id == transaction_id))

    def get_by_external_id(self, ext_id: str) -> Transaction | None:
        return self.db.scalar(select(Transaction).where(Transaction.transaction_id == ext_id))

    def paginate(self, stmt: Select, page: int, page_size: int) -> tuple[list[Transaction], int]:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all())
        return items, total
