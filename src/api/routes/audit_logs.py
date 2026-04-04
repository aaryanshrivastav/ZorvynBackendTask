from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.auth.dependencies import require_roles
from src.core.constants import RoleName
from src.db.session import get_db
from src.schemas.audit_log import AuditLogListResponse
from src.services.audit_log_service import AuditLogService

router = APIRouter()


@router.get("", response_model=AuditLogListResponse)
def list_logs(
    actor_user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ADMIN)),
):
    items, total = AuditLogService(db).list_logs(actor_user_id, action, resource_type, start, end, page, page_size)
    return {
        "items": [
            {
                "id": x.id,
                "actor_user_id": x.actor_user_id,
                "action": x.action,
                "resource_type": x.resource_type,
                "resource_id": x.resource_id,
                "result": x.result,
                "metadata": x.metadata_json,
                "created_at": x.created_at,
            }
            for x in items
        ],
        "total": total,
    }
