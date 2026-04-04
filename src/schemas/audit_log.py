from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    resource_type: str
    resource_id: str | None
    result: str
    metadata: dict | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
