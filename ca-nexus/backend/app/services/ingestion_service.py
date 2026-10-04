"""PDF/PNG extraction (Q-EXT-01..06, T2.5/T2.6).

- Native text via PyMuPDF per page; pages with < SCAN_THRESHOLD chars are flagged
  `needs_ocr` (never reported as full success).
- `raw_text` (verbatim extraction) is kept separate from `norm_text` (whitespace
  normalized, tags upper-cased with mapping back to source form).
- PNGs are images: no text extraction claimed. `describe_png` returns a vision
  description with provenance when a vision model is configured, else a stub
  record marked `vision_pending=true`.
"""
from pathlib import Path

SCAN_THRESHOLD = 50


def extract_pdf(path: Path) -> list[dict]:
    import fitz
    pages = []
    with fitz.open(path) as doc:  # DEL-B3: context manager closes the handle
        for i, page in enumerate(doc):
            raw = page.get_text("text") or ""
            norm = " ".join(raw.split())
            try:
                tables = page.find_tables()
                table_count = len(list(tables))
            except Exception:
                table_count = -1  # -1 = detection unsupported here, flagged not failed
            pages.append({
                "page": i + 1,
                "raw_text": raw,
                "norm_text": norm,
                # backward-compat key used by older callers
                "text": raw,
                "chars": len(raw),
                "needs_ocr": len(raw.strip()) < SCAN_THRESHOLD,
                "table_count": table_count,  # DEL-B3: layout beyond tables is out of slice (see AUDIT.md)
                "method": "pymupdf-text",
            })
    return pages


def chunk_text(text: str, size: int = 1000, overlap: int = 100) -> list[str]:
    toks = text.split()
    if not toks:
        return []
    out, i = [], 0
    step = max(size - overlap, 1)
    while i < len(toks):
        piece = " ".join(toks[i:i + size])
        if piece.strip():
            out.append(piece)
        i += step
    return out


def describe_png(path: Path, vision_text: str | None = None) -> dict:
    """Never claim OCR text = connectivity understanding (T2.6)."""
    if vision_text:
        return {"text": vision_text, "method": "gpt-4o-vision",
                "vision_pending": False, "region": "full-image"}
    return {
        "text": f"[P&ID image] {path.name}: vision description pending — no tags extracted yet.",
        "method": "stub", "vision_pending": True, "region": "full-image",
    }
