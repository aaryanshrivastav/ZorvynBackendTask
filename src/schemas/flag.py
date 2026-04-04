from datetime import datetime

from pydantic import BaseModel, Field

from src.core.constants import FlagStatus


class FlagCreate(BaseModel):
    transaction_id: int
    reason: str = Field(min_length=1)


class FlagReview(BaseModel):
    status: FlagStatus


class FlagResponse(BaseModel):
    id: int
    transaction_id: int
    created_by_user_id: int
    reason: str
    status: FlagStatus
    reviewed_by_user_id: int | None
    created_at: datetime
