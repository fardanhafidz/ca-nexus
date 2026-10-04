# DEL-I3 / T8.5 — Runbook (clean-environment reproduce)

## 0. Batasan path workspace (penting)
Direktori repo ini mengandung karakter `!` (`.../! Hackathon/...`). Webpack memakai
`!` untuk loader syntax, sehingga `npm run build` GAGAL bila dijalankan langsung di
path ini (ValidationError `contains exclamation mark`). Ini bukan bug kode:
- Build produksi frontend tetap sah via Docker (webpack jalan di `/app` dalam image).
- Untuk `npm run build` lokal: salin `frontend/` ke path tanpa `!`, lalu
  `npm ci && npm run build` (terbukti 2026-09-21: 9 route OK).
- `tsc --noEmit`, `pytest`, dan `run_checks.py` tidak terpengaruh `!`.

## 1. Prasyarat
Docker 24+ (`docker compose version`), 4 CPU / 8 GB RAM / 20 GB SSD,
satu dari `OPENAI_API_KEY` / `OPENROUTER_API_KEY` (retrieval jalan tanpanya,
jawaban LLM memakai fallback ekstraktif).

## 2. Boot bersih
```bash
cd manufacturing-knowledge-hub
cp .env.example .env   # isi JWT_SECRET (64 hex), API key, BOOTSTRAP_ADMIN_* sekali saja
docker compose up --build -d
docker compose ps                    # 4 service healthy (postgres, qdrant, backend, frontend)
curl http://localhost:8000/health    # {"ok": true}
```

## 3. Schema + data (dari host atau container backend)
```bash
alembic upgrade head                                             # T1.5 deploy path (bukan create_all)
python scripts/build_manifest.py --source ../supporting_data --out data/manifest.json
python scripts/seed_maintenance.py --xlsx "../supporting_data/Case 1_ Manufacturing Knowledge Hub/Maintenance History (All Equipment).xlsx"
python scripts/ingest_docs.py --source ../supporting_data --limit 20   # pełny load: hapus --limit
```

## 4. Checks
```bash
pytest backend/tests -q
python backend/tests/run_checks.py
python scripts/eval_golden.py   # butuh DATABASE_URL + QDRANT_URL + data ter-ingest
```

## 5. Backup / restore / rollback
```bash
docker compose exec postgres pg_dump -U mkh mkh > backup_mkh_$(date +%F).sql
docker volume ls | grep -E "pgdata|qdrant_storage|filedata"   # persistensi Qdrant + file
# restore: psql < backup file ke DB kosong, lalu alembic upgrade head
# rollback rilis: docker compose down && git checkout <tag> && docker compose up --build
```
Retensi: lihat `docs/RETENTION.md`. Deployment catat: DB analitik HARUS role
read-only (`GRANT SELECT`), `statement_timeout` 5 dtk sudah di `sql_service.run`
untuk postgres (DEL-B7).

## 5b. Role read-only analitik (T4.6 deployment requirement)
Validasi query di kode bukan pengganti hak akses DB. Terapkan di postgres produksi:
```sql
CREATE ROLE mkh_reader WITH LOGIN PASSWORD '<secret>';
GRANT CONNECT ON DATABASE mkh TO mkh_reader;
GRANT USAGE ON SCHEMA public TO mkh_reader;
GRANT SELECT ON maintenance_records TO mkh_reader;
ALTER ROLE mkh_reader SET statement_timeout = '5s';
```
Jalankan service analitik/`sql_service` dengan `DATABASE_URL` user `mkh_reader`.
Verifikasi: `UPDATE maintenance_records SET ...` sebagai `mkh_reader` harus ditolak
(`permission denied`), SELECT agregat tetap jalan.

## 6. CI (DEL-I3)
`.github/workflows/ci.yml`: backend `py_compile` + sqlite checks + frontend
`tsc --noEmit` + `next lint` + `docker compose config` (validasi compose tanpa run).
