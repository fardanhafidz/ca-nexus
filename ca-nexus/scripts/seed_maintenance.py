"""T2.3 — Maintenance seeding with reconciliation (D-09).

Modes: upsert (default, PK merge — safe re-run) | replace (explicit truncate, requires --confirm).
Every run writes an ImportBatch lineage row (source/sheet/sha/mode/accepted/rejected).
Coercion failures are per-record errors in the report — never silent NULLs at scale.
"""
import argparse, hashlib, os, sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.core.database import Base
from app.models.maintenance import MaintenanceRecord, KnowledgeEdge, ImportBatch, Document

COLMAP = {
    "WO_Number": "wo_number", "Notification_No": "notification_no",
    "Report_Date": "report_date", "Start_Date": "start_date",
    "Completion_Date": "completion_date", "Status": "status",
    "Equipment_Tag": "equipment_tag", "Equipment_Name": "equipment_name",
    "Functional_Location": "functional_location", "Area_Code": "area_code",
    "Area_Name": "area_name", "Plant": "plant", "Work_Type": "work_type",
    "Discipline": "discipline", "Priority": "priority", "Criticality": "criticality",
    "Problem_Description": "problem_description", "Root_Cause": "root_cause",
    "Corrective_Action": "corrective_action", "Spare_Parts_Used": "spare_parts_used",
    "Breakdown": "breakdown", "Downtime_Hours": "downtime_hours",
    "Labor_Hours": "labor_hours", "Labor_Cost_IDR": "labor_cost_idr",
    "Material_Cost_IDR": "material_cost_idr", "Total_Cost_IDR": "total_cost_idr",
    "Reported_By": "reported_by", "Executed_By": "executed_by",
    "Approved_By": "approved_by", "Related_Interlock": "related_interlock",
    "Remarks": "remarks",
}
SHEET_CANDIDATES = ["Maintenance History (All Equipm", "Maintenance History (All Equipment)"]


def sha_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.environ.get("DATABASE_URL", "postgresql+psycopg2://mkh:mkh_password@localhost:5432/mkh"))
    ap.add_argument("--xlsx", default=os.path.join(os.path.dirname(__file__), "..", "..", "supporting_data", "Case 1_ Manufacturing Knowledge Hub", "Maintenance History (All Equipment).xlsx"))
    ap.add_argument("--sheet", default="")
    ap.add_argument("--mode", choices=["upsert", "replace"], default="upsert")
    ap.add_argument("--confirm", action="store_true", help="Required for --mode replace")
    a = ap.parse_args()
    if a.mode == "replace" and not a.confirm:
        ap.error("--mode replace requires --confirm (destructive)")
    sheets = [a.sheet] if a.sheet else SHEET_CANDIDATES
    df = None
    used_sheet = ""
    for s in sheets:
        try:
            df = pd.read_excel(a.xlsx, sheet_name=s, engine="openpyxl")
            used_sheet = s
            break
        except ValueError:
            continue
    if df is None:
        raise SystemExit(f"Sheet not found, tried: {sheets}")
    missing = [c for c in COLMAP if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing workbook columns: {missing}")
    df = df.rename(columns=COLMAP)
    accepted, rejected, errors = 0, 0, []
    records = []
    for i, row in enumerate(df.to_dict("records")):
        try:
            clean = {}
            for k, v in row.items():
                if k not in COLMAP.values():
                    continue
                clean[k] = None if pd.isna(v) else v
            if not clean.get("wo_number"):
                raise ValueError("empty WO_Number")
            for c in ("report_date", "start_date", "completion_date"):
                clean[c] = pd.to_datetime(clean[c], errors="raise") if clean[c] is not None else None
            for c in ("downtime_hours", "labor_hours", "labor_cost_idr", "material_cost_idr", "total_cost_idr"):
                if clean[c] is not None:
                    clean[c] = float(clean[c])
            if clean.get("area_code") is not None:
                s_code = str(clean["area_code"])
                clean["area_code"] = s_code[:-2] if s_code.endswith(".0") else s_code
            records.append(clean)
            accepted += 1
        except Exception as e:
            rejected += 1
            errors.append({"row": int(i) + 2, "error": str(e)[:200]})
    eng = create_engine(a.db)
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        try:
            if a.mode == "replace":
                s.query(KnowledgeEdge).delete()
                s.query(MaintenanceRecord).delete()
            for r in records:
                s.merge(MaintenanceRecord(**r))
            # rebuild WO/interlock edges deterministically
            if a.mode == "upsert":
                s.query(KnowledgeEdge).filter(KnowledgeEdge.relation.in_(["HAS_INTERLOCK", "PROTECTS", "HAS_WO"])).delete(synchronize_session=False)
            for r in records:
                tag = str(r.get("equipment_tag") or "").upper().strip()
                il = str(r.get("related_interlock") or "").upper().strip()
                wo = str(r.get("wo_number") or "").strip()
                if tag and il and il not in ("", "NAN", "-", "NONE"):
                    s.add(KnowledgeEdge(src_tag=tag, dst_tag=il, relation="HAS_INTERLOCK", evidence_doc=f"Maintenance History:{wo}"))
                    s.add(KnowledgeEdge(src_tag=il, dst_tag=tag, relation="PROTECTS", evidence_doc=f"Maintenance History:{wo}"))
                if tag and wo:
                    s.add(KnowledgeEdge(src_tag=tag, dst_tag=wo, relation="HAS_WO", evidence_doc=f"Maintenance History:{wo}"))
            s.add(ImportBatch(source=a.xlsx, sheet=used_sheet, sha256=sha_of(a.xlsx),
                              mode=a.mode, accepted=accepted, rejected=rejected))
            # Register the workbook itself so SQL citations resolve (T4.9/Q-SQL-05).
            # File serving falls back to SOURCE_ROOT lookup by title (knowledge._resolve_file).
            wb_title = os.path.basename(a.xlsx)
            wb = s.query(Document).filter(Document.doc_title == wb_title).first()
            if not wb:
                wb = Document(equipment_tag="", doc_type="maintenance", doc_title=wb_title,
                              file_path=wb_title, division_access="All", access_reviewed=True,
                              version="v1.0.0", status="READY", checksum=sha_of(a.xlsx))
                s.add(wb)
            else:
                wb.status, wb.checksum = "READY", sha_of(a.xlsx)
            s.commit()
        except Exception:
            s.rollback()
            raise
    print(f"sheet={used_sheet} mode={a.mode} accepted={accepted} rejected={rejected}")
    for e in errors[:20]:
        print(f"  row {e['row']}: {e['error']}")
    if rejected:
        print(f"WARNING: {rejected} rows rejected (see above) — no silent drops")


if __name__ == "__main__":
    main()
