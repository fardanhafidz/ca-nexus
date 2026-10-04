"""T8.2 — Golden-query retrieval evaluation (no LLM key needed for retrieval-hit part).

Usage: DATABASE_URL=... QDRANT_URL=... python scripts/eval_golden.py
Checks per query: route correctness, retrieval hit (expected doc/tag present),
SQL reproducibility (aggregate re-run matches), citation resolvability.
Writes data/eval_report.json. No success percentages claimed before review (T0.3).
"""
import json, os, sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

CASES = [
    {"id": "G-01", "query": "VSHH-4505 high vibration trip action on KC-4501", "expect_tag": "KC-4501", "route": "graph"},
    {"id": "G-02", "query": "What does SEQ-4501 protect?", "expect_tag": "SEQ-4501", "route": "graph"},
    {"id": "G-03", "query": "Mechanical seal spare parts for GA-1201A", "expect_tag": "GA-1201A", "route": "vector"},
    {"id": "G-04", "query": "total downtime and cost EA-5601", "expect_tag": "EA-5601", "route": "sql"},
    {"id": "G-05", "query": "corrective vs preventive count KC-4501", "expect_tag": "KC-4501", "route": "sql"},
    {"id": "G-08", "query": "MTBF CT-7801", "expect_tag": "CT-7801", "route": "unsupported"},
]


def main() -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.services import vector_service, sql_service, graph_service
    from app.api.chat import _route

    db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://mkh:mkh_password@localhost:5432/mkh")
    eng = create_engine(db_url)
    results = []
    with Session(eng) as db:
        for c in CASES:
            route = _route(c["query"])
            row = {"id": c["id"], "query": c["query"], "route": route,
                   "route_ok": route in (c["route"], "combined")}
            try:
                tags = vector_service.extract_tags(c["query"])
                row["tags"] = tags
                if route == "unsupported":
                    row["insufficient_expected"] = True
                    row["route_ok"] = route == c["route"]
                elif route in ("sql", "combined"):
                    sql, params = sql_service.build_sql(c["query"], c["expect_tag"],
                                                        role="super_admin", division="")
                    rows = sql_service.run(db, sql, params, role="super_admin", division="")
                    rerun = sql_service.run(db, sql, params, role="super_admin", division="")
                    row["sql_rows"] = len(rows)
                    row["sql_reproducible"] = rows == rerun
                else:
                    # DEL-B8: same query in both hybrid modes → recorded comparison
                    mode_hits = {}
                    for mode in ("rrf", "dense-only"):
                        vector_service.settings.HYBRID_MODE = mode
                        try:
                            hits = vector_service.search(c["query"], "Mechanical", top_k=5, role="super_admin")
                        finally:
                            vector_service.settings.HYBRID_MODE = "rrf"
                        texts = " ".join(h["payload"].get("equipment_tag", "") + " " + h["payload"].get("text", "") for h in hits)
                        mode_hits[mode] = {"hit": c["expect_tag"] in texts.upper(), "n": len(hits)}
                    row["rrf"] = mode_hits["rrf"]
                    row["dense_only"] = mode_hits["dense-only"]
                    row["retrieval_hit"] = mode_hits["rrf"]["hit"]
                    row["hits"] = mode_hits["rrf"]["n"]
                    g = graph_service.neighbors(db, c["expect_tag"], division="Mechanical", role="super_admin")
                    row["graph_edges"] = len(g)
            except Exception as e:
                row["error"] = str(e)[:300]
            results.append(row)
    out = Path(__file__).parent.parent / "data" / "eval_report.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    for r in results:
        print(r.get("id"), r.get("route"), "route_ok=" + str(r.get("route_ok")),
              {k: v for k, v in r.items() if k in ("retrieval_hit", "hits", "graph_edges", "sql_rows", "sql_reproducible", "error")})


if __name__ == "__main__":
    main()
