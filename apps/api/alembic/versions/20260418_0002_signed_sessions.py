"""signed sessions

Revision ID: 20260418_0002
Revises: 20260418_0001
Create Date: 2026-04-18
"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260418_0002"
down_revision: Union[str, None] = "20260418_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("app_id", sa.String(length=36), nullable=False),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column("end_user_ref", sa.String(length=255), nullable=False),
        sa.Column("tenant_ref", sa.String(length=255), nullable=True),
        sa.Column("roles", sa.JSON(), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["app_id"], ["apps.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token_hash"),
    )
    op.create_index(op.f("ix_app_sessions_app_id"), "app_sessions", ["app_id"], unique=False)
    op.create_index(
        op.f("ix_app_sessions_end_user_ref"),
        "app_sessions",
        ["end_user_ref"],
        unique=False,
    )
    op.create_index(
        op.f("ix_app_sessions_expires_at"),
        "app_sessions",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_app_sessions_session_token_hash"),
        "app_sessions",
        ["session_token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_app_sessions_tenant_ref"),
        "app_sessions",
        ["tenant_ref"],
        unique=False,
    )

    with op.batch_alter_table("runs") as batch_op:
        batch_op.add_column(sa.Column("session_id", sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column("tenant_ref", sa.String(length=255), nullable=True))
        batch_op.create_foreign_key(
            "fk_runs_session_id_app_sessions",
            "app_sessions",
            ["session_id"],
            ["id"],
        )
        batch_op.create_index("ix_runs_session_id", ["session_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("runs") as batch_op:
        batch_op.drop_index("ix_runs_session_id")
        batch_op.drop_constraint("fk_runs_session_id_app_sessions", type_="foreignkey")
        batch_op.drop_column("tenant_ref")
        batch_op.drop_column("session_id")

    op.drop_index(op.f("ix_app_sessions_tenant_ref"), table_name="app_sessions")
    op.drop_index(op.f("ix_app_sessions_session_token_hash"), table_name="app_sessions")
    op.drop_index(op.f("ix_app_sessions_expires_at"), table_name="app_sessions")
    op.drop_index(op.f("ix_app_sessions_end_user_ref"), table_name="app_sessions")
    op.drop_index(op.f("ix_app_sessions_app_id"), table_name="app_sessions")
    op.drop_table("app_sessions")
