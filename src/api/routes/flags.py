from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user, require_roles
from src.core.constants import RoleName
from src.db.session import get_db
from src.schemas.flag import FlagCreate, FlagResponse, FlagReview
from src.services.flag_service import FlagService

router = APIRouter()


def _to_response(flag):
    return {
        "id": flag.id,
        "transaction_id": flag.transaction_id,
        "created_by_user_id": flag.created_by_user_id,
        "reason": flag.reason,
        "status": flag.status,
        "reviewed_by_user_id": flag.reviewed_by_user_id,
        "created_at": flag.created_at,
    }


@router.post("", response_model=FlagResponse)
def create_flag(payload: FlagCreate, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ANALYST))):
    flag = FlagService(db).create_flag(payload.transaction_id, payload.reason, current_user.id)
    return _to_response(flag)


@router.get("", response_model=list[FlagResponse])
def list_flags(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.APPROVER, RoleName.ADMIN))):
    return [_to_response(flag) for flag in FlagService(db).list_flags()]


@router.get("/{flag_id}", response_model=FlagResponse)
def get_flag(flag_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.APPROVER, RoleName.ADMIN))):
    return _to_response(FlagService(db).get_flag(flag_id))


@router.patch("/{flag_id}", response_model=FlagResponse)
def review_flag(
    flag_id: int,
    payload: FlagReview,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.APPROVER, RoleName.ADMIN)),
):
    return _to_response(FlagService(db).review_flag(flag_id, payload.status, current_user.id))
