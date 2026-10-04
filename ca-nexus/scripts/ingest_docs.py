"""T2.5/T2.7/T2.8 — Ingest PDFs/PNGs via the unified pipeline (services/pipeline.py).

- Division comes from --division-map (data/division_map.json) or --division flag.
  Files without mapping are stored with division_access from defaults AND
  access_reviewed=false (UNREVIEWED) — never silently guessed (T2.4).
- XLSX is rejected here (use seed_maintenance.py, T2.3).
- Stable chunk IDs → re-runs upsert, never duplicate.
- --max-chunks bounds cost; overflow is reported per file, not silently cut.
"""
import argparse, json, os, re, sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

EQUIP_RE = re.compile(r"(GA-1201A|YD-2301|DC-3401A|KC-4501|EA-5601|LV-6701|CT-7801|FA-8901)", re.I)
EQUIP_ALIAS_RE = re.compile(r"\b(GA|YD|DC|KC|EA|LV|CT|FA)[\s_]+(\d{3,5}[A-Z]?)\b", re.I)


def resolve_tag(*texts: str) -> tuple[str, bool]:
    """DEL-B13: exact match first, then alias variants (spaces/underscores).
    Returns (tag, from_alias). Unknown tags return ("", False) — never guessed."""
    for t in texts:
        m = EQUIP_RE.search(t or "")
        if m:
            return m.group(1).upper(), False
    for t in texts:
        m = EQUIP_ALIAS_RE.search(t or "")
        if m:
            return f"{m.group(1).upper()}-{m.group(2).upper()}", True
    return "", False


def guess_type(name: str) -> str:
    n = name.lower()
    if "opl" in n or "one point" in n:
        return "opl"
    if "datasheet" in n:
        return "datasheet"
    if "drawing" in n:
        return "drawing"
    if "interlock" in n:
        return "interlock"
    if "plot" in n:
        return "plot_plan"
    if "p&id" in n or "pid" in n or n.endswith(".png"):
        return "pid"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="supporting_data")
    ap.add_argument("--db", default=os.environ.get("DATABASE_URL", "postgresql+psycopg2://mkh:mkh_password@localhost:5432/mkh"))
    ap.add_argument("--qdrant", default=os.environ.get("QDRANT_URL", "http://localhost:6333"))
    ap.add_argument("--division-map", default=os.path.join(os.path.dirname(__file__), "..", "data", "division_map.json"))
    ap.add_argument("--division", default="", help="Override division for all files in this run")
    ap.add_argument("--max-chunks", type=int, default=400)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.maintenance import Document, KnowledgeEdge
    from app.services import pipeline, vector_service
    from app.core import config as cfg
    cfg.settings.QDRANT_URL = a.qdrant

    dmap = {"defaults": {}, "by_title": {}}
    if os.path.exists(a.division_map):
        dmap = json.loads(Path(a.division_map).read_text(encoding="utf-8"))

    root = Path(a.source)
    if root.name == "supporting_data" and (root / "Case 1_ Manufacturing Knowledge Hub").exists():
        root = root / "Case 1_ Manufacturing Knowledge Hub"
    files = [p for p in root.rglob("*") if p.suffix.lower() in (".pdf", ".png") and p.is_file()]
    xlsx = [p for p in root.rglob("*") if p.suffix.lower() in (".xlsx", ".xls") and p.is_file()]
    if xlsx:
        print(f"NOTE: {len(xlsx)} workbook(s) skipped here — import via seed_maintenance.py (T2.3)")
    if a.limit:
        files = sorted(files)[:a.limit]
    print(f"found {len(files)} files under {root}")
    eng = create_engine(a.db)
    Base.metadata.create_all(eng)
    vector_service.ensure_collection()
    n_docs, n_chunks, n_flagged = 0, 0, 0
    with Session(eng) as s:
        for fp in sorted(files):
            tag, from_alias = resolve_tag(fp.name, str(fp.parent))
            if from_alias:
                print(f"  NOTE alias-resolved tag {tag}: {fp.name}")
            if not tag:
                print(f"  SKIP unknown equipment tag: {fp}")
                continue
            dtype = guess_type(fp.name)
            title = fp.name
            rel = str(fp.relative_to(root))
            checksum = pipeline.checksum_of(fp)
            if a.division:
                access, reviewed = a.division, True
            elif title in dmap.get("by_title", {}):
                access, reviewed = dmap["by_title"][title], True
            else:
                access = dmap.get("defaults", {}).get(dtype, "All")
                reviewed = False  # UNREVIEWED — explicit policy, not a silent guess
            d = s.query(Document).filter(Document.checksum == checksum).first()
            if not d:
                d = s.query(Document).filter(Document.doc_title == title, Document.equipment_tag == tag).first()
            if not d:
                d = Document(equipment_tag=tag, doc_type=dtype, doc_title=title, file_path=rel,
                             division_access=access, access_reviewed=reviewed,
                             version="v1.0.0", status="PARSING", checksum=checksum)
                s.add(d)
                s.commit()
            else:
                d.file_path, d.division_access, d.checksum = rel, access, checksum
                if reviewed:
                    d.access_reviewed = True
                d.status = "PARSING"
                s.commit()
            try:
                if fp.suffix.lower() == ".pdf":
                    chunks, report = pipeline.prepare_pdf(fp, checksum, max_chunks=a.max_chunks)
                else:
                    chunks, report = pipeline.prepare_png_with_vision(fp, checksum)
                d.page_count = report["pages"]
                if report.get("scan_pages"):
                    print(f"  FLAG scan-like pages {report['scan_pages']}: {rel}")
                    n_flagged += 1
                if report.get("truncated"):
                    print(f"  NOTE truncated {report['truncated']} chunks (max {a.max_chunks}): {rel}")
                if report.get("vision_pending"):
                    print(f"  NOTE vision pending: {rel}")
                    n_flagged += 1
                d.status = "VECTORIZING"
                s.commit()
                n = pipeline.upsert_chunks(chunks, {"equipment_tag": tag, "doc_type": dtype,
                                                    "doc_title": title, "division_access": access,
                                                    "file_path": rel})
                n_chunks += n
                d.status = "READY"
                # DEL-B13: HAS_OPL evidence edge (deduped); revision pinned in evidence
                ev = f"{title}:{d.version}"
                exists = s.query(KnowledgeEdge).filter(
                    KnowledgeEdge.src_tag == tag, KnowledgeEdge.dst_tag == title,
                    KnowledgeEdge.relation == "HAS_OPL").first()
                if not exists:
                    s.add(KnowledgeEdge(src_tag=tag, dst_tag=title,
                                        relation="HAS_OPL", evidence_doc=ev))
                s.commit()
                n_docs += 1
            except Exception as e:
                print(f"  FAILED {rel}: {e}")
                d.status = "FAILED"  # FAILED is terminal for this run — never overwritten below
                s.commit()
    print(f"ingested {n_docs}/{len(files)} docs, {n_chunks} chunks, {n_flagged} flagged for review")


if __name__ == "__main__":
    main()
