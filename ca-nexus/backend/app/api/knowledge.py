import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from ..core.database import get_db
from ..core.deps import get_current_user
from ..core.config import settings
from ..core import policy as access_policy
from ..models.maintenance import Document

log = logging.getLogger("mkh.knowledge")
router = APIRouter(prefix="/knowledge", tags=["knowledge"])
STORE = Path(settings.FILE_STORAGE_ROOT)
SOURCE = Path(settings.SOURCE_ROOT)


def _like_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("/documents")
def list_docs(equipment_tag: str = "", doc_type: str = "", q: str = "",
              status: str = "", page: int = 1, per_page: int = 20,
              sort: str = "newest",
              db: Session = Depends(get_db), user=Depends(get_current_user)):
    per_page = min(max(per_page, 1), 100)
    page = max(page, 1)
    if sort not in ("newest", "title", "equipment"):
        raise HTTPException(400, "sort must be newest|title|equipment")
    query = db.query(Document)
    if equipment_tag:
        query = query.filter(Document.equipment_tag == equipment_tag.upper())
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    if status:
        if status not in ("PARSING", "VECTORIZING", "READY", "FAILED"):
            raise HTTPException(400, "Unknown status")
        query = query.filter(Document.status == status)
    if q:
        query = query.filter(Document.doc_title.ilike(f"%{_like_escape(q)}%", escape="\\"))
    # T3.6: hide non-READY from non-admins; T3.4: scope filter
    items = []
    for d in query.all():
        if d.status != "READY" and user.role not in ("admin", "super_admin"):
            continue
        if not access_policy.doc_visible(d.division_access, user.division, user.role):
            continue
        items.append({"id": d.id, "equipment_tag": d.equipment_tag, "doc_type": d.doc_type,
                      "doc_title": d.doc_title, "division_access": d.division_access,
                      "access_reviewed": d.access_reviewed, "version": d.version,
                      "status": d.status, "page_count": d.page_count,
                      "created_at": str(d.created_at)})
    if sort == "title":
        items.sort(key=lambda x: x["doc_title"].lower())
    elif sort == "equipment":
        items.sort(key=lambda x: (x["equipment_tag"], x["doc_title"].lower()))
    else:
        items.sort(key=lambda x: x["created_at"] or "", reverse=True)
    total = len(items)
    start = (page - 1) * per_page
    return {"total": total, "page": page, "per_page": per_page, "items": items[start:start + per_page]}


@router.get("/documents/{doc_id}")
def document_detail(doc_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.get(Document, doc_id)
    if not d or not access_policy.doc_visible(d.division_access, user.division, user.role):
        raise HTTPException(404, "Document not found or not authorized")
    if d.status != "READY" and user.role not in ("admin", "super_admin"):
        raise HTTPException(409, f"Document not ready (status={d.status})")
    return {"id": d.id, "equipment_tag": d.equipment_tag, "doc_type": d.doc_type,
            "doc_title": d.doc_title, "division_access": d.division_access,
            "access_reviewed": d.access_reviewed, "version": d.version,
            "status": d.status, "page_count": d.page_count,
            "checksum": d.checksum, "created_at": str(d.created_at)}


def _resolve_file(d: Document) -> Path:
    # Registry-only: file_path must be relative; absolute DB values rejected (T-clean-1)
    rel = Path(d.file_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise HTTPException(400, "Invalid stored path")
    fp = STORE / rel
    if fp.exists():
        return fp
    cand = SOURCE / rel
    if cand.exists():
        return cand
    # Legacy absolute-layout fallback: match by title under source root
    matches = list(SOURCE.rglob(d.doc_title))
    if matches:
        return matches[0]
    raise HTTPException(404, "File missing on server")


@router.get("/file/{doc_id}")
def get_file(doc_id: str, page: int | None = None,
             db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.get(Document, doc_id)
    if not d or not access_policy.doc_visible(d.division_access, user.division, user.role):
        raise HTTPException(404, "Document not found or not authorized")
    if d.status != "READY":
        raise HTTPException(409, f"Document not ready (status={d.status})")
    if page is not None and not (1 <= page <= max(d.page_count, 1)):
        raise HTTPException(400, "Invalid page locator")
    fp = _resolve_file(d)
    headers = {"X-Document-Id": d.id, "X-Document-Version": d.version}
    return FileResponse(str(fp), filename=d.doc_title, headers=headers)


@router.get("/file-by-path")
def get_file_by_path(path: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Resolve via Document registry only (no arbitrary path) — Q-CIT-01, D-18
    docs = [d for d in db.query(Document).filter(Document.file_path == path).all()
            if access_policy.doc_visible(d.division_access, user.division, user.role)
            and d.status == "READY"]
    if not docs:
        raise HTTPException(404, "Source not found, not ready, or not authorized")
    return get_file(docs[0].id, db, user)
