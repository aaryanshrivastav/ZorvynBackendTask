from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import require_roles
from src.core.constants import RoleName
from src.db.session import get_db
from src.schemas.common import APIMessage
from src.schemas.viewer_scope import ViewerScopeCreate, ViewerScopeResponse
from src.services.viewer_scope_service import ViewerScopeService

router = APIRouter()


@router.post("", response_model=ViewerScopeResponse, status_code=201)
def grant_scope(payload: ViewerScopeCreate, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    scope = ViewerScopeService(db).grant_scope(
        payload.viewer_user_id,
        payload.scope_type,
        payload.scoped_user_id,
        payload.account_number,
        current_user.id,
    )
    return {
        "id": scope.id,
        "viewer_user_id": scope.viewer_user_id,
        "scope_type": scope.scope_type,
        "scoped_user_id": scope.scoped_user_id,
        "account_number": scope.account_number,
        "created_at": scope.created_at,
    }


@router.get("/{viewer_user_id}", response_model=list[ViewerScopeResponse])
def list_scopes(viewer_user_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    scopes = ViewerScopeService(db).list_scopes(viewer_user_id)
    return [
        {
            "id": scope.id,
            "viewer_user_id": scope.viewer_user_id,
            "scope_type": scope.scope_type,
            "scoped_user_id": scope.scoped_user_id,
            "account_number": scope.account_number,
            "created_at": scope.created_at,
        }
        for scope in scopes
    ]


@router.delete("/{scope_id}", response_model=APIMessage)
def revoke_scope(scope_id: int, db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.ADMIN))):
    ViewerScopeService(db).revoke_scope(scope_id, current_user.id)
    return {"message": "Scope revoked"}
