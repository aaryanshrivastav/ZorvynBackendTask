from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditLogRepository(db)

    def list_logs(
        self,
        actor_user_id: int | None,
        action: str | None,
        resource_type: str | None,
        start: datetime | None,
        end: datetime | None,
        page: int,
        page_size: int,
    ):
        stmt = self.repo.build_filtered_query(actor_user_id, action, resource_type, start, end)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all())
        return items, total
