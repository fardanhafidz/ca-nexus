"""DEL-B6 (T5.3 second half) — idempotency_keys store.

Revision ID: 0004_idempotency
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_idempotency"
down_revision = "0003_edge_relation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    JSON_T = postgresql.JSONB().with_variant(sa.JSON(), "sqlite")
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("key", sa.String(100)),
        sa.Column("session_id", sa.String(36), server_default=""),
        sa.Column("answer_json", JSON_T),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "key", name="uq_idem_user_key"),
    )


def downgrade() -> None:
    op.drop_table("idempotency_keys")
