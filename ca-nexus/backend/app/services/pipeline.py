"""T2.9 — Unified ingestion pipeline.

Single code path for CLI (`scripts/ingest_docs.py`) and Admin upload
(`api/admin.py`), replacing the previously divergent implementations.

- Per-page `page_number` preserved (no hardcode).
- Stable chunk IDs: sha256(doc_checksum + page + chunk_index) → reindex is idempotent.
- No silent truncation: caller sets `max_chunks`; overflow is reported, not dropped quietly.
- XLSX is NOT routed here (workbook goes through seed_maintenance, T2.3).
- Returns a per-file quality report (scan flags, counts, errors).
"""
from __future__ import annotations
import hashlib, logging
from pathlib import Path
from . import ingestion_service
from ..core.config import settings

log = logging.getLogger("mkh.pipeline")


def stable_chunk_id(checksum: str, page: int, idx: int) -> str:
    return hashlib.sha256(f"{checksum}:{page}:{idx}".encode()).hexdigest()[:32]


def checksum_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def prepare_pdf(path: Path, checksum: str, max_chunks: int = 0) -> tuple[list[dict], dict]:
    pages = ingestion_service.extract_pdf(path)
    chunks: list[dict] = []
    scan_pages = [p["page"] for p in pages if p["needs_ocr"]]
    idx = 0
    for p in pages:
        for c in ingestion_service.chunk_text(p["norm_text"] or p["raw_text"],
                                              size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP):
            chunks.append({"page": p["page"], "text": c,
                           "id": stable_chunk_id(checksum, p["page"], idx),
                           "needs_ocr": p["needs_ocr"]})
            idx += 1
    truncated = 0
    if max_chunks and len(chunks) > max_chunks:
        truncated = len(chunks) - max_chunks
        chunks = chunks[:max_chunks]
    report = {"pages": len(pages), "chunks": len(chunks), "scan_pages": scan_pages,
              "truncated": truncated, "method": "pymupdf-text"}
    return chunks, report


def prepare_png(path: Path, checksum: str, vision_text: str | None = None) -> tuple[list[dict], dict]:
    desc = ingestion_service.describe_png(path, vision_text)
    chunk = {"page": 1, "text": desc["text"], "id": stable_chunk_id(checksum, 1, 0),
             "vision_pending": desc.get("vision_pending", True)}
    return [chunk], {"pages": 1, "chunks": 1, "scan_pages": [],
                     "vision_pending": desc.get("vision_pending", True), "method": desc["method"]}


def prepare_png_with_vision(path: Path, checksum: str) -> tuple[list[dict], dict]:
    """T2.6: vision description enters the pipeline when a vision provider is
    configured; otherwise the honest vision_pending stub is kept (never fake OCR)."""
    try:
        from . import llm_gateway
        vision_text = llm_gateway.vision_extract_tags(path.read_bytes())
    except Exception:
        vision_text = ""
    return prepare_png(path, checksum, vision_text or None)


def upsert_chunks(chunks: list[dict], meta: dict) -> int:
    """Embed in batches and upsert with stable IDs. Returns point count."""
    from . import vector_service  # lazy: keeps CLI/tests importable without qdrant/openai
    if not chunks:
        return 0
    B = 32
    total = 0
    for i in range(0, len(chunks), B):
        batch = chunks[i:i + B]
        vecs = vector_service.embed([c["text"] for c in batch])
        vector_service.upsert(
            [{"id": c["id"], "vector": v,
              "payload": {"text": c["text"][:2000], "equipment_tag": meta.get("equipment_tag", ""),
                          "doc_type": meta.get("doc_type", "other"), "doc_title": meta.get("doc_title", ""),
                          "division_access": meta.get("division_access", "All"),
                          "page_number": c["page"], "file_path": meta.get("file_path", ""),
                          "needs_ocr": c.get("needs_ocr", False),
                          "vision_pending": c.get("vision_pending", False)}}
             for c, v in zip(batch, vecs)])
        total += len(batch)
    return total
