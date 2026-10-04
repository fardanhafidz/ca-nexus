"""T3.4 — Shared access policy: single source of truth for every data path.

Catalog, file viewer, Qdrant, lexical, graph, SQL, chat history, attachments
all resolve scope here. Scope comes from backend identity — never from
client filters, prompt tags, or model output (docs/03 §5.1).
"""
from __future__ import annotations

# Discipline (maintenance row) -> divisions allowed to see the row (docs/DATA-DICTIONARY.md)
DISCIPLINE_DIVISIONS: dict[str, list[str]] = {
    "Mechanical": ["Mechanical"],
    "Instrument": ["Electrical & Instrumentation"],
    "Electrical": ["Electrical & Instrumentation"],
    "Process": ["Process / Operations"],
}


def is_privileged(role: str) -> bool:
    return role in ("admin", "super_admin")


def doc_visible(division_access: str | None, division: str, role: str) -> bool:
    if is_privileged(role):
        return True
    if division_access is None:
        return True  # legacy rows pre-T2.4 default to shared
    access = [a.strip() for a in division_access.split(",") if a.strip()]
    if not access:
        return False  # explicitly unlabeled → deny for users (explicit policy, T2.4)
    return "All" in access or division in access


def row_visible(discipline: str | None, division: str, role: str) -> bool:
    """Python-side row check mirroring the SQL filter (defense in depth)."""
    if is_privileged(role):
        return True
    if not discipline:
        return True
    allowed = DISCIPLINE_DIVISIONS.get(discipline.strip())
    if allowed is None:
        return True
    return division in allowed


def sql_discipline_filter(role: str, division: str) -> str:
    """SQL fragment AND-ed into every analytic query (T3.4/T4.6)."""
    if is_privileged(role):
        return "1=1"
    mapping = {
        "Mechanical": "('Mechanical')",
        "Electrical & Instrumentation": "('Instrument','Electrical')",
        "Process / Operations": "('Process')",
    }
    allowed = mapping.get(division)
    if allowed is None:
        return "1=1"
    return f"(discipline IS NULL OR discipline IN {allowed})"
