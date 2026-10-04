import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, Integer, func, ForeignKey, CheckConstraint, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB
    PayloadJSON = JSONB().with_variant(JSON(), "sqlite")  # PG JSONB, portable fallback
except Exception:  # pragma: no cover
    PayloadJSON = JSON()


def uid() -> str:
    return str(uuid.uuid4())


class MaintenanceRecord(Base):
    """31 columns, snake_case normalized from workbook header (verified 211 rows — docs/AUDIT.md)."""
    __tablename__ = "maintenance_records"
    wo_number: Mapped[str] = mapped_column(String(50), primary_key=True)
    notification_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    report_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    equipment_tag: Mapped[str | None] = mapped_column(String(30), index=True, nullable=True)
    equipment_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    functional_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    area_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    plant: Mapped[str | None] = mapped_column(String(200), nullable=True)
    work_type: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    discipline: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    priority: Mapped[str | None] = mapped_column(String(30), nullable=True)
    criticality: Mapped[str | None] = mapped_column(String(50), nullable=True)
    problem_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    spare_parts_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    breakdown: Mapped[str | None] = mapped_column(String(10), nullable=True)
    downtime_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    labor_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    labor_cost_idr: Mapped[float | None] = mapped_column(Float, nullable=True)
    material_cost_idr: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_cost_idr: Mapped[float | None] = mapped_column(Float, nullable=True)
    reported_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    executed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    related_interlock: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)


class ImportBatch(Base):
    """Lineage per import run (T2.3): workbook/sheet/sha + accepted/rejected counts."""
    __tablename__ = "import_batches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(500), default="")
    sheet: Mapped[str] = mapped_column(String(200), default="")
    sha256: Mapped[str] = mapped_column(String(64), default="")
    mode: Mapped[str] = mapped_column(String(20), default="upsert")
    accepted: Mapped[int] = mapped_column(Integer, default=0)
    rejected: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(300), default="New session")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # user|assistant
    text: Mapped[str] = mapped_column(Text, default="")
    payload_json = mapped_column(PayloadJSON, nullable=True)  # structured answer as JSON (single-encoded)
    schema_version: Mapped[str] = mapped_column(String(20), default="v1")
    status: Mapped[str] = mapped_column(String(20), default="complete")  # queued|generating|complete|failed
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("status IN ('PARSING','VECTORIZING','READY','FAILED','ARCHIVED')", name="ck_documents_status"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    equipment_tag: Mapped[str] = mapped_column(String(30), index=True, default="")
    doc_type: Mapped[str] = mapped_column(String(50), default="opl")  # opl|datasheet|drawing|interlock|plot_plan|pid|other
    doc_title: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[str] = mapped_column(String(800))  # relative to storage root, registry-only
    division_access: Mapped[str] = mapped_column(String(500), default="All")  # comma list or All
    access_reviewed: Mapped[bool] = mapped_column(default=False)  # False = filename-guess/UNREVIEWED (T2.4)
    version: Mapped[str] = mapped_column(String(20), default="v1.0.0")
    status: Mapped[str] = mapped_column(String(20), default="READY")  # PARSING|VECTORIZING|READY|FAILED
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    checksum: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class KnowledgeEdge(Base):
    """Relational graph: Equipment -> Interlock -> Instrument -> Document (Q-GRF-01..05)."""
    __tablename__ = "knowledge_edges"
    __table_args__ = (
        CheckConstraint(
            "relation IN ('HAS_INTERLOCK','HAS_INSTRUMENT','HAS_OPL','HAS_WO','PROTECTS')",
            name="ck_edges_relation"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    src_tag: Mapped[str] = mapped_column(String(50), index=True)
    dst_tag: Mapped[str] = mapped_column(String(500), index=True)  # DEL-V1 PG find: titles exceed 50 chars
    relation: Mapped[str] = mapped_column(String(50))  # see ck_edges_relation
    evidence_doc: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor: Mapped[str] = mapped_column(String(200), default="")
    action: Mapped[str] = mapped_column(String(100), default="chat.ask")
    user_name: Mapped[str] = mapped_column(String(200), default="")
    division: Mapped[str] = mapped_column(String(100), default="")
    equipment_tag: Mapped[str] = mapped_column(String(50), default="")
    query: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="ok")
    ref_id: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LLMUsage(Base):
    """T7.5 — persisted per-answer provider usage (cost estimated from docs/PRICING.md rates)."""
    __tablename__ = "llm_usage"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"),
                                         nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(30), default="")
    model: Mapped[str] = mapped_column(String(100), default="")
    ok: Mapped[bool] = mapped_column(default=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GatewayConfig(Base):
    """T7.6 — singleton runtime gateway config (id=1). Env vars stay authoritative for keys."""
    __tablename__ = "gateway_config"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    primary_model: Mapped[str] = mapped_column(String(100), default="gpt-4o")
    fallback_model: Mapped[str] = mapped_column(String(100), default="anthropic/claude-sonnet-4.5")
    timeout_s: Mapped[int] = mapped_column(Integer, default=45)
    max_retries: Mapped[int] = mapped_column(Integer, default=1)
    provider_order: Mapped[str] = mapped_column(String(100), default="openrouter,openai")
    updated_by: Mapped[str] = mapped_column(String(200), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())


class IdempotencyKey(Base):
    """DEL-B6 (T5.3): retry-safe POST /ask. Repeats of an Idempotency-Key within
    24h return the stored answer without duplicating messages."""
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_idem_user_key"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(100))
    session_id: Mapped[str] = mapped_column(String(36), default="")
    answer_json = mapped_column(PayloadJSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IngestionJob(Base):
    """T2.9/T7.2: tracked ingestion job (replaces bare BackgroundTasks).
    Stages: QUEUED → PARSING → VECTORIZING → READY | FAILED | CANCELLED.
    Cancel is cooperative: the worker checks the flag between stages."""
    __tablename__ = "ingestion_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), index=True)
    actor: Mapped[str] = mapped_column(String(200), default="")
    stage: Mapped[str] = mapped_column(String(20), default="QUEUED")
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0..100
    total_chunks: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                  onupdate=func.now())
