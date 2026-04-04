from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.db.session import get_db
from src.schemas.auth import LoginRequest, LogoutRequest, MeResponse, RefreshRequest, TokenPair
from src.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload.username, payload.password)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(payload.refresh_token)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    AuthService(db).logout(payload.refresh_token, current_user.id)
    return {"message": "Logged out"}


@router.get("/me", response_model=MeResponse)
def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.name,
        "status": current_user.status,
        "created_at": current_user.created_at,
    }
