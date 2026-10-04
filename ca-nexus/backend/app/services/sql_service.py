"""T4.6 — Read-only analytic templates over maintenance_records (D-10).

Formulas (agreed for slice-1, docs/DATA-DICTIONARY.md):
- Total Downtime (hours) = COALESCE(SUM(downtime_hours),0); NULL rows ignored (not 0-filled per-row).
- Total Cost (IDR)      = COALESCE(SUM(total_cost_idr),0); unit IDR, no conversion.
- Frequency             = COUNT(*) grouped by equipment_tag[, work_type].
- Timezone: naive workbook datetimes treated as plant local; no tz conversion in slice-1.
- MTBF/MTTR: NOT offered (formula unagreed → G-08 insufficient-evidence).

Safety: single SELECT only (no `;`, no multi-statement), LIMIT enforced ≤ 50,
division scope AND-ed via policy (T3.4), read-only enforced by validation
(deployments should additionally use a read-only DB role + statement_timeout).
"""
from __future__ import annotations
import logging, re
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..core import policy as access_policy

log = logging.getLogger("mkh.sql")
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|truncate|grant|exec|copy|call)\b", re.I)
AGG_RE = re.compile(r"(total|sum|average|avg|count|frequency|downtime|cost|breakdown|preventive|corrective|predictive|inspection|berapa|hour|idr|kpi)", re.I)
MAX_LIMIT = 50
# G-08 decision (easiest, recorded in docs/GOLDEN-QUERIES.md + SCOPE.md): MTBF/MTTR-family
# formulas are UNAGREED — never serve them from the downtime template. Callers must
# return insufficient-evidence instead of a number.
UNAGREED_RE = re.compile(r"\b(mtbf|mttr|mttf|oee|availability|failure rate|failure-rate)\b", re.I)


def unagreed_metric(query: str) -> bool:
    return bool(UNAGREED_RE.search(query or ""))


def needs_sql(query: str) -> bool:
    return bool(AGG_RE.search(query))


def build_sql(query: str, equipment: str | None, role: str = "user", division: str = "") -> tuple[str, dict]:
    q = query.lower()
    where = [access_policy.sql_discipline_filter(role, division)]
    params: dict = {}
    if equipment:
        where.append("equipment_tag = :tag")
        params["tag"] = equipment
    if "corrective" in q:
        where.append("work_type = 'Corrective'")
    elif "preventive" in q:
        where.append("work_type = 'Preventive'")
    elif "predictive" in q:
        where.append("work_type = 'Predictive'")
    elif "inspection" in q:
        where.append("work_type = 'Inspection'")
    w = f"WHERE {' AND '.join(where)}"
    if "cost" in q or "biaya" in q or "idr" in q:
        sql = (f"SELECT equipment_tag, COUNT(*) as wo_count, COALESCE(SUM(downtime_hours),0) as total_downtime, "
               f"COALESCE(SUM(total_cost_idr),0) as total_cost FROM maintenance_records {w} "
               f"GROUP BY equipment_tag ORDER BY total_cost DESC LIMIT {MAX_LIMIT}")
    elif "frequency" in q or "count" in q or "frekuensi" in q:
        sql = (f"SELECT equipment_tag, work_type, COUNT(*) as wo_count FROM maintenance_records {w} "
               f"GROUP BY equipment_tag, work_type ORDER BY wo_count DESC LIMIT {MAX_LIMIT}")
    else:
        sql = (f"SELECT equipment_tag, COUNT(*) as wo_count, COALESCE(SUM(downtime_hours),0) as total_downtime, "
               f"COALESCE(SUM(total_cost_idr),0) as total_cost FROM maintenance_records {w} "
               f"GROUP BY equipment_tag ORDER BY total_downtime DESC LIMIT {MAX_LIMIT}")
    validate(sql)
    return sql, params


def validate(sql: str) -> None:
    s = sql.strip().rstrip(";")
    if ";" in s or not re.match(r"(?i)^\s*select\b", s):
        raise ValueError("Only a single SELECT statement is allowed")
    if FORBIDDEN.search(s):
        raise ValueError("Forbidden keyword in analytic query")
    m = re.search(r"(?i)\blimit\s+(\d+)", s)
    if not m or int(m.group(1)) > MAX_LIMIT:
        raise ValueError(f"LIMIT 1..{MAX_LIMIT} required")


def run(db: Session, sql: str, params: dict, role: str = "user", division: str = "") -> list[dict]:
    validate(sql)
    try:
        # DEL-B7: bound analytic query time. Deployments must additionally use a
        # read-only DB role (see docs/RUNBOOK.md); validation above is not a substitute.
        if db.bind is not None and db.bind.dialect.name == "postgresql":
            db.execute(text("SET LOCAL statement_timeout = '5s'"))
        rows = db.execute(text(sql), params).mappings().all()
    except Exception:
        log.exception("analytic query failed")
        raise
    out = [dict(r) for r in rows]
    log.info("analytic rows=%d role=%s division=%s", len(out), role, division)
    return out
