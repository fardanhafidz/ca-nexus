# T8.3 — E2E Checklist (hanya centang dengan bukti di docs/VERIFICATION-LOG.md)

Legenda: `[x …]` = terbukti live 2026-09-28 via `e2e_http.py` (uvicorn + sqlite + cookie,
tanpa Qdrant/LLM key) kecuali disebut lain. Sisanya TETAP TERBUKA.

## Auth & access (T3.7)
- [x 2026-09-28] Register Mechanical user → status pending → visible in `/admin/users?status=pending`
- [x 2026-09-28] Approve WITH division allocation → login OK → `/auth/me` shows division
- [ ] Direct `GET /knowledge/file/{other-division-id}` as user → 404 (hanya unit-test resolver + archive-404 live)
- [ ] Direct SQL aggregate as Mechanical excludes Instrument-discipline rows (hanya unit-test policy)

## RAG & citations (T4.11 + G-01..G-09)
- [x 2026-10-01] G-01/G-02/G-03 retrieval hit via `eval_golden.py` (PG + Qdrant riil, full ingest)
- [x 2026-09-28] G-04 KPI table shows SQL + reproducible re-run + xlsx row_reference (sitasi workbook ter-resolve)
- [x 2026-10-01] G-08 MTBF → `insufficient_evidence=true` live (route unsupported, tanpa angka)
- [ ] Inspector PDF opens `#page=`; PNG shows region; XLSX shows rows (manual UI)

## Multimodal & history (T5.x)
- [ ] PNG upload (5 MB limit enforced) → `detected_tags` + confirmation hint when != 1 tag
- [x 2026-09-28] SSE `/ask-stream` emits progress → final → done (abort/disconnect: kode ada, belum live)
- [ ] Sidebar reopen renders stored payload version + citations unchanged

## Admin (T7.x)
- [x 2026-10-01] Upload PDF → PARSING → VECTORIZING → READY live (probe) dengan page/chunk counts
- [x 2026-10-01] Upload XLSX rejected with seed_maintenance pointer (live 400 + pesan)
- [x 2026-09-28 sebagian] `/admin/audit` — event chat + admin tercatat (assert DB count); UI filter/pagination belum diklik live
