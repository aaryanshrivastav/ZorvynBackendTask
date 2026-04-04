from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from src.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.flush()
        return log

    def build_filtered_query(
        self,
        actor_user_id: int | None,
        action: str | None,
        resource_type: str | None,
        start: datetime | None,
        end: datetime | None,
    ) -> Select:
        stmt = select(AuditLog)
        if actor_user_id is not None:
            stmt = stmt.where(AuditLog.actor_user_id == actor_user_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
        if start:
            stmt = stmt.where(AuditLog.created_at >= start)
        if end:
            stmt = stmt.where(AuditLog.created_at < end)
        return stmt.order_by(AuditLog.created_at.desc())
