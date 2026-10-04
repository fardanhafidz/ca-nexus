"""DEL-B2 — relation typo fix + relation check constraint.

Revision ID: 0003_edge_relation
Per-edge revision/access columns deferred (see docs/SLICE.md): edges carry
evidence_doc references; fine-grained revision tracking is out of slice-1.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_edge_relation"
down_revision = "0002_lifecycle_usage_gateway"
branch_labels = None
depends_on = None

RELATIONS = "('HAS_INTERLOCK','HAS_INSTRUMENT','HAS_OPL','HAS_WO','PROTECTS')"


def upgrade() -> None:
    op.execute("UPDATE knowledge_edges SET relation='HAS_INSTRUMENT' WHERE relation='HAS_INSTRUMENT'")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE knowledge_edges DROP CONSTRAINT IF EXISTS ck_edges_relation")
        op.execute(f"ALTER TABLE knowledge_edges ADD CONSTRAINT ck_edges_relation CHECK (relation IN {RELATIONS})")
    # sqlite: constraint applies to new tables via create_all; existing dev DBs
    # get the typo row fix above (portable UPDATE).


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE knowledge_edges DROP CONSTRAINT IF EXISTS ck_edges_relation")
