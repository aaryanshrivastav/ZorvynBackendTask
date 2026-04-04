from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.role import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Role | None:
        return self.db.scalar(select(Role).where(Role.name == name))

    def list_all(self) -> list[Role]:
        return list(self.db.scalars(select(Role)).all())
