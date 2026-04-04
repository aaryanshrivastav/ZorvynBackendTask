from sqlalchemy.orm import Session

from src.models.audit_log import AuditLog


def log_audit_event(
    db: Session,
    actor_user_id: int | None,
    action: str,
    resource_type: str,
    resource_id: str | None,
    result: str,
    metadata: dict | None = None,
) -> None:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        metadata_json=metadata,
    )
    db.add(entry)
