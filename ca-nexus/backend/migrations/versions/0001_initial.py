"""T1.5 initial revision — mirrors models (users/divisions/blocklist/maintenance/import_batches/chat/documents/edges/audit).

Revision ID: 0001_initial
Run: alembic upgrade head   (DATABASE_URL picked from env)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

JSON_T = postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("employee_id", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("email", sa.String(200), nullable=False, unique=True, index=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("division", sa.String(100), nullable=False, server_default="Mechanical"),
        sa.Column("division_requested", sa.String(100), nullable=False, server_default="Mechanical"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('super_admin','admin','user')", name="ck_users_role"),
        sa.CheckConstraint("status IN ('pending','approved','rejected','disabled')", name="ck_users_status"),
        sa.CheckConstraint("division IN ('Mechanical','Electrical & Instrumentation','Process / Operations','HSE & Reliability')", name="ck_users_division"),
    )
    op.create_table("divisions", sa.Column("name", sa.String(100), primary_key=True))
    op.create_table("token_blocklist",
        sa.Column("jti", sa.String(64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table(
        "maintenance_records",
        sa.Column("wo_number", sa.String(50), primary_key=True),
        sa.Column("notification_no", sa.String(50)), sa.Column("report_date", sa.DateTime(timezone=True)),
        sa.Column("start_date", sa.DateTime(timezone=True)), sa.Column("completion_date", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(30)), sa.Column("equipment_tag", sa.String(30), index=True),
        sa.Column("equipment_name", sa.String(200)), sa.Column("functional_location", sa.String(100)),
        sa.Column("area_code", sa.String(30)), sa.Column("area_name", sa.String(200)), sa.Column("plant", sa.String(200)),
        sa.Column("work_type", sa.String(50), index=True), sa.Column("discipline", sa.String(50), index=True),
        sa.Column("priority", sa.String(30)), sa.Column("criticality", sa.String(50)),
        sa.Column("problem_description", sa.Text()), sa.Column("root_cause", sa.Text()),
        sa.Column("corrective_action", sa.Text()), sa.Column("spare_parts_used", sa.Text()),
        sa.Column("breakdown", sa.String(10)), sa.Column("downtime_hours", sa.Float()),
        sa.Column("labor_hours", sa.Float()), sa.Column("labor_cost_idr", sa.Float()),
        sa.Column("material_cost_idr", sa.Float()), sa.Column("total_cost_idr", sa.Float()),
        sa.Column("reported_by", sa.String(200)), sa.Column("executed_by", sa.String(200)),
        sa.Column("approved_by", sa.String(200)), sa.Column("related_interlock", sa.String(50), index=True),
        sa.Column("remarks", sa.Text()),
    )
    op.create_table(
        "import_batches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source", sa.String(500), server_default=""), sa.Column("sheet", sa.String(200), server_default=""),
        sa.Column("sha256", sa.String(64), server_default=""), sa.Column("mode", sa.String(20), server_default="upsert"),
        sa.Column("accepted", sa.Integer(), server_default="0"), sa.Column("rejected", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("title", sa.String(300), server_default="New session"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("role", sa.String(20), nullable=False), sa.Column("text", sa.Text(), server_default=""),
        sa.Column("payload_json", JSON_T), sa.Column("schema_version", sa.String(20), server_default="v1"),
        sa.Column("status", sa.String(20), server_default="complete"),
        sa.Column("attachment_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("equipment_tag", sa.String(30), index=True, server_default=""),
        sa.Column("doc_type", sa.String(50), server_default="opl"), sa.Column("doc_title", sa.String(500)),
        sa.Column("file_path", sa.String(800)), sa.Column("division_access", sa.String(500), server_default="All"),
        sa.Column("access_reviewed", sa.Boolean(), server_default="false"),
        sa.Column("version", sa.String(20), server_default="v1.0.0"),
        sa.Column("status", sa.String(20), server_default="READY"),
        sa.Column("page_count", sa.Integer(), server_default="0"), sa.Column("checksum", sa.String(64), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('PARSING','VECTORIZING','READY','FAILED')", name="ck_documents_status"),
    )
    op.create_table(
        "knowledge_edges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("src_tag", sa.String(50), index=True), sa.Column("dst_tag", sa.String(50), index=True),
        sa.Column("relation", sa.String(50)), sa.Column("evidence_doc", sa.String(500), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor", sa.String(200), server_default=""), sa.Column("action", sa.String(100), server_default="chat.ask"),
        sa.Column("user_name", sa.String(200), server_default=""), sa.Column("division", sa.String(100), server_default=""),
        sa.Column("equipment_tag", sa.String(50), server_default=""), sa.Column("query", sa.Text(), server_default=""),
        sa.Column("status", sa.String(20), server_default="ok"), sa.Column("ref_id", sa.String(100), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for t in ("audit_logs", "knowledge_edges", "documents", "chat_messages", "chat_sessions",
              "import_batches", "maintenance_records", "token_blocklist", "divisions", "users"):
        op.drop_table(t)
