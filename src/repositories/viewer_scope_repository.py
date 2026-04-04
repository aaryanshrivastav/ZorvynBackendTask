from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.models.viewer_access_scope import ViewerAccessScope


class ViewerScopeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, scope: ViewerAccessScope) -> ViewerAccessScope:
        self.db.add(scope)
        self.db.flush()
        return scope

    def list_by_viewer(self, viewer_user_id: int) -> list[ViewerAccessScope]:
        return list(self.db.scalars(select(ViewerAccessScope).where(ViewerAccessScope.viewer_user_id == viewer_user_id)).all())

    def delete_scope(self, scope_id: int) -> int:
        result = self.db.execute(delete(ViewerAccessScope).where(ViewerAccessScope.id == scope_id))
        return result.rowcount or 0
