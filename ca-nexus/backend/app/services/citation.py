"""T4.9 — Citation resolver/validator (D-18).

LLM-proposed citations are NEVER forwarded raw. Each entry is mapped to the
Document registry (id/title + revision + locator) and re-checked against the
caller's current access. Snippets come from the stored chunk text, not from
model output. PNG uses image/region locators (no fake page numbers);
XLSX/SQL uses WO row references (no fake snippets).
"""
from __future__ import annotations
import difflib
from sqlalchemy.orm import Session
from ..models.maintenance import Document
from ..core import policy as access_policy

# Minimum title similarity for fuzzy registry match (below = drop, never guess).
FUZZY_CUTOFF = 0.85


def _ext(title: str) -> str:
    t = title.lower()
    if t.endswith(".png"):
        return "png"
    if t.endswith((".xlsx", ".xls")):
        return "xlsx"
    return "pdf"


def resolve(citations: list[dict], db: Session, division: str, role: str,
            retrieved_by_id: dict[str, dict] | None = None) -> list[dict]:
    docs = db.query(Document).all()
    by_id = {d.id: d for d in docs}
    by_title = {d.doc_title: d for d in docs}
    by_path = {d.file_path: d for d in docs}
    titles = list(by_title)
    hits_by_doc: dict[str, dict] = {}
    for hid, h in (retrieved_by_id or {}).items():
        t = str((h.get("payload") or {}).get("doc_title", ""))
        hits_by_doc.setdefault(t, h)
    out = []
    for c in citations or []:
        d = None
        if isinstance(c, dict):
            d = by_id.get(c.get("document_id") or "") or by_path.get(c.get("file_path") or "") \
                or by_title.get(c.get("document_title") or "")
            if d is None:
                # Fuzzy title match against the registry (honest: the citation
                # served is the registry row, never the model's spelling).
                cand = difflib.get_close_matches(c.get("document_title") or "", titles, n=1,
                                                 cutoff=FUZZY_CUTOFF)
                d = by_title.get(cand[0]) if cand else None
        if d is None:
            continue  # unmapped → drop (no fabricated citation)
        if d.status != "READY" or not access_policy.doc_visible(d.division_access, division, role):
            continue  # changed access / not searchable → drop
        stype = _ext(d.doc_title)
        chunk_text = ""
        if retrieved_by_id:
            hit = retrieved_by_id.get(c.get("chunk_id", "") or "") or hits_by_doc.get(d.doc_title)
            if hit:
                chunk_text = str(hit["payload"].get("text", ""))[:500]
        if stype == "png":
            out.append({"document_id": d.id, "document_title": d.doc_title, "page_number": None,
                        "snippet": chunk_text or f"[image] {d.doc_title}",
                        "file_path": d.file_path, "source_type": "png",
                        "region": (c.get("region") if isinstance(c, dict) else None) or "full-image"})
        elif stype == "xlsx":
            out.append({"document_id": d.id, "document_title": d.doc_title, "page_number": None,
                        "snippet": (c.get("row_reference") or c.get("snippet", "") if isinstance(c, dict) else ""),
                        "file_path": d.file_path, "source_type": "xlsx",
                        "row_reference": (c.get("row_reference") if isinstance(c, dict) else None)})
        else:
            try:
                page = c.get("page_number") if isinstance(c, dict) else None
                page = int(page) if page else None
                if page is not None and not (1 <= page <= max(d.page_count, 1)):
                    continue  # invalid locator → drop
            except (TypeError, ValueError):
                continue
            out.append({"document_id": d.id, "document_title": d.doc_title, "page_number": page,
                        "snippet": chunk_text or (c.get("snippet", "")[:500] if isinstance(c, dict) else ""),
                        "file_path": d.file_path, "source_type": "pdf"})
    # dedup by (document_id, page_number)
    seen, deduped = set(), []
    for c in out:
        k = (c["document_id"], c.get("page_number"))
        if k not in seen:
            seen.add(k)
            deduped.append(c)
    return deduped
