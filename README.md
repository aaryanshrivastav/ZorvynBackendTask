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

## Authentication Model

- `/auth/login` issues short-lived access token + long-lived refresh token
- refresh token sessions persisted in DB and revocable
- `/auth/refresh` rotates refresh session
- `/auth/logout` revokes refresh token session
- `/auth/me` returns current user profile

Note: password hashing is intentionally deferred in this phase. Passwords are stored as plain text temporarily to preserve the requested contract, and auth code is modular so hashing can be added later without API changes.

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

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize DB and seed roles/admin:

```bash
python scripts/init_db.py
```

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
pytest -q
```

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

## Assumptions and Tradeoffs

- SQLite chosen for portability and local take-home evaluation.
- Risk metadata is persisted but excluded from dashboard aggregates.
- Access token expiry is short; refresh token persistence enables revocation.
- Service layer keeps routes thin and allows future scaling.