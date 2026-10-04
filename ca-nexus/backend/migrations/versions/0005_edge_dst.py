"""DEL-V1 PG find — dst_tag 50 chars too short for document titles in HAS_OPL edges.

Revision ID: 0005_edge_dst
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_edge_dst"
down_revision = "0004_idempotency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column("knowledge_edges", "dst_tag", type_=sa.String(500),
                        existing_type=sa.String(50))
    # sqlite: applies via create_all for new databases.


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column("knowledge_edges", "dst_tag", type_=sa.String(50),
                        existing_type=sa.String(500))
