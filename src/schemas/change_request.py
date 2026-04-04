from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.core.constants import RequestStatus, RequestType


class ChangeRequestCreateUpdate(BaseModel):
    transaction_id: int
    reason: str = Field(min_length=1)
    proposed_changes: dict


class ChangeRequestCreateDelete(BaseModel):
    transaction_id: int
    reason: str = Field(min_length=1)


class ChangeRequestDecision(BaseModel):
    decision: Literal["APPROVE", "REJECT"]
    comment: str | None = None


class ChangeRequestResponse(BaseModel):
    id: int
    transaction_id: int
    request_type: RequestType
    status: RequestStatus
    reason: str
    proposed_changes: dict | None
    requester_user_id: int
    reviewer_user_id: int | None
    created_at: datetime
    reviewed_at: datetime | None


class ChangeRequestListResponse(BaseModel):
    items: list[ChangeRequestResponse]
    total: int
