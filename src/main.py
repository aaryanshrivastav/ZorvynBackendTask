from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import audit_logs, auth, change_requests, dashboard, flags, transactions, users, viewer_scopes

app = FastAPI(title="Zorvyn Finance Dashboard API")

frontend_dir = Path(__file__).resolve().parent / "frontend"
static_dir = frontend_dir / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/admin/users", tags=["users"])
app.include_router(viewer_scopes.router, prefix="/admin/viewer-scopes", tags=["viewer_scopes"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(change_requests.router, prefix="/change-requests", tags=["change_requests"])
app.include_router(flags.router, prefix="/flags", tags=["flags"])
app.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit_logs"])

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
