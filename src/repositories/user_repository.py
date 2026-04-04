from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.scalar(select(User).where(User.id == user_id))

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def list_users(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        total = self.db.scalar(select(func.count()).select_from(User)) or 0
        items = list(self.db.scalars(select(User).offset(skip).limit(limit)).all())
        return items, total
