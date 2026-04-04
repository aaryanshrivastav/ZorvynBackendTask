from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal


class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class TrendPoint(BaseModel):
    period: str
    total: Decimal


class RecentActivityItem(BaseModel):
    transaction_id: str
    amount: Decimal
    category: str
    transaction_type: str
    occurred_at: datetime
