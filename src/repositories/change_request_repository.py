from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.record_change_request import RecordChangeRequest


class ChangeRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, request: RecordChangeRequest) -> RecordChangeRequest:
        self.db.add(request)
        self.db.flush()
        return request

    def get_by_id(self, request_id: int) -> RecordChangeRequest | None:
        return self.db.scalar(select(RecordChangeRequest).where(RecordChangeRequest.id == request_id))

    def list_by_requester(self, requester_user_id: int) -> list[RecordChangeRequest]:
        return list(
            self.db.scalars(
                select(RecordChangeRequest).where(RecordChangeRequest.requester_user_id == requester_user_id).order_by(RecordChangeRequest.created_at.desc())
            ).all()
        )

    def list_pending(self) -> list[RecordChangeRequest]:
        return list(
            self.db.scalars(
                select(RecordChangeRequest)
                .where(RecordChangeRequest.status == "PENDING")
                .order_by(RecordChangeRequest.created_at.asc())
            ).all()
        )
