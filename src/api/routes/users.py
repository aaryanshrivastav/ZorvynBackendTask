from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.auth.dependencies import require_roles
from src.core.constants import RoleName
from src.db.session import get_db
from src.schemas.user import UserCreate, UserResponse, UserRoleUpdate, UserStatusUpdate, UserUpdate, UsersListResponse
from src.services.user_service import UserService

router = APIRouter()


@router.post("", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    user = UserService(db).create_user(payload.username, payload.password, payload.role, current_user.id)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.name,
        "status": user.status,
        "created_at": user.created_at,
    }


@router.get("", response_model=UsersListResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ADMIN)),
):
    items, total = UserService(db).list_users(page, page_size)
    return {
        "items": [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role.name,
                "status": user.status,
                "created_at": user.created_at,
            }
            for user in items
        ],
        "total": total,
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    user = UserService(db).get_user(user_id)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.name,
        "status": user.status,
        "created_at": user.created_at,
    }


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(payload: UserUpdate, user_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    user = UserService(db).update_user(user_id, payload.username, current_user.id)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.name,
        "status": user.status,
        "created_at": user.created_at,
    }


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(payload: UserRoleUpdate, user_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    user = UserService(db).update_user_role(user_id, payload.role, current_user.id)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.name,
        "status": user.status,
        "created_at": user.created_at,
    }


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(payload: UserStatusUpdate, user_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    user = UserService(db).update_user_status(user_id, payload.status, current_user.id)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.name,
        "status": user.status,
        "created_at": user.created_at,
    }
