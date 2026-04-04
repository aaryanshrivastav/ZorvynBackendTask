from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

INCOME_TYPES = {"Credit", "Refund", "Deposit", "Transfer In", "Income"}


def get_dashboard_summary(db: Session, scoped_stmt):
    subq = scoped_stmt.subquery()
    income_case = case((subq.c.transaction_type.in_(INCOME_TYPES), subq.c.amount), else_=0)
    expense_case = case((~subq.c.transaction_type.in_(INCOME_TYPES), subq.c.amount), else_=0)

    stmt = select(
        func.coalesce(func.sum(income_case), 0),
        func.coalesce(func.sum(expense_case), 0),
    ).select_from(subq)

    income, expenses = db.execute(stmt).one()
    return {
        "total_income": income,
        "total_expenses": expenses,
        "net_balance": income - expenses,
    }


def get_category_totals(db: Session, scoped_stmt):
    subq = scoped_stmt.subquery()
    stmt = (
        select(subq.c.category.label("category"), func.coalesce(func.sum(subq.c.amount), 0).label("total"))
        .group_by(subq.c.category)
        .order_by(func.sum(subq.c.amount).desc())
    )
    rows = db.execute(stmt).all()
    return [{"category": row.category, "total": row.total} for row in rows]


def get_recent_activity(db: Session, scoped_stmt, limit: int = 10):
    base = scoped_stmt.subquery()
    subq = select(base).order_by(base.c.occurred_at.desc()).limit(limit).subquery()
    stmt = select(
        subq.c.transaction_id,
        subq.c.amount,
        subq.c.category,
        subq.c.transaction_type,
        subq.c.occurred_at,
    ).order_by(subq.c.occurred_at.desc())
    rows = db.execute(stmt).all()
    return [dict(row._mapping) for row in rows]


def get_trend_data(db: Session, scoped_stmt, granularity: str = "month"):
    subq = scoped_stmt.subquery()
    if granularity == "week":
        period_expr = func.strftime("%Y-W%W", subq.c.occurred_at)
    else:
        period_expr = func.strftime("%Y-%m", subq.c.occurred_at)

    stmt = (
        select(period_expr.label("period"), func.coalesce(func.sum(subq.c.amount), 0).label("total"))
        .group_by(period_expr)
        .order_by(period_expr)
    )
    rows = db.execute(stmt).all()
    return [{"period": row.period, "total": row.total} for row in rows]
