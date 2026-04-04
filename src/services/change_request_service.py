from datetime import datetime

from sqlalchemy.orm import Session

from src.core.constants import RequestStatus, RequestType
from src.core.exceptions import conflict, forbidden, not_found
from src.models.record_change_request import RecordChangeRequest
from src.repositories.change_request_repository import ChangeRequestRepository
from src.repositories.transaction_repository import TransactionRepository
from src.utils.helpers.audit import log_audit_event


class ChangeRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.request_repo = ChangeRequestRepository(db)
        self.transaction_repo = TransactionRepository(db)

    def create_update_request(self, transaction_id: int, reason: str, proposed_changes: dict, requester_user_id: int):
        tx = self.transaction_repo.get_by_id(transaction_id)
        if not tx or tx.is_deleted:
            raise not_found("Transaction not found")

        allowed_update_fields = {"category", "counterparty", "payment_method", "notes"}
        unknown_fields = set(proposed_changes.keys()) - allowed_update_fields
        if unknown_fields:
            invalid_fields = ", ".join(sorted(unknown_fields))
            raise conflict(f"Unsupported change-request fields: {invalid_fields}")

        missing_model_fields = [field for field in proposed_changes if not hasattr(tx, field)]
        if missing_model_fields:
            invalid_fields = ", ".join(sorted(missing_model_fields))
            raise conflict(f"Requested fields are not mutable on transactions: {invalid_fields}")

        req = RecordChangeRequest(
            transaction_id=transaction_id,
            request_type=RequestType.UPDATE.value,
            status=RequestStatus.PENDING.value,
            reason=reason,
            proposed_changes=proposed_changes,
            requester_user_id=requester_user_id,
        )
        self.request_repo.create(req)
        log_audit_event(self.db, requester_user_id, "CHANGE_REQUEST_CREATE", "change_request", str(req.id), "SUCCESS", {"type": "UPDATE"})
        self.db.commit()
        self.db.refresh(req)
        return req

    def create_delete_request(self, transaction_id: int, reason: str, requester_user_id: int):
        tx = self.transaction_repo.get_by_id(transaction_id)
        if not tx or tx.is_deleted:
            raise not_found("Transaction not found")

        existing_pending_delete = [r for r in self.request_repo.list_pending() if r.transaction_id == transaction_id and r.request_type == "DELETE"]
        if existing_pending_delete:
            raise conflict("An active delete request already exists for this transaction")

        req = RecordChangeRequest(
            transaction_id=transaction_id,
            request_type=RequestType.DELETE.value,
            status=RequestStatus.PENDING.value,
            reason=reason,
            requester_user_id=requester_user_id,
        )
        self.request_repo.create(req)
        log_audit_event(self.db, requester_user_id, "CHANGE_REQUEST_CREATE", "change_request", str(req.id), "SUCCESS", {"type": "DELETE"})
        self.db.commit()
        self.db.refresh(req)
        return req

    def list_my_requests(self, requester_user_id: int):
        return self.request_repo.list_by_requester(requester_user_id)

    def list_pending_requests(self):
        return self.request_repo.list_pending()

    def get_request(self, request_id: int):
        req = self.request_repo.get_by_id(request_id)
        if not req:
            raise not_found("Change request not found")
        return req

    def get_request_for_user(self, request_id: int, current_user):
        req = self.get_request(request_id)

        if current_user.role.name == "Admin":
            return req
        if current_user.role.name == "Analyst" and req.requester_user_id == current_user.id:
            return req
        if current_user.role.name == "Approver" and (
            req.status == RequestStatus.PENDING.value or req.reviewer_user_id == current_user.id
        ):
            return req

        raise forbidden("You are not allowed to view this change request")

    def decide_request(self, request_id: int, approver_user_id: int, decision: str):
        req = self.get_request(request_id)
        if req.status != RequestStatus.PENDING.value:
            raise conflict("Only pending requests can be reviewed")
        if req.requester_user_id == approver_user_id:
            raise conflict("Approver cannot approve or reject their own request")

        tx = self.transaction_repo.get_by_id(req.transaction_id)
        if not tx:
            raise not_found("Transaction not found")

        if decision == "APPROVE":
            req.status = RequestStatus.APPROVED.value
            # Only whitelisted update fields can be persisted from proposed_changes.
            if req.request_type == RequestType.UPDATE.value and req.proposed_changes:
                for key, value in req.proposed_changes.items():
                    if hasattr(tx, key):
                        setattr(tx, key, value)
            if req.request_type == RequestType.DELETE.value:
                tx.is_deleted = True
                tx.deleted_at = datetime.utcnow()
                tx.deleted_by_user_id = approver_user_id
        else:
            req.status = RequestStatus.REJECTED.value

        req.reviewer_user_id = approver_user_id
        req.reviewed_at = datetime.utcnow()
        log_audit_event(self.db, approver_user_id, "CHANGE_REQUEST_DECIDE", "change_request", str(req.id), "SUCCESS", {"decision": decision})
        self.db.commit()
        self.db.refresh(req)
        return req
