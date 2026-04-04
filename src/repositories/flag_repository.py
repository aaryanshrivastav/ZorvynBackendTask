from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.flag import Flag


class FlagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, flag: Flag) -> Flag:
        self.db.add(flag)
        self.db.flush()
        return flag

    def get_by_id(self, flag_id: int) -> Flag | None:
        return self.db.scalar(select(Flag).where(Flag.id == flag_id))

    def list_all(self) -> list[Flag]:
        return list(self.db.scalars(select(Flag).order_by(Flag.created_at.desc())).all())
