"""T2.10 status ARCHIVED + T7.5 quota/usage + T7.6 gateway config.

Revision ID: 0002_lifecycle_usage_gateway
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_lifecycle_usage_gateway"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE documents DROP CONSTRAINT IF EXISTS ck_documents_status")
        op.execute("ALTER TABLE documents ADD CONSTRAINT ck_documents_status "
                   "CHECK (status IN ('PARSING','VECTORIZING','READY','FAILED','ARCHIVED'))")
    # sqlite: CHECK enforced only for new tables via create_all; existing dev DBs
    # accept ARCHIVED at the application layer (validated in API).
    op.add_column("users", sa.Column("quota_queries", sa.Integer(), nullable=True))
    op.create_table(
        "llm_usage",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), index=True),
        sa.Column("provider", sa.String(30), server_default=""),
        sa.Column("model", sa.String(100), server_default=""),
        sa.Column("ok", sa.Boolean(), server_default="true"),
        sa.Column("latency_ms", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "gateway_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("primary_model", sa.String(100), server_default="gpt-4o"),
        sa.Column("fallback_model", sa.String(100), server_default="anthropic/claude-sonnet-4.5"),
        sa.Column("timeout_s", sa.Integer(), server_default="45"),
        sa.Column("max_retries", sa.Integer(), server_default="1"),
        sa.Column("provider_order", sa.String(100), server_default="openrouter,openai"),
        sa.Column("updated_by", sa.String(200), server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("gateway_config")
    op.drop_table("llm_usage")
    op.drop_column("users", "quota_queries")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE documents DROP CONSTRAINT IF EXISTS ck_documents_status")
        op.execute("ALTER TABLE documents ADD CONSTRAINT ck_documents_status "
                   "CHECK (status IN ('PARSING','VECTORIZING','READY','FAILED'))")
