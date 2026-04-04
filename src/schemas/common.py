from datetime import datetime

from pydantic import BaseModel


class APIMessage(BaseModel):
    message: str


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class DateRangeFilter(BaseModel):
    start: datetime | None = None
    end: datetime | None = None
