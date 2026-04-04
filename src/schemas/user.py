from datetime import datetime

from pydantic import BaseModel, Field

from src.core.constants import RoleName, UserStatus


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=3, max_length=255)
    role: RoleName


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=100)


class UserRoleUpdate(BaseModel):
    role: RoleName


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserResponse(BaseModel):
    id: int
    username: str
    role: RoleName
    status: UserStatus
    created_at: datetime


class UsersListResponse(BaseModel):
    items: list[UserResponse]
    total: int


def user_to_response(user) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.name,
        "status": user.status,
        "created_at": user.created_at,
    }


def users_list_to_response(items: list, total: int) -> dict:
    return {"items": [user_to_response(user) for user in items], "total": total}
