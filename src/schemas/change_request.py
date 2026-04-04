from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ChangeRequestCreateUpdate(BaseModel):
    transaction_id: int
    reason: str = Field(min_length=1)
    proposed_changes: dict


class ChangeRequestCreateDelete(BaseModel):
    transaction_id: int
    reason: str = Field(min_length=1)


class ChangeRequestDecision(BaseModel):
    decision: str
    comment: str | None = None

    @model_validator(mode="after")
    def validate_decision(self):
        if self.decision not in {"APPROVE", "REJECT"}:
            raise ValueError("decision must be APPROVE or REJECT")
        return self


class ChangeRequestResponse(BaseModel):
    id: int
    transaction_id: int
    request_type: str
    status: str
    reason: str
    proposed_changes: dict | None
    requester_user_id: int
    reviewer_user_id: int | None
    created_at: datetime
    reviewed_at: datetime | None


class ChangeRequestListResponse(BaseModel):
    items: list[ChangeRequestResponse]
    total: int
