from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.constants import RoleName
from src.core.exceptions import forbidden, unauthorized
from src.core.security import TokenPayloadError, decode_token
from src.db.session import get_db
from src.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
    except TokenPayloadError as exc:
        raise unauthorized("Invalid access token") from exc

    if payload.get("type") != "access":
        raise unauthorized("Invalid token type")

    user_id = int(payload["sub"])
    user = UserRepository(db).get_by_id(user_id)
    if not user or user.status != "ACTIVE":
        raise unauthorized("User is inactive or missing")
    return user


def require_roles(*roles: RoleName):
    def checker(current_user=Depends(get_current_user)):
        if current_user.role.name not in {r.value for r in roles}:
            raise forbidden("Insufficient role permissions")
        return current_user

    return checker
