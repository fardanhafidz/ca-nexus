# Manufacturing Knowledge Hub — PoC CALIBER 2026

PoC for CALIBER 2026 Case 1. Audience: technical jury + Chandra Asri operations.
Decisions: per user Q-SCP..Q-WORK (final, binding for prototype).

## Quick start
```bash
cp .env.example .env
# fill OPENAI_API_KEY and/or OPENROUTER_API_KEY
docker compose up --build
# backend: http://localhost:8000/docs
# frontend: http://localhost:3000
```

## Seed
```bash
# inside backend container or locally with DATABASE_URL set
python scripts/seed_maintenance.py
python scripts/ingest_docs.py --source supporting_data --limit 20
```

Default super admin: `admin@chandraasri.com / Admin123!` (override via .env, change after first login).

## Structure
- `backend/` FastAPI + SQLAlchemy + Qdrant + OpenAI/gpt-4o + OpenRouter fallback
- `frontend/` Next.js 14 + Tailwind, English UI, Industrial Deep Blue #1E56A0
- `scripts/` ingestion + maintenance seeding (idempotent)

## Acceptance (Q-QA-01)
1. Login + division filter enforced.
2. OPL troubleshooting returns steps + citation.
3. Inspector opens original PDF page.
4. Downtime calc from Excel matches DB.

Data source root is configurable (`SOURCE_ROOT`); compose mounts `../supporting_data` read-only so no 98-file duplication into `scripts/data/`.
