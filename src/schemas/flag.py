from datetime import datetime

from pydantic import BaseModel, Field


class FlagCreate(BaseModel):
    transaction_id: int
    reason: str = Field(min_length=1)


class FlagReview(BaseModel):
    status: str


class FlagResponse(BaseModel):
    id: int
    transaction_id: int
    created_by_user_id: int
    reason: str
    status: str
    reviewed_by_user_id: int | None
    created_at: datetime
