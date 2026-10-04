"""T4.5 — Relational graph traversal with entity resolution + access policy (Q-GRF-01..05).

- Both edge directions traversed (Equipment→Interlock and Interlock→Equipment).
- Ambiguous/unknown tags resolve to no expansion (never guessed).
- Policy applied BEFORE expansion results enter the LLM context: edges whose
  evidence document is outside the caller scope are dropped (T4.5 acceptance).
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from ..models.maintenance import KnowledgeEdge, Document, MaintenanceRecord
from ..core import policy as access_policy

KNOWN_EQUIPMENT = {"GA-1201A", "YD-2301", "DC-3401A", "KC-4501", "EA-5601", "LV-6701", "CT-7801", "FA-8901"}


def resolve(tag: str | None, db: Session) -> str | None:
    if not tag:
        return None
    t = tag.strip().upper()
    if t in KNOWN_EQUIPMENT:
        return t
    exists = db.query(KnowledgeEdge).filter(
        (KnowledgeEdge.src_tag == t) | (KnowledgeEdge.dst_tag == t)).first()
    if exists:
        return t
    return None  # unknown → no expansion, caller handles as no-graph-evidence


def neighbors(db: Session, tag: str | None, depth: int = 2,
              division: str = "", role: str = "user") -> list[dict]:
    resolved = resolve(tag, db) if tag else None
    if not resolved:
        return []
    # Evidence scope: map evidence_doc prefix to Document.division_access
    docs = {d.doc_title: d for d in db.query(Document).all()}
    out, seen, frontier = [], {resolved}, [resolved]
    for _ in range(max(depth, 0)):
        if not frontier:
            break
        edges = db.query(KnowledgeEdge).filter(
            (KnowledgeEdge.src_tag.in_(frontier)) | (KnowledgeEdge.dst_tag.in_(frontier))).all()
        nxt = []
        for e in edges:
            # T4.5 fix (release blocker): evidence WITHOUT a registry mapping is
            # UNTRUSTED — deny expansion. Default-allow ("All") leaked cross-division
            # traversal through unmapped evidence. NOTE: workbook check comes first
            # because its evidence also contains ":".
            if e.evidence_doc.startswith("Maintenance History:"):
                # Workbook evidence: scope follows the WO row's discipline (T3.4),
                # not a blanket Allow.
                wo = e.evidence_doc.split(":", 1)[1].strip()
                row = db.query(MaintenanceRecord).filter(
                    MaintenanceRecord.wo_number == wo).first()
                if row is None or not access_policy.row_visible(row.discipline, division, role):
                    continue
            elif ":" in e.evidence_doc:
                ev = docs.get(e.evidence_doc.split(":")[0])
                if ev is None:
                    continue  # unknown document → deny
                if not access_policy.doc_visible(ev.division_access, division, role):
                    continue
            else:
                continue  # no mappable evidence → deny
            other = e.dst_tag if e.src_tag in frontier else e.src_tag
            direction = "out" if e.src_tag in frontier else "in"
            out.append({"src": e.src_tag, "dst": e.dst_tag, "relation": e.relation,
                        "evidence": e.evidence_doc, "direction": direction})
            if other not in seen:
                seen.add(other)
                nxt.append(other)
        frontier = nxt
    # dedup preserving order
    seen_key, deduped = set(), []
    for g in out:
        k = (g["src"], g["dst"], g["relation"])
        if k not in seen_key:
            seen_key.add(k)
            deduped.append(g)
    return deduped[:50]
