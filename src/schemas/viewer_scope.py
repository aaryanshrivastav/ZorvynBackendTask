from datetime import datetime

from pydantic import BaseModel, model_validator


class ViewerScopeCreate(BaseModel):
    viewer_user_id: int
    scope_type: str
    scoped_user_id: int | None = None
    account_number: str | None = None

    @model_validator(mode="after")
    def validate_scope(self):
        if self.scope_type == "USER" and not self.scoped_user_id:
            raise ValueError("scoped_user_id required for USER scope")
        if self.scope_type == "ACCOUNT" and not self.account_number:
            raise ValueError("account_number required for ACCOUNT scope")
        return self


class ViewerScopeResponse(BaseModel):
    id: int
    viewer_user_id: int
    scope_type: str
    scoped_user_id: int | None
    account_number: str | None
    created_at: datetime
