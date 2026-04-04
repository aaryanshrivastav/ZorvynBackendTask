from sqlalchemy.orm import Session

from src.core.constants import RoleName
from src.db.base import Base
from src.db.session import engine
from src.models import role  # noqa: F401
from src.models.role import Role


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_roles(db: Session) -> None:
    existing = {r.name for r in db.query(Role).all()}
    for role_name in [r.value for r in RoleName]:
        if role_name not in existing:
            db.add(Role(name=role_name))
    db.commit()
