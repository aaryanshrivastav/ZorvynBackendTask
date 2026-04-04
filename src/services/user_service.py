from sqlalchemy.orm import Session

from src.core.exceptions import bad_request, not_found
from src.models.user import User
from src.repositories.role_repository import RoleRepository
from src.repositories.user_repository import UserRepository
from src.utils.helpers.audit import log_audit_event


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def create_user(self, username: str, password: str, role_name: str, actor_user_id: int):
        if self.user_repo.get_by_username(username):
            raise bad_request("Username already exists")
        role = self.role_repo.get_by_name(role_name)
        if not role:
            raise bad_request("Invalid role")

        user = User(username=username, password=password, role_id=role.id, status="ACTIVE")
        self.user_repo.create(user)
        log_audit_event(self.db, actor_user_id, "USER_CREATE", "user", str(user.id), "SUCCESS")
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, page: int, page_size: int):
        return self.user_repo.list_users(skip=(page - 1) * page_size, limit=page_size)

    def get_user(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise not_found("User not found")
        return user

    def update_user(self, user_id: int, username: str | None, actor_user_id: int):
        user = self.get_user(user_id)
        if username:
            user.username = username
        log_audit_event(self.db, actor_user_id, "USER_UPDATE", "user", str(user.id), "SUCCESS")
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user_role(self, user_id: int, role_name: str, actor_user_id: int):
        user = self.get_user(user_id)
        role = self.role_repo.get_by_name(role_name)
        if not role:
            raise bad_request("Invalid role")
        user.role_id = role.id
        log_audit_event(self.db, actor_user_id, "USER_ROLE_UPDATE", "user", str(user.id), "SUCCESS", {"role": role_name})
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user_status(self, user_id: int, status: str, actor_user_id: int):
        if status not in {"ACTIVE", "INACTIVE"}:
            raise bad_request("Invalid status")
        user = self.get_user(user_id)
        user.status = status
        log_audit_event(self.db, actor_user_id, "USER_STATUS_UPDATE", "user", str(user.id), "SUCCESS", {"status": status})
        self.db.commit()
        self.db.refresh(user)
        return user
