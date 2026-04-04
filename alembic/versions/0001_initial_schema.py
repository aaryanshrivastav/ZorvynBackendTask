"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-04
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_role_status", "users", ["role_id", "status"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.String(length=50), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("account_number", sa.String(length=50), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("counterparty", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["deleted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )
    op.create_index("ix_transactions_active_occurred", "transactions", ["is_deleted", "occurred_at"])
    op.create_index("ix_transactions_active_owner", "transactions", ["is_deleted", "owner_user_id"])

    op.create_table(
        "viewer_access_scopes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("viewer_user_id", sa.Integer(), nullable=False),
        sa.Column("scope_type", sa.String(length=20), nullable=False),
        sa.Column("scoped_user_id", sa.Integer(), nullable=True),
        sa.Column("account_number", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["scoped_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["viewer_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint("scope_type IN ('USER','ACCOUNT')", name="ck_viewer_scope_type"),
        sa.CheckConstraint(
            "(scope_type = 'USER' AND scoped_user_id IS NOT NULL AND account_number IS NULL) OR "
            "(scope_type = 'ACCOUNT' AND account_number IS NOT NULL AND scoped_user_id IS NULL)",
            name="ck_viewer_scope_mapping",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("viewer_user_id", "scope_type", "scoped_user_id", "account_number", name="uq_viewer_scope_unique"),
    )
    op.create_index("ix_viewer_scope_lookup", "viewer_access_scopes", ["viewer_user_id", "scope_type"])

    op.create_table(
        "transaction_risk_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("risk_incident", sa.Boolean(), nullable=False),
        sa.Column("risk_type", sa.String(length=50), nullable=True),
        sa.Column("incident_severity", sa.String(length=50), nullable=True),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("system_latency", sa.Float(), nullable=True),
        sa.Column("login_frequency", sa.Integer(), nullable=True),
        sa.Column("failed_attempts", sa.Integer(), nullable=True),
        sa.Column("ip_region", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )

    op.create_table(
        "record_change_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("request_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("proposed_changes", sa.JSON(), nullable=True),
        sa.Column("requester_user_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_user_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["requester_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"),
        sa.CheckConstraint("request_type IN ('UPDATE','DELETE')", name="ck_change_request_type"),
        sa.CheckConstraint("status IN ('PENDING','APPROVED','REJECTED')", name="ck_change_request_status"),
        sa.CheckConstraint("length(trim(reason)) > 0", name="ck_change_request_reason_required"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_change_requests_pending", "record_change_requests", ["status", "request_type", "transaction_id"])
    op.create_index(
        "uq_active_delete_request_per_txn",
        "record_change_requests",
        ["transaction_id"],
        unique=True,
        sqlite_where=sa.text("request_type = 'DELETE' AND status = 'PENDING'"),
    )

    op.create_table(
        "flags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_flags_transaction_status", "flags", ["transaction_id", "status"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource_type", sa.String(length=120), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("result", sa.String(length=30), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_actor_action_time", "audit_logs", ["actor_user_id", "action", "created_at"])

    op.create_table(
        "refresh_token_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_id", sa.String(length=64), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_id"),
    )
    op.create_index("ix_refresh_tokens_user_active", "refresh_token_sessions", ["user_id", "is_revoked", "expires_at"])


def downgrade() -> None:
    op.drop_table("refresh_token_sessions")
    op.drop_table("audit_logs")
    op.drop_table("flags")
    op.drop_table("record_change_requests")
    op.drop_table("transaction_risk_profiles")
    op.drop_table("viewer_access_scopes")
    op.drop_table("transactions")
    op.drop_table("users")
    op.drop_table("roles")
