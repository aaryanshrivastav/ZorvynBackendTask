from sqlalchemy.orm import Session

from src.models.transaction import Transaction
from src.utils.helpers.dashboard_queries import get_category_totals, get_dashboard_summary, get_recent_activity, get_trend_data
from src.utils.helpers.transaction_filters import apply_viewer_scope


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _scoped_base_query(self, current_user):
        stmt = self.db.query(Transaction).filter(Transaction.is_deleted.is_(False)).statement
        if current_user.role.name == "Viewer":
            stmt = apply_viewer_scope(stmt, current_user.id)
        elif current_user.role.name == "Analyst":
            stmt = stmt.where(Transaction.owner_user_id == current_user.id)
        return stmt

    def summary(self, current_user):
        return get_dashboard_summary(self.db, self._scoped_base_query(current_user))

    def category_totals(self, current_user):
        return get_category_totals(self.db, self._scoped_base_query(current_user))

    def recent_activity(self, current_user):
        return get_recent_activity(self.db, self._scoped_base_query(current_user))

    def monthly_trends(self, current_user):
        return get_trend_data(self.db, self._scoped_base_query(current_user), granularity="month")

    def weekly_trends(self, current_user):
        return get_trend_data(self.db, self._scoped_base_query(current_user), granularity="week")
