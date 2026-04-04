from sqlalchemy.orm import Session

from src.core.constants import FlagStatus
from src.core.exceptions import bad_request, conflict, not_found
from src.models.flag import Flag
from src.repositories.flag_repository import FlagRepository
from src.repositories.transaction_repository import TransactionRepository
from src.utils.helpers.audit import log_audit_event


class FlagService:
    def __init__(self, db: Session):
        self.db = db
        self.flag_repo = FlagRepository(db)
        self.transaction_repo = TransactionRepository(db)

    def create_flag(self, transaction_id: int, reason: str, actor_user_id: int):
        tx = self.transaction_repo.get_by_id(transaction_id)
        if not tx or tx.is_deleted:
            raise not_found("Transaction not found")

        flag = Flag(transaction_id=transaction_id, created_by_user_id=actor_user_id, reason=reason, status=FlagStatus.OPEN.value)
        self.flag_repo.create(flag)
        log_audit_event(self.db, actor_user_id, "FLAG_CREATE", "flag", str(flag.id), "SUCCESS")
        self.db.commit()
        self.db.refresh(flag)
        return flag

    def list_flags(self):
        return self.flag_repo.list_all()

    def get_flag(self, flag_id: int):
        flag = self.flag_repo.get_by_id(flag_id)
        if not flag:
            raise not_found("Flag not found")
        return flag

    def review_flag(self, flag_id: int, status: str, actor_user_id: int):
        normalized_status = status.value if hasattr(status, "value") else status
        allowed_statuses = {FlagStatus.OPEN.value, FlagStatus.RESOLVED.value}
        if normalized_status not in allowed_statuses:
            raise bad_request("Invalid flag status")

        flag = self.get_flag(flag_id)
        if flag.status == FlagStatus.RESOLVED.value:
            raise conflict("Resolved flags cannot be reviewed again")

        flag.status = normalized_status
        flag.reviewed_by_user_id = actor_user_id
        log_audit_event(self.db, actor_user_id, "FLAG_REVIEW", "flag", str(flag.id), "SUCCESS", {"status": normalized_status})
        self.db.commit()
        self.db.refresh(flag)
        return flag
