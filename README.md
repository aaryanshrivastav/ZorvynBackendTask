# Zorvyn Finance Backend

Production-style FastAPI backend for a finance dashboard and approval workflow platform.

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy 2.0 style ORM
- Pydantic
- JWT access + refresh tokens with persisted refresh sessions
- Alembic migrations

## Project Structure

```
.
|-- alembic/
|-- scripts/
|-- src/
|   |-- api/routes/
|   |-- auth/
|   |-- core/
|   |-- db/
|   |-- models/
|   |-- repositories/
|   |-- schemas/
|   |-- services/
|   `-- utils/helpers/
|-- tests/
|-- accounting_dataset.csv
`-- README.md
```

## Architecture

Layered architecture with strict separation of concerns:

- Routes: transport layer only (request parsing + response shape)
- Services: business workflows and rule enforcement
- Repositories: persistence access wrappers
- Helpers: reusable filtering/aggregation/audit logic
- Auth dependencies: JWT validation + RBAC gates

## Roles and Permissions

- Viewer: read-only within assigned scope (user/account-based)
- Analyst: create records, create flags, submit update/delete requests
- Approver: review pending requests and flags, approve/reject requests
- Admin: user management, role/status updates, viewer scopes, full visibility

Important enforced rule: approver cannot review their own request.

## Core Workflow Rules

1. Analyst/Admin can create transactions.
2. Analyst submits UPDATE/DELETE requests (cannot directly mutate live transactions).
3. Approver approves/rejects.
4. Approved DELETE is soft delete (`is_deleted`, `deleted_at`, `deleted_by_user_id`).
5. Only one active pending delete request per transaction.

Direct mutation policy:

- Admins can directly update and soft-delete transactions through dedicated endpoints.
- Analysts use change requests for update/delete workflow.
- Viewers and approvers cannot directly mutate transactions.

## Schema Summary

Main tables:

- `roles`
- `users`
- `viewer_access_scopes`
- `transactions`
- `transaction_risk_profiles`
- `record_change_requests`
- `flags`
- `audit_logs`
- `refresh_token_sessions`

Highlights:

- strict FKs and unique constraints
- indexed filter paths (date, owner, category, soft-delete, status)
- partial unique index for one active delete request per transaction (SQLite)
- normalized risk metadata in `transaction_risk_profiles`

### Entity Purpose and Scope

| Entity | Purpose | Scope |
|---|---|---|
| `roles` | RBAC role catalog (`Viewer`, `Analyst`, `Approver`, `Admin`) | Core requirement |
| `users` | Auth principals with status and role linkage | Core requirement |
| `transactions` | Financial records (includes optional `notes`) | Core requirement |
| `record_change_requests` | Approval workflow for update/delete requests | Core requirement |
| `audit_logs` | Action traceability for sensitive operations | Core requirement |
| `refresh_token_sessions` | Refresh token revocation and session control | Core requirement |
| `viewer_access_scopes` | Fine-grained viewer visibility by user/account | Extension |
| `flags` | Analyst/approver fraud-risk review workflow | Extension |
| `transaction_risk_profiles` | Optional risk metadata normalized from dataset | Extension |

Why these extensions exist:

- `viewer_access_scopes` demonstrates least-privilege read access for finance reviewers.
- `flags` adds a realistic triage flow often paired with approval systems.
- `transaction_risk_profiles` preserves dataset risk signals without bloating the main transaction table.

Compact relationship map:

- `users.role_id -> roles.id`
- `transactions.owner_user_id -> users.id`
- `record_change_requests.transaction_id -> transactions.id`
- `record_change_requests.requester_user_id -> users.id`
- `record_change_requests.reviewer_user_id -> users.id`
- `flags.transaction_id -> transactions.id`
- `flags.created_by_user_id/reviewed_by_user_id -> users.id`
- `viewer_access_scopes.viewer_user_id/scoped_user_id -> users.id`
- `transaction_risk_profiles.transaction_id -> transactions.id`
- `refresh_token_sessions.user_id -> users.id`
- `audit_logs.actor_user_id -> users.id`

## Security

This section summarizes password, token, and session security behavior in one place.

### Password Storage

- Passwords are stored as bcrypt hashes via `passlib`.
- Login verifies hashes; plain-text comparison is not used.

### Token Expiry

- Access token expiry: `15` minutes (`access_token_expire_minutes`).
- Refresh token expiry: `10080` minutes / 7 days (`refresh_token_expire_minutes`).
- Expiry settings are configurable in `src/core/config.py`.

### Refresh Token Revocation

- Refresh tokens are persisted in `refresh_token_sessions` with token id (`jti`).
- `/auth/refresh` rotates tokens and revokes the previous refresh token.
- `/auth/logout` revokes the provided refresh token.
- Refresh is rejected for revoked/expired tokens and inactive users.

### Migration and Backfill Notes

- Existing databases created before hashing may still contain plain-text passwords.
- For a clean local migration path, recreate local DB state:

```bash
python scripts/init_db.py
```

- If you need to preserve existing users, backfill by hashing stored passwords before enabling login-only hash verification.

## Authentication Model

- `/auth/login` issues short-lived access token + long-lived refresh token
- refresh token sessions persisted in DB and revocable
- `/auth/refresh` rotates refresh session
- `/auth/logout` revokes refresh token session
- `/auth/me` returns current user profile

## CSV Import and Seeding

Dataset file: `accounting_dataset.csv`

Import behavior (`scripts/import_csv_to_db.py`):

- loads CSV rows
- converts string `None` and empty strings to SQL NULL
- parses date into datetime
- stores amount as decimal
- maps risk incident values into boolean
- maps dataset `User_ID` to generated app users (`dataset_<user_id>`)
- upserts transactions by `Transaction_ID` for rerun safety
- upserts risk profile per transaction

## Setup

Environment expectations:

- Python 3.11+ (tested with Python 3.11)
- Use a fresh local virtual environment (`.venv`) for reproducible setup
- Do not rely on any pre-existing checked-in runtime artifacts

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize DB and seed roles/admin:

```bash
python scripts/init_db.py
```

This creates the four demo login users used for testing:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Analyst | `analyst` | `analyst123` |
| Approver | `approver` | `approver123` |
| Viewer | `viewer` | `viewer123` |

If you want the CSV-backed demo accounts too, run the import step next. That creates `dataset_<user_id>` users with password `changeme`.

4. Import CSV:

```bash
python scripts/import_csv_to_db.py
```

5. Run API:

```bash
python scripts/run.py
```

## Migrations (Alembic)

Use included initial revision:

```bash
alembic upgrade head
```

Create future migration:

```bash
alembic revision --autogenerate -m "your message"
```

## Testing

Run test suite:

```bash
python -m pytest -q
```

Test environment notes:

- Tests use an in-memory SQLite database configured in `tests/conftest.py`.
- The suite is hermetic and does not require `test_finance.db` on disk.
- Always run tests from an environment where `requirements.txt` is installed.

Readiness note:

- If tests fail locally, first verify you are running from a fresh virtual environment and dependencies are installed via `pip install -r requirements.txt`.
- The repository is intended to be evaluated from a clean clone using the smoke-test steps below.

## Smoke Test (Fresh Clone)

Use this checklist to verify setup on a clean machine.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
python scripts/init_db.py
python scripts/import_csv_to_db.py
python scripts/run.py
```

Demo role test checklist:

1. Start the server with `python scripts/run.py`.
2. Log in with each account below against `POST /auth/login`.
3. Confirm the returned access token works with `GET /auth/me`.

Role logins to test:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Analyst | `analyst` | `analyst123` |
| Approver | `approver` | `approver123` |
| Viewer | `viewer` | `viewer123` |

Expected role checks after login:

- Admin: user management, viewer scopes, full visibility, direct transaction fix endpoints.
- Analyst: transaction creation, flags, and change-request submission.
- Approver: review and approve/reject pending requests and flags.
- Viewer: read-only access within assigned scope.

Coverage includes:

- auth login/refresh/logout flow
- RBAC enforcement
- viewer scope restrictions
- transaction filtering
- dashboard aggregation
- update/delete request workflows
- soft-delete behavior
- one-active-delete-request enforcement
- audit log generation

## API Route Overview

- Auth: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`
- Admin Users: `/admin/users/*`
- Viewer Scope: `/admin/viewer-scopes/*`
- Transactions: `/transactions/*`
- Dashboard: `/dashboard/*`
- Change Requests: `/change-requests/*`
- Flags: `/flags/*`
- Audit Logs: `/audit-logs`

Transaction mutation endpoints:

- `PUT /transactions/{transaction_id}` (Admin only): direct update for operational fixes.
- `DELETE /transactions/{transaction_id}` (Admin only): direct soft delete.

## Minimal Frontend

The backend now serves a lightweight demo frontend at:

- `/`

What it includes:

- login form for JWT auth
- one-click API calls for health, current user, dashboard, transactions, flags, change requests, and audit logs
- small forms to create a transaction and submit an update change request
- built-in request/response console so evaluators can see payloads without opening devtools

How to use it:

1. Start the backend with `python scripts/run.py`
2. Open `http://localhost:8000/`
3. Log in with a valid local user such as `admin` / `admin123`

Integration note:

- The frontend is served directly by FastAPI and calls the backend through the same app by default.
- CORS is also enabled for local/demo use in case you want to host the frontend separately later.

## Sample API Payloads

### 1) Login

Request:

```http
POST /auth/login
Content-Type: application/json

{
	"username": "analyst",
	"password": "analyst123"
}
```

Response `200`:

```json
{
	"access_token": "<jwt_access_token>",
	"refresh_token": "<jwt_refresh_token>",
	"token_type": "bearer"
}
```

### 2) Create Transaction (Analyst/Admin)

Request:

```http
POST /transactions
Authorization: Bearer <access_token>
Content-Type: application/json

{
	"transaction_id": "TX-1001",
	"occurred_at": "2025-01-12T10:00:00",
	"account_number": "ACC-100",
	"transaction_type": "Credit",
	"amount": "250.00",
	"currency": "USD",
	"counterparty": "Acme Corp",
	"category": "Sales",
	"notes": "Invoice settlement",
	"payment_method": "Card",
	"owner_user_id": 2
}
```

Response `200`:

```json
{
	"id": 1,
	"transaction_id": "TX-1001",
	"occurred_at": "2025-01-12T10:00:00",
	"account_number": "ACC-100",
	"transaction_type": "Credit",
	"amount": "250.00",
	"currency": "USD",
	"counterparty": "Acme Corp",
	"category": "Sales",
	"notes": "Invoice settlement",
	"payment_method": "Card",
	"owner_user_id": 2,
	"is_deleted": false
}
```

### 3) Submit Update Change Request (Analyst)

Request:

```http
POST /change-requests/update
Authorization: Bearer <access_token>
Content-Type: application/json

{
	"transaction_id": 1,
	"reason": "Normalize category",
	"proposed_changes": {
		"category": "Reconciled",
		"notes": "Updated after reconciliation"
	}
}
```

Response `200`:

```json
{
	"id": 7,
	"transaction_id": 1,
	"request_type": "UPDATE",
	"status": "PENDING",
	"reason": "Normalize category",
	"proposed_changes": {
		"category": "Reconciled",
		"notes": "Updated after reconciliation"
	},
	"requester_user_id": 2,
	"reviewer_user_id": null,
	"created_at": "2025-01-12T10:05:00",
	"reviewed_at": null
}
```

### 4) Review Change Request (Approver)

Request:

```http
POST /change-requests/7/review
Authorization: Bearer <access_token>
Content-Type: application/json

{
	"decision": "APPROVE"
}
```

Response `200`:

```json
{
	"id": 7,
	"transaction_id": 1,
	"request_type": "UPDATE",
	"status": "APPROVED",
	"reason": "Normalize category",
	"proposed_changes": {
		"category": "Reconciled",
		"notes": "Updated after reconciliation"
	},
	"requester_user_id": 2,
	"reviewer_user_id": 3,
	"created_at": "2025-01-12T10:05:00",
	"reviewed_at": "2025-01-12T10:06:00"
}
```

## Service Boundary Guide

Layer ownership reference:

- Routes: authentication dependencies, request parsing, and response envelope formatting only.
- Services: business rules, role/visibility decisions, workflow orchestration, and audit-event decisions.
- Repositories: SQLAlchemy query/data access with no business policy.
- Schemas: API contracts and shared response mapping helpers.
- Helpers: cross-cutting query builders and utility functions reused by services.

Rule examples:

- Analyst visibility limits and viewer scope enforcement are service responsibilities.
- Pagination and filtering query composition is repository/helper responsibility.
- Endpoint-specific status code and payload shape are route responsibilities.

## Assumptions and Tradeoffs

- SQLite chosen for portability and local take-home evaluation.
- Risk metadata is persisted but excluded from dashboard aggregates.
- Access token expiry is short; refresh token persistence enables revocation.
- Service layer keeps routes thin and allows future scaling.

## Known Limitations

- This project currently uses SQLite; production deployments should use a managed RDBMS (for example PostgreSQL).
- API examples are representative and may differ in generated IDs/timestamps.
- Some extension features (risk profile ingestion and advanced viewer scope combinations) are intentionally lightweight for take-home scope.
- The included default admin credentials are for local development only and should be replaced immediately in any shared environment.
