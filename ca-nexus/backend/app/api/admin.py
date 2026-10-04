import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pathlib import Path
import shutil, uuid
from ..core.database import get_db
from ..core.deps import get_current_user, require_role
from ..core.config import settings, DIVISIONS
from ..models.maintenance import Document, AuditLog, KnowledgeEdge, GatewayConfig, LLMUsage, IngestionJob
from ..models.user import User
from ..services import pipeline, vector_service
from ..services import llm_gateway

log = logging.getLogger("mkh.admin")
router = APIRouter(prefix="/admin", tags=["admin"])
STORE = Path(settings.FILE_STORAGE_ROOT)
admin_only = require_role("admin", "super_admin")
super_only = require_role("super_admin")


def _audit(db: Session, user: User, action: str, status: str = "ok", ref_id: str = "", query: str = "") -> None:
    db.add(AuditLog(actor=user.email, action=action, user_name=user.full_name,
                    division=user.division, status=status, ref_id=ref_id, query=query[:1000]))


@router.get("/users")
def list_users(status: str = "", db: Session = Depends(get_db), user=Depends(admin_only)):
    q = db.query(User).order_by(User.created_at.desc())
    if status:
        if status not in ("pending", "approved", "rejected", "disabled"):
            raise HTTPException(400, "Unknown status")
        q = q.filter(User.status == status)
    return [{"id": u.id, "full_name": u.full_name, "employee_id": u.employee_id,
             "email": u.email, "role": u.role, "division": u.division,
             "division_requested": u.division_requested, "status": u.status} for u in q.limit(500).all()]


@router.get("/users/{uid}")
def user_detail(uid: str, db: Session = Depends(get_db), user=Depends(admin_only)):
    u = db.get(User, uid)
    if not u:
        raise HTTPException(404, "User not found")
    return {"id": u.id, "full_name": u.full_name, "employee_id": u.employee_id,
            "email": u.email, "role": u.role, "division": u.division,
            "division_requested": u.division_requested, "status": u.status,
            "created_at": str(u.created_at)}


_VALID_TRANSITIONS = {
    "pending": {"approved", "rejected"},
    "approved": {"disabled", "approved"},
    "rejected": {"pending"},
    "disabled": {"approved"},
}


def _apply_transition(db: Session, actor: User, target: User, status: str,
                      division: str = "", role: str = "") -> dict:
    if status != target.status and status not in _VALID_TRANSITIONS.get(target.status, set()):
        raise HTTPException(400, f"Illegal transition {target.status} -> {status}")
    if division:
        if division not in DIVISIONS:
            raise HTTPException(400, "Unknown division")
        target.division = division
    elif status == "approved" and target.status == "pending":
        target.division = target.division_requested  # T7.1: alokasi divisi saat approve
    if role:
        if actor.role != "super_admin":
            raise HTTPException(403, "Only Super Admin may change roles")
        if role not in ("admin", "user", "super_admin"):
            raise HTTPException(400, "Unknown role")
        if target.id == actor.id:
            raise HTTPException(400, "Cannot change own role")
        target.role = role
    target.status = status
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Conflicting concurrent update — please retry")
    _audit(db, actor, f"admin.user.{status}", ref_id=target.id)
    db.commit()
    return {"ok": True, "status": target.status, "division": target.division, "role": target.role}


@router.post("/users/{uid}/approve")
def approve(uid: str, body: dict | None = None, division: str = "",
            db: Session = Depends(get_db), user=Depends(admin_only)):
    u = db.get(User, uid)
    if not u:
        raise HTTPException(404, "User not found")
    div = (body or {}).get("division", division) if body is not None else division
    return _apply_transition(db, user, u, "approved", division=div or "")


@router.post("/users/{uid}/reject")
def reject(uid: str, db: Session = Depends(get_db), user=Depends(admin_only)):
    u = db.get(User, uid)
    if not u:
        raise HTTPException(404, "User not found")
    return _apply_transition(db, user, u, "rejected")


@router.post("/users/{uid}/status")
def set_status(uid: str, body: dict, db: Session = Depends(get_db), user=Depends(admin_only)):
    u = db.get(User, uid)
    if not u:
        raise HTTPException(404, "User not found")
    return _apply_transition(db, user, u, body.get("status", ""),
                             division=body.get("division", ""), role=body.get("role", ""))


@router.post("/users/bulk")
def bulk(body: dict, db: Session = Depends(get_db), user=Depends(admin_only)):
    ids = body.get("ids", [])[:100]
    out = []
    for uid in ids:
        u = db.get(User, uid)
        if not u:
            out.append({"id": uid, "ok": False, "error": "not found"})
            continue
        try:
            out.append({"id": uid, **_apply_transition(
                db, user, u, body.get("status", ""),
                division=body.get("division", ""), role=body.get("role", ""))})
        except HTTPException as e:
            db.rollback()
            out.append({"id": uid, "ok": False, "error": e.detail})
    return {"results": out}


@router.get("/documents")
def admin_docs(db: Session = Depends(get_db), user=Depends(admin_only)):
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(500).all()
    return [{"id": d.id, "doc_title": d.doc_title, "equipment_tag": d.equipment_tag,
             "doc_type": d.doc_type, "status": d.status, "version": d.version,
             "division_access": d.division_access, "access_reviewed": d.access_reviewed,
             "page_count": d.page_count} for d in docs]


@router.post("/upload")
async def upload(bt: BackgroundTasks, file: UploadFile = File(...),
                 equipment_tag: str = Form(""), doc_type: str = Form("other"),
                 division_access: str = Form("All"),
                 db: Session = Depends(get_db), user=Depends(admin_only)):
    name = file.filename or ""
    if not name.lower().endswith((".pdf", ".png")):
        raise HTTPException(400, "Supported here: PDF, PNG. Workbook XLSX goes via seed_maintenance (T2.3).")
    STORE.mkdir(parents=True, exist_ok=True)
    rel = f"uploads/{uuid.uuid4().hex}_{Path(name).name}"
    dest = STORE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    if division_access not in DIVISIONS and division_access != "All":
        raise HTTPException(400, "Unknown division_access")
    d = Document(equipment_tag=equipment_tag.upper(), doc_type=doc_type, doc_title=Path(name).name,
                 file_path=rel, division_access=division_access, access_reviewed=True,
                 version="v1.0.0", status="PARSING",
                 checksum=pipeline.checksum_of(dest))
    db.add(d)
    db.commit()
    job = IngestionJob(document_id=d.id, actor=user.email, stage="QUEUED", progress=0)
    db.add(job)
    db.commit()
    _audit(db, user, "admin.upload", ref_id=d.id, query=name)
    db.commit()
    bt.add_task(_ingest_one, str(d.id), str(job.id))
    return {"id": d.id, "status": d.status, "job_id": job.id}


def _job_set(db, job_id: str, stage: str, progress: int, error: str = "") -> bool:
    """Returns False when the job was cancelled (worker must stop)."""
    job = db.get(IngestionJob, job_id) if job_id else None
    if job is None:
        return True
    if job.stage == "CANCELLED":
        return False
    job.stage, job.progress, job.error = stage, progress, error[:1000]
    db.commit()
    return True


def _ingest_one(doc_id: str, job_id: str = ""):
    """Same unified pipeline as the CLI (T2.9) — no divergent logic.
    Progress + cooperative cancel via ingestion_jobs (T2.9/T7.2)."""
    from ..core.database import SessionLocal
    db = SessionLocal()
    try:
        d = db.get(Document, doc_id)
        if not d:
            return
        if not _job_set(db, job_id, "PARSING", 10):
            return
        d.status = "PARSING"
        db.commit()
        fp = STORE / d.file_path
        vector_service.ensure_collection()
        if fp.suffix.lower() == ".pdf":
            chunks, report = pipeline.prepare_pdf(fp, d.checksum or pipeline.checksum_of(fp),
                                                  max_chunks=400)  # cost bound, overflow reported
        else:
            chunks, report = pipeline.prepare_png_with_vision(fp, d.checksum or pipeline.checksum_of(fp))
        d.page_count = report["pages"]
        db.commit()
        if not _job_set(db, job_id, "VECTORIZING", 40):
            d.status = "FAILED"
            db.commit()
            return
        d.status = "VECTORIZING"
        db.commit()
        n = pipeline.upsert_chunks(chunks, {"equipment_tag": d.equipment_tag, "doc_type": d.doc_type,
                                            "doc_title": d.doc_title, "division_access": d.division_access,
                                            "file_path": d.file_path})
        if not _job_set(db, job_id, "READY", 100):
            return
        d.status = "READY"
        db.commit()
        if job_id:
            job = db.get(IngestionJob, job_id)
            if job:
                job.total_chunks = n
                db.commit()
    except Exception as e:
        log.exception("ingestion failed for %s", doc_id)
        try:
            db.rollback()
            d = db.get(Document, doc_id)
            if d:
                d.status = "FAILED"
                db.commit()
            _job_set(db, job_id, "FAILED", 0, str(e))
        except Exception:
            log.exception("failed to mark FAILED")
    finally:
        db.close()


@router.get("/jobs")
def list_jobs(limit: int = 50, offset: int = 0,
              db: Session = Depends(get_db), user=Depends(admin_only)):
    q = db.query(IngestionJob).order_by(IngestionJob.created_at.desc())
    total = q.count()
    rows = q.offset(min(offset, 10000)).limit(min(limit, 200)).all()
    return {"total": total, "items": [
        {"id": j.id, "document_id": j.document_id, "actor": j.actor,
         "stage": j.stage, "progress": j.progress, "total_chunks": j.total_chunks,
         "error": j.error, "created_at": str(j.created_at)} for j in rows]}


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str, db: Session = Depends(get_db), user=Depends(admin_only)):
    j = db.get(IngestionJob, job_id)
    if not j:
        raise HTTPException(404, "Job not found")
    if j.stage in ("READY", "FAILED", "CANCELLED"):
        raise HTTPException(400, f"Job already {j.stage}")
    j.stage = "CANCELLED"
    _audit(db, user, "admin.job.cancel", ref_id=j.id)
    db.commit()
    return {"id": j.id, "stage": j.stage}


@router.post("/jobs/{job_id}/retry")
def retry_job(bt: BackgroundTasks, job_id: str,
              db: Session = Depends(get_db), user=Depends(admin_only)):
    j = db.get(IngestionJob, job_id)
    if not j:
        raise HTTPException(404, "Job not found")
    if j.stage not in ("FAILED", "CANCELLED"):
        raise HTTPException(400, f"Only FAILED/CANCELLED jobs can be retried (stage={j.stage})")
    d = db.get(Document, j.document_id)
    if not d:
        raise HTTPException(404, "Document gone — re-upload instead")
    j.stage, j.progress, j.error = "QUEUED", 0, ""
    db.commit()
    _audit(db, user, "admin.job.retry", ref_id=j.id)
    db.commit()
    bt.add_task(_ingest_one, str(d.id), str(j.id))
    return {"id": j.id, "stage": j.stage}


@router.get("/audit")
def audit(action: str = "", limit: int = 50, offset: int = 0,
          db: Session = Depends(get_db), user=Depends(admin_only)):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        q = q.filter(AuditLog.action == action)
    total = q.count()
    rows = q.offset(min(offset, 10000)).limit(min(limit, 200)).all()
    return {"total": total, "items": [
        {"id": r.id, "actor": r.actor, "action": r.action, "user_name": r.user_name,
         "division": r.division, "equipment_tag": r.equipment_tag, "status": r.status,
         "ref_id": r.ref_id, "created_at": str(r.created_at)} for r in rows]}


@router.get("/stats")
def stats(db: Session = Depends(get_db), user=Depends(admin_only)):
    total = db.query(User).count()
    pending = db.query(User).filter(User.status == "pending").count()
    docs = db.query(Document).count()
    return {"total_users": total, "pending_users": pending, "total_documents": docs,
            "llm_primary": llm_gateway.effective()["primary_model"],
            "qdrant": settings.QDRANT_PUBLIC_URL,
            "llm_recent": llm_gateway.USAGE[-20:],
            "usage_30d": _usage_summary(db, 30)}


# ---------------------------------------------------------------- T2.10 lifecycle

def _bump_version(v: str) -> str:
    import re
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", (v or "").strip())
    if not m:
        return "v1.0.0"
    major, minor, patch = map(int, m.groups())
    return f"v{major}.{minor}.{patch + 1}"


def _delete_qdrant_points(file_path: str) -> int:
    """Remove all points indexed from a file. Best-effort: returns removed count."""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        qc = QdrantClient(url=settings.QDRANT_URL)
        removed = 0
        while True:
            batch, _ = qc.scroll(settings.QDRANT_COLLECTION,
                                 scroll_filter=Filter(must=[FieldCondition(
                                     key="file_path", match=MatchValue(value=file_path))]),
                                 limit=256, with_payload=False, with_vectors=False)
            if not batch:
                break
            qc.delete(settings.QDRANT_COLLECTION, points_selector=[p.id for p in batch])
            removed += len(batch)
            if len(batch) < 256:
                break
        return removed
    except Exception:
        log.exception("qdrant point deletion failed for %s", file_path)
        return 0


@router.post("/documents/{doc_id}/archive")
def archive_doc(doc_id: str, db: Session = Depends(get_db), user=Depends(admin_only)):
    d = db.get(Document, doc_id)
    if not d:
        raise HTTPException(404, "Document not found")
    # Release-blocker fix (T2.10): archived points must not stay searchable.
    # Same purge as delete; registry row kept so history/citations resolve honestly.
    points = _delete_qdrant_points(d.file_path)
    d.status = "ARCHIVED"
    _audit(db, user, "admin.doc.archive", ref_id=d.id,
           query=f"{d.doc_title} points_removed={points}")
    db.commit()
    return {"id": d.id, "status": d.status, "points_removed": points}


@router.post("/documents/{doc_id}/delete")
def delete_doc(doc_id: str, db: Session = Depends(get_db), user=Depends(admin_only)):
    d = db.get(Document, doc_id)
    if not d:
        raise HTTPException(404, "Document not found")
    points = _delete_qdrant_points(d.file_path)
    db.query(KnowledgeEdge).filter(KnowledgeEdge.evidence_doc == d.doc_title).delete()
    db.query(KnowledgeEdge).filter(KnowledgeEdge.evidence_doc.like(f"{d.doc_title}:%")).delete()
    fp = STORE / d.file_path
    if not Path(d.file_path).is_absolute() and ".." not in Path(d.file_path).parts and fp.exists():
        try:
            fp.unlink()
        except OSError:
            log.exception("file delete failed for %s", d.file_path)
    _audit(db, user, "admin.doc.delete", ref_id=doc_id,
           query=f"{d.doc_title} points_removed={points}")
    db.delete(d)
    db.commit()
    return {"ok": True, "points_removed": points}


@router.post("/documents/{doc_id}/replace")
async def replace_doc(doc_id: str, bt: BackgroundTasks, file: UploadFile = File(...),
                      db: Session = Depends(get_db), user=Depends(admin_only)):
    d = db.get(Document, doc_id)
    if not d:
        raise HTTPException(404, "Document not found")
    name = (file.filename or "").lower()
    if not name.endswith((".pdf", ".png")):
        raise HTTPException(400, "Supported: PDF, PNG")
    _delete_qdrant_points(d.file_path)
    # DEL-B5: replace cleans stale graph evidence like delete does (rebuilt on re-ingest)
    db.query(KnowledgeEdge).filter(KnowledgeEdge.evidence_doc == d.doc_title).delete()
    db.query(KnowledgeEdge).filter(KnowledgeEdge.evidence_doc.like(f"{d.doc_title}:%")).delete()
    rel = f"uploads/{uuid.uuid4().hex}_{Path(file.filename or 'doc').name}"
    dest = STORE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    d.file_path = rel
    d.checksum = pipeline.checksum_of(dest)
    d.version = _bump_version(d.version)
    d.status = "PARSING"
    d.page_count = 0
    job = IngestionJob(document_id=d.id, actor=user.email, stage="QUEUED", progress=0)
    db.add(job)
    db.commit()
    _audit(db, user, "admin.doc.replace", ref_id=d.id, query=f"{d.doc_title} -> {d.version}")
    db.commit()
    bt.add_task(_ingest_one, str(d.id), str(job.id))
    return {"id": d.id, "version": d.version, "status": d.status, "job_id": job.id}


# ---------------------------------------------------------------- T7.5 usage & quota

RATE_SOURCES = "docs/PRICING.md — override RATES in services/pricing.py with contract rates before billing use"


def estimate_cost(provider: str, model: str, answers: int) -> float:
    """Rough order-of-magnitude estimate per persisted answer (EXAMPLE rates, not a bill)."""
    table = {("openai", "gpt-4o"): 0.004, ("openrouter", "openai/gpt-4o"): 0.004,
             ("openrouter", "anthropic/claude-sonnet-4.5"): 0.005}
    return round(table.get((provider, model), 0.004) * answers, 4)


def _usage_summary(db: Session, days: int) -> dict:
    from datetime import datetime, timedelta, timezone
    from ..services.pricing import estimate_cost as _est, monthly_spend
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(LLMUsage).filter(LLMUsage.created_at >= since).all()
    by_model: dict[str, dict] = {}
    for r in rows:
        key = f"{r.provider}/{r.model}"
        slot = by_model.setdefault(key, {"answers": 0, "failures": 0})
        slot["answers"] += 1
        if not r.ok:
            slot["failures"] += 1
    out = []
    for key, slot in by_model.items():
        provider, _, model = key.partition("/")
        out.append({**slot, "provider": provider, "model": model,
                    "est_cost_usd": _est(provider, model, slot["answers"])})
    spend_30d, _ = monthly_spend(db)
    return {"days": days, "total_answers": len(rows), "by_model": out,
            "rates": RATE_SOURCES, "spend_30d_usd": spend_30d,
            "budget_cap_usd": settings.BUDGET_USD_CAP}


@router.get("/usage")
def usage(days: int = 30, db: Session = Depends(get_db), user=Depends(admin_only)):
    return _usage_summary(db, min(max(days, 1), 365))


@router.post("/users/{uid}/quota")
def set_quota(uid: str, body: dict, db: Session = Depends(get_db), user=Depends(admin_only)):
    u = db.get(User, uid)
    if not u:
        raise HTTPException(404, "User not found")
    q = body.get("quota_queries")
    if q is not None and (not isinstance(q, int) or q < 0):
        raise HTTPException(400, "quota_queries must be a non-negative integer or null")
    u.quota_queries = q
    _audit(db, user, "admin.user.quota", ref_id=u.id, query=f"quota={q}")
    db.commit()
    return {"ok": True, "quota_queries": u.quota_queries}


# ---------------------------------------------------------------- T7.6 gateway runtime config

@router.get("/gateway")
def get_gateway(db: Session = Depends(get_db), user=Depends(super_only)):
    cfg = db.get(GatewayConfig, 1)
    eff = llm_gateway.effective()
    return {"stored": {"primary_model": cfg.primary_model, "fallback_model": cfg.fallback_model,
                       "timeout_s": cfg.timeout_s, "max_retries": cfg.max_retries,
                       "provider_order": cfg.provider_order,
                       "updated_by": cfg.updated_by,
                       "updated_at": str(cfg.updated_at)} if cfg else None,
            "effective": eff,
            "note": "API keys always come from environment, never from runtime config."}


@router.put("/gateway")
def put_gateway(body: dict, db: Session = Depends(get_db), user=Depends(super_only)):
    primary = str(body.get("primary_model", "")).strip()
    fallback = str(body.get("fallback_model", "")).strip()
    order = str(body.get("provider_order", "openrouter,openai")).strip().lower()
    try:
        timeout = int(body.get("timeout_s", 45))
        retries = int(body.get("max_retries", 1))
    except (TypeError, ValueError):
        raise HTTPException(400, "timeout_s and max_retries must be integers")
    if not primary or not fallback:
        raise HTTPException(400, "primary_model and fallback_model are required")
    if not (5 <= timeout <= 120) or not (0 <= retries <= 3):
        raise HTTPException(400, "timeout_s must be 5..120 and max_retries 0..3")
    parts = [p.strip() for p in order.split(",") if p.strip()]
    if set(parts) != {"openai", "openrouter"}:
        raise HTTPException(400, "provider_order must list exactly openai,openrouter in any order")
    cfg = db.get(GatewayConfig, 1) or GatewayConfig(id=1)
    cfg.primary_model, cfg.fallback_model = primary, fallback
    cfg.timeout_s, cfg.max_retries, cfg.updated_by = timeout, retries, user.email
    cfg.provider_order = ",".join(parts)
    db.add(cfg)
    _audit(db, user, "admin.gateway.update", query=f"{primary} / {fallback} / {cfg.provider_order}")
    db.commit()
    llm_gateway.apply_runtime(primary, fallback, timeout, retries, cfg.provider_order)
    return {"ok": True, "effective": llm_gateway.effective()}
