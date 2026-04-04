from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user, require_roles
from src.core.constants import RoleName
from src.db.session import get_db
from src.schemas.dashboard import CategoryTotal, DashboardSummary, RecentActivityItem, TrendPoint
from src.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.VIEWER, RoleName.ANALYST, RoleName.APPROVER, RoleName.ADMIN))):
    return DashboardService(db).summary(current_user)


@router.get("/category-totals", response_model=list[CategoryTotal])
def category_totals(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.VIEWER, RoleName.ANALYST, RoleName.APPROVER, RoleName.ADMIN))):
    return DashboardService(db).category_totals(current_user)


@router.get("/recent-activity", response_model=list[RecentActivityItem])
def recent_activity(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.VIEWER, RoleName.ANALYST, RoleName.APPROVER, RoleName.ADMIN))):
    return DashboardService(db).recent_activity(current_user)


@router.get("/monthly-trends", response_model=list[TrendPoint])
def monthly_trends(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.VIEWER, RoleName.ANALYST, RoleName.APPROVER, RoleName.ADMIN))):
    return DashboardService(db).monthly_trends(current_user)


@router.get("/weekly-trends", response_model=list[TrendPoint])
def weekly_trends(db: Session = Depends(get_db), current_user=Depends(require_roles(RoleName.VIEWER, RoleName.ANALYST, RoleName.APPROVER, RoleName.ADMIN))):
    return DashboardService(db).weekly_trends(current_user)
