from enum import Enum


class RoleName(str, Enum):
    VIEWER = "Viewer"
    ANALYST = "Analyst"
    APPROVER = "Approver"
    ADMIN = "Admin"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class RequestType(str, Enum):
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ScopeType(str, Enum):
    USER = "USER"
    ACCOUNT = "ACCOUNT"


class FlagStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
