from sqlalchemy.orm import Session

from src.core.exceptions import bad_request, not_found
from src.models.viewer_access_scope import ViewerAccessScope
from src.repositories.user_repository import UserRepository
from src.repositories.viewer_scope_repository import ViewerScopeRepository
from src.utils.helpers.audit import log_audit_event


class ViewerScopeService:
    def __init__(self, db: Session):
        self.db = db
        self.scope_repo = ViewerScopeRepository(db)
        self.user_repo = UserRepository(db)

    def grant_scope(self, viewer_user_id: int, scope_type: str, scoped_user_id: int | None, account_number: str | None, actor_user_id: int):
        viewer = self.user_repo.get_by_id(viewer_user_id)
        if not viewer or viewer.role.name != "Viewer":
            raise bad_request("Target user must have Viewer role")

        if scope_type == "USER":
            if not scoped_user_id or not self.user_repo.get_by_id(scoped_user_id):
                raise bad_request("Valid scoped_user_id is required")
            account_number = None
        elif scope_type == "ACCOUNT":
            if not account_number:
                raise bad_request("account_number is required")
            scoped_user_id = None
        else:
            raise bad_request("Invalid scope_type")

        scope = ViewerAccessScope(
            viewer_user_id=viewer_user_id,
            scope_type=scope_type,
            scoped_user_id=scoped_user_id,
            account_number=account_number,
        )
        self.scope_repo.create(scope)
        log_audit_event(self.db, actor_user_id, "VIEWER_SCOPE_GRANT", "viewer_scope", str(scope.id), "SUCCESS")
        self.db.commit()
        self.db.refresh(scope)
        return scope

    def list_scopes(self, viewer_user_id: int):
        return self.scope_repo.list_by_viewer(viewer_user_id)

    def revoke_scope(self, scope_id: int, actor_user_id: int):
        deleted = self.scope_repo.delete_scope(scope_id)
        if not deleted:
            raise not_found("Scope not found")
        log_audit_event(self.db, actor_user_id, "VIEWER_SCOPE_REVOKE", "viewer_scope", str(scope_id), "SUCCESS")
        self.db.commit()
