"""T2.9/T7.2 — tracked ingestion jobs (replaces bare BackgroundTasks).

Revision ID: 0006_jobs
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_jobs"
down_revision = "0005_edge_dst"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), index=True),
        sa.Column("actor", sa.String(200), server_default=""),
        sa.Column("stage", sa.String(20), server_default="QUEUED"),
        sa.Column("progress", sa.Integer(), server_default="0"),
        sa.Column("total_chunks", sa.Integer(), server_default="0"),
        sa.Column("error", sa.Text(), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ingestion_jobs")
