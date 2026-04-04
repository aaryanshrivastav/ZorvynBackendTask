from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user, require_roles
from src.core.constants import RoleName
from src.db.session import get_db
from src.schemas.change_request import (
    ChangeRequestCreateDelete,
    ChangeRequestCreateUpdate,
    ChangeRequestDecision,
    ChangeRequestListResponse,
    ChangeRequestResponse,
)
from src.services.change_request_service import ChangeRequestService

router = APIRouter()


def _to_response(req):
    return {
        "id": req.id,
        "transaction_id": req.transaction_id,
        "request_type": req.request_type,
        "status": req.status,
        "reason": req.reason,
        "proposed_changes": req.proposed_changes,
        "requester_user_id": req.requester_user_id,
        "reviewer_user_id": req.reviewer_user_id,
        "created_at": req.created_at,
        "reviewed_at": req.reviewed_at,
    }


@router.post("/update", response_model=ChangeRequestResponse)
def create_update_request(
    payload: ChangeRequestCreateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ANALYST)),
):
    req = ChangeRequestService(db).create_update_request(
        payload.transaction_id,
        payload.reason,
        payload.proposed_changes,
        current_user.id,
    )
    return _to_response(req)


@router.post("/delete", response_model=ChangeRequestResponse)
def create_delete_request(
    payload: ChangeRequestCreateDelete,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.ANALYST)),
):
    req = ChangeRequestService(db).create_delete_request(payload.transaction_id, payload.reason, current_user.id)
    return _to_response(req)


@router.get("/mine", response_model=ChangeRequestListResponse)
def list_my_requests(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ANALYST))):
    items = ChangeRequestService(db).list_my_requests(current_user.id)
    return {"items": [_to_response(i) for i in items], "total": len(items)}


@router.get("/pending", response_model=ChangeRequestListResponse)
def list_pending(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.APPROVER))):
    items = ChangeRequestService(db).list_pending_requests()
    return {"items": [_to_response(i) for i in items], "total": len(items)}


@router.get("/{request_id}", response_model=ChangeRequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    req = ChangeRequestService(db).get_request(request_id)
    return _to_response(req)


@router.post("/{request_id}/review", response_model=ChangeRequestResponse)
def review_request(
    request_id: int,
    payload: ChangeRequestDecision,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleName.APPROVER)),
):
    req = ChangeRequestService(db).decide_request(request_id, current_user.id, payload.decision)
    return _to_response(req)
