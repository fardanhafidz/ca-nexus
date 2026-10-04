# Manufacturing Knowledge Hub — PoC (slice-1)

Scope: `docs/SCOPE.md` (proposal). Audit: `docs/AUDIT.md`. Golden queries: `docs/GOLDEN-QUERIES.md`.

## Quick start (T8.5 runbook)
```bash
cd ca-nexus
cp .env.example .env
# Fill: JWT_SECRET (random 64 hex chars), one of OPENAI_API_KEY / OPENROUTER_API_KEY,
# and BOOTSTRAP_ADMIN_* ONLY for the first bootstrap (empty afterwards).
docker compose up --build
# backend: http://localhost:8000/docs | frontend: http://localhost:3000
```
`NEXT_PUBLIC_API_BASE_URL` is baked at frontend **build** time via compose `build.args` —
changing it requires `docker compose up --build` (T1.4).

## Data (T1.1 — paths with spaces/`&`/case variants)
Commands below assume CWD = `ca-nexus/`. Quote paths in shells:
```bash
python scripts/build_manifest.py --source "../supporting_data" --out data/manifest.json
python scripts/seed_maintenance.py --xlsx "../supporting_data/Case 1_ Manufacturing Knowledge Hub/Maintenance History (All Equipment).xlsx"
python scripts/ingest_docs.py --source "../supporting_data" --limit 20
```
From workspace root, replace `../supporting_data` with `supporting_data`.
Compose mounts `../supporting_data` read-only — no 98-file duplication into `scripts/data/`.
OPL folder variants (`One Point Lesson`, `One Point Lesson (OPL)`, `OPL (One Point Lessons)`)
and PNG names (`PID_Set_01.png` … `P&ID_Set 8.png`) are resolved via `pathlib`, never hard-coded.

## Migrations (T1.5)
```bash
alembic upgrade head            # versioned schema (replaces create_all for deploys)
pytest backend/tests -q         # T8.1 integrity checks
```

## Acceptance (T0.3 golden set + E2E checklist in docs/)
1. Login + division filter enforced (incl. direct file/row access denied).
2. OPL troubleshooting returns steps + registry-checked citation.
3. Inspector opens original PDF page via authorized `file/{id}`.
4. Downtime/cost from Excel reproduces DB numbers + shows the SQL.
