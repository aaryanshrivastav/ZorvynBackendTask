from fastapi import FastAPI

from src.api.routes import audit_logs, auth, change_requests, dashboard, flags, transactions, users, viewer_scopes

app = FastAPI(title="Zorvyn Finance Dashboard API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/admin/users", tags=["users"])
app.include_router(viewer_scopes.router, prefix="/admin/viewer-scopes", tags=["viewer_scopes"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(change_requests.router, prefix="/change-requests", tags=["change_requests"])
app.include_router(flags.router, prefix="/flags", tags=["flags"])
app.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit_logs"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
