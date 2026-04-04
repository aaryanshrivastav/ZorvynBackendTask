from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=3, max_length=255)
    role: str


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=100)


class UserRoleUpdate(BaseModel):
    role: str


class UserStatusUpdate(BaseModel):
    status: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    status: str
    created_at: datetime


class UsersListResponse(BaseModel):
    items: list[UserResponse]
    total: int
